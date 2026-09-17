# Shiwen v0.1.0-beta.4 / 拾文 · 打开即搜

## 简体中文

正常启动自动扫描本机，不再要求选择文件夹，也不要求文件夹只包含文档。图片、视频、压缩包、代码和文件夹均支持名称搜索；PDF、Markdown、DOCX 继续支持离线正文检索。名称发现和正文解析独立运行，慢速文档不会阻塞文件名入库。

新增“文件名 + 内容”“仅文件名”“仅文档内容”切换和文件夹筛选。文件名允许单字符，正文至少双字符。保留旧版排除规则与收藏；清除数据后暂停自动索引，可手动继续重建。

Windows 发现带盘符的固定磁盘，Linux / macOS 遍历本地目录树。跳过虚拟系统目录、网络挂载、缓存 / 依赖目录、符号链接和自己的索引；权限不足时跳过，不提权。文件不会上传或修改。

这是普通文件遍历实现，约 30 秒间隔核对加扫描耗时；尚未实现 Everything 的 MFT / USN 加速，不承诺同等全盘首建速度。既有 beta.3 文档基准不代表此版本全盘性能。没有 OCR、原文排版渲染、硬内存上限、数据库自动修复或重命名收藏迁移。

提供 Linux x64 DEB / tar.gz、Windows x64 ZIP、macOS arm64 ZIP、源码和校验和。Linux 依赖系统 Python 3.10+、GTK 3 和 WebKit；Windows 需 WebView2。测试包没有可信发布者签名或 macOS 公证。详见仓库中的中英文安装说明和新版 PRD。

## English

Normal startup discovers local files automatically, with no folder picker or document-only folder requirement. Find images, videos, archives, code and folders by name; retain offline PDF, Markdown and DOCX content search. Independent discovery and parsing workers keep slow documents from blocking name indexing.

Adds Names + contents, File names only, Document contents only and a Folders filter. Names accept single-character terms; content terms require two characters. Existing exclusions and bookmarks survive upgrades. Clearing data pauses indexing until resumed.

Windows discovers fixed disks with drive letters; Linux/macOS traverse local directory trees. Virtual filesystems, network mounts, caches/dependencies, symlinks and the index itself are skipped. Respect account permissions without elevation. Originals are neither uploaded nor modified.

This uses ordinary traversal and approximately 30-second reconciliation intervals plus scan time, without Everything's MFT / USN acceleration or equivalent first-index speed claims. The earlier beta.3 document baseline does not establish full-disk performance. OCR, original-layout rendering, hard memory caps, automatic database repair and bookmark migration on rename remain unimplemented.

Includes Linux x64 DEB / tar.gz, Windows x64 ZIP, macOS arm64 ZIP, source distributions and checksums. Linux needs system Python 3.10+, GTK 3 and WebKit; Windows needs WebView2. Packages have no trusted publisher signature or macOS notarization. See bilingual installation guides and the revised PRD.
