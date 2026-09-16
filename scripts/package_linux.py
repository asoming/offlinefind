"""Build small Linux packages using the system Python and GTK/WebKit runtime."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from shiwen import __version__

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.platform != "linux":
        raise SystemExit("Linux packages must be built and tested on Linux.")
    architecture = subprocess.check_output(["dpkg", "--print-architecture"], text=True).strip()
    if architecture != "amd64":
        raise SystemExit("Only the tested amd64 target is currently supported.")
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    staging = ROOT / "build" / "linux"
    shutil.rmtree(staging, ignore_errors=True)
    bundle = staging / "Shiwen"
    bundle.mkdir(parents=True)
    vendor = bundle / "vendor"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-compile",
            "--target",
            str(vendor),
            str(ROOT),
        ],
        check=True,
    )
    # No platform binaries: GTK, Python and WebKit are maintained by the OS.
    if list(vendor.rglob("*.so")):
        raise RuntimeError("Unexpected native Python extension in the portable bundle.")
    shutil.rmtree(vendor / "bin", ignore_errors=True)
    for provenance in vendor.glob("*.dist-info/direct_url.json"):
        provenance.unlink()
    for name in ["shiwen", "launch.py", "shiwen.svg"]:
        shutil.copy2(ROOT / "packaging" / "linux" / name, bundle / name)
    (bundle / "shiwen").chmod(0o755)
    for name in ["LICENSE", "THIRD_PARTY_NOTICES.md", "README.md", "README.zh-CN.md"]:
        shutil.copy2(ROOT / name, bundle / name)
    shutil.copytree(ROOT / "docs", bundle / "docs")
    shutil.copy2(ROOT / "packaging" / "linux" / "README.txt", bundle / "START-HERE.txt")
    executable = bundle / "shiwen"
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    for flag, filename in [("--self-test", "linux-core.json"), ("--gui-smoke", "linux-gui.json")]:
        result = output / filename
        result.unlink(missing_ok=True)
        subprocess.run(
            [str(executable), flag, str(result), "--data-dir", str(staging / "smoke-data")],
            check=True,
            timeout=120,
            env=environment,
        )
        if not json.loads(result.read_text(encoding="utf-8"))["ok"]:
            raise RuntimeError(f"Packaged smoke test failed: {result}")
    # Smoke tests may generate bytecode. Exclude it from the distributed source modules.
    for cache in vendor.rglob("__pycache__"):
        shutil.rmtree(cache)
    portable = output / f"Shiwen-{__version__}-linux-x64.tar.gz"
    with tarfile.open(portable, "w:gz") as archive:
        archive.add(bundle, arcname="Shiwen")

    deb_root = staging / "deb"
    shutil.copytree(bundle, deb_root / "opt" / "shiwen")
    binaries = deb_root / "usr" / "bin"
    binaries.mkdir(parents=True)
    (binaries / "shiwen").symlink_to("/opt/shiwen/shiwen")
    applications = deb_root / "usr" / "share" / "applications"
    applications.mkdir(parents=True)
    shutil.copy2(ROOT / "packaging" / "linux" / "shiwen.desktop", applications)
    icons = deb_root / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps"
    icons.mkdir(parents=True)
    shutil.copy2(bundle / "shiwen.svg", icons)
    subprocess.run(["desktop-file-validate", str(applications / "shiwen.desktop")], check=True)
    control = deb_root / "DEBIAN"
    control.mkdir()
    size = sum(path.stat().st_size for path in deb_root.rglob("*") if path.is_file()) // 1024
    deb_version = __version__.replace("b", "~beta.")
    (control / "control").write_text(
        f"Package: shiwen\nVersion: {deb_version}\nArchitecture: amd64\n"
        "Maintainer: asoming <185788094+asoming@users.noreply.github.com>\n"
        "Section: utils\nPriority: optional\n"
        "Depends: python3 (>= 3.10), python3-gi, python3-gi-cairo, gir1.2-gtk-3.0, "
        "gir1.2-webkit2-4.1 | gir1.2-webkit2-4.0, xdg-utils\n"
        f"Installed-Size: {size}\nHomepage: https://github.com/asoming/shiwen\n"
        "Description: Offline full-text document search\n"
        " Search PDF, Markdown and DOCX locally with a bilingual desktop interface.\n"
        " Document contents and indexes stay on your computer.\n",
        encoding="utf-8",
    )
    deb = output / f"Shiwen-{__version__}-linux-amd64.deb"
    subprocess.run(
        ["dpkg-deb", "--root-owner-group", "--build", str(deb_root), str(deb)], check=True
    )
    for archive in [portable, deb]:
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        Path(f"{archive}.sha256").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
        print(f"Built and smoke-tested {archive.name} ({archive.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
