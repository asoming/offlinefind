import hashlib
import io
import json
import threading
from urllib.error import HTTPError, URLError

import pytest

from shiwen.app import Bridge
from shiwen.library import Library
from shiwen.updates import (
    API,
    MANIFEST,
    REPOSITORY,
    GitHubRedirects,
    Updater,
    release_info,
    version,
)


def release(tag="v0.1.0-beta.5", package="0.1.0b5", content=b"package"):
    assets = []
    for suffix in ["linux-amd64.deb", "linux-x64.tar.gz", "windows-x64.zip", "macos-arm64.zip"]:
        name = f"Shiwen-{package}-{suffix}"
        assets.append(
            {
                "name": name,
                "state": "uploaded",
                "size": len(content),
                "digest": "sha256:" + hashlib.sha256(content).hexdigest(),
                "browser_download_url": f"{REPOSITORY}/releases/download/{tag}/{name}",
            }
        )
    return {
        "tag_name": tag,
        "draft": False,
        "prerelease": "beta" in tag,
        "published_at": "2026-09-17T00:00:00Z",
        "assets": assets,
        "body": "New version <script>not HTML</script>",
    }


def finish(updater):
    updater.worker.join(timeout=5)
    assert not updater.worker.is_alive()
    return updater.status()


def test_release_order_beta_channel_and_platform_matching():
    items = [release("v0.1.0-beta.9", "0.1.0b9"), release("v0.1.0-beta.10", "0.1.0b10")]
    result = release_info(items, "0.1.0b4", "linux", "x86_64")
    assert result["newer"] and result["version"] == "v0.1.0-beta.10"
    assert [a["name"].split("-0.1.0b10-")[1] for a in result["assets"]] == [
        "linux-amd64.deb",
        "linux-x64.tar.gz",
    ]
    assert len(release_info(items, "0.1.0b4", "win32", "AMD64")["assets"]) == 1
    assert len(release_info(items, "0.1.0b4", "darwin", "arm64")["assets"]) == 1
    assert not release_info(items, "0.1.0b4", "darwin", "x86_64")["assets"]
    stable = release("v0.1.0", "0.1.0")
    newer_beta = release("v0.2.0-beta.1", "0.2.0b1")
    assert release_info([stable, newer_beta], "0.1.0", "linux", "x86_64")["version"] == "v0.1.0"
    assert version("0.1.0rc1") > version("0.1.0b10")
    assert version("0.1.0") > version("0.1.0rc1")


def test_offline_startup_and_checks_only_on_request(tmp_path):
    calls = []

    def opener(url):
        calls.append(url)
        return io.BytesIO(json.dumps([release()]).encode())

    updater = Updater(current="0.1.0b4", downloads=tmp_path, opener=opener)
    assert updater.status()["phase"] == "idle" and calls == []
    updater.check()
    assert finish(updater)["phase"] == "available"
    assert calls == [MANIFEST]
    updater.status()
    assert calls == [MANIFEST]


def test_verified_download_is_atomic_and_does_not_overwrite_existing_files(tmp_path):
    data = b"package" * 20000
    item = release(content=data)
    updater = Updater(downloads=tmp_path, opener=lambda url: io.BytesIO(data))
    updater.release = release_info([item], "0.1.0b4", "linux", "x86_64")
    name = updater.release["assets"][0]["name"]
    original = tmp_path / name
    original.write_bytes(b"keep this")
    updater.download(name)
    result = finish(updater)
    assert result["phase"] == "downloaded"
    assert result["received"] == len(data) == result["total"]
    from pathlib import Path

    assert Path(result["path"]).read_bytes() == data
    assert original.read_bytes() == b"keep this"
    assert not list(tmp_path.rglob("*.part"))


@pytest.mark.parametrize("body", [b"bad", b"packagf", b"package-extra"])
def test_corrupt_truncated_or_oversized_download_is_removed(tmp_path, body):
    updater = Updater(downloads=tmp_path, opener=lambda url: io.BytesIO(body))
    updater.release = release_info([release()], "0.1.0b4", "linux", "x86_64")
    updater.download(updater.release["assets"][0]["name"])
    result = finish(updater)
    assert result["phase"] == "error" and result["error"] == "update_integrity"
    assert list(tmp_path.iterdir()) == []


def test_cancellation_and_parallel_requests(tmp_path):
    entered, proceed = threading.Event(), threading.Event()

    class SlowResponse(io.BytesIO):
        def read(self, count=-1):
            entered.set()
            proceed.wait(3)
            return super().read(count)

    updater = Updater(downloads=tmp_path, opener=lambda url: SlowResponse(b"package"))
    updater.release = release_info([release()], "0.1.0b4", "linux", "x86_64")
    updater.download(updater.release["assets"][0]["name"])
    assert entered.wait(3)
    with pytest.raises(ValueError, match="update_busy"):
        updater.check()
    updater.cancel()
    proceed.set()
    assert finish(updater)["phase"] == "cancelled"
    assert list(tmp_path.iterdir()) == []


def test_checksum_fallback_and_arbitrary_urls_rejected(tmp_path):
    item = release()
    asset = item["assets"][0]
    asset.pop("digest")
    item["assets"].append(
        {
            "name": asset["name"] + ".sha256",
            "state": "uploaded",
            "browser_download_url": asset["browser_download_url"] + ".sha256",
        }
    )
    checksum = hashlib.sha256(b"package").hexdigest() + "  " + asset["name"] + "\n"
    updater = Updater(
        downloads=tmp_path,
        opener=lambda url: io.BytesIO(checksum.encode() if url.endswith(".sha256") else b"package"),
    )
    updater.release = release_info([item], "0.1.0b4", "linux", "x86_64")
    updater.download(asset["name"])
    assert finish(updater)["phase"] == "downloaded"
    with pytest.raises(ValueError):
        updater.download("../../untrusted.deb")
    asset["browser_download_url"] = "https://evil.invalid/payload"
    assert len(release_info([item], "0.1.0b4", "linux", "x86_64")["assets"]) == 1
    for url in [
        "http://github.com/file",
        "https://127.0.0.1/file",
        "file:///tmp/test",
        "https://github.com.evil.invalid/file",
    ]:
        with pytest.raises(ValueError):
            GitHubRedirects().redirect_request(None, None, 302, "", {}, url)


@pytest.mark.parametrize(
    "error,code",
    [
        (URLError("offline"), "update_network"),
        (HTTPError(API, 429, "rate", {}, None), "update_rate_limit"),
    ],
)
def test_network_failures_can_be_retried(error, code):
    def failed(url):
        raise error

    updater = Updater(current="0.1.0", opener=failed)
    updater.check()
    assert finish(updater)["error"] == code
    updater.opener = lambda url: io.BytesIO(json.dumps([release("v0.1.0", "0.1.0")]).encode())
    updater.check()
    assert finish(updater)["phase"] in {"available", "current"}


def test_bridge_cannot_download_an_arbitrary_url_or_path(tmp_path):
    library = Library(tmp_path / "index")
    try:
        bridge = Bridge(library)
        assert bridge.call("update_status")["data"]["phase"] == "idle"
        assert not bridge.call(
            "download_update", {"url": "https://evil.invalid", "path": "/tmp/x"}
        )["ok"]
        assert not bridge.call("download_folder")["ok"]
    finally:
        library.close()


def test_newer_local_build_never_offers_a_downgrade():
    result = release_info([release()], "0.1.0b6", "linux", "x86_64")
    assert not result["newer"] and result["assets"] == []


def test_download_directory_failure_is_reported(tmp_path):
    path = tmp_path / "not-a-directory"
    path.write_text("untouched")
    updater = Updater(downloads=path, opener=lambda url: io.BytesIO(b"package"))
    updater.release = release_info([release()], "0.1.0b4", "linux", "x86_64")
    updater.download(updater.release["assets"][0]["name"])
    assert finish(updater)["error"] == "update_storage"
    assert path.read_text() == "untouched"


def test_missing_feed_falls_back_to_releases_api():
    calls = []

    def opener(url):
        calls.append(url)
        if url == MANIFEST:
            raise HTTPError(url, 404, "missing", {}, None)
        return io.BytesIO(json.dumps([release("v0.1.0", "0.1.0")]).encode())

    updater = Updater(current="0.1.0", opener=opener)
    updater.check()
    assert finish(updater)["phase"] == "current"
    assert calls == [MANIFEST, API]
