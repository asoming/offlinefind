# 拾文 · Shiwen

**Remember the words. Find the file.**

[简体中文](README.zh-CN.md) · [Releases](https://github.com/asoming/shiwen/releases) · [User guide](docs/USER_GUIDE.en.md) · [Development](docs/DEVELOPMENT.en.md)

Shiwen automatically discovers local files for offline desktop search. Open it and type: no folder selection is required. Find images, archives, code and folders by name; search PDF, Markdown and DOCX contents with highlighted excerpts. The interface retains its frosted-glass appearance.

**Status: v0.1.0-beta.5.** This is an early public preview, not a claim that every requirement in the PRD is complete. See [release notes and limitations](docs/RELEASE_NOTES.md).

## What works

- Automatically discover local disks, index file/folder names first, and extract document contents independently.
- Choose Names + contents, File names only, or Document contents only.
- Literal phrase queries, space-separated AND conditions, type/folder filters and bookmarks.
- Real excerpts with highlights; PDF page, Markdown line and DOCX paragraph references.
- Local SQLite FTS5 bigram index, followed by exact text verification to reject false positives.
- Read-only isolated parsers, periodic disk reconciliation, pause/resume, editable subfolder exclusions and clear-data controls.
- Paginated problem-file lists and individual retries that stay pending across pause/restart.
- Light/dark/system appearance, optional frosted glass, Chinese/English interface and keyboard navigation.
- Manual update checks, platform-matched downloads, progress/cancellation and SHA-256 verification in Settings.
- No account, telemetry, external fonts, remote document rendering or automatic updates.

## Download

Get the package for your platform from [GitHub Releases](https://github.com/asoming/shiwen/releases): Windows x64 ZIP, macOS Apple Silicon ZIP, or Linux x64 DEB / tar.gz. Extract the entire archive before launching **Shiwen**. Windows/macOS packages include Python; Linux reuses the system runtime.

- **Windows 11 x64:** uses Microsoft Edge WebView2. The runtime must already be installed; Shiwen does not silently download it. Most Windows 11 installations include it. Air-gapped machines need the runtime provisioned separately.
- **macOS 14+ Apple Silicon:** uses the system WebKit. The beta is not notarized and has no developer signing certificate. macOS may require approval through System Settings → Privacy & Security after the first launch attempt.
- These beta binaries are unsigned (macOS packaging may apply an ad-hoc signature). Verify the published SHA-256 checksum. Do not disable system-wide security settings.
- **Ubuntu 22.04 / 24.04 x64:** install the `.deb` through your software installer or `sudo apt install ./Shiwen-*-linux-amd64.deb`. Search **Shiwen** in the application menu. The portable tar.gz runs with `./Shiwen/shiwen`; see the [Linux guide](docs/USER_GUIDE.en.md#linux-installation). Both use system Python 3.10+, GTK 3 and WebKit; Python modules are included, so no pip setup is needed.

## First search

1. Open Shiwen; local file discovery starts automatically.
2. Type immediately. Names become searchable first, followed by document contents.
3. Search for `部署`, `budget approval`, or `"offline deployment"`.
4. Select a result to read its extracted text. Use **Open original** for the original layout.

`Ctrl+K` / `Cmd+K` focuses search inside the app. Names support single-character terms; content terms need at least two characters. Space-separated terms must all appear in the same document. Search is literal, not AI-powered or semantic.

## Privacy and limits

Files are never moved, renamed or modified. The local index contains extracted document text and **is not separately encrypted**. Protect it as you would the original documents, using OS account permissions and disk encryption. Use Index & exclusions to exclude folders, or clear local data and pause indexing.

Automatic indexing skips virtual filesystems, network mounts, cache/dependency directories, symlinks and its own index. Inaccessible directories are skipped without elevation. Windows discovers drive-letter fixed disks; Linux/macOS traverse local directory trees. Changes are reconciled at approximately 30-second intervals plus scan time; NTFS MFT / USN acceleration is not implemented.

Scanned pages need OCR, which is not included. Password-protected files, unsupported encodings, parser errors and size limits are shown explicitly. File names may remain searchable when their contents cannot be parsed. Default limits: 100 MiB per file, 1,000 PDF pages and 10 MiB of extracted text. DOCX previews contain ordinary paragraphs and table text, not original Word pagination.

The synthetic measurements below do not establish the PRD’s complete desktop latency and memory budgets. See the [roadmap](docs/ROADMAP.md).

## Run from source

Requires Python 3.10+ (Windows/macOS bundles use Python 3.12; Linux uses system Python).

```bash
git clone https://github.com/asoming/shiwen.git
cd shiwen
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
python -m pip install -e '.[dev]'
shiwen
```

Development-only browser mode (bound to loopback, authenticated per process):

```bash
shiwen --serve --port 8765 --folder /absolute/path/to/documents
```

`--folder` limits development tests to an explicit scope; normal launching needs no such argument. File opening uses the desktop app. Browser mode is a development convenience, not a hosted service. Indexing and searching work offline. Manual update checks/downloads connect to GitHub without sending local documents, paths or indexes; installing source dependencies requires a prepared package cache or internet access.

## Contributing and license

Read the [development guide](docs/DEVELOPMENT.en.md) and [contributing notes](CONTRIBUTING.md). Please use synthetic or explicitly shareable examples in bug reports; do not upload private documents or indexes.

MIT © 2026 asoming. See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md).

## Performance measurements

The [benchmark script](scripts/benchmark.py) builds a synthetic 10,000-document corpus and runs the production isolated parsers. See the [measurement report](docs/PERFORMANCE.en.md) for reproducible commands, results and limits. Full desktop memory, OS-cold queries and cross-platform performance targets remain unverified.
