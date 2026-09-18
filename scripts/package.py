"""Build and smoke-test a native release on the host OS."""

import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from release_assets import finish_archive

from shiwen import __version__

ROOT = Path(__file__).resolve().parents[1]


def collect_notices() -> Path:
    destination = ROOT / "build" / "license-notices"
    destination.mkdir(parents=True, exist_ok=True)
    dependencies = []
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata["Name"]
        dependencies.append({"name": name, "version": distribution.version})
        for entry in distribution.files or []:
            if any(part.lower().startswith(("license", "copying")) for part in entry.parts):
                source = Path(distribution.locate_file(entry))
                if source.is_file():
                    target = destination / name / source.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
    (destination / "build-dependencies.json").write_text(
        json.dumps(dependencies, indent=2), encoding="utf-8"
    )
    shutil.copy2(ROOT / "THIRD_PARTY_NOTICES.md", destination)
    shutil.copy2(ROOT / "LICENSE", destination / "OFFLINEFIND-LICENSE")
    for candidate in [Path(sys.base_prefix) / "LICENSE.txt", Path(sys.base_prefix) / "LICENSE"]:
        if candidate.is_file():
            shutil.copy2(candidate, destination / "PYTHON-LICENSE")
            break
    return destination


def main():
    os.chdir(ROOT)
    if sys.platform == "linux":
        subprocess.run([sys.executable, str(ROOT / "scripts" / "package_linux.py")], check=True)
        return
    output = ROOT / "dist"
    notices = collect_notices()
    args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name",
        "OfflineFind",
        "--paths",
        "src",
        "--add-data",
        "src/shiwen/ui:shiwen/ui",
        "--add-data",
        f"{notices}:licenses",
        "--collect-data",
        "webview",
        "--collect-data",
        "certifi",
        "--hidden-import",
        "pypdf",
        "--hidden-import",
        "defusedxml.ElementTree",
    ]
    for module in ["PyQt5", "PyQt6", "PySide2", "PySide6", "IPython", "pytest", "reportlab"]:
        args.extend(["--exclude-module", module])
    if sys.platform in {"win32", "darwin"}:
        args.append("--windowed")
    if sys.platform == "darwin":
        args.extend(["--osx-bundle-identifier", "io.github.asoming.shiwen"])
    subprocess.run([*args, "launcher.py"], check=True)
    if sys.platform == "darwin":
        bundle = output / "OfflineFind.app"
        executable = bundle / "Contents" / "MacOS" / "OfflineFind"
        label = "macos-arm64" if platform.machine() == "arm64" else "macos-x64"
    else:
        bundle = output / "OfflineFind"
        executable = bundle / ("OfflineFind.exe" if sys.platform == "win32" else "OfflineFind")
        label = "windows-x64" if sys.platform == "win32" else "linux-x64"
    result = output / "smoke-result.json"
    subprocess.run([str(executable), "--self-test", str(result)], check=True, timeout=120)
    assert json.loads(result.read_text(encoding="utf-8"))["ok"]
    gui_result = output / "gui-smoke-result.json"
    subprocess.run(
        [str(executable), "--gui-smoke", str(gui_result), "--data-dir", str(output / "smoke-data")],
        check=True,
        timeout=60,
    )
    assert json.loads(gui_result.read_text(encoding="utf-8"))["ok"]
    name = f"OfflineFind-{__version__}-{label}"
    archive = output / f"{name}.zip"
    if sys.platform == "darwin":
        subprocess.run(
            ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(bundle), str(archive)],
            check=True,
        )
    else:
        shutil.make_archive(str(output / name), "zip", output, bundle.name)
    finish_archive(archive)
    print(f"Built and smoke-tested {archive.name}")


if __name__ == "__main__":
    main()
