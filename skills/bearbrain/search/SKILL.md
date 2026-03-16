---
name: bearbrain/search
description: Use when executing Bear-Brain retrieval across memory, daily-memory, docs, explicit note references, or local vector search, after the search target and order are already decided.
---

这是统一搜索执行器，负责“怎么查”。

支持模式：
- `memory_db`
- `note_refs`
- `docs_scope`
- `tags_and`
- `hybrid`

要求：
- 统一输出结果结构
- 默认服务 `#memory` / `#memory/daily` / `path/docs/*`
- Bear `repo/*` 不走默认向量索引，只做显式读取
