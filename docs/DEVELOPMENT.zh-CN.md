# 开发说明

[English](DEVELOPMENT.en.md)

## 架构

桌面使用 Python + pywebview，Windows 使用 WebView2，macOS 使用 WKWebView，Linux 使用 GTK 3 / WebKitGTK。HTML/CSS/JavaScript 随包分发，无前端构建步骤和 CDN。PRD 中的 Rust 只是候选方案；本版本选择更易验证和交付的 Python 实现。

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

`Tests` 工作流在三个系统运行。`Release` 工作流依次测试、构建 Windows x64 / macOS arm64 / Linux x64、检查冻结后的可执行文件、构建 Python 源码包与 wheel，**全部成功后**才发布版本（`vX.Y.Z` 为正式版，带后缀标签为预发行版）。手动运行仅生成构建产物。版本标签必须与 `pyproject.toml`、`__version__`、中英文发布说明保持一致。

直接运行依赖已固定版本；传递依赖和平台依赖在 runner 上解析，尚不属于完全封闭可复现构建。升级依赖时需显式提交并重跑平台矩阵。


## Linux 打包

在 Ubuntu 22.04 上使用 Python 3.10+ 虚拟环境，安装系统依赖 `python3-gi`、`python3-gi-cairo`、`gir1.2-gtk-3.0`、`gir1.2-webkit2-4.1`、`xdg-utils` 和 `desktop-file-utils`，执行同一个 `python scripts/package.py`。它调用 `scripts/package_linux.py`，将应用和 Python 依赖打为 DEB 与 tar.gz。启动器通过 `-I` 使用隔离的系统 Python，GTK/WebKit 由系统维护，不捆绑整套浏览器。核心和原生桥接自检通过后才归档；CI 还会在 Ubuntu 22.04 与 24.04 真正安装 DEB 并运行核心和 GUI 检查。无显示器的 CI 使用 `xvfb-run`，本机使用当前桌面。包中不含用户文档数据库。

## 恢复机制与性能检查

`tests/test_recovery.py` 覆盖单文件重试持久化、收藏保留、不可访问或越界目标、问题列表分页、重叠排除和全库重试竞态。单文件重试复用持久化的 `pending` 状态，无需数据库迁移。全库请求带独立标识，只有完整扫描结束且请求未被更新时才确认消费。

执行 `python scripts/benchmark.py /tmp/shiwen-benchmark`，在一个新目录内运行万文档基准；加 `--documents 100 --rounds 3` 可快速检查。详见[性能测量方法](PERFORMANCE.zh-CN.md)。基准仅生成合成文件，逐文件使用正式的独立解析进程，并核对已知搜索结果。CI 不在每个任务中重复万文档工作量。

## beta.4 自动发现

正常桌面启动构造 `Library(automatic=True)`，`discovery.py` 发现系统磁盘与不可扫描挂载。`--folder` 保留为开发用显式语料范围；`--gui-smoke` 使用空的磁盘提供器，避免 CI 扫描整台构建机。打包核心自检使用自动模式的合成磁盘。

名称遍历每 128 项提交，使用 `seen_scan` 标记完整扫描；中断时不清理未访问记录。另一个线程以每页 64 项读取 pending 文档并串行启动解析进程。全盘模式不创建递归 watchdog 监听器，使用周期核对。测试可注入 `disk_provider`，避免读取个人文件。旧模式仍供既有文档基准使用。

`tests/test_automatic.py` 覆盖无选择启动、混合文件类型与目录、名称先可查、搜索方式、单字符名称、更新删除、暂停中断、排除迁移、挂载策略及系统磁盘发现。

## 手动更新服务

`updates.py` 只在桥接接口收到检查 / 下载请求后联网。优先读取主分支公开的 `updates/latest.json`，无法打开时回退到 GitHub Releases API。所有打包检查通过并发布 Release 后，发布任务通过 `scripts/release_feed.py` 将已发布版本元数据提交到 main；版本标签保持不变，更新清单是独立提交。

版本比较区分 alpha、beta、候选版和正式版。下载仅接受服务端已匹配的本仓库标准资源，校验 HTTPS 重定向，使用系统信任证书与随包 certifi 证书，并在核对长度和 SHA-256 后才将临时文件改为正式安装包。取消和失败会清理部分下载，不调用自动安装器。`tests/test_updates.py` 覆盖版本 / 平台、离线启动、完整性、取消、网络 / 存储失败和桥接参数限制；打包后的核心自检还验证证书可用性。

## 退出回归验证

`desktop.guard_evaluation` 为 GTK 的 `evaluate_js` 和 `run_js` 等待绑定窗口关闭事件。底层 WebKit 调用放在守护线程，因为 GTK 事件循环销毁后可能不再发回完成回调；关闭时释放桥接调用线程。不使用强制退出整个进程的方式。已有桥接请求结束后才关闭数据库。独立解析器轮询取消事件，终止并回收子进程，中断文档保持待处理。

`tests/test_shutdown.py` 覆盖回调结果 / 异常、回调丢失、真实解析子进程取消及重启续处理、请求与数据库关闭顺序。`--gui-close-smoke RESULT_JSON` 在 JavaScript 尚未返回时关闭原生窗口，要求发出关闭请求后 15 秒内正常退出，单独排除 WebKit 启动耗时。Linux 打包与 Ubuntu 22.04 / 24.04 的已安装 DEB 检查均执行此回归，并保留普通 GUI 自检。


## 桌面验收与发布测量

先安装 `.[dev]`，执行 `python scripts/acceptance_benchmark.py /tmp/acceptance --documents 1000 --metadata 100000` 在新目录生成混合语料并验证查询，再在桌面会话执行 `python scripts/desktop_acceptance.py /tmp/acceptance --existing-index`。Linux 需要系统 GTK / WebKit 绑定，隔离 venv 可仅在原生桌面测试时设置 `PYTHONPATH=/usr/lib/python3/dist-packages`；CI 使用 Xvfb + Openbox。详见[测量方法与限制](PERFORMANCE.zh-CN.md)。

`desktop.WindowControls` 管理原生按钮、还原尺寸及缩放锚点；桥接动作使用白名单。回归测试确保精确候选过滤不会绕过可访问性检查。普通 GUI 自检点击自绘关闭按钮；关闭竞态自检在脚本执行期间销毁原生窗口。

Linux 无可读写 GPU 设备时，`configure_linux_rendering` 在 WebView 启动前默认设置 `WEBKIT_DISABLE_COMPOSITING_MODE=1`，保留用户显式值。这只是软件渲染回退，不保证所有环境低内存。空闲采样排除关闭阶段并扣除采样线程 CPU；macOS 在独立 CI 环境纳入新建的 WebKit XPC 服务，因其可能归 launchd 所有。

Release 对 `vX.Y.Z` 标签发布正式版，对带后缀标签发布预发行版；所有必需打包与自检任务成功后才公开发布。
