"""Reproducible synthetic benchmark. Never reads or modifies personal documents."""

import argparse
import json
import math
import os
import platform
import statistics
import threading
import time
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from shiwen import __version__
from shiwen.library import Library


def rss_tree(pid):
    """Sample Linux process-tree RSS in bytes; other platforms report unavailable."""
    base = Path("/proc") / str(pid)
    try:
        rss = next(
            int(line.split()[1]) * 1024
            for line in (base / "status").read_text().splitlines()
            if line.startswith("VmRSS:")
        )
        children = (base / "task" / str(pid) / "children").read_text().split()
        return rss + sum(rss_tree(int(child)) or 0 for child in children)
    except (OSError, StopIteration):
        return None


def corpus(folder, count, target_bytes, mixed):
    """A fixed 70/20/10 Markdown/DOCX/PDF mix with known literal search results."""
    if mixed:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfgen.canvas import Canvas

        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    folder.mkdir()
    total = 0
    formats = {}
    for index in range(count):
        lines = [f"SHIWENID{index:06d} 离线部署 offline deployment 预算审批\n"]
        line = "文档保存在本地。搜索资料并检查上下文。Local documents remain private.\n"
        lines.extend(
            [line] * max(1, math.ceil((target_bytes - len(lines[0].encode())) / len(line.encode())))
        )
        content = "".join(lines)
        kind = "pdf" if mixed and index % 10 == 9 else "docx" if mixed and index % 10 >= 7 else "md"
        formats[kind] = formats.get(kind, 0) + 1
        path = folder / f"document-{index:06d}.{kind}"
        if kind == "md":
            path.write_text(content, encoding="utf-8")
        elif kind == "docx":
            paragraphs = "".join(
                f"<w:p><w:r><w:t>{escape(line.strip())}</w:t></w:r></w:p>" for line in lines
            )
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    "word/document.xml",
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                    + paragraphs
                    + "</w:body></w:document>",
                )
        else:
            canvas = Canvas(str(path), invariant=1)
            for start in range(0, len(lines), 45):
                canvas.setFont("STSong-Light", 10)
                for number, text in enumerate(lines[start : start + 45]):
                    canvas.drawString(40, 800 - number * 16, text.strip())
                canvas.showPage()
            canvas.save()
        os.utime(path, (1_700_000_000, 1_700_000_000))
        total += len(content.encode())
    return {"documents": count, "formats": formats, "source_text_bytes": total}


def percentile(values, fraction):
    return sorted(values)[math.ceil(len(values) * fraction) - 1]


def measure_queries(library, count, rounds):
    queries = [
        "离线部署",
        '"offline deployment"',
        "预算 审批",
        f"SHIWENID{count - 1:06d}",
        "不存在的基准短语",
    ]
    timings = {query: [] for query in queries}
    for _ in range(rounds):
        for query in queries:
            before = time.perf_counter()
            result = library.search(query=query)
            timings[query].append((time.perf_counter() - before) * 1000)
            expected = 0 if query == queries[-1] else 1 if query == queries[-2] else min(50, count)
            assert len(result["items"]) == expected, (query, len(result["items"]), expected)
    return {
        q: {
            "samples": len(v),
            "first_ms": v[0],
            "median_ms": statistics.median(v),
            "p95_ms": percentile(v, 0.95),
        }
        for q, v in timings.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="New directory for synthetic files and report")
    parser.add_argument("--documents", type=int, default=10_000)
    parser.add_argument("--bytes-per-document", type=int, default=10_240)
    parser.add_argument("--markdown-only", action="store_true")
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument(
        "--queries-only",
        action="store_true",
        help="Reuse this benchmark's existing index; save a separate search-report.json",
    )
    args = parser.parse_args()
    if args.documents < 1 or args.bytes_per_document < 128 or args.rounds < 1:
        parser.error("documents and rounds must be positive; bytes-per-document must be >=128")
    if args.queries_only:
        baseline = json.loads((args.directory / "report.json").read_text(encoding="utf-8"))
        library = Library(args.directory / "index")
        try:
            count = baseline["corpus"]["documents"]
            assert library.store.counts()["by_status"] == {"ready": count}
            before = time.perf_counter()
            library.search(query="离线部署")
            reopen_ms = (time.perf_counter() - before) * 1000
            report = {
                "version": __version__,
                "platform": platform.platform(),
                "python": platform.python_version(),
                "corpus": baseline["corpus"],
                "mode": (
                    "queries only, existing production index; no reindexing or OS cache eviction"
                ),
                "reopened_connection_first_query_ms": reopen_ms,
                "queries": measure_queries(library, count, args.rounds),
            }
            content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
            (args.directory / "search-report.json").write_text(content, encoding="utf-8")
            print(content, end="", flush=True)
        finally:
            library.close()
        return
    args.directory.mkdir(parents=True, exist_ok=False)
    fixture = corpus(
        args.directory / "documents",
        args.documents,
        args.bytes_per_document,
        not args.markdown_only,
    )
    library = Library(args.directory / "index")
    library.add_root(str(args.directory / "documents"))
    samples = []
    first_batch = None
    started = time.perf_counter()
    stopped = threading.Event()

    def monitor():
        nonlocal first_batch
        last_progress = started
        while not stopped.wait(0.05):
            sample = rss_tree(os.getpid())
            if sample is not None:
                samples.append(sample)
            if first_batch is None and library.progress["processed"] >= min(50, args.documents):
                first_batch = time.perf_counter() - started
            if time.perf_counter() - last_progress >= 30:
                print(f"Indexed {library.progress['processed']}/{args.documents}", flush=True)
                last_progress = time.perf_counter()

    watcher = threading.Thread(target=monitor, daemon=True)
    watcher.start()
    print("Indexing synthetic corpus with production isolated parsers...", flush=True)
    try:
        library.scan()
        indexing_seconds = time.perf_counter() - started
        counts = library.store.counts()
        assert counts["by_status"] == {"ready": args.documents}, counts
        timings = measure_queries(library, args.documents, args.rounds)
        # Reopen only the connection; this is not an OS-cold-cache measurement.
        library.close()
        library = Library(args.directory / "index")
        before = time.perf_counter()
        library.search(query="离线部署")
        reopen_ms = (time.perf_counter() - before) * 1000
        report = {
            "version": __version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "logical_cpus": os.cpu_count(),
            "python": platform.python_version(),
            "corpus": fixture,
            "parser": "production: one isolated spawned process per document",
            "indexing_seconds": indexing_seconds,
            "first_50_indexed_seconds_sampled": first_batch or indexing_seconds,
            "index_bytes": library.status()["disk_bytes"],
            "engine_and_parser_tree_peak_rss_bytes_sampled": max(samples) if samples else None,
            "engine_rss_bytes_after_queries": rss_tree(os.getpid()),
            "reopened_connection_first_query_ms": reopen_ms,
            "queries": timings,
            "limitations": [
                "Synthetic repetitive text, not representative user documents",
                "DOCX fixtures contain only word/document.xml, not complete Office packages",
                "Headless engine and parser memory only; excludes native GUI/WebKit",
                "50 ms RSS samples can miss short peaks",
                "No OS cache eviction; cold-search latency not measured",
                "Queries retrieve the first page (up to 50 documents)",
            ],
        }
        destination = args.directory / "report.json"
        destination.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    finally:
        stopped.set()
        watcher.join()
        library.close()


if __name__ == "__main__":
    main()
