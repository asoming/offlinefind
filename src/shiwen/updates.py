"""User-triggered GitHub release checks and verified package downloads."""

import hashlib
import json
import platform
import re
import ssl
import sys
import tempfile
import threading
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

import certifi
from platformdirs import user_downloads_path

from . import __version__

REPOSITORY = "https://github.com/asoming/offlinefind"
LEGACY_REPOSITORY = "https://github.com/asoming/shiwen"
RELEASES = REPOSITORY + "/releases"
API = "https://api.github.com/repos/asoming/offlinefind/releases?per_page=100"
MANIFEST = "https://raw.githubusercontent.com/asoming/offlinefind/main/updates/latest.json"
MAX_PACKAGE = 512 * 1024 * 1024


def version(value):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:-?(alpha|beta|rc|a|b)[.-]?(\d+))?", value)
    if not match:
        return None
    major, minor, patch, stage, number = match.groups()
    rank = {"a": 0, "alpha": 0, "b": 1, "beta": 1, "rc": 2, None: 3}[stage]
    return int(major), int(minor), int(patch), rank, int(number or 0)


def package_version(parsed):
    major, minor, patch, rank, number = parsed
    suffix = "" if rank == 3 else f"{['a', 'b', 'rc'][rank]}{number}"
    return f"{major}.{minor}.{patch}{suffix}"


def allowed_url(url):
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return (
        parsed.scheme == "https"
        and not parsed.username
        and not parsed.password
        and parsed.port in {None, 443}
        and (host in {"github.com", "api.github.com"} or host.endswith(".githubusercontent.com"))
    )


class GitHubRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl):
            raise ValueError("update_invalid")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def tls_context():
    context = ssl.create_default_context()
    context.load_verify_locations(certifi.where())
    return context


def open_url(url):
    if not allowed_url(url):
        raise ValueError("update_invalid")
    request = Request(url, headers={"User-Agent": f"OfflineFind/{__version__}", "Accept": "*/*"})
    return build_opener(GitHubRedirects(), HTTPSHandler(context=tls_context())).open(
        request, timeout=15
    )


def release_info(releases, current, system, machine):
    current_version = version(current)
    candidates = []
    for release in releases:
        parsed = version(release.get("tag_name", ""))
        if not parsed or release.get("draft") or not release.get("published_at"):
            continue
        if current_version[3] == 3 and (release.get("prerelease") or parsed[3] != 3):
            continue
        candidates.append((parsed, release))
    if not candidates:
        raise ValueError("update_no_release")
    parsed, release = max(candidates, key=lambda item: item[0])
    package = package_version(parsed)
    suffixes = {
        ("linux", "x64"): ["linux-amd64.deb", "linux-x64.tar.gz"],
        ("win32", "x64"): ["windows-x64.zip"],
        ("darwin", "arm64"): ["macos-arm64.zip"],
    }
    arch = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64", "aarch64": "arm64"}.get(
        machine.lower(), machine.lower()
    )
    by_name = {a["name"]: a for a in release.get("assets", []) if a.get("state") == "uploaded"}
    choices = []
    for suffix in suffixes.get((system, arch), []):
        name = f"OfflineFind-{package}-{suffix}"
        if name not in by_name:
            name = f"Shiwen-{package}-{suffix}"
        asset = by_name.get(name)
        if not asset or not 0 < asset.get("size", 0) <= MAX_PACKAGE:
            continue
        url = f"{REPOSITORY}/releases/download/{release['tag_name']}/{name}"
        legacy_url = f"{LEGACY_REPOSITORY}/releases/download/{release['tag_name']}/{name}"
        if asset.get("browser_download_url") not in {url, legacy_url}:
            continue
        digest = asset.get("digest") or ""
        checksum = by_name.get(name + ".sha256")
        if re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest):
            checksum_url = None
        elif checksum and checksum.get("browser_download_url") in {
            url + ".sha256",
            legacy_url + ".sha256",
        }:
            checksum_url = url + ".sha256"
            digest = ""
        else:
            continue
        choices.append(
            {
                "name": name,
                "size": asset["size"],
                "url": url,
                "digest": digest.removeprefix("sha256:").lower(),
                "checksum_url": checksum_url,
            }
        )
    return {
        "version": release["tag_name"],
        "newer": parsed > current_version,
        "notes": str(release.get("body") or "")[:16000],
        "release_url": f"{RELEASES}/tag/{release['tag_name']}",
        "assets": choices if parsed >= current_version else [],
    }


class Updater:
    def __init__(self, current=__version__, downloads=None, opener=open_url):
        self.current = current
        self.downloads = downloads
        self.opener = opener
        self.lock = threading.RLock()
        self.cancelled = threading.Event()
        self.worker = None
        self.release = None
        self.state = {"phase": "idle", "current": current, "received": 0, "total": 0}

    def status(self):
        with self.lock:
            return dict(self.state)

    def _set(self, **values):
        with self.lock:
            self.state.update(values)

    def _start(self, phase, action):
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("update_busy")
            self.cancelled.clear()
            if phase == "checking":
                self.release = None
                self.state.update(assets=[], notes="", version=None)
            self.state.update(phase=phase, error=None, path=None, received=0, total=0)
            self.worker = threading.Thread(target=self._perform, args=(action,), daemon=True)
            self.worker.start()
        return self.status()

    def check(self):
        return self._start("checking", self._check)

    def _check(self):
        try:
            response = self.opener(MANIFEST)
        except (HTTPError, URLError):
            response = self.opener(API)
        with response:
            body = response.read(2 * 1024 * 1024 + 1)
        if len(body) > 2 * 1024 * 1024:
            raise ValueError("update_invalid")
        releases = json.loads(body)
        if not isinstance(releases, list):
            raise ValueError("update_invalid")
        info = release_info(releases, self.current, sys.platform, platform.machine())
        if self.cancelled.is_set():
            raise ValueError("update_cancelled")
        with self.lock:
            self.release = info
            self.state.update(
                phase="available" if info["newer"] else "current",
                version=info["version"],
                notes=info["notes"],
                assets=[{"name": a["name"], "size": a["size"]} for a in info["assets"]],
            )

    def download(self, name):
        with self.lock:
            asset = next(
                (a for a in (self.release or {}).get("assets", []) if a["name"] == name), None
            )
            if asset is None:
                raise ValueError("update_invalid")
            return self._start("downloading", lambda: self._download(asset))

    def _download(self, asset):
        expected = asset["digest"]
        if not expected:
            with self.opener(asset["checksum_url"]) as response:
                text = response.read(4097).decode("utf-8").strip()
            match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+)", text)
            if not match or match[2] != asset["name"]:
                raise ValueError("update_integrity")
            expected = match[1].lower()
        base = Path(self.downloads) if self.downloads else user_downloads_path()
        base.mkdir(parents=True, exist_ok=True)
        destination = Path(tempfile.mkdtemp(prefix="OfflineFind-", dir=base))
        partial = destination / (asset["name"] + ".part")
        target = destination / asset["name"]
        self._set(total=asset["size"])
        try:
            digest = hashlib.sha256()
            received = 0
            with self.opener(asset["url"]) as response, partial.open("xb") as output:
                while True:
                    if self.cancelled.is_set():
                        raise ValueError("update_cancelled")
                    chunk = response.read(64 * 1024)
                    if not chunk:
                        break
                    received += len(chunk)
                    if received > asset["size"]:
                        raise ValueError("update_integrity")
                    output.write(chunk)
                    digest.update(chunk)
                    self._set(received=received)
            if received != asset["size"] or digest.hexdigest() != expected:
                raise ValueError("update_integrity")
            with self.lock:
                if self.cancelled.is_set():
                    raise ValueError("update_cancelled")
                partial.replace(target)
                self.state.update(phase="downloaded", path=str(target))
        finally:
            partial.unlink(missing_ok=True)
            if not target.exists():
                destination.rmdir()

    def _perform(self, action):
        try:
            action()
        except HTTPError as error:
            self._set(
                phase="error",
                error="update_rate_limit" if error.code in {403, 429} else "update_network",
            )
        except (URLError, TimeoutError, ConnectionError, HTTPException, ssl.SSLError):
            self._set(phase="error", error="update_network")
        except OSError:
            self._set(phase="error", error="update_storage")
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            known = {"update_no_release", "update_integrity", "update_cancelled"}
            code = str(error) if str(error) in known else "update_invalid"
            self._set(phase="cancelled" if code == "update_cancelled" else "error", error=code)

        finally:
            with self.lock:
                if self.cancelled.is_set() and self.state["phase"] != "downloaded":
                    self.state.update(phase="cancelled", error=None)

    def cancel(self):
        with self.lock:
            if self.state["phase"] in {"checking", "downloading"}:
                self.cancelled.set()
        return self.status()

    def close(self):
        self.cancel()
        if self.worker:
            self.worker.join(timeout=20)
