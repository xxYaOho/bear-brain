---
name: bearbrain/search
description: 当需要在 memory、daily-memory、docs、显式笔记引用或本地向量搜索中执行 Bear-Brain 检索时使用，且搜索目标和顺序已确定。
---

# Search

## 概述
使用本 skill 来执行搜索。

这是统一搜索执行器，负责"怎么查"。

## 支持模式
| 模式 | 说明 |
| --- | --- |
| `memory_db` | 本地 Vector DB 查询 |
| `note_refs` | 显式笔记引用 |
| `docs_scope` | 项目文档范围 |
| `tags_and` | 多标签 AND 搜索 |
| `hybrid` | 混合模式 |

## 默认索引范围
- `#memory`
- `#memory/daily`
- `path/docs/*`

## 规则
- Bear `repo/*` 不走默认向量索引，只做显式读取
- 统一输出结果结构
- 默认服务 `#memory` / `#memory/daily` / `path/docs/*`
