"""Keep GTK WebView callbacks from holding the process open after window close."""

import os
import threading
from pathlib import Path
from sys import platform


def guard_evaluation(window, closing):
    # GTK may destroy its event loop before delivering evaluate_javascript's
    # callback. pywebview's non-daemon RPC thread would then wait forever.
    window.evaluate_js = _until_closed(window.evaluate_js, closing)
    window.run_js = _until_closed(window.run_js, closing)


def _until_closed(evaluate, closing):

    def evaluate_until_closed(*args, **kwargs):
        if closing.is_set():
            return None
        completed = threading.Event()
        result, errors = [], []

        def run():
            try:
                if not closing.is_set():
                    result.append(evaluate(*args, **kwargs))
            except Exception as error:
                errors.append(error)
            finally:
                completed.set()

        threading.Thread(target=run, name="shiwen-webview", daemon=True).start()
        while not completed.wait(0.05):
            if closing.is_set():
                return None
        if closing.is_set():
            return None
        if errors:
            raise errors[0]
        return result[0] if result else None

    return evaluate_until_closed


def configure_linux_rendering():
    """Avoid expensive software GL compositing when no render device is accessible."""
    if platform != "linux":
        return
    devices = [*Path("/dev/dri").glob("renderD*"), Path("/dev/nvidia0")]
    if not any(os.access(path, os.R_OK | os.W_OK) for path in devices):
        os.environ.setdefault("WEBKIT_DISABLE_COMPOSITING_MODE", "1")


class WindowControls:
    """A narrow command surface for the app's own frameless window."""

    def __init__(self, window):
        self.window = window
        self.maximized = False
        self.restore_bounds = None
        self.minimized = False
        window.events.maximized += lambda: self._set_maximized(True)
        window.events.minimized += self._minimized
        window.events.restored += self._restored

    def _set_maximized(self, value):
        self.maximized = value

    def _minimized(self):
        self.minimized = True

    def _restored(self):
        if not self.minimized:
            self.maximized = False
        self.minimized = False

    def state(self):
        return {"maximized": self.maximized}

    def action(self, action, width=None, height=None, edge="se"):
        if action == "minimize":
            self.window.minimize()
        elif action == "maximize":
            target = not self.maximized
            if target:
                self.restore_bounds = (
                    self.window.width,
                    self.window.height,
                    self.window.x,
                    self.window.y,
                )
                self.window.maximize()
            elif platform == "linux":
                # GTK's pywebview restore only deiconifies; it does not unmaximize.
                from gi.repository import GLib

                GLib.idle_add(self.window.native.unmaximize)
            elif platform == "darwin" and self.restore_bounds:
                # Cocoa's restore also only deminiaturizes.
                width, height, x, y = self.restore_bounds
                self.window.resize(width, height)
                self.window.move(x, y)
            else:
                self.window.restore()
            self.maximized = target
        elif action == "close":
            # Return the RPC before the native WebView is destroyed.
            closer = threading.Timer(0.05, self.window.destroy)
            closer.daemon = True
            closer.start()
        elif action == "resize":
            if edge not in {"n", "ne", "e", "se", "s", "sw", "w", "nw"}:
                raise ValueError("invalid_setting")
            if type(width) is not int or type(height) is not int:
                raise ValueError("invalid_setting")
            if not self.maximized:
                from webview.window import FixPoint

                anchor = (FixPoint.EAST if "w" in edge else FixPoint.WEST) | (
                    FixPoint.SOUTH if "n" in edge else FixPoint.NORTH
                )
                self.window.resize(
                    max(780, min(width, 16384)), max(580, min(height, 16384)), anchor
                )
        elif action != "state":
            raise ValueError("invalid_setting")
        return self.state()
