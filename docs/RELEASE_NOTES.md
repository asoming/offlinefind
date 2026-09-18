# OfflineFind / 拾文 0.1.1

## 中文

英文名正式改为 **OfflineFind**：Offline + Find，突出“离线查找”。功能说明为 **Offline file & full-text search**。中文名继续使用“拾文”，公开仓库改为 [asoming/offlinefind](https://github.com/asoming/offlinefind)。

- 英文界面、窗口、菜单、Windows / macOS 应用名及安装包采用新名；中文界面保留“拾文”。
- 无需选文件夹，自动收录本机文件名；PDF、Markdown、DOCX 正文离线搜索功能保持不变。
- 更新中英文文档、仓库链接与检查更新入口。
- 升级保留原有索引、收藏、排除规则与应用身份；旧命令和快捷方式继续可用。
- 旧版更新器支持升级到新版，额外提供 `Shiwen-*` 同内容兼容文件。正常下载请选择 `OfflineFind-*`。

Windows x64、macOS Apple Silicon、Linux x64 DEB / tar.gz，以及 Python wheel / 源码包均提供。退出旧窗口后升级；Linux tar.gz 解压后执行 `OfflineFind/install-user`，然后从菜单重新打开。新命令为 `offlinefind`，原 DEB 包名 `shiwen` 与含 `Shiwen` 的数据目录保留用于兼容。

本次为命名和升级兼容更新，不是性能重构。[0.1.0 实测与限制](https://github.com/asoming/offlinefind/blob/main/docs/PERFORMANCE.zh-CN.md)仍适用：本机完整桌面空闲 RSS 约 574 MiB，部分查询超过 300 ms；没有 OCR / NTFS MFT 加速，安装包尚无可信发布者签名 / macOS 公证。未重新宣称达到原始低内存预算。

## English

The English product name is now **OfflineFind**: **Offline file & full-text search**. The Chinese name remains **拾文**. The public repository is [asoming/offlinefind](https://github.com/asoming/offlinefind).

- New branding in the English interface, windows, menus, native applications and download packages.
- Automatic local discovery and offline PDF, Markdown and DOCX content search remain unchanged.
- Updated bilingual documentation, repository links and update endpoints.
- Existing indexes, bookmarks, exclusions and application identities are preserved. Legacy commands and shortcuts continue to work.
- Earlier updaters can upgrade through byte-identical `Shiwen-*` compatibility assets. Choose `OfflineFind-*` for a new download.

Packages cover Windows x64, macOS Apple Silicon and Linux x64 DEB / tar.gz, plus Python wheel/source. Quit the old window before upgrading. On Linux, extract and run `OfflineFind/install-user`, then reopen from the application menu. The primary command is `offlinefind`; the Debian ID `shiwen` and existing data directories containing `Shiwen` remain for upgrade compatibility.

This is a naming and migration release, not a performance rewrite. The [0.1.0 measurements and limits](https://github.com/asoming/offlinefind/blob/main/docs/PERFORMANCE.en.md) still apply: local full-desktop idle RSS around 574 MiB, some queries exceeding 300 ms, no OCR or NTFS MFT acceleration, and no trusted publisher signing/macOS notarization. The original low-memory target is not claimed.
