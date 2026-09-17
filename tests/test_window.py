import os
import threading
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from webview.event import Event

from shiwen.app import Bridge
from shiwen.desktop import WindowControls
from shiwen.library import Library


def test_window_actions_toggle_and_keep_resize_bounds(monkeypatch):
    monkeypatch.setattr("shiwen.desktop.platform", "win32")
    window = Mock()
    window.events = SimpleNamespace(
        maximized=Event(window), restored=Event(window), minimized=Event(window)
    )
    controls = WindowControls(window)
    assert controls.action("maximize")["maximized"]
    window.maximize.assert_called_once()
    controls.action("resize", width=900, height=700)
    window.resize.assert_not_called()
    assert not controls.action("maximize")["maximized"]
    window.restore.assert_called_once()
    controls.action("resize", width=1, height=1, edge="nw")
    assert window.resize.call_args.args[:2] == (780, 580)
    controls.action("minimize")
    window.minimize.assert_called_once()
    with pytest.raises(ValueError):
        controls.action("resize", width="bad", height=900)
    with pytest.raises(ValueError):
        controls.action("launch_process")
    closed = threading.Event()
    window.destroy.side_effect = closed.set
    controls.action("close")
    assert closed.wait(2)


def test_browser_preview_cannot_control_desktop(tmp_path):
    library = Library(tmp_path)
    bridge = Bridge(library)
    try:
        assert bridge.call("window", {"action": "close"}) == {"ok": False, "error": "desktop_only"}
    finally:
        bridge._close()


def test_software_rendering_fallback_preserves_explicit_preference(monkeypatch):
    from shiwen.desktop import configure_linux_rendering

    monkeypatch.setattr("shiwen.desktop.platform", "linux")
    monkeypatch.setattr("shiwen.desktop.os.access", lambda *_: False)
    monkeypatch.delenv("WEBKIT_DISABLE_COMPOSITING_MODE", raising=False)
    configure_linux_rendering()
    assert os.environ["WEBKIT_DISABLE_COMPOSITING_MODE"] == "1"
    monkeypatch.setenv("WEBKIT_DISABLE_COMPOSITING_MODE", "0")
    configure_linux_rendering()
    assert os.environ["WEBKIT_DISABLE_COMPOSITING_MODE"] == "0"
