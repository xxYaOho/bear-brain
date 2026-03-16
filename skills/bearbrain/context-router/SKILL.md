---
name: bearbrain/context-router
description: 当需要决定 Bear-Brain 搜索顺序、搜索范围和搜索模式切换时使用，特别适合 memory-first 路由和 repo/workstream 感知的文档访问。
---

# Context Router

## 概述

使用本 skill 来决定"这次该查什么、按什么顺序查"。

这是上下文路由器。不要直接执行搜索，执行交给 `bearbrain/search`。

## 默认搜索顺序

1. `#memory`（优先）
2. `#memory/daily`（不足时补充）
3. `path/docs/*`（仅在明确 repo / workstream 上下文时）

## 切换信号

| 信号                                | 切换到       |
| ----------------------------------- | ------------ |
| 显式 note id / 内链                 | `note_refs`  |
| 明确 repo / workstream 且需项目真相 | `docs_scope` |
| 多标签过滤                          | `tags_and`   |
| 需要交叉验证                        | `hybrid`     |

## 检索模式

- `memory_db`：本地 Vector DB 查询
- `note_refs`：显式笔记引用
- `docs_scope`：项目文档范围
- `tags_and`：多标签 AND 搜索
- `hybrid`：混合模式
