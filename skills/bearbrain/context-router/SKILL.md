---
name: bearbrain/context-router
description: Use when deciding Bear-Brain search order, search scope, and search mode switching before executing retrieval, especially for memory-first routing and repo/workstream-aware docs access.
---

这是上下文路由器，负责“这次该查什么、按什么顺序查”。

默认顺序：
1. `#memory`
2. `#memory/daily`
3. `path/docs/*`（仅在明确 repo / workstream 时）

切换信号：
- 显式 note id / 内链 -> `note_refs`
- 明确 repo / workstream 且需项目真相 -> `docs_scope`
- 多标签过滤 -> `tags_and`
- 需要交叉验证 -> `hybrid`

不要直接执行搜索，执行交给 `bearbrain/search`。
