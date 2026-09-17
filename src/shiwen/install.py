"""Install a Linux portable bundle into a user's local prefix without touching indexes."""

import argparse
import ast
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .updates import version


def bundle_version(bundle):
    tree = ast.parse((bundle / "vendor/shiwen/__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            if isinstance(value, str) and version(value):
                return value
    raise ValueError("Invalid Shiwen bundle version")


def atomic_text(path, text, mode=0o644):
    temporary = path.with_name("." + path.name + ".install")
    temporary.write_text(text, encoding="utf-8")
    temporary.chmod(mode)
    os.replace(temporary, path)


def install_bundle(source, prefix):
    import fcntl

    source, prefix = source.resolve(), prefix.resolve()
    release = bundle_version(source)
    for required in ["shiwen", "launch.py", "shiwen.svg"]:
        if not (source / required).is_file():
            raise ValueError(f"Incomplete bundle: {required}")
    base = prefix / "share/shiwen"
    base.mkdir(parents=True, exist_ok=True)
    with (base / "install.lock").open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        current = base / "current"
        if current.exists() and version(bundle_version(current)) > version(release):
            raise ValueError("Refusing to replace a newer installed version")
        target = base / release
        if target.exists():
            # Reinstalling repairs entry points only when the application payload matches.
            for path in (source / "vendor/shiwen").rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    existing = target / path.relative_to(source)
                    if not existing.is_file() or existing.read_bytes() != path.read_bytes():
                        raise ValueError(f"Existing version differs; preserved at {target}")
        else:
            staging = Path(tempfile.mkdtemp(prefix=".install-", dir=base))
            try:
                shutil.copytree(
                    source, staging / "bundle", ignore=shutil.ignore_patterns("__pycache__")
                )
                os.replace(staging / "bundle", target)
            finally:
                shutil.rmtree(staging)
        link = base / ".current-install"
        link.unlink(missing_ok=True)
        link.symlink_to(target.name, target_is_directory=True)
        os.replace(link, current)

        # Keep legacy absolute shortcuts useful, including cached launch.py commands.
        for old in base.iterdir():
            if not re.fullmatch(r"\d+\.\d+\.\d+(?:[ab]|rc)?\d*", old.name) or old == target:
                continue
            entry = old / "launch.py"
            if not entry.is_file():
                continue
            backup = old / "launch.py.before-upgrade"
            if not backup.exists():
                shutil.copy2(entry, backup)
            text = backup.read_text(encoding="utf-8")
            marker = 'if __name__ == "__main__":'
            if marker not in text:
                continue
            redirect = (
                marker + "\n    import os\n"
                f"    target = Path({str(current / 'launch.py')!r}).resolve(strict=True)\n"
                '    os.execv("/usr/bin/python3",\n'
                '             ["/usr/bin/python3", "-I", str(target), *sys.argv[1:]])\n\n' + marker
            )
            atomic_text(entry, text.replace(marker, redirect, 1))

        binaries = prefix / "bin"
        applications = prefix / "share/applications"
        binaries.mkdir(parents=True, exist_ok=True)
        applications.mkdir(parents=True, exist_ok=True)
        launcher = binaries / "shiwen-app"
        atomic_text(
            launcher, f'#!/bin/sh\nexec {shlex.quote(str(current / "shiwen"))} "$@"\n', 0o755
        )
        command = (
            str(launcher)
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("`", "\\`")
            .replace("$", "\\$")
            .replace("%", "%%")
        )
        desktop = (
            "[Desktop Entry]\nVersion=1.0\nType=Application\nName=Shiwen\nName[zh_CN]=拾文\n"
            f'Exec="{command}"\nIcon={current / "shiwen.svg"}\n'
            "Terminal=false\nCategories=Office;\nKeywords=search;documents;pdf;markdown;docx;\n"
            "StartupNotify=true\nStartupWMClass=Shiwen\n"
        )
        atomic_text(applications / "io.github.asoming.shiwen.desktop", desktop)
        if shutil.which("update-desktop-database"):
            subprocess.run(["update-desktop-database", str(applications)], check=True)
        return target


def main():
    parser = argparse.ArgumentParser(description="Install Shiwen for the current Linux user")
    parser.add_argument("--prefix", type=Path, default=Path.home() / ".local")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("This installer requires Linux")
    source = Path(__file__).resolve().parents[2]
    try:
        target = install_bundle(source, args.prefix)
    except (OSError, ValueError) as error:
        parser.exit(1, f"安装失败 / Installation failed: {error}\n")
    print(
        f"安装完成 / Installed: {target}\n"
        "请退出旧窗口后从菜单打开拾文 / Quit the old app, then reopen Shiwen."
    )
