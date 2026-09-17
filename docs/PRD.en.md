# Shiwen · Product requirements

[简体中文](PRD.zh-CN.md)

Version v0.2, September 17, 2026. This revision supersedes the earlier manual document-folder selection workflow.

## 1. Goal

Deliver an Everything-like workflow: **open the app → discover local files automatically → type a query → open a result**. Users do not select folders or reorganize files into document-only directories. Add offline PDF, Markdown and DOCX content search and contextual previews to filename search.

Everything-like describes the interaction and file-search capability. It does not claim NTFS MFT / USN implementation or equivalent speed, and does not assume competitors lack content search.

## 2. Default behavior

- Discover local disks on normal launch; existing indexes remain immediately searchable.
- Index regular files of all types and folders by name, without a document-format restriction.
- Extract PDF, Markdown and DOCX text in an independent background worker; slow parsers must not block name discovery.
- Keep search, previews and indexes offline, without accounts, telemetry or document uploads.
- Never move, edit, rename or delete original files.

## 3. Scope

Windows discovers fixed disks with drive letters. Linux/macOS traverse local directory trees, prioritizing the user's home directory. Respect the current account and macOS privacy permissions without elevation.

Skip virtual filesystems, network mounts, symlinks, common cache/dependency/trash directories and the index itself. Ordinary hidden files remain searchable. Do not download cloud placeholders. Optional **Index & exclusions** controls exclude subfolders; no initial inclusion setup is required.

Preserve existing exclusions and bookmarks on upgrade. Overlapping scopes must not duplicate results. Clearing data pauses automatic indexing; resuming rebuilds from discovered disks without modifying originals.

## 4. Search and interaction

- Offer Names + contents, File names only, and Document contents only.
- Names accept single-character terms; contents require two characters per term. Single-character conditions match names only.
- Support Chinese substrings, English case and full-width normalization, quoted phrases and space-separated AND conditions.
- Combine file type (including folders), disk and bookmark filters; sort by relevance or modification time.
- Show names, types, paths and actual matching excerpts. Preserve name search and explain failures when text extraction fails.
- Select to preview extracted text; double-click, Enter or Open original launches the system app. Folder results open as folders.
- Retain Chinese/English, light/dark/system themes, optional glass effects and keyboard navigation.
- Neither the home screen nor automatic-mode management requires selecting a folder.

## 5. Index lifecycle

Commit discovered names to SQLite in batches without loading a full-disk inventory into memory. Parse contents serially in an independent worker, using an isolated process and 60-second timeout per document. Persist pending work across pause/restart.

Reconcile new, changed and disappeared files periodically. Interrupted or paused traversals must not mark unvisited records as deleted. Withdraw stale extracted text before replacing it. Individual retries preserve bookmarks; exclusions immediately affect queries.

Beta.4 uses ordinary traversal and approximately 30-second reconciliation intervals plus scan duration, without recursive whole-disk watchers. MFT / USN, change journals and larger-library performance improvements remain future work.

## 6. Document and privacy boundaries

Extract PDF, UTF-8 Markdown and DOCX paragraphs / ordinary tables. Default parser limits: 100 MiB per file, 1,000 PDF pages and 10 MiB extracted text. OCR, AI, original-layout rendering, automatic database repair and bookmark migration on rename are excluded.

Indexes contain paths and extracted text, without application-level encryption. Protect them using account permissions and disk encryption. Issue reports should contain synthetic fixtures, not private documents or databases.

## 7. Acceptance

1. A fresh installation discovers files and displays progress without a folder picker.
2. Images, archives, code, documents and subfolders in the same mixed directory are searchable by name; PDF / Markdown / DOCX also support contents.
3. Pause, restart, deletion/update and exclusion/restoration work without modifying originals.
4. Names become available before extraction completes; metadata-only entries are not parser failures.
5. Windows, macOS and Linux builds and native bridge checks pass; public releases include checksums and bilingual documentation.
6. Verify legacy-index migration and exclusion preservation, and document hidden-file / inaccessible-location behavior.

## 8. Performance acceptance remains open

Full-disk first-index time, million-entry memory/latency, timely updates and full-GUI memory need separate measurements. The earlier document benchmark's 4-core / 8 GB environment, 40% PDF / 40% Markdown / 20% DOCX mix, at least 100 queries and cross-platform cold/warm tests remain incomplete.

The [beta.3 synthetic baseline](PERFORMANCE.en.md) measures a selected document corpus, not beta.4 full-disk performance.
