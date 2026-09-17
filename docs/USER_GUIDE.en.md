# User guide

[简体中文](USER_GUIDE.zh-CN.md) · [Home](../README.md)

## Linux installation

Supported desktop targets are Ubuntu 22.04 / 24.04 x64. Open the downloaded `.deb` in your software installer, or run:

```bash
sudo apt install ./Shiwen-*-linux-amd64.deb
shiwen
```

Find **Shiwen** in the application menu after installation. For the portable tar.gz, extract it and run `./shiwen` inside the Shiwen folder. Both packages use system Python 3.10+, GTK 3 and WebKit. Install missing dependencies with:

```bash
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1 xdg-utils
```

Existing `gir1.2-webkit2-4.0` also works on Ubuntu 22.04. Application Python modules are bundled; no pip or virtual-environment setup is needed. Provision system dependencies beforehand; launching, indexing and searching then work offline. Other distributions, ARM64 and headless systems are not validated targets. `sudo apt remove shiwen` removes the application but keeps your index and source files; clear the index from app settings.

## Portable installation and repeated launches

On Linux, extract the tar.gz, enter `Shiwen`, then run `./install-user`. It installs into `~/.local/share/shiwen/<version>`, creates `~/.local/bin/shiwen-app` and a menu entry, and atomically updates the `current` link. Run the same installer from each downloaded new version. No administrator privileges are needed for the app; system runtime dependencies still apply. DEB installations should be upgraded through the package manager.

Older portable launch paths under that installation follow the current version. Launcher backups are kept as `launch.py.before-upgrade`. The default index in `~/.local/share/Shiwen` is preserved. Quit the old app before installing: versions before beta.9 cannot participate in the single-instance protocol. The installer does not stop running processes.

From beta.9, a repeated launch using the same data directory requests the existing window to restore/show and exits. Different `--data-dir` values may run independently. Activation uses a random-token authenticated socket bound only to `127.0.0.1`; this is local communication, not Internet access. If local sockets are restricted, the lock still prevents duplicate indexers. Crashed processes release the lock automatically; do not delete the lock file while running.


## Open and search

Open Shiwen normally to discover local disks automatically. No folder selection is required, and mixed folders are supported. Regular files and folders are indexed by name first; an independent worker extracts PDF, Markdown and DOCX contents. Images, videos, archives, code and other formats receive a name index only, without reading their contents.

Windows discovers fixed disks with drive letters. Linux/macOS traverse the local directory tree, prioritizing the user's home directory. Virtual filesystems, network mounts, `.git`, `.cache`, dependencies, trash, symlinks and the app's own index are skipped. Ordinary hidden files remain searchable. Inaccessible folders are skipped without elevation; cloud placeholders are not downloaded. macOS privacy permissions may restrict searchable locations.

**Index & exclusions** is optional. Existing folder scopes and exclusions survive upgrades, and overlapping scopes do not duplicate results.

Discovery runs independently of content parsing, so a slow PDF does not block name indexing. Pause stops new discovery and subsequent parsing tasks. Disk reconciliation runs at approximately 30-second intervals plus traversal time. This uses ordinary filesystem traversal, not Everything's NTFS MFT / USN acceleration; equivalent first-index speed or immediate updates are not promised.

## Search

| Input | Meaning |
| --- | --- |
| `部署` | Find this exact two-character substring in a name or the extracted text |
| `budget approval` | Both terms must appear somewhere in the same document |
| `"offline deployment"` | Find a continuous phrase after case and whitespace normalization |
| `C++` | Literal substring; no regular expression or special query language |

Names support single normalized characters; single-character conditions match names only. Document contents only requires at least two characters per term. Up to 12 terms and 256 input characters are accepted. English case and full-width character variants are normalized. Simplified/traditional conversion, OCR, typo correction and semantic search are not included.

Choose Names + contents, File names only, or Document contents only. Combine type buttons (including Folders), disks and bookmarks. **Bookmarks** narrows the same search to saved references. **Last modified** uses the file's modification time, not its indexing time. Clear the text to browse recently modified documents in the current scope.

Results are shown in batches of 50. **Load more** continues without implying a precise total before all candidates have been checked.

## Read and open

Click a result to see the extracted text. Use arrows in the preview to visit matching pages or blocks. The references are PDF physical pages, Markdown starting line numbers and DOCX paragraph numbers. The preview is not a PDF renderer or a faithful Word layout.

**Open original** uses the operating system's default app. Double-clicking a result or pressing Enter in the result list does the same. **Show in folder** reveals the original location. External opening does not promise a page or paragraph jump.

Files without extracted text show the reason: OCR may be required, the document is encrypted, encoding is unsupported, or a parser limit was reached. Open the sidebar indexing status to browse a paginated list of problem files with their paths and reasons. Fix the original file or permissions, then choose **Retry this document** there or in its preview. Only that document is reparsed, preserving its bookmark; stale extracted text is withdrawn while it is pending. Paused retries wait for resume and survive restart. **Recheck all documents** still covers the whole library and retains requests made while paused or during another scan.

## Manage data

**Index & exclusions → Exclude subfolder** accepts a relative path such as `archive/private`. Exclusions override overlapping inclusions. Choose **Restore indexing** beside a rule to remove just that exclusion. The next scan rediscovers its contents; exclusions on other scopes still apply. Previously removed bookmark references are not restored when the derived index is recreated.

Automatic disks cannot be removed here; exclude subfolders instead. Clearing local data removes the index, bookmarks, exclusions and settings, then pauses indexing. Resume to rebuild from automatically discovered disks. Original files are unchanged. SQLite free space is compacted, but no forensic secure-erasure guarantee is made for SSDs.

Default data directories are `%LOCALAPPDATA%\Shiwen` on Windows, `~/Library/Application Support/Shiwen` on macOS, and `$XDG_DATA_HOME/Shiwen` (normally `~/.local/share/Shiwen`) on Linux. Settings shows the actual path. `--data-dir` overrides it for development.

## Check for updates and download

Open **Settings → Software updates → Check for updates**. The app shows the latest compatible release and its notes. Choose a package (Linux offers DEB and portable tar.gz), then **Download package**. Progress and cancellation are available. A completed download must pass size and SHA-256 verification; incomplete or invalid packages are removed.

Choose **Show download folder** after completion. Downloads go into a new `Shiwen-…` subfolder of your system Downloads directory, without overwriting earlier downloads. Quit Shiwen before installing the DEB or replacing the extracted application. Keep the existing data directory to preserve your index and settings. This version downloads packages but does not install or restart automatically.

Only manual update actions connect to GitHub. Startup, indexing, searching and opening Settings do not check online. Documents, file paths and index contents are never sent. Beta installations follow newer beta or stable releases; stable installations ignore prereleases. Older published versions are not offered as downgrades. If networking fails, retry or use **View releases** to download through your browser.

## Troubleshooting

- **No result:** check the selected folder/type, indexing progress and file status. Scanned PDFs need OCR outside Shiwen.
- **A changed file shows no text temporarily:** the stale content is withdrawn until its new version is ready. A failed update never silently serves old text as current.
- **Moved file lost its bookmark:** cross-path identity and bookmark transfer are not yet implemented. Re-bookmark its new location.
- **Windows window does not start:** verify that Edge WebView2 is installed; the app intentionally does not fall back to Internet Explorer.
- **macOS blocks launch:** use the OS's approval flow for a downloaded unsigned app; do not turn off global protections.
- **Damaged local database:** quit Shiwen and move its data directory aside, then restart to discover disks automatically. Automatic repair is planned. Do not upload the old database: it contains document text.


## Window shutdown

Clicking the integrated upper-right × exits the desktop window and requests cancellation of indexing and downloads. Unfinished documents remain pending for the next launch. There is no minimize-to-tray behavior. Beta.8 fixes a Linux callback race that could leave the old process waiting after window destruction. If an older frozen copy is still running, end that Shiwen process in the system monitor once, then reopen the upgraded application. Network cleanup may still wait for the active request's timeout.


## Frameless window controls

The system title bar is hidden. Use the upper-right buttons to minimize, maximize/restore and close. Drag the heading or brand area to move the window; double-click that area to maximize/restore. Drag any edge or corner to resize. The minimum window size is 780 × 580. Closing exits the application; it does not hide to a tray. Browser development mode cannot control a native window.

Full desktop memory can be several hundred MiB, and broad searches may take seconds. See the [measured performance](PERFORMANCE.en.md). When upgrading, quit the running old window and reopen from the application menu; installing a new version does not replace an already-running process.
