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

## Troubleshooting

- **No result:** check the selected folder/type, indexing progress and file status. Scanned PDFs need OCR outside Shiwen.
- **A changed file shows no text temporarily:** the stale content is withdrawn until its new version is ready. A failed update never silently serves old text as current.
- **Moved file lost its bookmark:** cross-path identity and bookmark transfer are not yet implemented. Re-bookmark its new location.
- **Windows window does not start:** verify that Edge WebView2 is installed; the app intentionally does not fall back to Internet Explorer.
- **macOS blocks launch:** use the OS's approval flow for a downloaded unsigned app; do not turn off global protections.
- **Damaged local database:** quit Shiwen and move its data directory aside, then restart to discover disks automatically. Automatic repair is planned. Do not upload the old database: it contains document text.

