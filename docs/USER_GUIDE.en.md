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

## Add your documents

Select **Add folder**. Shiwen reads PDF, `.md`, `.markdown` and `.docx` files inside that folder. Overlapping folders do not create duplicate results. Hidden folders, common dependency folders, symlinks and the application's own data directory are excluded. Whole drives and ancestors of Shiwen's data directory cannot be added.

Only add local folders that are actually stored on the device. Cloud placeholders are not downloaded. Network shares and removable-drive lifecycle management are not supported in this beta.

Indexing runs in the background. Select the status at the bottom of the sidebar to see processed counts, pause/resume or request a recheck. Newly saved files are coalesced for roughly one second before parsing. A periodic reconciliation supplements file notifications; updates can take about 30 seconds if notifications are lost.

## Search

| Input | Meaning |
| --- | --- |
| `部署` | Find this exact two-character substring in a name or the extracted text |
| `budget approval` | Both terms must appear somewhere in the same document |
| `"offline deployment"` | Find a continuous phrase after case and whitespace normalization |
| `C++` | Literal substring; no regular expression or special query language |

Each term must contain at least two normalized characters. Up to 12 terms and 256 input characters are accepted. English case and full-width character variants are normalized. Simplified/traditional conversion, OCR, typo correction and semantic search are not included.

Use the type buttons and sidebar folders together. **Bookmarks** narrows the same search to saved references. **Last modified** uses the file's modification time, not its indexing time. Clear the text to browse recently modified documents in the current scope.

Results are shown in batches of 50. **Load more** continues without implying a precise total before all candidates have been checked.

## Read and open

Click a result to see the extracted text. Use arrows in the preview to visit matching pages or blocks. The references are PDF physical pages, Markdown starting line numbers and DOCX paragraph numbers. The preview is not a PDF renderer or a faithful Word layout.

**Open original** uses the operating system's default app. Double-clicking a result or pressing Enter in the result list does the same. **Show in folder** reveals the original location. External opening does not promise a page or paragraph jump.

Files without extracted text show the reason: OCR may be required, the document is encrypted, encoding is unsupported, or a parser limit was reached. For this beta, recheck retries the whole selected library; per-file retry is planned.

## Manage data

**Manage folders → Exclude subfolder** accepts a relative path such as `archive/private`. Exclusions override overlapping inclusions. Exclusions cannot currently be removed individually; remove and re-add the scope to reset its rules.

Removing a scope drops its derived search data unless another remaining scope still includes the file. Clearing all local data removes the index, bookmarks, scopes and settings. Neither action changes the original files. SQLite free space is compacted, but no forensic secure-erasure guarantee is made for SSDs.

Default data directories are `%LOCALAPPDATA%\Shiwen` on Windows, `~/Library/Application Support/Shiwen` on macOS, and `$XDG_DATA_HOME/Shiwen` (normally `~/.local/share/Shiwen`) on Linux. Settings shows the actual path. `--data-dir` overrides it for development.

## Troubleshooting

- **No result:** check the selected folder/type, indexing progress and file status. Scanned PDFs need OCR outside Shiwen.
- **A changed file shows no text temporarily:** the stale content is withdrawn until its new version is ready. A failed update never silently serves old text as current.
- **Moved file lost its bookmark:** cross-path identity and bookmark transfer are not yet implemented. Re-bookmark its new location.
- **Windows window does not start:** verify that Edge WebView2 is installed; the app intentionally does not fall back to Internet Explorer.
- **macOS blocks launch:** use the OS's approval flow for a downloaded unsigned app; do not turn off global protections.
- **Damaged local database:** quit Shiwen and move its data directory aside, then restart and re-add scopes. Automatic repair is planned. Do not upload the old database: it contains document text.

