# 开发说明

[English](DEVELOPMENT.en.md)

## 架构

桌面使用 Python + pywebview，Windows 使用 WebView2，macOS 使用 WKWebView。HTML/CSS/JavaScript 随包分发，无前端构建步骤和 CDN。PRD 中的 Rust 只是候选方案；本测试版选择更易验证和交付的 Python 实现。

| 文件 | 职责 |
| --- | --- |
| `src/shiwen/app.py` | 桌面生命周期、原生调用白名单、可选本机开发服务 |
| `library.py` | 范围规则、后台扫描、文件监听、解析调度、版本防护 |
| `store.py` | SQLite、外部内容 FTS5 索引、收藏与原文核对 |
| `text.py` | NFKC / 大小写规范化、查询解析、字符二元索引、高亮坐标 |
| `extract.py` | 在独立进程中解析 PDF / Markdown / DOCX |
| `ui/` | 中英文玻璃界面、界面状态、安全文本节点渲染 |

FTS 存储编码后的字符二元组，用每个关键词的二元组交集召回候选，再核对规范化原文。这样可支持中文双字词，并过滤不连续字符造成的误报。索引存储的是去重二元组，BM25 衡量字符组合覆盖和稀有度，而非原始词频；排序质量仍需真实查询集评估。

解析任务串行运行在单独的 spawn 进程中，父进程限制 60 秒；POSIX 额外设置 CPU 时间上限。当前尚无跨平台硬内存上限。预览只创建安全文本节点，不执行文档 HTML。索引是受账户权限保护的本地明文，不提供应用级加密。

更新检测使用文件大小、纳秒修改时间、设备 / inode / ctime 指纹，并结合监听与 30 秒周期核对。该指纹不是完整内容哈希，无法涵盖所有保留元数据的修改。发现变化时先撤下旧正文，再加入新版本；持续可搜的原子新旧版本切换后续完善。

## 开发与验证

```bash
python -m venv .venv
# 按平台激活 .venv。
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
pytest -q
python -m shiwen.app --self-test smoke.json
python -m build
```

避免继承其他项目的 `PYTHONPATH` 和 pytest 插件。必要时使用 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` 隔离本地测试；CI 在干净的 Linux、Windows、macOS 环境执行。

使用合成文件检查界面：

```bash
python scripts/demo_documents.py /tmp/shiwen-fixtures
shiwen --serve --folder /tmp/shiwen-fixtures --data-dir /tmp/shiwen-index
```

开发服务仅绑定 `127.0.0.1`，校验 Host / Origin、使用启动时随机请求令牌，并限制请求体积。不要公开托管或穿透到外网。系统文件夹选择器仅由桌面桥接调用。

## 打包与发布

在目标系统的干净虚拟环境中运行：

```bash
python -m pip install -e '.[dev]'
python scripts/package.py
```

脚本创建 PyInstaller 目录包，运行打包后程序的 `--self-test`，成功后归档并生成 SHA-256。macOS 用 `ditto` 保留应用包链接。尚未配置可信证书签名与公证，不能声称已签名。

`Tests` 工作流在三个系统运行。`Release` 工作流依次测试、构建 Windows x64 / macOS arm64、检查冻结后的可执行文件、构建 Python 源码包与 wheel，**全部成功后**才发布 prerelease。手动运行仅生成构建产物。版本标签必须与 `pyproject.toml`、`__version__`、中英文发布说明保持一致。

直接运行依赖已固定版本；传递依赖和平台依赖在 runner 上解析，尚不属于完全封闭可复现构建。升级依赖时需显式提交并重跑平台矩阵。

