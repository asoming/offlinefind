"""Desktop entry point, narrow native bridge, and opt-in loopback developer mode."""

import argparse
import hmac
import json
import multiprocessing
import os
import secrets
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from platformdirs import user_data_path

from . import __version__
from .library import Library


class Bridge:
    def __init__(self, library: Library):
        self._library = library
        self._window = None

    def call(self, method: str, args: dict | None = None) -> dict:
        args = args or {}
        library = self._library
        actions = {
            "status": library.status,
            "search": library.search,
            "document": library.document,
            "choose_folder": self._choose_folder,
            "remove_root": library.remove_root,
            "exclude": library.exclude,
            "remove_exclusion": library.remove_exclusion,
            "issues": library.issues,
            "bookmark": library.store.bookmark,
            "pause": library.pause,
            "retry": library.retry_all,
            "retry_document": library.retry_document,
            "setting": self._setting,
            "clear": library.clear,
            "open": self._open,
        }
        if method not in actions:
            return {"ok": False, "error": "unknown_action"}
        try:
            return {"ok": True, "data": actions[method](**args)}
        except ValueError as exc:
            code = str(exc)
            known = {
                "query_too_long",
                "unclosed_quote",
                "too_many_terms",
                "query_too_short",
                "invalid_folder",
                "folder_too_broad",
                "invalid_exclusion",
                "unavailable",
                "invalid_setting",
                "cloud",
                "desktop_only",
            }
            return {"ok": False, "error": code if code in known else "operation_failed"}
        except (OSError, TypeError):
            return {"ok": False, "error": "operation_failed"}

    def _choose_folder(self):
        if self._window is None:
            raise ValueError("desktop_only")
        import webview

        paths = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if paths:
            return self._library.add_root(paths[0])
        return None

    def _setting(self, key: str, value):
        valid = {
            "theme": {"system", "light", "dark"},
            "language": {"zh", "en"},
            "resource": {"standard", "low"},
            "glass": {True, False},
        }
        if key not in valid or value not in valid[key]:
            raise ValueError("invalid_setting")
        self._library.store.set_setting(key, value)

    def _open(self, document_id: int, reveal: bool = False):
        path = self._library.verified_path(document_id)
        if sys.platform == "win32":
            if reveal:
                subprocess.Popen(["explorer.exe", "/select,", str(path)])
            else:
                os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", *(["-R"] if reveal else []), str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path.parent if reveal else path)])


def html(token: str = "") -> str:
    ui = Path(__file__).with_name("ui")
    return (
        ui.joinpath("index.html")
        .read_text(encoding="utf-8")
        .replace("/*__STYLE__*/", ui.joinpath("style.css").read_text(encoding="utf-8"))
        .replace("/*__SCRIPT__*/", ui.joinpath("app.js").read_text(encoding="utf-8"))
        .replace(
            "/*__BOOT__*/",
            f"window.SHIWEN_BOOT={json.dumps({'token': token, 'version': __version__})};",
        )
    )


def serve(bridge: Bridge, port: int):
    token = secrets.token_urlsafe(32)
    content = html(token).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def _respond(self, code, body, content_type="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def _valid_host(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def do_GET(self):
            if not self._valid_host():
                self._respond(403, b"{}")
            elif self.path == "/":
                self._respond(200, content, "text/html; charset=utf-8")
            else:
                self._respond(404, b"{}")

        def do_POST(self):
            expected_origin = f"http://127.0.0.1:{self.server.server_port}"
            if (
                not self._valid_host()
                or self.path != "/api"
                or not hmac.compare_digest(self.headers.get("X-Shiwen-Token", ""), token)
                or self.headers.get("Origin", expected_origin) != expected_origin
            ):
                self._respond(403, b"{}")
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 1 or size > 32768:
                    raise ValueError
                payload = json.loads(self.rfile.read(size))
                result = bridge.call(payload["method"], payload.get("args", {}))
            except (ValueError, KeyError, TypeError):
                self._respond(400, b"{}")
                return
            self._respond(200, json.dumps(result, ensure_ascii=False).encode("utf-8"))

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Shiwen developer preview: http://127.0.0.1:{server.server_port}/", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def self_test(destination: Path):
    """Exercise the packaged parser, FTS, and persistence without requiring a GUI."""
    import time

    from .extract import extract_isolated

    with tempfile.TemporaryDirectory(prefix="shiwen-smoke-") as temporary:
        base = Path(temporary)
        folder = base / "documents"
        folder.mkdir()
        note = folder / "测试.md"
        note.write_text("# Offline\n支持离线部署。Local files stay private.", encoding="utf-8")
        os.utime(note, (time.time() - 5, time.time() - 5))
        library = Library(
            base / "data",
            extractor=extract_isolated,
            automatic=True,
            disk_provider=lambda: ([folder], set()),
        )
        try:
            library.scan()
            assert len(library.search(query="测试")["items"]) == 1
            library.parse_pending()
            result = library.search(query="部署")
            assert len(result["items"]) == 1
            assert "离线部署" in library.document(result["items"][0]["id"])["blocks"][0]["text"]
            destination.write_text(
                json.dumps({"ok": True, "version": __version__, "platform": sys.platform}),
                encoding="utf-8",
            )
        finally:
            library.close()


def main():
    multiprocessing.freeze_support()
    parser = argparse.ArgumentParser(description="Shiwen · offline document search")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--data-dir", type=Path, default=user_data_path("Shiwen", appauthor=False))
    parser.add_argument(
        "--folder", action="append", default=[], help="Explicitly add a local folder"
    )
    parser.add_argument(
        "--serve", action="store_true", help="Loopback-only browser development mode"
    )
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--self-test", type=Path, metavar="RESULT_JSON")
    parser.add_argument("--gui-smoke", type=Path, metavar="RESULT_JSON")
    args = parser.parse_args()
    if args.self_test:
        self_test(args.self_test)
        return
    library = Library(
        args.data_dir,
        automatic=not args.folder,
        disk_provider=(lambda: ([], set())) if args.gui_smoke else None,
    )
    bridge = Bridge(library)
    try:
        for folder in args.folder:
            library.add_root(folder)
        library.start()
        if args.serve:
            serve(bridge, args.port)
        else:
            import webview

            window = webview.create_window(
                "拾文 · Shiwen",
                html=html(),
                js_api=bridge,
                width=1220,
                height=820,
                min_size=(780, 580),
                background_color="#f5f7fa",
                text_select=True,
                hidden=bool(args.gui_smoke),
            )
            bridge._window = window
            smoke = None
            if args.gui_smoke:

                def smoke():
                    finished = threading.Event()
                    result = {"ok": False, "timeout": True}

                    def complete(value):
                        nonlocal result
                        result = value
                        finished.set()

                    window.events.loaded.wait(20)
                    window.evaluate_js(
                        "window.pywebview.api.call('status', {}).then(function(r) {"
                        "return {ok: r.ok && !!document.querySelector('#query'),"
                        "bridge: !!r.data, title: document.title}; })",
                        callback=complete,
                    )
                    finished.wait(30)
                    args.gui_smoke.write_text(json.dumps(result), encoding="utf-8")
                    # Let GTK finish returning the RPC result before destroying its WebView.
                    window.evaluate_js("document.title")
                    window.destroy()

            webview.start(
                func=smoke,
                gui={"win32": "edgechromium", "linux": "gtk"}.get(sys.platform),
                private_mode=True,
                debug=False,
            )
    finally:
        library.close()


if __name__ == "__main__":
    main()
