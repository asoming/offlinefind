# Development

[简体中文](DEVELOPMENT.zh-CN.md)

## Architecture

The desktop is Python + pywebview using WebView2 on Windows and WKWebView on macOS, and GTK 3 / WebKitGTK on Linux. The UI is bundled vanilla HTML/CSS/JavaScript with no build step or CDN dependencies. This beta chooses a testable Python implementation over the PRD's tentative Rust option; that option was not a committed requirement.

| File | Responsibility |
| --- | --- |
| `src/shiwen/app.py` | Desktop lifecycle, narrow native RPC allowlist, optional authenticated loopback server |
| `library.py` | Scope policy, background scan, file watcher, parser orchestration and version guards |
| `store.py` | SQLite data, external-content FTS5 index, bookmarks and exact result verification |
| `text.py` | NFKC/case normalization, literal query parsing, encoded bigrams, highlight offsets |
| `extract.py` | Bounded PDF/Markdown/DOCX extraction in a spawned process |
| `ui/` | Bilingual glass UI, local state and safe text-node rendering |

The FTS index stores encoded character bigrams. Each input term becomes an AND of its bigrams; candidate documents are then checked against the actual normalized text. This supports Chinese two-character terms without trusting a default word tokenizer. The index contains distinct grams, so its BM25 score measures gram coverage and rarity rather than original word frequency. Ranking remains an area for evaluation.

Parsers run serially in independent spawned processes with a 60-second parent timeout. On POSIX an additional CPU limit is applied. There is no hard cross-platform memory cap yet. UI rendering never evaluates document HTML. The index is local plaintext, protected by account permissions, not application encryption.

Changes are detected by size, nanosecond mtime and platform metadata fingerprint (device/inode/ctime), plus file notifications and a 30-second reconciliation. This is not a full content hash and does not cover every metadata-preserving modification. Changed text is withdrawn before replacement; uninterrupted atomic old/new snapshots remain future work.

## Set up and test

```bash
python -m venv .venv
# Activate .venv using your platform's command.
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
pytest -q
python -m shiwen.app --self-test smoke.json
python -m build
```

Avoid inheriting unrelated `PYTHONPATH` or pytest plugins from other projects. For example, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` can isolate a local test run. CI runs clean environments on Linux, Windows and macOS.

Create synthetic QA documents and run the browser preview:

```bash
python scripts/demo_documents.py /tmp/shiwen-fixtures
shiwen --serve --folder /tmp/shiwen-fixtures --data-dir /tmp/shiwen-index
```

The preview server binds to `127.0.0.1`, validates Host/Origin, requires a per-process token and rejects oversized requests. It must not be exposed through tunnels or public hosting. Only the desktop bridge can invoke a native directory picker.

## Native packages

On each target platform, from a clean virtual environment:

```bash
python -m pip install -e '.[dev]'
python scripts/package.py
```

The script builds a PyInstaller directory bundle, runs its packaged `--self-test`, then archives it and writes a SHA-256 checksum. On macOS it uses `ditto` to preserve application-bundle links. Signing and notarization are not configured; do not label these binaries signed.

The `Tests` workflow covers three operating systems. The `Release` workflow runs tests, builds Windows x64, macOS arm64 and Linux x64 packages, checks the frozen executable, builds Python source/wheel distributions, and publishes a prerelease **only after all required jobs pass**. A manual workflow run builds artifacts without publishing. Version tags must match `pyproject.toml`, `__version__` and the bilingual release notes.

On Linux, `scripts/package.py` delegates to `scripts/package_linux.py`. Build on Ubuntu 22.04 with Python 3.10+ in a virtual environment; install system `python3-gi`, `python3-gi-cairo`, `gir1.2-gtk-3.0`, `gir1.2-webkit2-4.1`, `xdg-utils` and `desktop-file-utils`. It vendors the application and Python dependencies into a DEB and a tar.gz; the launcher uses isolated system Python (`-I`) and OS-maintained GTK/WebKit. It does not bundle an entire browser. Core and native bridge smoke tests run before archiving. CI also installs the actual DEB and runs its core/GUI checks on Ubuntu 22.04 and 24.04. Headless CI uses `xvfb-run`; desktop builds use the current display. No document databases are packaged.

Top-level runtime dependencies are pinned. Transitive/platform-specific dependencies are resolved on the build runner; this is not a fully hermetic build. Keep dependency updates explicit and re-run the platform matrix.


## Recovery and benchmark checks

`tests/test_recovery.py` covers individual retry persistence, bookmark preservation, inaccessible/out-of-scope targets, issue pagination, overlapping exclusions, and full-library retry races. Single-file retries reuse the persistent `pending` status; no database schema migration is required. Full-library requests carry an identity and are acknowledged only after a complete scan if no newer request has replaced them.

Run `python scripts/benchmark.py /tmp/shiwen-benchmark` in a new directory for the 10,000-document benchmark, or add `--documents 100 --rounds 3` for a quick check. See [performance methodology](PERFORMANCE.en.md). The benchmark generates synthetic files only, uses the production spawned parser for each file and verifies known search results. It is not run as a 10,000-file workload in every CI job.
