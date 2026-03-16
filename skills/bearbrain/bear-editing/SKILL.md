---
name: bear-editing
description: 编辑任何 Bear-Brain 笔记时必须使用本 skill。当用户要求创建、更新、追加、替换、清理任何 Bear 笔记内容时，本 skill 提供安全编辑协议。即使用户没有明确提到"结构"或"格式"，只要涉及 Bear 笔记写入操作，都应触发本 skill。包括：更新 workstream、写入 memory、追加日志、修改 Meta/Task/Related Notes 等所有场景。
---

# Bear 笔记编辑规范

## 概述

使用本 skill 来决定**如何安全地**编辑一条 Bear-Brain 笔记。

本 skill 不决定**内容应该放在哪里**。如果路由不明确，先运行 `bearbrain/admission`。

## 使用场景

以下情况使用本 skill：

- Bear 笔记已有稳定的 section 结构，需要更新但不破坏结构
- 长期主笔记需要快照 + 覆写，而不是无限追加
- 需要添加或清理 `Related Notes`
- 需要更新 `Meta`、`Task`、`Notes`、`Promote Status` 等 section

不要用本 skill 来决定内容路由，也不要在未确定笔记类型前就重写大量正文。

## 核心规则

- 使用 Bear 标题字段作为笔记标题；不要在正文中重复 H1
- 使用 Bear 原生标签；不要在正文中裸写 `#tag`
- 如正文必须提及标签，统一用代码包裹形式，如 `#memory`、`#memory/daily`、`#repo/bear-brain`
- 长期规划和治理笔记使用快照 + 覆写
- `#memory/daily` 和运行日志使用追加
- `Related Notes` 使用嵌套列表，不使用表格
- 无效入口用删除线标记，不要直接删除

## 正文中提及标签的规则

- **禁止**裸写：`#memory`、`#memory/daily`、`#repo/bear-brain`
- **允许**代码包裹：`#memory`、`#memory/daily`、`#repo/bear-brain`
- 不默认把标签改写成 `tags/...`；只有在明确讨论逻辑层名而非 Bear tag 时才使用普通文字描述

## 编辑决策表

| 场景                                  | 操作            |
| ------------------------------------- | --------------- |
| 长期主笔记需要结构性刷新              | 快照 + 覆写     |
| `#memory/daily` 日志增长              | 追加            |
| `Notes` 增量状态记录                  | 追加            |
| `Meta`、`Task`、`Promote Status` 更新 | Section 替换    |
| 没有稳定的锚点                        | 优先快照 + 覆写 |

## 快照操作步骤

覆写长期主笔记前，必须先创建快照：

1. 读取原笔记全文
2. 用 `bear-create-note` 新建快照笔记
   - 标题格式：`[原标题] snapshot YYYY-MM-DD`
   - 正文：复制原笔记全文
   - Tag：原笔记相同的 tag + `snapshot`
3. 在原笔记 `Related Notes` 中记录快照笔记 ID
4. 然后对原笔记执行覆写

## Related Notes 格式

```md
- [[笔记标题]]

  - `NOTE-ID`
  - 描述

- ~~[[旧笔记标题]]~~
  - `NOTE-ID`
  - 已被新入口覆盖 / 历史参考
```

## 锚点定位顺序

编辑前，按以下顺序定位锚点：

1. Section 标题，如 `## Related Notes`
2. 稳定字段行，如 `- Status:`
3. 列表结构或表格头
4. 分隔块

如果以上都不稳定，停止使用 section 级编辑，改为快照 + 覆写。

## 各笔记类型规范

### Workstream

建议维护以下 section：

- `## Meta`
- `## Related Notes`
- `## Notes`
- `## Task`

**何时读模板**：新建 workstream 笔记时必须读；更新已有笔记时可跳过，除非结构不确定。
**完整模板参考**：[reference/workstream.md](reference/workstream.md)

### Daily memory

始终保留：

- `## Promote Status`
- `## Summary`
- `## Log`

**何时读模板**：新建 daily 笔记时必须读。
**完整模板参考**：[reference/daily-memory.md](reference/daily-memory.md)

### Memory

维护：

- `## Position`
- `## Core Memory` / `## Core`
- `## Recall Keys`
- `## Related Notes`

**何时读模板**：新建 memory 笔记或主题笔记时必须读。
**完整模板参考**：[reference/memory.md](reference/memory.md)

### Book

使用通用骨架：

- `## Summary`
- `## Content`
- `## My Take`

**何时读模板**：新建 book 笔记时必须读。
**完整模板参考**：[reference/book.md](reference/book.md)

### 计划与治理笔记

试迭代阶段，Bear 是主要草稿面。Repo 文件只持有稳定快照。

## 常见错误

- 把标签写在正文中
- 重新引入 `Related Notes` 表格
- 长期主笔记应该覆写时却追加
- 覆写前没有先创建快照
- 没有稳定锚点时强制 section 替换

## 最终检查

完成前确认：

- Bear 标题仍然存在
- 标签仍然正确
- 必需的 section 仍然存在
- `Related Notes` 仍然使用嵌套列表
- 如果是长期主笔记覆写，存在快照
