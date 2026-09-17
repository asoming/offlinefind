"""Exercise production frameless UI and sample its complete desktop process tree."""

import argparse
import json
import platform
import sys
import threading
import time
from pathlib import Path

import psutil
import webview

from shiwen import __version__, app
from shiwen.library import Library


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Acceptance corpus directory")
    parser.add_argument("--existing-index", action="store_true")
    args = parser.parse_args()
    directory = args.directory.resolve()
    folder = directory / "documents"
    data = directory / ("index" if args.existing_index else "desktop-index")
    result = {
        "version": __version__,
        "platform": platform.platform(),
        "ok": False,
        "checks": [],
        "memory_scope": (
            "Application/descendant RSS including WebView and parser; "
            "shared pages can be counted twice"
        ),
    }
    samples, stop = [], threading.Event()
    process = psutil.Process()
    initial_pids = set(psutil.pids())
    webkit_services = {}
    phase = "startup"
    before_launch = time.perf_counter()

    def monitor():
        sampler_cpu = 0.0
        while not stop.wait(0.1):
            sample_started = time.thread_time()
            rss, cpu, names = 0, 0, set()
            if sys.platform == "darwin":
                for candidate in psutil.process_iter(["name"]):
                    if candidate.pid not in initial_pids and "WebKit" in (
                        candidate.info["name"] or ""
                    ):
                        webkit_services[candidate.pid] = candidate
            members = {p.pid: p for p in [process, *process.children(recursive=True)]}
            members.update(webkit_services)
            for child in members.values():
                try:
                    rss += child.memory_info().rss
                    times = child.cpu_times()
                    cpu += times.user + times.system
                    names.add(child.name())
                except psutil.Error:
                    pass
            sampler_cpu += time.thread_time() - sample_started
            samples.append((phase, time.perf_counter(), rss, cpu - sampler_cpu, sorted(names)))

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    original_start = webview.start

    # Bound automatic discovery to the generated fixture disk, keeping the production UI/lifecycle.
    def scoped_library(*a, **kw):
        library = Library(*a, **(kw | {"disk_provider": lambda: ([folder], set())}))
        library.store.set_setting("language", "zh")
        library.store.set_setting("theme", "light")
        return library

    app.Library = scoped_library

    def check():
        nonlocal phase
        window = webview.windows[0]

        def wait(expression, timeout=30):
            until = time.monotonic() + timeout
            while time.monotonic() < until:
                value = window.evaluate_js(expression)
                if value:
                    return value
                time.sleep(0.1)
            raise AssertionError("UI condition timed out: " + expression)

        def click(selector):
            window.evaluate_js(f"window.qa({json.dumps(selector)}).click()")

        def change(selector, value, event="change"):
            window.evaluate_js(
                f"(()=>{{const el=window.qa({json.dumps(selector)});"
                f"el.value={json.dumps(value)};el.dispatchEvent(new Event('{event}',"
                "{bubbles:true}));})()"
            )

        def capture(name):
            if sys.platform != "linux":
                return
            from webview.platforms.gtk import BrowserView, glib, webkit

            done, errors = threading.Event(), []
            view = BrowserView.instances[window.uid].webview

            def received(view, response, _):
                try:
                    surface = view.get_snapshot_finish(response)
                    surface.write_to_png(str(directory / name))
                except Exception as error:
                    errors.append(error)
                finally:
                    done.set()

            def save():
                view.get_snapshot(
                    webkit.SnapshotRegion.VISIBLE, webkit.SnapshotOptions.NONE, None, received, None
                )
                return False

            glib.idle_add(save)
            assert done.wait(10), "WebKit snapshot timed out"
            if errors:
                raise errors[0]

        try:
            assert window.events.loaded.wait(30)
            window.evaluate_js(
                "window.qa = s => document.querySelector(s);"
                "window.qas = s => document.querySelectorAll(s)"
            )
            wait(
                "!window.qa('#window-controls').hidden && window.qas('#results .result').length > 0"
            )
            result["first_results_seconds"] = time.perf_counter() - before_launch
            result["checks"].append("production automatic discovery and integrated controls")
            if args.existing_index:
                phase = "ready_before_interaction"
                time.sleep(10)
                phase = "interaction"
            assert window.frameless and not window.easy_drag and window.resizable
            if sys.platform == "linux":
                assert not window.native.get_decorated()
            minimized, maximized, restored = threading.Event(), threading.Event(), threading.Event()
            window.events.minimized += minimized.set
            window.events.maximized += maximized.set
            window.events.restored += restored.set
            click("#window-minimize")
            assert minimized.wait(8), "Native minimize event missing"
            window.restore()
            window.show()
            time.sleep(0.3)
            click("#window-maximize")
            if sys.platform != "darwin":
                assert maximized.wait(8), "Native maximize event missing"
            wait("window.qa('#window-maximize').getAttribute('aria-pressed') === 'true'")
            restored.clear()
            click("#window-maximize")
            if sys.platform != "darwin":
                assert restored.wait(8), "Native restore event missing"
            wait("window.qa('#window-maximize').getAttribute('aria-pressed') === 'false'")
            result["checks"].append("native minimize, maximize and restore from custom buttons")
            window.evaluate_js(
                "window.pywebview.api.call('window',{action:'resize',width:900,height:620,edge:'se'})"
            )
            wait("innerWidth === 900 && innerHeight === 620")
            result["checks"].append("frameless resize")
            # Exercise the actual pywebview drag-region handler with a bounded displacement.
            x, y = window.x, window.y
            window.evaluate_js(f"""(()=>{{const el=window.qa('.heading-drag');
              el.dispatchEvent(new MouseEvent('mousedown',{{bubbles:true,clientX:300,clientY:45,
                screenX:{x + 300},screenY:{y + 45}}}));
              window.dispatchEvent(new MouseEvent('mousemove',{{bubbles:true,
                screenX:{x + 330},screenY:{y + 65}}}));
              window.dispatchEvent(new MouseEvent('mouseup',{{bubbles:true}}));}})()""")
            deadline = time.monotonic() + 5
            while (window.x, window.y) == (x, y) and time.monotonic() < deadline:
                time.sleep(0.1)
            assert (window.x, window.y) != (x, y), "Drag region did not move the native window"
            result["checks"].append("drag region moves native window")
            window.move(x, y)
            phase = "indexing"
            wait(
                "window.qa('#status-label').textContent.includes('就绪')",
                600,
            )
            change("#query", "离线部署", "input")
            wait("window.qas('#results mark').length > 0")
            click("#results .result")
            wait("window.qas('#document mark').length > 0")
            saved = window.evaluate_js("window.qa('#bookmark').getAttribute('aria-pressed')")
            click("#bookmark")
            target = "false" if saved == "true" else "true"
            wait(f"window.qa('#bookmark').getAttribute('aria-pressed') === '{target}'")
            result["checks"].append("content search, preview highlights and bookmark")
            for kind in ["pdf", "md", "docx"]:
                click(f"[data-type='{kind}']")
                wait(
                    "window.qas('#results .result').length > 0 && "
                    f"window.qa('#results .file-icon.{kind}')"
                )
            click("[data-type='all']")
            result["checks"].append("PDF, Markdown and complete DOCX filters")
            click("#settings-button")
            wait("window.qa('#settings-dialog').open")
            change("#language", "en")
            wait("document.documentElement.lang === 'en'")
            change("#theme", "dark")
            wait("document.documentElement.dataset.theme === 'dark'")
            click("[data-close='settings-dialog']")
            capture("desktop-dark.png")
            click("#settings-button")
            change("#language", "zh")
            wait("document.documentElement.lang === 'zh-CN'")
            change("#theme", "light")
            wait("document.documentElement.dataset.theme === 'light'")
            click("[data-close='settings-dialog']")
            width = min(1220, int(window.evaluate_js("screen.availWidth")))
            height = min(820, int(window.evaluate_js("screen.availHeight")))
            window.resize(width, height)
            wait(f"innerWidth === {width}")
            capture("desktop-light.png")
            result["checks"].append("settings dialog, Chinese/English, dark/light layouts")
            phase = "idle"
            time.sleep(10)
            result["ok"] = True
        except Exception as error:
            result["error"] = str(error)
            result["geometry"] = window.evaluate_js(
                "({width:innerWidth,height:innerHeight,dpr:devicePixelRatio,"
                "screenWidth:screen.availWidth,screenHeight:screen.availHeight})"
            )
        finally:
            phase = "closing"
            result["close_requested_at"] = time.monotonic()
            try:
                click("#window-close")
            except Exception:
                window.destroy()

    def start(*a, **kw):
        return original_start(*a, **(kw | {"func": check}))

    webview.start = start
    sys.argv = ["shiwen", "--data-dir", str(data)]
    try:
        app.main()
    finally:
        stop.set()
        thread.join(2)
        result["close_seconds"] = time.monotonic() - result.get(
            "close_requested_at", time.monotonic()
        )
        result["ok"] = result["ok"] and result["close_seconds"] < 15
        result["webkit_service_sampling"] = (
            "New WebKit XPC processes on this otherwise isolated CI desktop; "
            "not necessarily private memory; pre-existing shared services excluded"
            if sys.platform == "darwin"
            else "Application descendants"
        )
        result["cpu_note"] = (
            "One-core percent; sampler thread CPU subtracted; closing is a separate phase"
        )
        result["memory"] = {}
        for name in {row[0] for row in samples}:
            group = [row for row in samples if row[0] == name]
            result["memory"][name] = {
                "samples": len(group),
                "rss_peak_bytes": max(row[2] for row in group),
                "rss_last_bytes": group[-1][2],
                "process_names": sorted({p for row in group for p in row[4]}),
            }
            if name == "idle" and len(group) > 1:
                result["idle_cpu_percent_one_core"] = (
                    max(0, group[-1][3] - group[0][3]) / (group[-1][1] - group[0][1]) * 100
                )
        (directory / "desktop-report.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2), flush=True)
    assert result["ok"], result


if __name__ == "__main__":
    main()
