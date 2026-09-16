# Roadmap / 路线图

This is a staged implementation of the [original PRD](PRD.zh-CN.md), not a completed PRD claim.

本项目分阶段实现[原始 PRD](PRD.zh-CN.md)，测试版发布不代表所有 P0 验收项已经完成。

| Next work / 后续工作 | Purpose / 目的 |
| --- | --- |
| Fixed 10,000-document benchmark / 固定万文档基准 | Measure latency, indexing time, disk and memory instead of guessing / 用测量验证轻量目标 |
| Ranking and Unicode offset evaluation / 排序与 Unicode 高亮评估 | Improve relevance and complex normalization mappings / 改善相关性和复杂字符映射 |
| Native GUI smoke automation and signed releases / 原生界面测试与签名 | Verify OS dialogs, WebViews and trusted installation / 验证原生交互与安装体验 |
| Stable file identity / 稳定文件身份 | Preserve bookmarks on rename / 重命名后保留收藏 |
| Per-file errors and retry, editable exclusions / 单文件错误重试与排除编辑 | Better recovery / 更方便地排查漏搜 |
| Atomic rebuild and corruption repair / 原子重建与损坏修复 | Improve index reliability / 提升索引可靠性 |
| Hard resource budgets and power awareness / 硬资源限制与电源感知 | Make background usage predictable / 控制后台负担 |
| Optional offline OCR / 可选离线 OCR | Search scanned pages without uploading / 离线检索扫描件 |
| Global search shortcut / 全局唤起快捷键 | Reach search from another application / 随时唤起搜索 |

AI chat, document editing, automatic renaming and cloud synchronization are outside the initial product scope.

AI 问答、文档编辑、自动重命名、云同步不属于首版主线。

