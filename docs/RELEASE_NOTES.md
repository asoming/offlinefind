# Shiwen v0.1.0-beta.9 / 拾文 · 启动与升级

## 简体中文

同一索引只运行一个拾文实例。再次打开应用时会请求唤起已有窗口，避免重复索引；崩溃后系统自动释放锁，不需删除锁文件。窗口唤起仅使用带随机令牌的本机回环通信，不上传文件。回环被系统禁用时仍能阻止重复启动，但无法唤起窗口。

Linux tar.gz 解压后，在 Shiwen 目录运行 `./install-user`，无需管理员权限即可安装到 `~/.local` 并创建应用菜单入口。以后安装新版时，同一个入口指向新版；旧版本的绝对启动路径也会转到新版。安装器保留旧版本备份、索引、收藏和原文档，并阻止降级覆盖。系统 Python / GTK / WebKit 依赖仍需预先安装。DEB 用户继续使用系统软件安装器升级。

**从 beta.8 或更早版本升级，请先退出旧窗口。** 旧版本尚无实例锁，安装不会强制结束正在运行的旧进程。设置中的下载仍需完成后手动安装；不是静默自动更新。

保留 beta.8 的 Linux 标题栏关闭修复。新增跨进程锁与崩溃恢复、安装升级与旧入口、原生窗口唤起验证。提供 Windows x64、macOS Apple Silicon、Linux x64 DEB / tar.gz。

仍为公开测试版：完整桌面内存、真实全盘检索性能和跨平台人工验收尚未完成，不能据此宣称已满足正式版全部指标。签名与 macOS 公证仍未提供。详见 [路线图](ROADMAP.md)。

## English

One Shiwen process owns each index. Reopening requests activation of the existing window instead of starting another indexer. OS locks release after a crash without deleting lock files. Activation uses authenticated loopback communication only; no documents are uploaded. If loopback is disabled, duplicate launches remain blocked but activation is unavailable.

Extract the Linux tar.gz and run `./install-user` inside Shiwen to install under `~/.local` and create a menu entry without administrator privileges. Subsequent upgrades update the same entry and redirect older absolute portable launch paths. Installation preserves old launcher backups, indexes, bookmarks and originals, and rejects downgrades. System Python / GTK / WebKit dependencies must already be installed. DEB users should continue upgrading through the OS package installer.

**Quit beta.8 or older before upgrading.** Those versions do not implement the instance lock; installation does not forcibly terminate running processes. Downloads in Settings still require manual installation, not silent automatic updates.

Retains beta.8's Linux title-bar close fix. Adds checks for cross-process locking, crash recovery, installer upgrades, legacy entry points and native window activation. Includes Windows x64, macOS Apple Silicon and Linux x64 DEB / tar.gz packages.

This remains a public preview: complete desktop memory, representative whole-disk performance and cross-platform manual acceptance are unfinished. Trusted publisher signing and macOS notarization are also unavailable. See the [roadmap](ROADMAP.md).
