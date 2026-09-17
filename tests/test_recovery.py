import os

import pytest

from shiwen.app import Bridge
from shiwen.extract import extract
from shiwen.library import Library


def note(path, text="离线部署"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    os.utime(path, (1_700_000_000, 1_700_000_000))
    return path


def test_single_retry_survives_pause_restart_and_preserves_bookmark(tmp_path):
    folder = tmp_path / "documents"
    broken = note(folder / "broken.md")
    note(folder / "good.md")
    library = Library(tmp_path / "index", extractor=extract)
    try:
        library.add_root(str(folder))
        library.scan()
        document_id = library.store.inventory()[str(broken)]["id"]
        library.store.invalidate(str(broken), "parse_error")
        library.store.bookmark(document_id, True)
        library.pause(True)
        bridge = Bridge(library)
        assert bridge.call("retry_document", {"document_id": document_id})["ok"]
        assert not library.scan()
        assert library.store.get(document_id)["status"] == "pending"
    finally:
        library.close()
    calls = []

    def tracking_extract(path):
        calls.append(path)
        return extract(path)

    reopened = Library(tmp_path / "index", extractor=tracking_extract)
    try:
        assert reopened.paused()
        reopened.pause(False)
        assert reopened.scan()
        assert calls == [broken]
        assert reopened.store.get(document_id)["status"] == "ready"
        assert reopened.store.get(document_id)["saved"] == 1
        assert reopened.issues()["items"] == []
        assert len(reopened.search(query="离线部署")["items"]) == 2
        assert broken.read_text(encoding="utf-8") == "离线部署"
    finally:
        reopened.close()


def test_retry_rejects_missing_and_out_of_scope_documents(tmp_path):
    library = Library(tmp_path / "index", extractor=extract)
    path = note(tmp_path / "documents" / "lost.md")
    try:
        root_id = library.add_root(str(path.parent))
        library.scan()
        document_id = library.store.inventory()[str(path)]["id"]
        path.unlink()
        library.scan()
        assert library.issues()["items"][0]["status"] == "unavailable"
        assert not Bridge(library).call("retry_document", {"document_id": document_id})["ok"]
        library.remove_root(root_id)
        assert not library.issues()["items"]
        assert not Bridge(library).call("retry_document", {"document_id": document_id})["ok"]
        assert not Bridge(library).call("retry_document", {"path": str(path)})["ok"]
    finally:
        library.close()


def test_issue_pagination_does_not_return_document_contents(tmp_path):
    folder = tmp_path / "documents"
    library = Library(tmp_path / "index", extractor=extract)
    try:
        for index in range(23):
            note(folder / f"empty-{index:02}.md", "")
        note(folder / "ready.md")
        library.add_root(str(folder))
        library.scan()
        first = library.issues()
        second = library.issues(offset=20)
        assert len(first["items"]) == 20 and first["has_more"]
        assert len(second["items"]) == 3 and not second["has_more"]
        assert not {i["id"] for i in first["items"]} & {i["id"] for i in second["items"]}
        for item in first["items"] + second["items"]:
            assert item["status"] == "no_text"
            assert set(item) == {"id", "name", "path", "type", "status"}
    finally:
        library.close()


def test_remove_exclusion_restores_only_the_selected_rule(tmp_path):
    folder = tmp_path / "documents"
    public = note(folder / "public.md", "公开内容")
    restored = note(folder / "private" / "restored.md", "恢复内容")
    nested = note(folder / "private" / "nested" / "secret.md", "秘密内容")
    library = Library(tmp_path / "index", extractor=extract)
    try:
        root_id = library.add_root(str(folder))
        child_id = library.add_root(str(folder / "private"))
        library.scan()
        public_id = library.store.inventory()[str(public)]["id"]
        library.store.bookmark(public_id, True)
        library.exclude(root_id, "private")
        library.exclude(child_id, "nested")
        library.remove_exclusion(root_id, "private")
        library.scan()
        assert [i["path"] for i in library.search(query="恢复内容")["items"]] == [str(restored)]
        assert not library.search(query="秘密内容")["items"]
        assert library.store.get(public_id)["saved"] == 1
        assert nested.read_text(encoding="utf-8") == "秘密内容"
        library.exclude(root_id, "already-gone")
        library.remove_exclusion(root_id, "already-gone")
        with pytest.raises(ValueError, match="invalid_exclusion"):
            library.remove_exclusion(root_id, "../outside")
        library.remove_exclusion(child_id, "nested")
        library.scan()
        assert library.search(query="秘密内容")["items"]
    finally:
        library.close()


def test_new_global_retry_during_scan_is_not_lost(tmp_path, monkeypatch):
    library = Library(tmp_path / "index", extractor=extract)
    try:
        library.retry_all()
        first_request = library.store.setting("retry")

        def another_request(force):
            assert force
            library.retry_all()
            library.stop_event.set()
            return True

        monkeypatch.setattr(library, "scan", another_request)
        library._run()
        assert library.store.setting("retry")
        assert library.store.setting("retry") != first_request
    finally:
        library.close()


def test_paused_global_retry_is_not_consumed(tmp_path, monkeypatch):
    library = Library(tmp_path / "index", extractor=extract)
    try:
        library.pause(True)
        library.retry_all()
        request = library.store.setting("retry")

        def end_iteration(_timeout):
            library.stop_event.set()
            return True

        monkeypatch.setattr(library.wake, "wait", end_iteration)
        library._run()
        assert library.store.setting("retry") == request
    finally:
        library.close()
