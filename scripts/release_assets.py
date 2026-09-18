"""Publish checksums and byte-identical legacy names for pre-rename updaters."""

import hashlib
import shutil


def finish_archive(archive):
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    legacy = archive.with_name(archive.name.replace("OfflineFind-", "Shiwen-", 1))
    shutil.copy2(archive, legacy)
    for path in (archive, legacy):
        path.with_name(path.name + ".sha256").write_text(
            f"{digest}  {path.name}\n", encoding="utf-8"
        )
