---
name: bearbrain/search-core
description: Core retrieval workflow for Bear-Brain. Use when deciding what to search first, switching between memory-first retrieval and docs-scoped retrieval, or executing unified search across memory, docs, explicit note references, and local vector search.
---

Search is split into two layers:
- search: executes retrieval
- context-router: decides search order

Default order is memory-first, then daily-memory, then docs when repo or workstream context is explicit.
