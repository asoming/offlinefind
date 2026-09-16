# 拾文 · Shiwen

**Remember the words. Find the file.**

[简体中文](README.zh-CN.md) · [Releases](https://github.com/asoming/shiwen/releases) · [User guide](docs/USER_GUIDE.en.md) · [Development](docs/DEVELOPMENT.en.md)

Shiwen is an offline desktop search app for PDF, Markdown and DOCX documents. Choose your folders, type a phrase, and read the matching passage before opening the original file. A frosted-glass interface keeps the navigation quiet and the document text readable.

**Status: v0.1.0-beta.1.** This is an early public preview, not a claim that every requirement in the PRD is complete. See [release notes and limitations](docs/RELEASE_NOTES.md).

## What works

- Search file names and document contents, including two-character Chinese terms and mixed Chinese/English text.
- Literal phrase queries, space-separated AND conditions, type/folder filters and bookmarks.
- Real excerpts with highlights; PDF page, Markdown line and DOCX paragraph references.
- Local SQLite FTS5 bigram index, followed by exact text verification to reject false positives.
- Read-only isolated parsers, file watcher plus reconciliation, pause/resume, subfolder exclusions and clear-data controls.
- Light/dark/system appearance, optional frosted glass, Chinese/English interface and keyboard navigation.
- No account, telemetry, external fonts, remote document rendering or automatic updates.

## Download

Get the Windows x64 ZIP or macOS Apple Silicon ZIP from [GitHub Releases](https://github.com/asoming/shiwen/releases). Extract the entire archive before launching **Shiwen**. Python is bundled; you do not need to install it.

- **Windows 11 x64:** uses Microsoft Edge WebView2. The runtime must already be installed; Shiwen does not silently download it. Most Windows 11 installations include it. Air-gapped machines need the runtime provisioned separately.
- **macOS 14+ Apple Silicon:** uses the system WebKit. The beta is not notarized and has no developer signing certificate. macOS may require approval through System Settings → Privacy & Security after the first launch attempt.
- These beta binaries are unsigned (macOS packaging may apply an ad-hoc signature). Verify the published SHA-256 checksum. Do not disable system-wide security settings.
- Linux source execution is supported for development with a compatible GTK/WebKit or Qt backend; no Linux binary is promised in this release.

## First search

1. Select **Add folder** and choose a local document folder.
2. Wait for the first documents to be indexed; you can search while indexing continues.
3. Search for `部署`, `budget approval`, or `"offline deployment"`.
4. Select a result to read its extracted text. Use **Open original** for the original layout.

`Ctrl+K` / `Cmd+K` focuses search inside the app. Every search term needs at least two characters. Space-separated terms must all appear in the same document. Search is literal, not AI-powered or semantic.

## Privacy and limits

Files are never moved, renamed or modified. The local index contains extracted document text and **is not separately encrypted**. Protect it as you would the original documents, using OS account permissions and disk encryption. You can remove scopes or clear all application data in Settings.

Scanned pages need OCR, which is not included. Password-protected files, unsupported encodings, parser errors and size limits are shown explicitly. File names may remain searchable when their contents cannot be parsed. Default limits: 100 MiB per file, 1,000 PDF pages and 10 MiB of extracted text. DOCX previews contain ordinary paragraphs and table text, not original Word pagination.

The PRD’s 10,000-document latency and memory budgets are targets, **not measured claims for this beta**. See the [roadmap](docs/ROADMAP.md).

## Run from source

Requires Python 3.10+ (3.12 is used for release builds).

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

Folder selection and native file opening belong to the desktop app. Browser mode is a development convenience, not a hosted service. Runtime operation is offline; installing source dependencies requires a prepared package cache or internet access.

## Contributing and license

Read the [development guide](docs/DEVELOPMENT.en.md) and [contributing notes](CONTRIBUTING.md). Please use synthetic or explicitly shareable examples in bug reports; do not upload private documents or indexes.

MIT © 2026 asoming. See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md).

