# Shiwen v0.1.0-beta.2 / 拾文 Linux 支持测试版

## 简体中文

新增 Linux x64 DEB 与免安装 tar.gz，支持 Ubuntu 22.04 / 24.04 桌面。修复 GTK 自检退出顺序，补齐中英文安装说明和应用菜单入口。

离线全文检索包括：PDF / Markdown / DOCX 解析、中文双字词与英文搜索、原文高亮预览、目录范围与排除、收藏、后台更新、暂停恢复，以及中英文玻璃界面。

Windows/macOS 下载 ZIP 并完整解压，包内包含 Python；Windows x64 需要预装 WebView2，macOS arm64 使用系统 WebKit。Linux 可用系统软件安装器打开 DEB，或执行 `sudo apt install ./Shiwen-*-linux-amd64.deb`；免安装 tar.gz 解压后执行 `./Shiwen/shiwen`。Linux 包复用系统 Python 3.10+、GTK 3 和 WebKit，Python 模块已随包提供。系统依赖准备好后即可离线使用。SHA-256 文件用于核对下载完整性。此版本没有可信发布者签名或 macOS 公证。

已提供自动化核心测试、跨平台 CI、打包后自检。**不代表已通过所有真实桌面人工验收或 PRD 的万文档性能目标。**

已知边界：不含 OCR / AI；仅提取文本预览，不还原 PDF / Word 排版；不保证外部应用页码定位；不迁移重命名后的收藏；失败重试以全库复查为单位；排除规则暂不能单独删除；未实现数据库自动修复、全局快捷键、硬内存限额、电池感知暂停和应用级索引加密。网络共享、移动磁盘、Intel Mac 暂无正式支持保证。

文件内容不会上传，也不会被应用移动、改写或删除。索引含原文，请像保护原文件一样保护它。

## English

Adds Linux x64 DEB and portable tar.gz packages for Ubuntu 22.04 / 24.04 desktops, fixes GTK smoke-test shutdown ordering, and includes bilingual install instructions and an application-menu launcher.

Offline full-text search includes: PDF / Markdown / DOCX extraction, Chinese two-character and English queries, highlighted original excerpts, folder scopes and exclusions, bookmarks, background updates, pause/resume, and a bilingual frosted-glass interface.

Fully extract the Windows/macOS ZIP; Python is included. Windows x64 needs WebView2 installed; macOS arm64 uses system WebKit. On Linux, open the DEB in your software installer or run `sudo apt install ./Shiwen-*-linux-amd64.deb`; alternatively extract the tar.gz and run `./Shiwen/shiwen`. Linux reuses system Python 3.10+, GTK 3 and WebKit, with the application Python modules included. Provision system dependencies before offline use. Verify downloads with the accompanying SHA-256 files. This beta has no trusted publisher signature or macOS notarization.

Automated core tests, cross-platform CI and packaged self-tests are included. **These do not establish complete manual desktop acceptance or the PRD's 10,000-document performance targets.**

Known limits: no OCR/AI; extracted-text previews instead of original PDF/Word layout; no guaranteed external page navigation; no bookmark migration on rename; retries recheck the whole library; individual exclusion removal is not implemented; automatic database repair, a global shortcut, hard memory limits, battery-aware pausing and application-level index encryption remain future work. Network shares, removable drives and Intel Macs have no formal support guarantee yet.

Document contents are not uploaded, and originals are never moved, modified or deleted by the app. The index contains original text; protect it accordingly.

