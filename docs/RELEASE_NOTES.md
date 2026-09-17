# Shiwen / 拾文 0.1.0

## 中文

首个正式版：打开即可发现本机文件，无需选择文件夹；文件和文件夹按名称搜索，PDF、Markdown、DOCX 支持离线正文检索、命中预览与收藏。文件和索引留在本机，无账号、无遥测、无文档上传。

- 隐藏系统顶部标题栏，最小化、最大化 / 还原、关闭按钮融入玻璃界面；支持标题区域拖动、双击和边缘缩放。
- 保留 Linux 关闭竞态修复、同索引单实例和旧启动路径升级兼容；关闭取消后台任务，未完成解析可重启继续。
- 优化大文件库的最近文件查询和候选文字核对，保留逐项权限检查；无可访问 GPU 的 Linux 环境启用软件渲染回退。
- 设置提供手动检查更新、下载安装包、进度、取消和 SHA-256 校验；正式版忽略后续预发行版。不自动安装或后台联网。
- 60 项自动测试；三平台原生桌面验收覆盖搜索、预览、收藏、筛选、语言、主题与窗口操作。Release 打包另有原生桥接、安装与关闭自检。

### 性能与明确限制

保留当前界面并公开实测后发布，**未达到原始完整桌面低于 100 MiB、所有查询低于 300 ms 的目标**。本机万份合成文档索引约 16 分 20 秒；完整桌面空闲 RSS 约 **574 MiB**，十秒空闲样本约单核 **25.2% CPU**。100 条查询中，主题词中位数 265 ms，唯一记录 747 ms，短语 / AND 423 ms；百万合成名称的大量匹配约 2.7 秒。真实本机名称发现约 73.9 万项 / 305 秒。它们来自不同测试，不能合并成“百万文件瞬搜”承诺。

测量环境、三平台结果、原始汇总及复现方法见[性能报告](https://github.com/asoming/shiwen/blob/main/docs/PERFORMANCE.zh-CN.md)。严格冷缓存、4 核 / 8 GB 参考机、复杂真实语料、长期功耗与实体机全面系统对话框人工验收仍待补充。未实现 OCR、NTFS MFT / USN、自动损坏修复或跨路径重命名收藏迁移。索引未单独加密。

### 下载与升级

- Windows 11 x64：ZIP，完整解压，需要已安装 Edge WebView2。
- macOS 14+ Apple Silicon：ZIP，完整解压；尚无可信开发者签名 / 公证。
- Ubuntu 22.04 / 24.04 x64：DEB 或 tar.gz，使用系统 Python 3.10+、GTK 3、WebKit；应用依赖已随包提供。
- Python：wheel 与源码包。

二进制无可信发布者签名（macOS 可能有临时签名），请核对 SHA-256。Linux tar.gz 解压后运行 `Shiwen/install-user`，DEB 通过包管理器升级。**先退出旧窗口，升级后从应用菜单重开**。升级保留原有索引和文档；安装器不会结束正在运行的旧进程。详见[使用说明](https://github.com/asoming/shiwen/blob/main/docs/USER_GUIDE.zh-CN.md)。

## English

First stable release: automatic local discovery without folder selection; file/folder name search plus offline PDF, Markdown and DOCX contents, highlights and bookmarks. Files and indexes stay local, without accounts, telemetry or document uploads.

- Frameless glass desktop with integrated minimize, maximize/restore and close, draggable/double-clickable headings and edge resizing.
- Linux shutdown-race fix, one instance per index and compatible older launcher paths. Closing cancels background work; unfinished parsing resumes on restart.
- Faster recent-file queries and candidate verification for large inventories, preserving per-result permission checks. Linux software-rendering fallback when no accessible GPU is present.
- Manual update checks, package downloads, progress, cancellation and SHA-256 validation. Stable installations ignore prereleases. No automatic installation or background online checks.
- 60 automated tests; native desktop acceptance on three platforms covers search, previews, bookmarks, filters, languages, themes and window operations. Release packaging adds native bridge, installation and shutdown smoke checks.

### Performance and limits

The current interface is retained with published measurements. **The original full-desktop sub-100 MiB and universal sub-300 ms targets are not met.** The local synthetic 10,000-document index took about 16m 20s; full desktop idle RSS was **574 MiB**, with **25.2% of one CPU core** in a ten-second idle sample. Across 100 queries, median topic search was 265 ms, unique-record search 747 ms and phrase/AND search 423 ms. A broad match on one million synthetic names took 2.7s. Real local name discovery found approximately 739,000 entries in 305s. These are separate workloads, not a promise of instant million-file searches.

See the [methodology, platform results, raw aggregates and reproduction commands](https://github.com/asoming/shiwen/blob/main/docs/PERFORMANCE.en.md). Strict cold caches, the 4-core / 8 GB reference machine, complex representative documents, long-term power use and comprehensive physical-machine native-dialog acceptance remain unverified. OCR, NTFS MFT/USN, automatic corruption repair and bookmarks surviving cross-path renames are not implemented. Indexes are not separately encrypted.

### Downloads and upgrade

Windows 11 x64 ZIP requires an installed Edge WebView2 runtime. macOS 14+ Apple Silicon ZIP is not developer-signed/notarized. Ubuntu 22.04 / 24.04 x64 DEB and tar.gz use system Python 3.10+, GTK 3 and WebKit, with application dependencies included. Python wheel and source distributions are also provided.

Binaries lack a trusted publisher signature (macOS may use an ad-hoc signature); verify SHA-256. Extract archives completely. On Linux, run `Shiwen/install-user` from the tar.gz, or upgrade the DEB through the package manager. **Quit the old window before upgrading, then reopen from the application menu.** Existing indexes/documents are preserved; the installer does not terminate running processes. See the [user guide](https://github.com/asoming/shiwen/blob/main/docs/USER_GUIDE.en.md).
