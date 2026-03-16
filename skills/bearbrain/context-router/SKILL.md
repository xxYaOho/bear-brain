---
name: bearbrain/context-router
description: 当 agent 需要查找任何 Bear-Brain 信息时，先用本 skill 决定查什么、按什么顺序查。当用户或 agent 发起任何检索请求时，本 skill 是搜索的前置路由层。通常在调用 bearbrain/search 之前使用。如果已知 note ID，可以跳过本 skill 直接用 note_refs 模式。
---

# Context Router

## 概述

使用本 skill 来决定"这次该查什么、按什么顺序查"。

这是上下文路由器。不要直接执行搜索，执行交给 `bearbrain/search`。

## 默认搜索顺序

1. `#memory`（优先，经验主轴）
2. `#memory/daily`（不足时补充近期过程）
3. `docs/*`（仅在明确 repo / workstream 上下文时）

## 切换信号

| 信号 | 识别方式 | 切换到 |
| --- | --- | --- |
| 显式 note ID | 用户提供了 UUID 格式的 ID | `note_refs` |
| Bear 内链 | 用户提供了 `[[笔记标题]]` 格式 | `note_refs` |
| 明确 repo / workstream 且需项目真相 | 用户提到了具体项目名或 workstream | `docs_scope` |
| 多标签过滤 | 用户要求按多个 tag 交叉查找 | `tags_and` |
| 需要交叉验证 | 用户要求从多个来源对比 | `hybrid` |

## 路由决策流程

```
1. 有显式 note ID 或内链？
   → 是：直接用 note_refs，跳过其他步骤
   → 否：继续

2. 有明确 repo / workstream 上下文？
   → 是：memory_db + docs_scope（hybrid）
   → 否：继续

3. 需要多标签交叉过滤？
   → 是：tags_and
   → 否：继续

4. 默认：memory_db（先查 #memory，不足时补 #memory/daily）
```

## Fallback 逻辑

信号不明确时，默认走 `memory_db`，不要求用户澄清搜索模式。如果结果不足，自动补充 `#memory/daily`，再不足时询问用户是否需要扩展到 `docs_scope`。

## 检索模式

- `memory_db`：本地 Vector DB 查询（语义检索）
- `note_refs`：显式笔记引用（已知 ID 或内链）
- `docs_scope`：项目文档范围（`docs/*`）
- `tags_and`：多标签 AND 搜索
- `hybrid`：混合模式

## 与 search 的协作边界

- **context-router**：决定用什么模式、按什么顺序
- **bearbrain/search**：执行具体的搜索操作

已知 note ID 时可以跳过 context-router，直接调用 `bearbrain/search` 的 `note_refs` 模式。
