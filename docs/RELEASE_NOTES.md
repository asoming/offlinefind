# Shiwen v0.1.0-beta.5 / 拾文 · 检查更新与下载

## 简体中文

设置新增“软件更新”：手动检查新版本、阅读版本说明，下载当前系统的安装包。Linux 可选 DEB 或免安装 tar.gz；Windows x64 和 macOS Apple Silicon 自动匹配 ZIP。

下载支持进度、取消、大小与 SHA-256 校验。完成后可打开下载目录；失败或取消会删除不完整安装包，不覆盖已有下载。下载到系统下载目录的独立子目录；退出应用后自行安装或解压替换，保留已有索引与设置。

只在手动更新时连接 GitHub，不上传文档、路径或索引。启动、索引、搜索不自动联网检查。使用随 Release 发布的轻量清单，避免依赖匿名 API 的配额，并为打包程序提供 HTTPS 信任证书。没有自动安装、自动重启或静默升级。

保留 beta.4 的自动磁盘发现、各类文件名检索与 PDF / Markdown / DOCX 正文搜索，无需选择文档文件夹。磁盘变化仍通过周期遍历核对，尚无 MFT / USN 加速或 OCR。

提供 Linux x64 DEB / tar.gz、Windows x64 ZIP、macOS arm64 ZIP、源码和校验和。Linux 支持 Ubuntu 22.04 / 24.04，需系统 Python 3.10+、GTK 3 / WebKit；Windows 需 WebView2。测试包没有可信发布者签名或 macOS 公证。其他架构暂无匹配安装包。

## English

Settings now includes Software updates: manually check releases, read release notes and download a package for this system. Linux offers DEB and portable tar.gz; Windows x64 and macOS Apple Silicon receive the matching ZIP.

Downloads provide progress, cancellation, size/SHA-256 verification and a button to reveal the completed package. Failed or cancelled downloads remove partial packages; previous downloads are preserved. Packages are saved in unique subfolders of Downloads. Quit the app and install or extract the package yourself, preserving the existing data directory for your index and settings.

Only manual update actions contact GitHub; documents, paths and indexes are never uploaded. Startup, indexing and searching do not check online. A lightweight feed published with each Release avoids reliance on anonymous API quotas, and packaged apps include HTTPS trust roots. There is no automatic installation, restart or silent upgrade.

Retains beta.4 automatic local-disk discovery, all-format filename search and PDF / Markdown / DOCX content search, without folder selection. Filesystem changes still use periodic traversal; MFT / USN acceleration and OCR are not implemented.

Includes Linux x64 DEB / tar.gz, Windows x64 ZIP, macOS arm64 ZIP, sources and checksums. Linux targets Ubuntu 22.04 / 24.04 with system Python 3.10+, GTK 3 / WebKit; Windows requires WebView2. Packages lack trusted publisher signing and macOS notarization. Other architectures have no matching binary package yet.
