# Performance and acceptance: 0.1.0

[简体中文](PERFORMANCE.zh-CN.md) · [Historical beta.3 engine baseline](PERFORMANCE-beta3.en.md)

Measured September 17, 2026. **0.1.0 retains the glass desktop and publishes its measured limits. It does not meet the original sub-100 MiB full-desktop or universal sub-300 ms search targets.** Stable describes the supported release scope, not completion of every PRD objective.

## Local workload and method

Ubuntu 22.04 x64, Linux 6.8, Python 3.10, Intel Core i9-14900HX (32 logical CPUs), approximately 15.32 GiB RAM. Development tools were active. This is not the original 4-core / 8 GB reference machine. Caches were not evicted; reopening SQLite is not a cold-cache test.

The new fixture contains **10,000 documents: 4,000 three-page text PDFs, 4,000 Markdown files and 2,000 complete DOCX packages with paragraphs and tables**. Total file size is 119,439,763 bytes (113.91 MiB). Contents are generated Chinese/English text with known matches, not a representative sample of private or complex documents. Production automatic discovery and isolated spawned parsers are used. All query results are checked against expected counts.

The full baseline was recorded during the release candidate work, before the final query optimizations; its raw version remains `0.1.0b9`. The final query and desktop reports use `0.1.0` production code from `9c3bb7a`, with measurement corrections in `e848222`. We preserve both stages rather than relabeling earlier results.

| Indexing metric | Measurement |
| --- | ---: |
| Discover 10,000 names in the fixture | 1.01 s |
| Finish document extraction/indexing | 980.11 s (16m 20s) |
| Names searched during parsing: median / P95, 1,565 samples | 124.91 / 204.88 ms |
| Document database + WAL, baseline | 181.64 MiB |

The baseline controller/parser peak was 395.85 MiB, including fixture-generator imports. It is a benchmark-process measurement, **not full application memory**.

## Document searches: final implementation

100 queries, 25 per group, first page of up to 50 results. P95 uses nearest rank. The same existing 10,000-document index was reused without reindexing or cache eviction. Many similar numeric identifiers deliberately generate numerous bigram candidates, making the unique-record group costly.

| Query group | Median | P95 |
| --- | ---: | ---: |
| Topic | 265.11 ms | 301.13 ms |
| Unique record | 747.24 ms | 761.90 ms |
| Phrase / AND conditions | 422.69 ms | 545.02 ms |
| Absent term | 0.39 ms | 0.46 ms |

Candidate literal checks now precede filesystem permission checks, and large block/token fields are loaded only for accepted results. Every returned result still passes scope and accessibility checks. These changes reduce rejected-candidate costs; they do not guarantee instant searches.

## Real local names and one million synthetic names

A fresh, isolated names-only index discovered **739,334 files/folders in 305.15 seconds** on the local machine. No document bodies were parsed for this run. Only aggregate counts and timings are published; private paths and indexes are excluded. After adding query indexes, empty-search median was 18.67 ms (previously 464.16), single-character 69.23 ms (previously 559.09), common filename 38.31 ms and extension 40.82 ms. Ten samples per query; no controlled cache reset. Database + WAL: 510.59 MiB.

A separate **1,000,000-entry synthetic metadata index** took 73.25 s to populate and occupied 533.74 MiB after optimization. This is an SQL workload with virtual paths, **excluding filesystem traversal and per-result permission checks**. Five samples per query:

| Query | Median | P95 |
| --- | ---: | ---: |
| Empty | 0.97 ms | 1.45 ms |
| Broad `File` match | 2,689.38 ms | 2,700.58 ms |
| Unique `0999999` | 149.35 ms | 154.41 ms |
| Single `f` | 0.99 ms | 1.21 ms |
| Absent | 0.10 ms | 0.27 ms |

The broad query still takes about 2.7 seconds. This is not an Everything/NTFS MFT performance comparison. Automatic reconciliation uses ordinary traversal, approximately every 30 seconds plus scan duration.

## Actual desktop

The native desktop harness exercises the production app, automatic discovery, Chinese content search, highlighted previews, bookmarks, PDF/Markdown/DOCX filters, settings, both languages/themes, custom minimize/maximize/restore/close, dragging and resizing. It uses an isolated synthetic index and does not alter a user's library.

On the local 10,000-document index, the first results appeared in **0.91 s**, and closing exited in **0.28 s** after the request. Full app/descendant RSS before interaction was **527.72 MiB**; after interaction, idle was **573.79 MiB**, with an overall sampled peak of **600.02 MiB**. The ten-second post-interaction idle sample used **25.2% of one CPU core** after subtracting the sampler thread. This environment has no accessible GPU device; software-rendering fallback was active. Idle CPU is not negligible and remains an optimization target.

RSS sums include Python, parser children when present and WebView processes. Shared pages may be counted twice; short peaks may be missed. The ten-second sample is not a battery-life or long-duration idle test. The phase called `indexing` in an existing-index desktop run includes startup reconciliation, not a fresh full-corpus rebuild. Linux disables WebKit compositing only when no accessible GPU device is found, while respecting an explicit user environment override.

Cross-platform CI measurements are recorded below separately; runner hardware, corpus sizes and rendering differ, so these are not controlled OS comparisons.

All three jobs passed in [run 35207745672](https://github.com/asoming/offlinefind/actions/runs/35207745672), revision `e848222`. Each desktop reopens a 1,000-document index; the separate 100,000-name benchmark is not loaded into its desktop. Windows runs on Server 2025 CI, not a physical Windows 11 workstation. macOS sums new WebKit XPC processes in the otherwise isolated runner; pre-existing shared services are excluded. First-results times include native WebView initialization, which was particularly slow on Linux CI. Closing time starts at the close request, not process startup.

| CI desktop | Idle RSS (MiB) | Peak RSS (MiB) | Idle CPU, one core | First results / close (s) |
| --- | ---: | ---: | ---: | ---: |
| Windows Server 2025 / WebView2 | 464.92 | 500.43 | 2.21% | 5.15 / 0.45 |
| macOS 14 arm64 / WebKit XPC | 235.95 | 235.98 | 3.42% | 6.29 / 0.27 |
| Ubuntu 22.04 / Xvfb + WebKit | 431.29 | 440.38 | 5.60% | 25.65 / 0.21 |

Raw desktop reports / 桌面原始报告：[windows-latest](benchmarks/0.1.0-ci-windows-latest-desktop-report.json) · [macos-14](benchmarks/0.1.0-ci-macos-14-desktop-report.json) · [ubuntu-22.04](benchmarks/0.1.0-ci-ubuntu-22.04-desktop-report.json).


## Evidence and reproduction

Raw aggregates: [full baseline](benchmarks/0.1.0-linux-10000-baseline.json), [final 100 queries](benchmarks/0.1.0-linux-10000-search.json), [million names](benchmarks/0.1.0-linux-million-names.json), [local desktop](benchmarks/0.1.0-linux-desktop.json), [real names before](benchmarks/0.1.0-local-names-before.json), [real names after](benchmarks/0.1.0-local-names-after.json).

```bash
python -m pip install -e '.[dev]'
# Use a NEW directory; generation/indexing may take many minutes.
python scripts/acceptance_benchmark.py /tmp/shiwen-acceptance --documents 10000 --metadata 1000000
# Requires a graphical desktop and the platform's WebView runtime.
python scripts/desktop_acceptance.py /tmp/shiwen-acceptance --existing-index
```

The benchmark writes `report.json`; desktop checks write `desktop-report.json` and, on Linux, light/dark screenshots. Current code reruns final queries as part of the full benchmark. The separate final-query JSON files above retain measurements on the already-built candidate index. The `Desktop acceptance` workflow uses 1,000 documents and 100,000 synthetic names on each OS.

## Deferred acceptance and limits

Strict OS-cold caches, a 4-core / 8 GB reference machine, representative complex documents, long-duration power use, and comprehensive manual native-dialog/permission/recovery checks on physical Windows/macOS/Linux machines remain unverified. Automated runner checks are not a substitute for those manual checks. Installers remain unsigned by a trusted publisher (macOS may have an ad-hoc signature). OCR, NTFS MFT/USN, automatic corruption repair and bookmarks surviving cross-path renames are not implemented. See the [roadmap](ROADMAP.md).
