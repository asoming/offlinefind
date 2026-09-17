# Roadmap / 路线图

This is a staged implementation of the [original PRD](PRD.zh-CN.md), not a completed PRD claim.

本项目分阶段实现[原始 PRD](PRD.zh-CN.md)，测试版发布不代表所有 P0 验收项已经完成。

| Next work / 后续工作 | Purpose / 目的 |
| --- | --- |
| Representative corpus and full desktop benchmarks / 真实语料与完整桌面基准 | Extend the synthetic baseline to GUI memory, cold cache and Windows/macOS / 补充 GUI 内存、冷缓存及 Windows/macOS 测量 |
| Ranking and Unicode offset evaluation / 排序与 Unicode 高亮评估 | Improve relevance and complex normalization mappings / 改善相关性和复杂字符映射 |
| Native dialog acceptance and signed releases / 原生对话框验收与签名 | Extend existing native bridge smoke checks to OS dialogs and trusted installation / 在现有原生桥接检查基础上完善系统对话框与安装体验 |
| Stable file identity / 稳定文件身份 | Preserve bookmarks on rename / 重命名后保留收藏 |
| Atomic rebuild and corruption repair / 原子重建与损坏修复 | Improve index reliability / 提升索引可靠性 |
| Hard resource budgets and power awareness / 硬资源限制与电源感知 | Make background usage predictable / 控制后台负担 |
| Optional offline OCR / 可选离线 OCR | Search scanned pages without uploading / 离线检索扫描件 |
| Global search shortcut / 全局唤起快捷键 | Reach search from another application / 随时唤起搜索 |

AI chat, document editing, automatic renaming and cloud synchronization are outside the initial product scope.

AI 问答、文档编辑、自动重命名、云同步不属于首版主线。


beta.3 delivers per-file retries, issue pagination and removable exclusions, plus a synthetic performance baseline. This does not complete the PRD’s full performance acceptance.

beta.3 已交付单文件重试、问题列表分页与排除撤销，并建立合成性能基线；PRD 的完整性能验收仍未完成。

## Automatic discovery follow-up / 自动发现后续

Beta.4 replaces folder onboarding with automatic disk discovery and independent name/content indexing. Next: NTFS MFT / USN or platform change journals, larger file-library benchmarks, and lower-cost incremental reconciliation.

beta.4 已取消文件夹选择前置步骤，自动发现磁盘，名称与正文独立索引。后续关注 NTFS MFT / USN 或平台变更日志、大型文件库基准和增量核对成本。

## Stable release gates / 正式版发布门槛

Beta.9 completes per-index single-instance protection and repeatable Linux user installation. These fix startup/upgrade friction; they do not finish performance acceptance.

beta.9 已完成同索引单实例保护和可重复执行的 Linux 用户级安装，解决启动与升级入口问题，尚未完成性能验收。

- [ ] Measure representative whole-disk filename and mixed-content search, including concurrent indexing and cold starts. / 测量真实全盘名称与混合正文检索、边索引边搜索及冷启动。
- [ ] Record full process-tree desktop memory (WebView and parser included), background CPU and index size on supported platforms against the PRD. / 对照 PRD 测量各平台完整进程树内存（含 WebView 与解析器）、后台 CPU 和索引体积。
- [ ] Complete manual Windows/macOS/Linux acceptance for native dialogs, permissions, install/upgrade, restart and recovery. / 完成 Windows、macOS、Linux 的原生对话框、权限、安装升级、重启与恢复人工验收。
- [ ] Resolve release-blocking findings and document any deliberately deferred PRD requirements before choosing a stable version. / 修复阻断问题，明确延期的 PRD 项后再确定正式版。

Existing automated core, native bridge, activation and Linux close checks remain release gates. A passing package build alone does not satisfy the items above.

现有核心、原生桥接、窗口唤起及 Linux 关闭检查继续作为发布门槛；打包通过不等于上述验收已完成。
