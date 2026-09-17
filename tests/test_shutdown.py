import multiprocessing
import os
import sqlite3
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

import shiwen.extract as extract_module
from shiwen.app import Bridge
from shiwen.desktop import guard_evaluation
from shiwen.library import Library


def slow_worker(path, sender):
    Path(path).with_suffix(".started").write_text("ready")
    time.sleep(60)


def wait_for(predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < deadline, "Worker did not reach the expected state"
        time.sleep(0.02)


def test_window_evaluation_preserves_results_and_errors():
    closing = threading.Event()
    calls = []

    def evaluate(script, callback=None):
        calls.append(script)
        if script == "bad":
            raise ValueError("script error")
        if callback:
            callback(42)
        return 42

    window = SimpleNamespace(evaluate_js=evaluate, run_js=evaluate)
    guard_evaluation(window, closing)
    values = []
    assert window.evaluate_js("ok", callback=values.append) == 42
    assert values == [42]
    assert window.run_js("injection") == 42
    with pytest.raises(ValueError, match="script error"):
        window.evaluate_js("bad")
    closing.set()
    assert window.evaluate_js("after close") is None
    assert window.run_js("after close") is None
    assert calls == ["ok", "injection", "bad"]


@pytest.mark.parametrize("method", ["evaluate_js", "run_js"])
def test_destroyed_window_releases_waiting_caller(method):
    entered, release, closing = threading.Event(), threading.Event(), threading.Event()

    def never_returns(script):
        entered.set()
        release.wait(10)

    window = SimpleNamespace(evaluate_js=never_returns, run_js=never_returns)
    guard_evaluation(window, closing)
    caller = threading.Thread(target=lambda: getattr(window, method)("pending"))
    caller.start()
    try:
        assert entered.wait(3)
        closing.set()
        caller.join(1)
        assert not caller.is_alive()
    finally:
        release.set()
        caller.join(3)


def test_close_cancels_real_parser_and_keeps_work_pending(tmp_path, monkeypatch):
    monkeypatch.setattr(extract_module, "_worker", slow_worker)
    disk = tmp_path / "disk"
    disk.mkdir()
    note = disk / "unfinished.md"
    note.write_text("resume this document")
    os.utime(note, (1_700_000_000, 1_700_000_000))
    library = Library(tmp_path / "index", automatic=True, disk_provider=lambda: ([disk], set()))
    children = {p.pid for p in multiprocessing.active_children()}
    library.scan()
    library.start()
    try:
        wait_for(note.with_suffix(".started").exists)
        begin = time.monotonic()
        library.close()
        assert time.monotonic() - begin < 4
        assert not library.thread.is_alive() and not library.parser_thread.is_alive()
        assert {p.pid for p in multiprocessing.active_children()} == children
    finally:
        library.request_stop()
    reopened = Library(tmp_path / "index", automatic=True, disk_provider=lambda: ([disk], set()))
    try:
        assert reopened.search(query="unfinished")["items"][0]["status"] == "pending"
        monkeypatch.undo()
        reopened.parse_pending()
        assert reopened.search(query="resume", mode="content")["items"]
    finally:
        reopened.close()


def test_close_drains_rpc_before_closing_database(tmp_path):
    library = Library(tmp_path / "index")
    bridge = Bridge(library)
    entered, release = threading.Event(), threading.Event()
    original = library.status
    replies = []

    def slow_status():
        entered.set()
        assert release.wait(3)
        return original()

    library.status = slow_status
    caller = threading.Thread(target=lambda: replies.append(bridge.call("status")))
    caller.start()
    assert entered.wait(3)
    closer = threading.Thread(target=bridge._close)
    closer.start()
    try:
        wait_for(bridge._closing.is_set)
        assert bridge.call("status") == {"ok": False, "error": "app_closing"}
        assert library.store.counts() is not None
        release.set()
        caller.join(3)
        closer.join(3)
        assert not caller.is_alive() and not closer.is_alive()
        assert replies[0]["ok"]
        with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
            library.store.counts()
    finally:
        release.set()
        caller.join(3)
        closer.join(3)


def test_stopping_directory_walk_does_not_withdraw_unvisited_documents(tmp_path, monkeypatch):
    from shiwen.extract import extract

    disk = tmp_path / "disk"
    disk.mkdir()
    note = disk / "saved.md"
    note.write_text("retain searchable content")
    os.utime(note, (1_700_000_000, 1_700_000_000))
    library = Library(tmp_path / "index", extractor=extract)
    try:
        library.add_root(str(disk))
        assert library.scan()
        document = library.search(query="searchable")["items"][0]
        library.store.bookmark(document["id"], True)

        def interrupted_walk():
            library.request_stop()
            return iter(())

        monkeypatch.setattr(library, "_files", interrupted_walk)
        assert not library.scan()
        assert library.search(query="searchable", saved=True)["items"][0]["id"] == document["id"]
    finally:
        library.close()
