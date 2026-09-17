import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from shiwen.install import install_bundle

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Linux user installer")


def bundle(base, version):
    path = base / version
    package = path / "vendor/shiwen"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(f'__version__ = "{version}"\n')
    (package / "app.py").write_text(f'def main():\n    print("{version}")\n')
    root = Path(__file__).resolve().parents[1]
    for name in ["launch.py", "shiwen", "shiwen.svg"]:
        (path / name).write_bytes((root / "packaging/linux" / name).read_bytes())
    (path / "shiwen").chmod(0o755)
    return path


def test_install_upgrade_and_old_absolute_entry_follow_current(tmp_path):
    prefix = tmp_path / "local space"
    data = prefix / "share/Shiwen"
    data.mkdir(parents=True)
    (data / "keep.sqlite3").write_bytes(b"user data stays untouched")
    old = install_bundle(bundle(tmp_path / "sources", "0.1.0b8"), prefix)
    new = install_bundle(bundle(tmp_path / "sources", "0.1.0b9"), prefix)
    assert (prefix / "share/shiwen/current").resolve() == new
    for entry in [old / "shiwen", prefix / "bin/shiwen-app", new / "shiwen"]:
        assert subprocess.check_output([str(entry), "--version"], text=True).strip() == "0.1.0b9"
    assert (
        subprocess.check_output(
            ["/usr/bin/python3", "-I", str(old / "launch.py")], text=True
        ).strip()
        == "0.1.0b9"
    )
    assert (old / "launch.py.before-upgrade").exists()
    assert (data / "keep.sqlite3").read_bytes() == b"user data stays untouched"
    menu = prefix / "share/applications/io.github.asoming.shiwen.desktop"
    if shutil.which("desktop-file-validate"):
        subprocess.run(["desktop-file-validate", str(menu)], check=True)
    assert str(prefix / "bin/shiwen-app") in menu.read_text()


def test_reinstall_repairs_entry_but_preserves_modified_install_and_blocks_downgrade(tmp_path):
    source = bundle(tmp_path / "sources", "0.1.0b9")
    prefix = tmp_path / "local"
    target = install_bundle(source, prefix)
    (prefix / "bin/shiwen-app").unlink()
    install_bundle(source, prefix)
    assert (prefix / "bin/shiwen-app").is_file()
    with pytest.raises(ValueError, match="newer"):
        install_bundle(bundle(tmp_path / "sources", "0.1.0b8"), prefix)
    (target / "vendor/shiwen/app.py").write_text("customized")
    with pytest.raises(ValueError, match="differs"):
        install_bundle(source, prefix)
    assert (target / "vendor/shiwen/app.py").read_text() == "customized"
