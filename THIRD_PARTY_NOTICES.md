# Third-party notices / 第三方依赖说明

OfflineFind's source is MIT licensed. Dependencies retain their own licenses; this file is an index, not a replacement for those terms. Binary bundles include dependency metadata and license material collected by the packaging tools where available.

拾文源码使用 MIT；依赖各自保留原许可。本文件仅提供索引，不替代原条款。打包工具在可用时收集依赖元数据与许可材料。

| Dependency | Use | Upstream |
| --- | --- | --- |
| Python | Runtime | https://www.python.org/psf/license/ |
| pywebview | Native WebView bridge | https://github.com/r0x0r/pywebview |
| pypdf | PDF text extraction | https://github.com/py-pdf/pypdf |
| platformdirs | OS data directories | https://github.com/tox-dev/platformdirs |
| watchdog | Filesystem notifications | https://github.com/gorakhargosh/watchdog |
| defusedxml | Hardened XML parsing | https://github.com/tiran/defusedxml |
| certifi | HTTPS certificate bundle for manual updates | https://github.com/certifi/python-certifi |
| SQLite | Local storage and FTS5 | https://www.sqlite.org/copyright.html |
| PyInstaller | Packaging with its bootloader exception | https://pyinstaller.org/en/stable/license.html |

Platform-dependent components, including pythonnet/.NET, PyObjC and WebView2, retain their respective terms. ReportLab is used only to generate synthetic test fixtures and is excluded from app bundles.

pythonnet/.NET、PyObjC、WebView2 等平台组件适用各自条款。ReportLab 仅用于生成测试样例，不随应用包分发。


Linux packages additionally include bottle, proxy-tools and typing_extensions Python modules, with their distribution metadata/license files. GTK, PyGObject and WebKitGTK are system dependencies, not redistributed in the Linux archive; they retain their upstream terms.

Linux 包还包含 bottle、proxy-tools 和 typing_extensions Python 模块及各自分发元数据与许可文件。GTK、PyGObject 和 WebKitGTK 作为系统依赖使用，不包含在 Linux 压缩包内，保留各自许可。
