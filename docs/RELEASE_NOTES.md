# Shiwen v0.1.0-beta.6 / 拾文 · 关闭窗口修复

## 简体中文

修复 Linux 上点击标题栏 × 后应用可能无法完全退出的问题：窗口销毁时，尚未返回的 WebView 回调可能使界面请求线程永久等待。现在关闭窗口会解除这些等待，并停止接收新请求。

关闭时主动取消文档解析子进程，不再等待长文档的完整解析超时。未完成的文档保留待处理状态，下次启动继续；已完成的索引与收藏保留。数据库会在已有界面请求和索引任务结束后再关闭，避免退出时访问已关闭数据库。

新增退出回归测试和安装包级 GTK 关闭竞态自检。保留 beta.5 的手动检查更新、下载进度、取消和 SHA-256 校验，以及自动发现本机文件的搜索流程。

Linux x64 提供 DEB / tar.gz，Windows x64 和 macOS Apple Silicon 提供 ZIP。测试版仍无可信发布者签名或 macOS 公证。退出期间正在进行的联网操作仍受网络超时影响；关闭窗口不等待界面回调。原文件不会修改或上传。

## English

Fixes a Linux exit hang after clicking the title-bar ×. Destroying the WebView with an outstanding JavaScript callback could leave a non-daemon request thread waiting forever. Closing now releases these waits and rejects new requests.

In-flight document parser processes are cancelled instead of waiting for the full document timeout. Unfinished documents remain pending for the next launch; completed indexes and bookmarks are preserved. The database stays open until existing bridge requests and indexing tasks finish.

Adds shutdown regression tests and a packaged GTK close-race smoke test. Retains beta.5 manual update checks, download progress/cancellation, SHA-256 verification and automatic local-file discovery.

Includes Linux x64 DEB / tar.gz, Windows x64 ZIP and macOS Apple Silicon ZIP. Beta packages still lack trusted publisher signing and macOS notarization. An in-flight network operation remains subject to its network timeout during cleanup; closing the window no longer waits for UI callbacks. Originals are neither modified nor uploaded.
