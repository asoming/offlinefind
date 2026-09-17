# Roadmap / 路线图

0.1.0 is a stable release within its documented scope. The current interface is retained with published performance limits; unmet PRD budgets are deferred explicitly, not marked as achieved. / 0.1.0 按公开范围正式发布，保留当前界面并披露性能限制；未达标的 PRD 预算明确延期，不标为完成。

## Delivered in 0.1.0 / 已交付

- [x] Automatic local disk discovery without folder selection; names before independently extracted PDF/Markdown/DOCX contents. / 无需选文件夹，自动发现磁盘，名称优先、正文独立解析。
- [x] Offline search, exact verification, previews, bookmarks, retry/exclusion controls, bilingual glass UI and integrated frameless controls. / 离线搜索、精确核对、预览、收藏、重试排除、中英文玻璃界面及无边框窗口操作。
- [x] Manual update download/checksum, single instance, Linux user installer and shutdown fixes. / 手动更新下载校验、单实例、Linux 用户安装与关闭修复。
- [x] 10,000 mixed documents, 100 queries, names searched during parsing, 739,334 real local name entries and one million synthetic names. / 万份混合文档、100 条查询、边解析边搜名称、73.9 万真实本机名称与百万合成名称测量。
- [x] Full desktop RSS/CPU samples and native automated interactions on Windows/macOS/Linux. / 三平台完整桌面 RSS / CPU 采样与原生自动操作验收。
- [x] Public bilingual performance evidence and explicit release limits. / 公开双语性能证据及版本限制。

See [English measurements](PERFORMANCE.en.md) / [中文测量报告](PERFORMANCE.zh-CN.md). Automated CI is not comprehensive manual OS acceptance. / CI 自动检查不等同完整人工系统验收。

## Next work / 后续

| Work / 工作 | Purpose / 目的 |
| --- | --- |
| Lower desktop idle memory and CPU / 降低桌面空闲内存与 CPU | Original sub-100 MiB target is unmet / 原定低于 100 MiB 未达成 |
| Broad-match search and ranking / 大量匹配查询与排序 | Some searches exceed 300 ms, million-name broad query ~2.7s / 部分查询超过 300 ms，百万名称大量匹配约 2.7 秒 |
| NTFS MFT/USN, platform journals and cheaper reconciliation / 文件变更日志与低成本核对 | Faster discovery and updates / 加快发现与更新 |
| Strict cold-cache and reference hardware testing / 严格冷缓存与参考硬件 | 4-core / 8 GB, representative complex documents, long-duration power / 4 核 8 GB、复杂真实文档与长期功耗 |
| Physical-machine native-dialog, permission and recovery acceptance / 实体机系统对话框、权限与恢复验收 | Extend automated bridge checks / 补充自动桥接检查 |
| Trusted signing and notarization / 可信签名与公证 | Improve installation trust / 改善安装信任体验 |
| Stable file identity / 稳定文件身份 | Preserve bookmarks on rename / 重命名保留收藏 |
| Atomic rebuild and corruption repair / 原子重建与损坏修复 | Improve index reliability / 提升索引可靠性 |
| Unicode offset evaluation / Unicode 高亮评估 | Complex normalization mappings / 复杂字符映射 |
| Hard resource budgets and power awareness / 硬资源限制与电源感知 | Predictable background usage / 控制后台负担 |
| Optional offline OCR / 可选离线 OCR | Search scanned pages locally / 本地检索扫描件 |
| Global search shortcut / 全局唤起快捷键 | Reach search from other apps / 从其他应用唤起 |

AI chat, editing, automatic renaming and cloud synchronization remain outside the initial scope. / AI 问答、编辑、自动重命名和云同步仍不属于首版主线。
