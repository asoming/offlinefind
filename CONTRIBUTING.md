# Contributing / 贡献指南

Use a feature branch and open a pull request against `main`. Explain the behavior change and relevant validation. Run `ruff check .`, `ruff format --check .` and `pytest -q`. Keep UI strings paired in Chinese and English and update both guides when behavior changes.

请在功能分支开发，通过 Pull Request 合入 `main`。说明行为变化与验证结果，运行上述检查。界面文字维护中英文两份；行为变化时同步更新双语说明。

Use synthetic fixtures. Never commit real user documents, local indexes, credentials, absolute developer-machine paths or generated caches. Dependency changes and release scripts require platform testing. Do not add telemetry or outbound requests to runtime flows.

测试使用合成资料。不要提交真实用户文档、索引、凭据、开发机绝对路径或缓存。依赖与发布脚本变更需检查目标平台；运行流程不得加入遥测或外部请求。

