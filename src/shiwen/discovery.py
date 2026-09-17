"""Discover local disk roots without asking the user to pick document folders."""

import ctypes
import re
import subprocess
import sys
from pathlib import Path

# Virtual filesystems and remote shares are not local document storage.
LOCAL_FILESYSTEMS = {
    "ext2",
    "ext3",
    "ext4",
    "btrfs",
    "xfs",
    "zfs",
    "ntfs",
    "ntfs3",
    "fuseblk",
    "exfat",
    "vfat",
    "f2fs",
    "jfs",
    "reiserfs",
    "hfs",
    "hfsplus",
    "apfs",
    "overlay",
}
SKIP_NAMES = {
    ".git",
    ".cache",
    ".Trash",
    ".Trashes",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "$RECYCLE.BIN",
    "System Volume Information",
}


def unescape_mount(value):
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), value)


def linux_exclusions(text):
    excluded = {Path(p) for p in ("/proc", "/sys", "/dev", "/run", "/tmp")}
    for line in text.splitlines():
        fields = line.split()
        if "-" not in fields or len(fields) < 7:
            continue
        separator = fields.index("-")
        mount = Path(unescape_mount(fields[4]))
        if mount != Path("/") and fields[separator + 1] not in LOCAL_FILESYSTEMS:
            excluded.add(mount)
    return excluded


def local_disks():
    """Return automatic roots and filesystem exclusions; never request elevation."""
    if sys.platform == "win32":
        kernel = ctypes.windll.kernel32
        kernel.GetDriveTypeW.argtypes = [ctypes.c_wchar_p]
        drives = kernel.GetLogicalDrives()
        roots = [
            Path(f"{chr(65 + index)}:\\")
            for index in range(26)
            if drives & (1 << index) and kernel.GetDriveTypeW(f"{chr(65 + index)}:\\") == 3
        ]
        return roots, set()
    if sys.platform == "darwin":
        excluded = {
            Path(p) for p in ("/dev", "/private/tmp", "/private/var/run", "/System/Volumes")
        }
        # mount's filesystem flags distinguish local volumes from network mounts.
        result = subprocess.run(
            ["/sbin/mount"], capture_output=True, text=True, check=True, timeout=10
        )
        for line in result.stdout.splitlines():
            match = re.match(r".+ on (.+) \((.+)\)$", line)
            if match and "local" not in match[2].split(", "):
                excluded.add(Path(match[1]))
        return [Path("/")], excluded
    return [Path("/")], linux_exclusions(Path("/proc/self/mountinfo").read_text())


def linked_directory(path):
    """Skip symlinks and Windows reparse directories without following their target."""
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
    except OSError:
        return True
