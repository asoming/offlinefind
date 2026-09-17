# 拾文 · Shiwen

**记得内容，就找得到。**

[English](README.md) · [下载 Releases](https://github.com/asoming/shiwen/releases) · [使用说明](docs/USER_GUIDE.zh-CN.md) · [开发说明](docs/DEVELOPMENT.zh-CN.md)

拾文是一款自动扫描本机的离线文件检索工具。打开即可搜索，无需选择文件夹：图片、压缩包、代码和文件夹都可按名称找到，PDF、Markdown、DOCX 还支持正文检索和命中预览。界面保留轻磨砂玻璃效果。

**当前版本：v0.1.0-beta.9。** 这是公开测试版，不代表 PRD 全部功能已完成。请先阅读[版本说明与限制](docs/RELEASE_NOTES.md)。

## 已实现

- 启动后自动发现本地磁盘，优先收录各类文件和文件夹名称，正文独立后台解析。
- 提供“文件名 + 内容”“仅文件名”“仅文档内容”三种搜索方式。
- 精确短语、空格分隔的多条件搜索，以及文件类型、目录、收藏筛选。
- 真实原文摘要与高亮；PDF 物理页、Markdown 源行号、DOCX 段落位置。
- 磁盘 SQLite FTS5 字符二元索引，再核对原文，过滤相似字符造成的误报。
- 独立进程解析、磁盘定期核对、暂停恢复、排除子目录与撤销排除、清除本地数据。
- 问题文档列表、单文件重试；暂停或重启后保留待处理任务。
- 浅色 / 深色 / 跟随系统、可关闭玻璃效果、中英文界面和键盘操作。
- 设置内手动检查更新、匹配系统安装包、下载进度 / 取消与 SHA-256 校验。
- 无账号、无遥测、无外部字体、无远程文档渲染、无自动联网更新。

同一索引只运行一个实例，重复打开会唤起已有窗口；Linux 压缩包提供用户级安装器。

## 下载与安装

前往 [GitHub Releases](https://github.com/asoming/shiwen/releases)，下载 Windows x64 ZIP、macOS Apple Silicon ZIP，或 Linux x64 DEB / tar.gz。压缩包需**完整解压**后运行。Windows/macOS 包含 Python；Linux 复用系统运行时。

- **Windows 11 x64：** 使用 Edge WebView2，需要电脑已安装该运行时；应用不会偷偷联网下载。大部分 Windows 11 环境已提供，隔离网络机器需提前准备。
- **macOS 14+ Apple Silicon：** 使用系统 WebKit。测试版没有开发者证书签名和公证，首次启动可能需要在“系统设置 → 隐私与安全性”中批准。
- 测试版没有可信发布者签名（macOS 打包可能带临时签名），可核对 Release 中的 SHA-256。无需关闭系统整体安全功能。
- **Ubuntu 22.04 / 24.04 x64：** 用系统软件安装器打开 `.deb`，或执行 `sudo apt install ./Shiwen-*-linux-amd64.deb`，然后在应用菜单搜索“拾文”。免安装压缩包解压后执行 `./Shiwen/shiwen`。两者复用系统 Python 3.10+、GTK 3 与 WebKit，已带齐 Python 模块，无需手动配置 pip。详见 [Linux 安装说明](docs/USER_GUIDE.zh-CN.md#linux-安装)。

## 第一次搜索

1. 打开拾文，自动发现本机文件，无需添加文件夹。
2. 直接输入关键词；文件名先可搜索，文档正文陆续加入。
3. 输入 `部署`、`预算 审批` 或 `"offline deployment"`。
4. 点击结果查看提取文本；需要原排版时点击“打开原文件”。

应用内 `Ctrl+K` / `Cmd+K` 聚焦搜索。文件名支持单字符；正文搜索词至少两个字符；空格分隔的条件必须同时出现在同一文档。当前为文字匹配，不进行 AI 语义理解。

## 隐私与边界

原文件不会被移动、重命名或改写。索引包含提取的文档原文，**没有单独加密**，请使用系统用户权限和磁盘加密保护它。可在“索引与排除”中排除目录，或清除全部本地数据并暂停索引。

自动索引跳过虚拟系统目录、网络挂载、缓存 / 依赖目录、符号链接和自己的索引目录；权限不足的目录会跳过。Windows 自动发现盘符式固定磁盘，Linux / macOS 从本地目录树发现文件。名称更新通过约 30 秒间隔的核对实现，还需加上扫描耗时，尚未实现 Everything 的 NTFS MFT / USN 加速。

当前不含 OCR。扫描页、密码保护、编码问题、解析失败与超限均显示状态，正文不可读时仍可按文件名搜索。默认限制为单文件 100 MiB、PDF 1,000 页、提取文本 10 MiB。DOCX 只预览正文和普通表格的提取文字，不伪造 Word 页码。

可使用[基准脚本](scripts/benchmark.py)复现合成万文档测试；测量方法和局限见[性能报告](docs/PERFORMANCE.zh-CN.md)。PRD 的完整桌面内存、冷启动和跨平台预算仍需验证。后续工作见[路线图](docs/ROADMAP.md)。

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

浏览器模式只监听本机回环地址，带每次启动生成的请求令牌，不是云端服务。`--folder` 仅用于开发时限制测试范围；正常启动不需要此参数。系统应用打开功能以桌面版为准。索引与搜索可离线；手动检查更新和下载时连接 GitHub，不发送本机文档、路径或索引；源码安装依赖需联网或事先准备包缓存。

## 参与开发

阅读[开发说明](docs/DEVELOPMENT.zh-CN.md)和[贡献指南](CONTRIBUTING.md)。反馈问题时请使用合成样例，不要上传私密文档或索引数据库。

MIT © 2026 asoming。参见 [LICENSE](LICENSE) 与[第三方依赖说明](THIRD_PARTY_NOTICES.md)。

