import os
from pathlib import Path

from shiwen.discovery import linux_exclusions, local_disks
from shiwen.extract import extract
from shiwen.library import Library


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    os.utime(path, (1_700_000_000, 1_700_000_000))
    return path


def automatic(tmp_path, extractor=extract):
    disk = tmp_path / "disk"
    disk.mkdir(exist_ok=True)
    library = Library(
        disk / "index", extractor=extractor, automatic=True, disk_provider=lambda: ([disk], set())
    )
    return library, disk


def test_automatic_names_precede_content_and_include_files_and_folders(tmp_path):
    calls = []

    def parser(path):
        calls.append(path)
        return extract(path)

    library, disk = automatic(tmp_path, parser)
    try:
        note = write(disk / "mixed" / "notes.md", "可检索的预算审批")
        write(disk / "mixed" / "holiday.png", "not an actual image")
        write(disk / "archive.zip", "not an actual archive")
        assert library.status()["automatic"]
        assert library.scan()
        assert calls == []
        assert {item["name"] for item in library.search(query="ｈ", mode="name")["items"]} == {
            "holiday.png",
            "archive.zip",
        }
        assert library.search(query="预")["items"] == []
        assert len(library.search(query="holiday")["items"]) == 1
        assert len(library.search(query="mixed", file_type="folder")["items"]) == 1
        assert not library.search(query="预算审批")["items"]
        assert library.search(query="notes")["items"][0]["status"] == "pending"
        assert not library.search(query="library.sqlite")["items"]
        assert len(library.issues()["items"]) == 1
        library.parse_pending()
        assert calls == [note]
        assert len(library.search(query="预算审批", mode="content")["items"]) == 1
        assert not library.search(query="预算审批", mode="name")["items"]
        assert not library.search(query="notes", mode="content")["items"]
        assert library.search(query="notes", mode="name")["items"]
        assert not library.issues()["items"]
    finally:
        library.close()


def test_automatic_updates_deletes_and_preserves_bookmarks(tmp_path):
    library, disk = automatic(tmp_path)
    try:
        path = write(disk / "notes.md", "原来的短语")
        library.scan()
        library.parse_pending()
        item = library.search(query="notes")["items"][0]
        library.store.bookmark(item["id"], True)
        write(path, "替换后的正文")
        library.scan()
        assert not library.search(query="原来的短语")["items"]
        assert library.search(query="notes", saved=True)["items"]
        library.parse_pending()
        assert library.search(query="替换后的正文")["items"]
        path.unlink()
        library.scan()
        assert not library.search(query="notes")["items"]
        assert library.store.get(item["id"])["status"] == "unavailable"
    finally:
        library.close()


def test_automatic_pause_and_interrupted_discovery_keep_existing_records(tmp_path, monkeypatch):
    library, disk = automatic(tmp_path)
    try:
        write(disk / "notes.md", "原来的内容")
        library.scan()
        library.parse_pending()
        original_entries = library._all_entries

        def interrupted():
            for item in original_entries():
                library.pause(True)
                yield item

        monkeypatch.setattr(library, "_all_entries", interrupted)
        assert not library.scan()
        assert library.search(query="原来的内容")["items"]
        library.clear()
        assert library.paused()
        assert library.status()["roots"]
        assert not library.scan()
        assert not library.store.inventory()
    finally:
        library.close()


def test_automatic_preserves_legacy_exclusions_and_deduplicates_roots(tmp_path):
    disk = tmp_path / "disk"
    public = write(disk / "mixed" / "notes.md", "公开内容")
    write(disk / "mixed" / "private" / "secret.md", "机密内容")
    write(disk / ".hidden-note.md", "隐藏文件仍可查找")
    write(disk / ".git" / "internal.md", "缓存内容")
    old = Library(tmp_path / "data", extractor=extract)
    root_id = old.add_root(str(public.parent))
    old.exclude(root_id, "private")
    old.scan()
    old.close()
    library = Library(
        tmp_path / "data", extractor=extract, automatic=True, disk_provider=lambda: ([disk], set())
    )
    try:
        library.scan()
        library.parse_pending()
        assert len(library.search(query="公开内容")["items"]) == 1
        assert library.search(query="隐藏文件")["items"]
        assert not library.search(query="缓存内容")["items"]
        assert not library.search(query="机密内容")["items"]
        library.remove_exclusion(root_id, "private")
        library.scan()
        library.parse_pending()
        assert library.search(query="机密内容")["items"]
    finally:
        library.close()


def test_automatic_skips_special_files_and_does_not_follow_symlinks(tmp_path):
    library, disk = automatic(tmp_path)
    try:
        target = write(tmp_path / "outside.md", "越界正文")
        try:
            (disk / "linked.md").symlink_to(target)
        except OSError:
            pass  # Windows may not grant symlink privilege.
        if hasattr(os, "mkfifo"):
            os.mkfifo(disk / "pipe.md")
        library.scan()
        library.parse_pending()
        assert not library.search(query="linked")["items"]
        assert not library.search(query="pipe")["items"]
    finally:
        library.close()


def test_mount_policy_excludes_network_and_virtual_filesystems():
    mounts = (
        "1 0 8:1 / / rw - ext4 /dev/root rw\n"
        "2 1 8:2 / /mnt/local rw - ext4 /dev/sdb rw\n"
        "3 1 0:2 / /mnt/shared\\040files rw - nfs host:/files rw\n"
        "4 1 0:3 / /proc rw - proc proc rw\n"
    )
    excluded = linux_exclusions(mounts)
    assert Path("/mnt/shared files") in excluded
    assert Path("/proc") in excluded
    assert Path("/") not in excluded
    assert Path("/mnt/local") not in excluded


def test_native_disk_discovery_is_read_only_and_finds_local_roots():
    roots, excluded = local_disks()
    assert roots and all(path.is_absolute() for path in roots)
    assert all(path.is_absolute() for path in excluded)
