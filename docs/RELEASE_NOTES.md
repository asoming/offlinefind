# Shiwen v0.1.0-beta.3 / 拾文索引恢复与性能基准

## 简体中文

新增问题文档列表、单文件重试和单条排除规则撤销。修复暂停或扫描期间全库重试请求丢失的问题。提供使用真实独立解析进程的合成万文档基准脚本与性能报告。继续提供 Linux x64 DEB / tar.gz、Windows x64 和 macOS arm64 包。

减少查询排序阶段的正文搬运开销；本机合成万文档测试中，三类常见查询 P95 从 418–509 ms 降至 169–281 ms。详见[实测方法、原始数据与限制](https://github.com/asoming/shiwen/blob/v0.1.0-beta.3/docs/PERFORMANCE.zh-CN.md)。

离线全文检索包括：PDF / Markdown / DOCX 解析、中文双字词与英文搜索、原文高亮预览、目录范围与排除、收藏、后台更新、暂停恢复，以及中英文玻璃界面。

Windows/macOS 下载 ZIP 并完整解压，包内包含 Python；Windows x64 需要预装 WebView2，macOS arm64 使用系统 WebKit。Linux 可用系统软件安装器打开 DEB，或执行 `sudo apt install ./Shiwen-*-linux-amd64.deb`；免安装 tar.gz 解压后执行 `./Shiwen/shiwen`。Linux 包复用系统 Python 3.10+、GTK 3 和 WebKit，Python 模块已随包提供。系统依赖准备好后即可离线使用。SHA-256 文件用于核对下载完整性。此版本没有可信发布者签名或 macOS 公证。

已提供自动化核心测试、跨平台 CI、打包后自检。**不代表已通过所有真实桌面人工验收或 PRD 的万文档性能目标。**

已知边界：不含 OCR / AI；仅提取文本预览，不还原 PDF / Word 排版；不保证外部应用页码定位；不迁移重命名后的收藏；未实现数据库自动修复、全局快捷键、硬内存限额、电池感知暂停和应用级索引加密。网络共享、移动磁盘、Intel Mac 暂无正式支持保证。

文件内容不会上传，也不会被应用移动、改写或删除。索引含原文，请像保护原文件一样保护它。

## English

Adds a paginated problem-file list, individual retries, and removal of individual exclusion rules. Fixes lost full-library retry requests while paused or during a scan. Includes a reproducible synthetic 10,000-document benchmark using production isolated parsers and a measurement report. Linux x64 DEB / tar.gz, Windows x64 and macOS arm64 packages remain available.

Reduces document-body copying during query sorting. On this machine's synthetic 10,000-document corpus, P95 for three common queries decreased from 418–509 ms to 169–281 ms. See the [methodology, raw data and limitations](https://github.com/asoming/shiwen/blob/v0.1.0-beta.3/docs/PERFORMANCE.en.md).

Offline full-text search includes: PDF / Markdown / DOCX extraction, Chinese two-character and English queries, highlighted original excerpts, folder scopes and exclusions, bookmarks, background updates, pause/resume, and a bilingual frosted-glass interface.

Fully extract the Windows/macOS ZIP; Python is included. Windows x64 needs WebView2 installed; macOS arm64 uses system WebKit. On Linux, open the DEB in your software installer or run `sudo apt install ./Shiwen-*-linux-amd64.deb`; alternatively extract the tar.gz and run `./Shiwen/shiwen`. Linux reuses system Python 3.10+, GTK 3 and WebKit, with the application Python modules included. Provision system dependencies before offline use. Verify downloads with the accompanying SHA-256 files. This beta has no trusted publisher signature or macOS notarization.

Automated core tests, cross-platform CI and packaged self-tests are included. **These do not establish complete manual desktop acceptance or the PRD's 10,000-document performance targets.**

Known limits: no OCR/AI; extracted-text previews instead of original PDF/Word layout; no guaranteed external page navigation; no bookmark migration on rename; automatic database repair, a global shortcut, hard memory limits, battery-aware pausing and application-level index encryption remain future work. Network shares, removable drives and Intel Macs have no formal support guarantee yet.

Document contents are not uploaded, and originals are never moved, modified or deleted by the app. The index contains original text; protect it accordingly.
