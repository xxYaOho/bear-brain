# Changelog

## [Unreleased]

### Added
- 初始化本地 Bear-Brain 原型仓库结构
- 添加 `#memory` / `#memory/daily` 基础数据模型与解析逻辑
- 添加本地 SQLite memory store 与 `sqlite-vec` 接入骨架
- 添加 `bootstrap`、`promote-yesterday`、`search`、`publish-doc` CLI 路径
- 添加第一阶段 docs 骨架与 BearBrain skill 源文件

### Changed
- 将向量维度从“实现时确认”收敛为固定 `512` 并运行时校验
- 将计划文档边界明确为：草稿先留 Bear，稳定后再发布到 `path/docs/*`

### Fixed
- 修正 search 路径中对 Ollama host/model 的显式 client 使用
- 修正 skill 结构，移除错误的伪 core skill 目录

### Removed
- 移除 `write-core`、`governance-core`、`search-core` 作为实际 skill 的错误实现
