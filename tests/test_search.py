import os
import time
import zipfile

import pytest

from shiwen.app import Bridge
from shiwen.extract import extract, extract_isolated
from shiwen.library import Library
from shiwen.text import grams, query_terms, ranges


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    os.utime(path, (time.time() - 5, time.time() - 5))
    return path


@pytest.fixture
def collection(tmp_path):
    folder = tmp_path / "documents"
    folder.mkdir()
    library = Library(tmp_path / "index", extractor=extract)
    library.add_root(str(folder))
    yield library, folder
    library.close()


def names(library, query, **kwargs):
    return [item["name"] for item in library.search(query=query, **kwargs)["items"]]


def test_chinese_literal_and_mixed_search(collection):
    library, folder = collection
    write(folder / "方案.md", "支持离线部署，预算完成审批。Offline deployment uses C++.")
    write(folder / "干扰.md", "离线的说明。部署的说明。预算没有其他内容。")
    library.scan()
    assert names(library, "离线部署") == ["方案.md"]
    assert set(names(library, "部署")) == {"方案.md", "干扰.md"}
    assert names(library, "预算 审批") == ["方案.md"]
    assert names(library, '"OFFLINE deployment"') == ["方案.md"]
    assert names(library, "C++") == ["方案.md"]
    assert not names(library, "不存在")


def test_disconnected_bigrams_never_return_false_match(collection):
    library, folder = collection
    write(folder / "false.md", "甲乙，然后乙丙，再来丙丁")
    library.scan()
    assert not names(library, "甲乙丙丁")


def test_titles_filters_bookmarks_and_reopen(collection):
    library, folder = collection
    write(folder / "技术方案.md", "原文内容")
    library.scan()
    result = library.search(query="技术方案")["items"][0]
    assert result["name_only"]
    assert not names(library, "技术", file_type="pdf")
    library.store.bookmark(result["id"], True)
    assert names(library, "技术", saved=True) == ["技术方案.md"]
    other = Library(library.store.directory, extractor=extract)
    try:
        assert names(other, "技术", saved=True) == ["技术方案.md"]
    finally:
        other.close()


def test_updates_deletions_and_missing_folders(collection):
    library, folder = collection
    path = write(folder / "note.md", "旧的离线部署")
    library.scan()
    write(path, "新的预算审批")
    library.scan()
    assert not names(library, "离线部署")
    assert names(library, "预算审批")
    path.unlink()
    assert not names(library, "预算审批")  # Before the watcher has reconciled.
    library.scan()
    assert not names(library, "预算审批")
    assert library.store.counts()["by_status"]["unavailable"] == 1


def test_pending_version_is_retried(collection):
    library, folder = collection
    path = write(folder / "note.md", "离线部署")
    library.scan()
    library.store.invalidate(str(path), "pending")
    library.scan()
    assert names(library, "离线部署")


def test_exclusions_override_overlapping_roots(collection):
    library, folder = collection
    child = folder / "private"
    write(child / "secret.md", "秘密内容")
    write(folder / "public.md", "公开内容")
    root = library.store.roots()[0]["id"]
    library.add_root(str(child))
    library.scan()
    assert len(names(library, "秘密内容")) == 1
    library.exclude(root, "private")
    assert not names(library, "秘密内容")
    assert names(library, "公开内容")
    assert (child / "secret.md").exists()
    with pytest.raises(ValueError):
        library.exclude(root, "../outside")


def test_hidden_dependencies_and_symlinks_are_not_indexed(collection, tmp_path):
    library, folder = collection
    write(folder / ".hidden" / "note.md", "隐藏内容")
    write(folder / "node_modules" / "note.md", "依赖内容")
    target = write(tmp_path / "outside" / "note.md", "越界内容")
    try:
        (folder / "link.md").symlink_to(target)
    except OSError:
        pass  # Symlink privilege is optional on Windows.
    library.scan()
    assert library.search(query="")["items"] == []


def test_scope_removal_and_clear_never_modify_originals(collection):
    library, folder = collection
    path = write(folder / "note.md", "原始内容不得改变")
    original = path.read_bytes()
    library.scan()
    root = library.store.roots()[0]["id"]
    library.remove_root(root)
    assert not library.store.inventory()
    library.add_root(str(folder))
    library.scan()
    library.clear()
    assert library.store.roots() == []
    assert library.store.inventory() == {}
    assert path.read_bytes() == original


def test_docx_body_and_table(tmp_path):
    path = tmp_path / "notes.docx"
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>普通正文</w:t></w:r></w:p><w:tbl><w:tr><w:tc>"
        "<w:p><w:r><w:t>表格预算审批</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)
    result = extract(path)
    assert [b["text"] for b in result["blocks"]] == ["普通正文", "表格预算审批"]


def test_pdf_page_locations_partial_and_encrypted(tmp_path):
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen.canvas import Canvas

    path = tmp_path / "paper.pdf"
    canvas = Canvas(str(path))
    canvas.drawString(70, 700, "Offline deployment on page one")
    canvas.showPage()
    canvas.showPage()
    canvas.save()
    result = extract(path)
    assert result["status"] == "partial"
    assert result["blocks"][0]["location"] == 1
    assert "Offline deployment" in result["blocks"][0]["text"]
    locked = tmp_path / "locked.pdf"
    writer = PdfWriter()
    writer.add_page(PdfReader(path).pages[0])
    writer.encrypt("password")
    writer.write(locked)
    assert extract_isolated(locked)["status"] == "encrypted"


def test_isolated_parser_errors_and_unicode(tmp_path):
    path = write(tmp_path / "中文.md", "中文短语，offline")
    assert extract_isolated(path)["blocks"][0]["text"] == "中文短语，offline"
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not a PDF")
    assert extract_isolated(bad)["status"] == "parse_error"
    assert extract_isolated(path, timeout=0)["status"] == "timeout"


def test_pause_prevents_new_content(collection):
    library, folder = collection
    write(folder / "note.md", "离线部署")
    library.pause(True)
    library.scan()
    assert not names(library, "离线部署")
    library.pause(False)
    library.scan()
    assert names(library, "离线部署")


def test_queries_are_safe_and_explicit(collection):
    library, folder = collection
    write(folder / "note.md", '<script>alert(1)</script> "quoted"')
    library.scan()
    assert names(library, "<script>")
    for query in ["部", '"unfinished', "x" * 257]:
        with pytest.raises(ValueError):
            library.search(query=query)
    assert query_terms('预算 "offline deployment"') == ["预算", "offline deployment"]
    assert all(token.isalnum() for token in grams("中/文<script> OR").split())
    assert ranges("ＡＢＣ  部署", ["abc", "部署"]) == [[0, 3], [5, 7]]


def test_bridge_exposes_only_intended_actions(collection):
    library, folder = collection
    bridge = Bridge(library)
    assert not bridge.call("eval", {"code": "dangerous"})["ok"]
    assert not bridge.call("open", {"document_id": 999})["ok"]
    assert not bridge.call("setting", {"key": "arbitrary", "value": 1})["ok"]
    assert bridge.call("setting", {"key": "theme", "value": "dark"})["ok"]
    assert bridge.call("status")["data"]["settings"]["theme"] == "dark"


def test_paginated_results(collection):
    library, folder = collection
    for index in range(55):
        write(folder / f"{index:03}.md", "同样的检索短语")
    library.scan()
    first = library.search(query="检索")
    second = library.search(query="检索", offset=50)
    assert len(first["items"]) == 50 and first["has_more"]
    assert len(second["items"]) == 5 and not second["has_more"]
    assert not {i["id"] for i in first["items"]} & {i["id"] for i in second["items"]}


def test_pagination_verifies_candidates_before_counting_results(collection):
    library, folder = collection
    for index in range(115):
        # Newer false candidates must not consume the page or its lookahead item.
        text = "甲乙，然后乙丙，再来丙丁" if index < 60 else "完整短语甲乙丙丁"
        path = write(folder / f"{index:03}.md", text)
        os.utime(path, (1_700_000_000 - index, 1_700_000_000 - index))
    library.scan()
    first = library.search(query="甲乙丙丁", sort="date")
    second = library.search(query="甲乙丙丁", sort="date", offset=50)
    assert first["has_more"] and not second["has_more"]
    assert [i["name"] for i in first["items"]] == [f"{i:03}.md" for i in range(60, 110)]
    assert [i["name"] for i in second["items"]] == [f"{i:03}.md" for i in range(110, 115)]


def test_replacing_scope_during_parse_cannot_restore_removed_content(collection):
    library, folder = collection
    write(folder / "note.md", "敏感内容")
    root = library.store.roots()[0]["id"]

    def remove_during_parse(path):
        result = extract(path)
        library.remove_root(root)
        return result

    library.extractor = remove_during_parse
    library.scan()
    assert not library.store.inventory()
    assert not library.store.roots()
