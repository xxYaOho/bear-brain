# Changelog

## [Unreleased]

## [0.3.0] - 2026-03-17

### Added
- 完成 memory core runtime 闭环：auto-promote 触发链、SQLite 状态持久化
- 实现 `/bb-promote` 真实落盘路径（更新 daily 文件、追加 memory 文件）
- 接通 promote 状态跨会话恢复（StateMachine + PromoteStateStore）
- 支持 file/payload 降级链（符合方案 B 架构）

### Changed
- 重构 BearAdapter 为纯数据适配器（静态方法），移除 MCP 客户端职责
- auto-promote 默认启用（`auto_promote=True`）
- 收紧 `list_pending()` 日期计算，改用 `timedelta` 避免跨月错误

### Architecture
- 明确方案 B 职责边界：host 层负责 MCP 调用，runtime 层负责业务逻辑
- Bear preload 当前采用 file/payload 降级链，host 层 MCP 注入待后续实现

## [0.2.1] - 2026-03-17

### Changed
- 收紧 Bear 写入协议，明确先查后写、先取真实时间、再执行追加或替换
- 为 `#memory/daily` 与 workstream 补充写前检查，禁止凭对话上下文猜时间或元数据

### Fixed
- 修正 BearBrain 写入类规范中过于宽松的问题，明确 NOTE-ID、Status、release、Related Notes 条目必须来自当前查询结果
- 为 note-lint 与 skill 文件补充回归测试，防止再次出现跳过 editing、猜时间、猜元数据的行为

## [0.2.0] - 2026-03-16

### Added
- 初始化本地 Bear-Brain 原型仓库结构
- 添加 `#memory` / `#memory/daily` 基础数据模型与解析逻辑
- 添加本地 SQLite memory store 与 `sqlite-vec` 接入骨架
- 添加 `bootstrap`、`promote-yesterday`、`search`、`publish-doc` CLI 路径
- 添加第一阶段 docs 骨架与 BearBrain skill 源文件
- 添加 `append-daily` CLI 与 OpenCode daily hook 原型
- 添加本地 markdown 默认路径发现与索引同步
- 添加 `BEAR_BRAIN_DAILY_GLOBAL` 严格布尔开关

### Changed
- 将向量维度从“实现时确认”收敛为固定 `512` 并运行时校验
- 将计划文档边界明确为：草稿先留 Bear，稳定后再发布到 `path/docs/*`
- 将 search 默认索引范围收敛为 `memory.md`、`daily/`、`docs/`
- 将多条 BearBrain skills 与仓库实现对齐并中文化

### Fixed
- 修正 search 路径中对 Ollama host/model 的显式 client 使用
- 修正 skill 结构，移除错误的伪 core skill 目录
- 修正 promote 写入 `## Core Memory` 的目标 section
- 修正手动 compact 场景下的 daily hook 命令匹配与测试覆盖

### Removed
- 移除 `write-core`、`governance-core`、`search-core` 作为实际 skill 的错误实现
