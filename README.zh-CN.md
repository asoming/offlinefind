# 拾文 · Shiwen

**记得内容，就找得到。**

[English](README.md) · [下载 Releases](https://github.com/asoming/shiwen/releases) · [使用说明](docs/USER_GUIDE.zh-CN.md) · [开发说明](docs/DEVELOPMENT.zh-CN.md)

拾文是一款离线桌面文档检索工具。选择文件夹，输入记得的一句话，就能在 PDF、Markdown、DOCX 中找到相关文档，并直接阅读命中上下文。轻磨砂玻璃用于导航和搜索区域，正文保持清晰。

**当前版本：v0.1.0-beta.2。** 这是公开测试版，不代表 PRD 全部功能已完成。请先阅读[版本说明与限制](docs/RELEASE_NOTES.md)。

## 已实现

- 搜索文件名和文档正文，支持中文双字词、连续中文与中英文混排。
- 精确短语、空格分隔的多条件搜索，以及文件类型、目录、收藏筛选。
- 真实原文摘要与高亮；PDF 物理页、Markdown 源行号、DOCX 段落位置。
- 磁盘 SQLite FTS5 字符二元索引，再核对原文，过滤相似字符造成的误报。
- 独立进程解析、目录监听加定期核对、暂停恢复、排除子目录、清除本地数据。
- 浅色 / 深色 / 跟随系统、可关闭玻璃效果、中英文界面和键盘操作。
- 无账号、无遥测、无外部字体、无远程文档渲染、无自动联网更新。

## 下载与安装

前往 [GitHub Releases](https://github.com/asoming/shiwen/releases)，下载 Windows x64 ZIP、macOS Apple Silicon ZIP，或 Linux x64 DEB / tar.gz。压缩包需**完整解压**后运行。Windows/macOS 包含 Python；Linux 复用系统运行时。

- **Windows 11 x64：** 使用 Edge WebView2，需要电脑已安装该运行时；应用不会偷偷联网下载。大部分 Windows 11 环境已提供，隔离网络机器需提前准备。
- **macOS 14+ Apple Silicon：** 使用系统 WebKit。测试版没有开发者证书签名和公证，首次启动可能需要在“系统设置 → 隐私与安全性”中批准。
- 测试版没有可信发布者签名（macOS 打包可能带临时签名），可核对 Release 中的 SHA-256。无需关闭系统整体安全功能。
- **Ubuntu 22.04 / 24.04 x64：** 用系统软件安装器打开 `.deb`，或执行 `sudo apt install ./Shiwen-*-linux-amd64.deb`，然后在应用菜单搜索“拾文”。免安装压缩包解压后执行 `./Shiwen/shiwen`。两者复用系统 Python 3.10+、GTK 3 与 WebKit，已带齐 Python 模块，无需手动配置 pip。详见 [Linux 安装说明](docs/USER_GUIDE.zh-CN.md#linux-安装)。

## 第一次搜索

1. 点击“添加文件夹”，选择本机文档目录。
2. 等待首批文档完成索引；不必等全部完成再搜索。
3. 输入 `部署`、`预算 审批` 或 `"offline deployment"`。
4. 点击结果查看提取文本；需要原排版时点击“打开原文件”。

应用内 `Ctrl+K` / `Cmd+K` 聚焦搜索。每个搜索词至少两个字符；空格分隔的条件必须同时出现在同一文档。当前为文字匹配，不进行 AI 语义理解。

## 隐私与边界

原文件不会被移动、重命名或改写。索引包含提取的文档原文，**没有单独加密**，请使用系统用户权限和磁盘加密保护它。可在设置中移除范围或清除全部本地数据。

当前不含 OCR。扫描页、密码保护、编码问题、解析失败与超限均显示状态，正文不可读时仍可按文件名搜索。默认限制为单文件 100 MiB、PDF 1,000 页、提取文本 10 MiB。DOCX 只预览正文和普通表格的提取文字，不伪造 Word 页码。

PRD 中的万份文档性能与内存预算是待验证目标，**本版本没有宣称已经达到**。后续工作见[路线图](docs/ROADMAP.md)。

## 源码运行

需要 Python 3.10+，Windows/macOS Release 使用 Python 3.12 构建；Linux 使用系统 Python 3.10+。

```bash
git clone https://github.com/asoming/shiwen.git
cd shiwen
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
python -m pip install -e '.[dev]'
shiwen
```

开发预览：

```bash
shiwen --serve --port 8765 --folder /你的/本地文档目录
```

浏览器模式只监听本机回环地址，带每次启动生成的请求令牌，不是云端服务。添加目录与系统应用打开功能以桌面版为准。运行时可离线；源码安装依赖需联网或事先准备包缓存。

## 参与开发

阅读[开发说明](docs/DEVELOPMENT.zh-CN.md)和[贡献指南](CONTRIBUTING.md)。反馈问题时请使用合成样例，不要上传私密文档或索引数据库。

MIT © 2026 asoming。参见 [LICENSE](LICENSE) 与[第三方依赖说明](THIRD_PARTY_NOTICES.md)。

