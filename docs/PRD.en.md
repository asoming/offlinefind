# Shiwen product requirements — English implementation brief

This is the English companion to the [full Chinese PRD v0.1](PRD.zh-CN.md), dated 2026-09-16. It summarizes the intended product; it is not a statement that the current beta implements every requirement. See [release notes](RELEASE_NOTES.md) for actual scope.

## Product and audience

An offline desktop utility for people who remember a passage but not a file name: office workers, researchers, students and personal knowledge collectors. The core task is to choose folders, index locally, search a phrase, verify its original context and open the source file.

System search and Everything already have some content-search capabilities. Shiwen aims to differentiate through approachable configuration, dependable Chinese search, clear passage previews and understandable indexing states; superiority has not been established by comparative testing.

## Target platforms

Windows 11 x64, macOS 14+ Apple Silicon, and Ubuntu 22.04 / 24.04 x64 desktops. Linux was explicitly added by the user on 2026-09-16 for use on their Ubuntu computer; provide DEB and portable archive packages. Other distributions, Linux ARM64 and Intel Macs remain unvalidated.

## P0 product scope

- User-selected local folders, exclusions and overlapping-root deduplication; no default whole-drive scan.
- Extractable-text PDF, UTF-8 Markdown and ordinary DOCX paragraphs/tables. Scanned pages, encryption and parser limits must be visible.
- Literal Chinese/English search, two-character Chinese terms, phrase queries and AND conditions; type/folder filters and relevant/recent sorting.
- Genuine excerpts with highlights; page/line/paragraph positions, previous/next matches, opening and revealing originals.
- Persistent bookmarks, incremental updates, pause/resume, reconciliation after sleep or missed notifications, error recovery and safe cleanup.
- Three-pane frosted-glass desktop UI; light/dark/system appearance, keyboard focus and reduced motion. Reading surfaces remain opaque.
- No account or telemetry. No document, path, search text or crash-data uploads. A local index may contain sensitive plaintext and must be managed accordingly.

## Deferred scope

Offline OCR, global hotkey, additional formats and date filters follow the core loop. AI question-answering, semantic search, automatic organization, document editing and cloud synchronization are outside the initial release.

## Desired reliability

File changes should replace versions coherently. Confirmed deletions and revoked permissions must withdraw searchable content; temporarily inaccessible folders must not masquerade as deleted files. Removing a scope or clearing application data must never change originals. Parser failures must not stop other files. Tests should cover Chinese input composition, stale asynchronous results, special characters, overlapping scopes, large/encrypted/corrupt documents, script-bearing Markdown and abnormal shutdowns.

## Provisional performance goals

On a documented 4-core / 8 GB / SSD reference machine, with 10,000 files and around 100 MiB of extracted text: hot-search P95 ≤ 300 ms, cold-search P95 ≤ 1 s, first searchable batch ≤ 30 s, full indexing ≤ 15 min, idle process-tree resident memory ≤ 250 MiB, indexing peak ≤ 600 MiB, and derived data ≤ 500 MiB. These are targets, not beta measurements. Exact-phrase fixtures should have full recall; a labeled relevance set should achieve at least 90% Top-5 success.

## Delivery gates

1. Validate parsers, Chinese indexing and resource assumptions.
2. Deliver the complete local search/preview/open loop.
3. Add recovery, scope management, usability and accessibility.
4. Verify offline installation, target-platform packages, performance and user task completion.

The current Python/WebView beta implements a subset. beta.3 adds per-file recovery and removable exclusions. Atomic rebuilds, stable rename identity, resource hard limits and comprehensive performance acceptance remain explicitly tracked in the [roadmap](ROADMAP.md).
