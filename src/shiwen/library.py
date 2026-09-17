"""Index lifecycle, permission boundaries, and background reconciliation."""

import os
import sqlite3
import stat as stat_types
import threading
import time
import uuid
from pathlib import Path

from .discovery import SKIP_NAMES, linked_directory, local_disks
from .extract import MAX_FILE, SUPPORTED, extract_isolated
from .store import Store

EXCLUDED_NAMES = {
    "node_modules",
    "__pycache__",
    "venv",
    ".venv",
    "target",
    "$RECYCLE.BIN",
    "System Volume Information",
}


def placeholder(stat) -> bool:
    return bool(getattr(stat, "st_file_attributes", 0) & (0x1000 | 0x40000 | 0x400000))


class Library:
    def __init__(
        self, directory: Path, extractor=extract_isolated, automatic=False, disk_provider=None
    ):
        self.store = Store(directory)
        self.extractor = extractor
        self.operation = threading.RLock()
        self.stop_event = threading.Event()
        self.wake = threading.Event()
        self.thread = None
        self.observer = None
        self.progress = {"phase": "idle", "processed": 0, "discovered": 0, "error": None}
        self.revision = 0
        self.automatic = automatic
        self.disk_provider = disk_provider or local_disks
        self.blocked_paths = set()
        self.parser_thread = None
        if automatic:
            self._refresh_disks()

    def allowed(self, path: Path, check_file: bool = False) -> bool:
        if path.is_relative_to(self.store.directory) or any(
            path.is_relative_to(blocked) for blocked in self.blocked_paths
        ):
            return False
        roots = self.store.roots()
        included = False
        for root in roots:
            base = Path(root["path"])
            if not path.is_relative_to(base):
                continue
            relative = path.relative_to(base)
            if any(
                part in SKIP_NAMES
                if self.automatic
                else part.startswith(".") or part in EXCLUDED_NAMES
                for part in relative.parts
            ):
                return False
            if any(path.is_relative_to(base / rule) for rule in root["excluded"]):
                return False
            included = True
            if check_file:
                try:
                    # No symlinks/junctions may escape an explicitly selected root.
                    if (
                        path.resolve() != path
                        or not base.is_dir()
                        or not (path.is_file() or (self.automatic and path.is_dir()))
                    ):
                        return False
                    if any(
                        part.is_symlink() for part in [path, *path.parents] if part != base.parent
                    ):
                        return False
                    if not os.access(path, os.R_OK):
                        return False
                except OSError:
                    return False
        return included

    def add_root(self, path: str):
        with self.operation:
            result = self.store.add_root(Path(path))
            self.revision += 1
        self._watch()
        self.wake.set()
        return result

    def remove_root(self, root_id: int):
        with self.operation:
            self.store.remove_root(root_id)
            self.store.delete_outside(self.allowed)
            self.revision += 1
        self._watch()
        self.wake.set()

    def exclude(self, root_id: int, relative: str):
        with self.operation:
            self.store.exclude(root_id, relative)
            self.store.delete_outside(self.allowed)
            self.revision += 1
        self.wake.set()

    def clear(self):
        with self.operation:
            self.store.clear()
            self.revision += 1
            self.progress = {"phase": "idle", "processed": 0, "discovered": 0, "error": None}
        if self.automatic:
            self._refresh_disks()
            self.pause(True)
        self._watch()

    def remove_exclusion(self, root_id: int, relative: str):
        with self.operation:
            self.store.remove_exclusion(root_id, relative)
            self.revision += 1
        self.wake.set()

    def retry_document(self, document_id: int):
        with self.operation:
            path = self.verified_path(document_id)
            if self.automatic and (path.is_dir() or path.suffix.lower() not in SUPPORTED):
                raise ValueError("invalid_setting")
            self.store.invalidate(str(path), "pending")
        self.wake.set()

    def retry_all(self):
        with self.operation:
            self.store.set_setting("retry", uuid.uuid4().hex)
        self.wake.set()

    def issues(self, offset: int = 0):
        return self.store.issues(offset=offset, allowed=self.allowed)

    def paused(self):
        return self.store.setting("paused", False)

    def pause(self, paused: bool):
        self.store.set_setting("paused", bool(paused))
        self.wake.set()

    def _files(self):
        seen = set()
        for root in self.store.roots():
            base = Path(root["path"])
            try:
                list(base.iterdir())  # Distinguish inaccessible from empty directories.
                available = True
            except OSError:
                available = False
            with self.store.lock, self.store.connection:
                self.store.connection.execute(
                    "UPDATE roots SET available=? WHERE id=?", (int(available), root["id"])
                )
            if not available:
                continue
            for parent, directories, files in os.walk(base, followlinks=False):
                directories[:] = [
                    d
                    for d in directories
                    if not d.startswith(".")
                    and d not in EXCLUDED_NAMES
                    and not (Path(parent) / d).is_symlink()
                    and self.allowed(Path(parent) / d)
                ]
                for name in files:
                    path = Path(parent) / name
                    if path.suffix.lower() not in SUPPORTED or path in seen or path.is_symlink():
                        continue
                    if self.allowed(path):
                        seen.add(path)
                        yield path

    def scan(self, force: bool = False):
        if self.automatic:
            return self._scan_names(force)
        with self.operation:
            if self.paused() or self.stop_event.is_set():
                return False
            generation = self.revision
            inventory = self.store.inventory()
            self.progress = {"phase": "scanning", "processed": 0, "discovered": 0, "error": None}
        seen = set()
        completed = False
        for path in self._files():
            if self.stop_event.is_set() or self.paused() or generation != self.revision:
                break
            seen.add(str(path))
            self.progress["discovered"] += 1
            try:
                stat = path.stat()
                old = inventory.get(str(path))
                fingerprint = f"{stat.st_dev}:{stat.st_ino}:{stat.st_ctime_ns}"
                unchanged = (
                    old and old["size"] == stat.st_size and old["mtime_ns"] == stat.st_mtime_ns
                )
                if (
                    unchanged
                    and old["fingerprint"] == fingerprint
                    and old["status"] not in {"unavailable", "pending"}
                    and not force
                ):
                    self.progress["processed"] += 1
                    continue
                with self.operation:
                    if generation != self.revision:
                        break
                    if old:
                        self.store.invalidate(str(path), "pending")
                if placeholder(stat):
                    result = {"status": "cloud", "blocks": []}
                elif stat.st_size > MAX_FILE:
                    result = {"status": "file_limit", "blocks": []}
                elif time.time() - stat.st_mtime < 1:
                    self.wake.set()
                    continue
                else:
                    self.progress["phase"] = "indexing"
                    result = self.extractor(path)
                after = path.stat()
                if (after.st_size, after.st_mtime_ns, after.st_ctime_ns) != (
                    stat.st_size,
                    stat.st_mtime_ns,
                    stat.st_ctime_ns,
                ):
                    self.wake.set()
                    continue
                with self.operation:
                    if generation != self.revision or not self.allowed(path):
                        break
                    self.store.upsert(path, stat, fingerprint, result)
                    self.progress["processed"] += 1
            except PermissionError:
                self.store.invalidate(str(path), "permission")
            except OSError:
                self.store.invalidate(str(path))
            if self.store.setting("resource", "standard") == "low":
                self.stop_event.wait(0.1)
        else:
            with self.operation:
                if generation == self.revision:
                    for path in inventory:
                        if path not in seen or not self.allowed(Path(path), check_file=True):
                            self.store.invalidate(path)
                    completed = True
        self.progress["phase"] = "paused" if self.paused() else "idle"
        return completed

    def _refresh_disks(self):
        roots, blocked = self.disk_provider()
        self.blocked_paths = set(blocked)
        for path in roots:
            self.store.add_automatic_root(Path(path).resolve())

    def _all_entries(self):
        roots = sorted(
            {Path(root["path"]) for root in self.store.roots()}, key=lambda p: len(p.parts)
        )
        roots = [
            root
            for i, root in enumerate(roots)
            if not any(root.is_relative_to(p) for p in roots[:i])
        ]
        home = Path.home().resolve()
        starts = ([home] if any(home.is_relative_to(root) for root in roots) else []) + roots
        finished = []
        for base in starts:
            if base in finished or not self.allowed(base):
                continue
            for parent, directories, files in os.walk(base, followlinks=False):
                if self.stop_event.is_set() or self.paused():
                    return
                directories[:] = [
                    name
                    for name in directories
                    if not linked_directory(Path(parent) / name)
                    and not any((Path(parent) / name).is_relative_to(done) for done in finished)
                    and self.allowed(Path(parent) / name)
                ]
                for name in directories + files:
                    path = Path(parent) / name
                    if not self.allowed(path):
                        continue
                    try:
                        str(path).encode("utf-8")
                        stat = path.lstat()
                    except (OSError, UnicodeError):
                        continue
                    if stat_types.S_ISDIR(stat.st_mode) or stat_types.S_ISREG(stat.st_mode):
                        yield path, stat
            finished.append(base)

    def _scan_names(self, force=False):
        with self.operation:
            if self.paused() or self.stop_event.is_set():
                return False
            self._refresh_disks()
            generation = self.revision
            scan_id = uuid.uuid4().hex
            self.progress = {"phase": "scanning", "processed": 0, "discovered": 0, "error": None}
        batch = []
        for path, stat in self._all_entries():
            if self.paused() or self.stop_event.is_set() or generation != self.revision:
                return False
            kind = "folder" if stat_types.S_ISDIR(stat.st_mode) else path.suffix.lower().lstrip(".")
            if kind == "markdown":
                kind = "md"
            kind = kind or "file"
            status = "pending" if kind in {"pdf", "md", "docx"} else "metadata"
            fingerprint = f"{stat.st_dev}:{stat.st_ino}:{stat.st_ctime_ns}"
            batch.append((path, stat, fingerprint, kind, status))
            self.progress["discovered"] += 1
            if len(batch) >= 128:
                with self.operation:
                    if generation != self.revision:
                        return False
                    self.store.discover_batch(batch, scan_id)
                self.progress["processed"] += len(batch)
                batch.clear()
        with self.operation:
            if self.paused() or self.stop_event.is_set() or generation != self.revision:
                return False
            self.store.discover_batch(batch, scan_id)
            self.progress["processed"] += len(batch)
            self.store.finish_discovery(scan_id)
            if force:
                self.store.queue_contents()
            self.progress["phase"] = "idle"
        return True

    def parse_pending(self):
        # Independent from disk discovery: a slow PDF cannot hold up filename search.
        after_id = 0
        while not self.stop_event.is_set() and not self.paused():
            rows = self.store.pending_batch(after_id)
            if not rows:
                return
            for row in rows:
                after_id = row["id"]
                if self.stop_event.is_set() or self.paused():
                    return
                generation = self.revision
                path = Path(row["path"])
                try:
                    if not self.allowed(path, check_file=True):
                        continue
                    before = path.stat()
                    if placeholder(before):
                        result = {"status": "cloud", "blocks": []}
                    elif before.st_size > MAX_FILE:
                        result = {"status": "file_limit", "blocks": []}
                    elif time.time() - before.st_mtime < 1:
                        continue
                    else:
                        result = self.extractor(path)
                    after = path.stat()
                    if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                        after.st_size,
                        after.st_mtime_ns,
                        after.st_ctime_ns,
                    ):
                        continue
                    with self.operation:
                        if generation == self.revision and self.allowed(path):
                            fingerprint = f"{before.st_dev}:{before.st_ino}:{before.st_ctime_ns}"
                            self.store.upsert(path, before, fingerprint, result)
                except PermissionError:
                    self.store.invalidate(str(path), "permission")
                except OSError:
                    self.store.invalidate(str(path))
                if self.store.setting("resource", "standard") == "low":
                    self.stop_event.wait(0.1)

    def _parse_loop(self):
        while not self.stop_event.is_set():
            try:
                self.parse_pending()
            except (sqlite3.Error, OSError):
                self.progress.update(error="storage_error")
            self.stop_event.wait(1)

    def _run(self):
        while not self.stop_event.is_set():
            self.wake.clear()
            try:
                request = self.store.setting("retry", False)
                completed = self.scan(force=bool(request))
                if completed and request:
                    with self.operation:
                        if self.store.setting("retry", False) == request:
                            self.store.set_setting("retry", False)
            except (sqlite3.Error, OSError):
                self.progress.update(phase="error", error="storage_error")
            self.wake.wait(30)
            if self.wake.is_set():
                self.stop_event.wait(1.1)  # Coalesce editor atomic saves.

    def start(self):
        if self.thread:
            return
        self.thread = threading.Thread(target=self._run, name="shiwen-index", daemon=True)
        self.thread.start()
        if self.automatic:
            self.parser_thread = threading.Thread(target=self._parse_loop, daemon=True)
            self.parser_thread.start()
        self._watch()

    def _watch(self):
        if not self.thread or self.automatic:
            return
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer

        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2)

        wake = self.wake

        class Handler(FileSystemEventHandler):
            def on_any_event(self, event):
                if event.event_type in {"created", "modified", "deleted", "moved"}:
                    wake.set()

        self.observer = Observer()
        for root in self.store.roots():
            try:
                self.observer.schedule(Handler(), root["path"], recursive=True)
            except OSError:
                continue
        try:
            self.observer.start()
        except OSError:
            self.observer = None  # Periodic reconciliation remains available.

    def close(self):
        self.stop_event.set()
        self.wake.set()
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=3)
        if self.thread:
            self.thread.join(timeout=65)
        if self.parser_thread:
            self.parser_thread.join(timeout=65)
        self.store.close()

    def search(self, **kwargs):
        return self.store.search(**kwargs, allowed=self.allowed)

    def status(self):
        size = sum(p.stat().st_size for p in self.store.directory.glob("library.sqlite3*"))
        return {
            "automatic": self.automatic,
            "roots": self.store.roots(),
            "counts": self.store.counts(),
            "progress": dict(self.progress),
            "paused": self.paused(),
            "disk_bytes": size,
            "data_directory": str(self.store.directory),
            "settings": {
                key: self.store.setting(key, value)
                for key, value in {
                    "theme": "system",
                    "language": "zh",
                    "glass": True,
                    "resource": "standard",
                }.items()
            },
        }

    def document(self, document_id: int, query: str = "") -> dict:
        from .text import query_terms, ranges

        document = self.store.get(document_id)
        if document is None or not self.allowed(Path(document["path"]), check_file=True):
            raise ValueError("unavailable")
        import json

        terms = query_terms(query, allow_single=True)
        blocks = json.loads(document["blocks"])
        for block in blocks:
            block["ranges"] = ranges(block["text"], terms)
        return {
            key: document[key] for key in ("id", "name", "path", "type", "size", "status", "saved")
        } | {"blocks": blocks}

    def verified_path(self, document_id: int) -> Path:
        document = self.store.get(document_id)
        if document is None or not self.allowed(Path(document["path"]), check_file=True):
            raise ValueError("unavailable")
        path = Path(document["path"])
        if placeholder(path.stat()):
            raise ValueError("cloud")
        return path
