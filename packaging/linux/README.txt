拾文 / Shiwen · Linux x64

简体中文
已验证目标：Ubuntu 22.04 / 24.04 x64 桌面。
解压后，在本目录执行 ./shiwen，或用系统软件安装器安装 .deb。
也可执行 sudo apt install ./Shiwen-*-linux-amd64.deb。

Linux 包复用系统 Python 3.10+、GTK 3 和 WebKit，不内置浏览器引擎。
免安装版如果缺少依赖，可先运行：
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1 xdg-utils
Ubuntu 22.04 也可使用 gir1.2-webkit2-4.0。准备好这些系统依赖后，日常使用完全离线。
默认索引目录为 ~/.local/share/Shiwen，卸载应用不会删除索引或原文档。
完整说明见 docs/USER_GUIDE.zh-CN.md。

English
Validated targets: Ubuntu 22.04 / 24.04 x64 desktops.
Run ./shiwen from this directory, or install the .deb using your software installer.
Alternatively: sudo apt install ./Shiwen-*-linux-amd64.deb

Linux packages reuse system Python 3.10+, GTK 3 and WebKit instead of bundling a browser.
For the portable archive, install missing system dependencies with:
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1 xdg-utils
On Ubuntu 22.04, gir1.2-webkit2-4.0 also works. Daily use is fully offline once dependencies exist.
The default index lives at ~/.local/share/Shiwen. Uninstalling keeps the index and source documents.
See docs/USER_GUIDE.en.md for the full guide.
