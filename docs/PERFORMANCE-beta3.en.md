# Performance measurements: 0.1.0b3

[简体中文](PERFORMANCE-beta3.zh-CN.md)

On September 17, 2026, a complete run indexed **10,000 synthetic documents** successfully on one Ubuntu computer. The run exposed the cost of carrying full document bodies through query sorting. Beta.3 now sorts IDs / paths first and reads bodies as needed, preserving scope checks, literal verification and pagination.

This is a reproducible engine baseline, **not complete desktop performance acceptance**. It does not measure GUI / WebKit, OS-cold caches, complex real documents or other operating systems.

## Environment and corpus

- Intel Core i9-14900HX, 32 logical CPUs visible to the OS, approximately 15.32 GiB RAM, local NVMe filesystem.
- Ubuntu 22.04.5 x64, Linux 6.8.0-138-generic, glibc 2.35, Python 3.10.12.
- 7,000 Markdown files, 2,000 DOCX extraction fixtures and 1,000 text PDFs; approximately 10 KiB of Chinese / English text each. Generated source text totals 102,950,000 bytes (98.18 MiB), not total file size or final extracted text size.
- Highly repetitive text with unique identifiers and known query results. PDFs are generated with ReportLab. DOCX fixtures are minimal ZIPs containing only `word/document.xml`, **not complete Office packages**; they do not represent real Word document complexity.
- Production isolated parsers: one spawned subprocess per document, processed serially. No replacement with an in-process test parser.
- Development tools and a browser were active in the background. Machine load and filesystem caching affect results.

## Indexing and memory

| Metric | This run |
| --- | ---: |
| Full indexing, excluding corpus generation | 708.65 seconds (about 11m 49s) |
| First 50 documents indexed, sampled | 4.10 seconds |
| Index database plus WAL | 244.45 MiB |
| Engine and parser process-tree peak RSS, sampled | 94.16 MiB |
| Process-tree RSS after queries, baseline run | 66.89 MiB |

These figures come from the full run before the query optimization. Parsing and index format did not change. RSS is sampled every 50 ms from Linux `/proc` and summed across the parent and child processes. It includes the benchmark script, libraries imported for fixture generation and the Python resource tracker. Shared pages may be counted more than once, and brief peaks may be missed. **It excludes the desktop window / WebKit and is not total application resident memory.**

## Search on the same index, before and after

Ten samples per query, five queries, 50 samples total. Each search retrieves the first page of up to 50 results and checks its expected result count. P95 uses nearest-rank, so with ten samples it is the maximum. OS file caches were not evicted; the two runs are not a strictly isolated A/B experiment.

| Query | Before: median / P95 | Beta.3: median / P95 |
| --- | ---: | ---: |
| `离线部署` | 418.49 / 443.95 ms | 170.57 / 176.37 ms |
| `"offline deployment"` | 501.92 / 508.83 ms | 266.25 / 280.96 ms |
| `预算 审批` | 415.48 / 418.43 ms | 166.34 / 168.53 ms |
| `SHIWENID009999` (unique identifier) | 32.80 / 33.19 ms | 31.39 / 31.70 ms |
| `不存在的基准短语` (absent phrase) | 0.22 / 0.45 ms | 0.21 / 0.31 ms |

The first `离线部署` query after reopening the SQLite connection took 420.51 ms before and 171.55 ms after. **This is not OS-cold search latency.** The second run reused the existing index and measured queries only; it did not reindex all 10,000 documents.

Raw data: [full baseline](benchmarks/beta3-linux-10000-baseline.json), [optimized queries](benchmarks/beta3-linux-10000-search.json). Both report `version: 0.1.0b3` because both runs occurred before this release; filenames identify the measurement stages.

## Reproduction

Install this repository's `.[dev]` dependencies in your development environment, then use a new directory that does not already exist:

```bash
python scripts/benchmark.py /tmp/shiwen-benchmark-10000
# Remeasure queries on the same corpus/index, saving a separate search-report.json:
python scripts/benchmark.py /tmp/shiwen-benchmark-10000 --queries-only
# Short smoke run, using another new directory:
python scripts/benchmark.py /tmp/shiwen-benchmark-pilot --documents 100
```

The script generates and reads synthetic files in the chosen directory; it does not read personal documents. Full runs write `report.json`; query-only runs write `search-report.json`. The released code measures the optimized query implementation by default. The committed baseline JSON preserves the earlier measurements and does not represent final-code query latency.

## Targets still unverified

The PRD specifies a 4-core / 8 GB reference environment with a different corpus mix and query workload. Remaining work includes representative real documents, a 40% PDF / 40% Markdown / 20% DOCX mix, at least 100 queries, full-GUI idle / peak memory, cold caches and Windows / macOS measurements. These results do not establish sub-300 ms searches for every 10,000-document collection or sub-100 MiB memory for the entire app.
