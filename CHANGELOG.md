# Changelog / 更新记录

## 0.1.0-beta.7 — 2026-09-17

- Fix Linux exit hanging when a WebView callback is outstanding as the window closes.
- Cancel in-flight document parsing on close and keep unfinished documents pending for restart.
- Drain active bridge requests before closing the index database; add shutdown regression tests and a packaged GTK close-race smoke test.
- 修复 Linux 关闭窗口时等待界面回调、导致进程不退出的竞态。
- 关闭时取消正在执行的文档解析，未完成文档保留待处理状态，重启后继续。
- 等待已有桥接请求结束后再关闭索引数据库；新增退出回归测试与打包后的 GTK 关闭竞态自检。

## 0.1.0-beta.5 — 2026-09-17

- Add manual update checks and release notes in Settings, with platform-matched package downloads.
- Show progress, allow cancellation, verify size/SHA-256 and reveal completed downloads.
- Publish a lightweight release feed to avoid anonymous API rate limits; bundle HTTPS trust roots.
- 设置新增手动检查更新、版本说明与适合当前系统的安装包下载。
- 支持下载进度、取消、大小 / SHA-256 校验和打开下载目录。
- 发布轻量版本清单，避免依赖匿名 API 配额；随包提供 HTTPS 信任证书。

## 0.1.0-beta.4 — 2026-09-17

- Open and search: automatically discover local disks with no folder selection.
- Index all regular file/folder names in batches; extract PDF/Markdown/DOCX contents independently.
- Add name/content modes and single-character filename queries. Preserve existing exclusions on upgrade.
- 开机式使用流程：打开即自动发现本机文件，无需选择文档文件夹。
- 分批收录各类文件和文件夹名称，正文独立后台解析。
- 新增名称 / 正文筛选、单字符名称查询，升级保留已有排除规则。

## 0.1.0-beta.3 — 2026-09-17

- Added paginated problem-file details and per-document retries, preserving bookmarks and pending work across pause/restart.
- Added individual exclusion removal; other overlapping exclusions remain effective.
- Fixed full-library retry requests lost while paused or during another scan.
- Added a reproducible mixed-format 10,000-document benchmark and bilingual performance documentation.
- Reduced query-sort overhead by loading document bodies after candidate sorting; exact matching and pagination remain intact.
- 新增问题文档详情、分页与单文件重试；保留收藏，暂停与重启后继续待处理工作。
- 支持逐条撤销目录排除，继续遵守其他范围的排除规则。
- 修复暂停和扫描期间提交的全库重试请求丢失的问题。
- 新增混合格式万文档基准脚本与中英文性能说明。
- 搜索先排序候选文档，再按需读取正文，减少排序开销并保留精确匹配和分页行为。

## 0.1.0-beta.2 — 2026-09-16

- Added Linux x64 DEB and portable tar.gz packages using system Python / GTK / WebKit.
- Added installed-package core and native GUI checks on Ubuntu 22.04 and 24.04.
- Fixed GUI smoke-test shutdown ordering to avoid an unfinished GTK bridge callback.
- Added bilingual Linux install/build instructions and an application-menu launcher.
- 新增 Linux x64 DEB 与免安装压缩包，复用系统 Python / GTK / WebKit。
- 新增 Ubuntu 22.04 / 24.04 安装包核心与原生 GUI 检查。
- 修复 GTK 桥接回调尚未结束时关闭自检窗口导致进程挂起的问题。
- 补充中英文 Linux 安装与打包说明、应用菜单入口。

## 0.1.0-beta.1 — 2026-09-16

- Added offline PDF, Markdown and DOCX search with Chinese bigram indexing and exact verification.
- Added scopes, exclusions, watcher reconciliation, isolated parsing, bookmarks and safe text previews.
- Added bilingual frosted-glass UI, themes, resource controls, status feedback and local-data clearing.
- Added English/Chinese documentation, core tests, platform CI and gated binary prereleases.
- 新增离线三格式全文检索、中文二元索引与原文核对。
- 新增目录排除、更新核对、独立解析、收藏和安全文本预览。
- 新增中英文玻璃界面、主题、资源设置、状态反馈与本地数据清除。
- 新增双语文档、测试、跨平台 CI 和通过检查后发布的二进制测试版。
