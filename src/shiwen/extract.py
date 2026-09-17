"""Bounded, read-only extractors. No network, macros, or document rendering."""

import multiprocessing
import os
import time
import zipfile
from pathlib import Path

MAX_FILE = 100 * 1024 * 1024
MAX_TEXT = 10 * 1024 * 1024
MAX_PAGES = 1000
SUPPORTED = {".pdf", ".md", ".markdown", ".docx"}


class ExtractionError(Exception):
    pass


def _check_size(size: int) -> None:
    if size > MAX_TEXT:
        raise ExtractionError("text_limit")


def extract(path: Path) -> dict:
    if path.stat().st_size > MAX_FILE:
        raise ExtractionError("file_limit")
    suffix = path.suffix.lower()
    blocks = []
    status = "ready"
    if suffix in {".md", ".markdown"}:
        text = path.read_text(encoding="utf-8-sig")
        _check_size(len(text.encode("utf-8")))
        lines = text.splitlines(keepends=True)
        # Preserve source line coordinates; overlaps keep boundary phrases findable.
        for start in range(0, len(lines), 40):
            blocks.append(
                {"location": start + 1, "kind": "line", "text": "".join(lines[start : start + 42])}
            )
    elif suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(path, strict=False)
        if reader.is_encrypted:
            raise ExtractionError("encrypted")
        if len(reader.pages) > MAX_PAGES:
            raise ExtractionError("page_limit")
        size, empty = 0, 0
        for index, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            size += len(text.encode("utf-8"))
            _check_size(size)
            if not text.strip():
                empty += 1
            blocks.append({"location": index, "kind": "page", "text": text})
        if empty:
            status = "partial" if empty < len(reader.pages) else "no_text"
    elif suffix == ".docx":
        from defusedxml.ElementTree import fromstring

        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with zipfile.ZipFile(path) as archive:
            info = archive.getinfo("word/document.xml")
            if info.file_size > 32 * 1024 * 1024:
                raise ExtractionError("text_limit")
            tree = fromstring(archive.read(info))
        size = 0
        # Paragraph traversal also includes ordinary table cells in document order.
        for index, paragraph in enumerate(tree.iter(ns + "p"), 1):
            parts = []
            for node in paragraph.iter():
                if node.tag == ns + "t":
                    parts.append(node.text or "")
                elif node.tag in {ns + "tab", ns + "br", ns + "cr"}:
                    parts.append(" ")
            text = "".join(parts)
            size += len(text.encode("utf-8"))
            _check_size(size)
            if text.strip():
                blocks.append({"location": index, "kind": "paragraph", "text": text})
    else:
        raise ExtractionError("unsupported")
    if not any(block["text"].strip() for block in blocks):
        status = "no_text"
    return {"status": status, "blocks": blocks}


def _worker(path: str, sender) -> None:
    try:
        if os.name == "posix":
            import resource

            # CPU limit supplements the parent-enforced wall timeout.
            resource.setrlimit(resource.RLIMIT_CPU, (55, 60))
        sender.send(extract(Path(path)))
    except ExtractionError as exc:
        sender.send({"status": str(exc), "blocks": []})
    except UnicodeError:
        sender.send({"status": "encoding", "blocks": []})
    except PermissionError:
        sender.send({"status": "permission", "blocks": []})
    except Exception:
        # Parser exceptions may contain document content; don't leak them to logs.
        sender.send({"status": "parse_error", "blocks": []})
    finally:
        sender.close()


def extract_isolated(path: Path, timeout: float = 60, cancel=None) -> dict:
    if cancel is not None and cancel.is_set():
        return {"status": "cancelled", "blocks": []}
    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=_worker, args=(str(path), sender), daemon=True)
    process.start()
    sender.close()
    try:
        deadline = time.monotonic() + timeout
        while True:
            if cancel is not None and cancel.is_set():
                return {"status": "cancelled", "blocks": []}
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return {"status": "timeout", "blocks": []}
            if receiver.poll(min(remaining, 0.1)):
                try:
                    return receiver.recv()
                except EOFError:
                    return {"status": "parse_error", "blocks": []}
    finally:
        receiver.close()
        if process.is_alive():
            process.terminate()
        process.join(timeout=2)
        if process.is_alive():
            process.kill()
            process.join()
