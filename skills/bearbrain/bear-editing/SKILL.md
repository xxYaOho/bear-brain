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
- Bear 写入一律先查后写：先搜索或打开目标笔记，再决定追加、替换或快照 + 覆写
- 任何时间戳都必须来自真实系统时间或 Bear 当前返回值；禁止猜测、禁止沿用对话时间
- NOTE-ID、Status、release、Related Notes 目标条目都必须来自当前查询结果；不得凭记忆填写 NOTE-ID 或元数据
- 长期规划和治理笔记使用快照 + 覆写
- `#memory/daily` 和运行日志使用追加
- `Related Notes` 使用嵌套列表，不使用表格
- 无效入口用删除线标记，不要直接删除

## 强制写入流程

凡是 Bear 写入，必须按以下顺序执行：

1. 确认目标层；如果路由不明确，先用 `bearbrain/admission`
2. 先搜索或打开目标笔记，拿到当前标题、NOTE-ID、现有 section 和现有字段
3. 获取真实系统时间；若 Bear 返回更权威的当前值，优先使用 Bear 返回值
4. 根据现有结构选择 `bear-add-text`、`bear-replace-text` 或快照 + 覆写
5. 写入后立即运行 `bearbrain/note-lint` 做结构自检

缺少任一步骤，都不应宣称“已记录”或“已更新”。

## 写入前证据清单

执行写入前，至少拿到以下证据：

- 目标 note 的 NOTE-ID 或 Bear 返回的明确匹配结果
- 目标 section 是否存在，如 `## Log`、`## Meta`、`## Related Notes`
- 本次要更新的关键字段当前值，如 Status、Target release、Actual release
- 真实时间来源，用于 daily log、Notes 时间块、Promoted At 等字段

如果证据缺失，停止写入并先补查询；禁止猜测。

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
- 没有先搜索或打开目标笔记，就直接生成 Bear 写入内容
- 用聊天上下文推断时间，而不查询真实系统时间
- 凭记忆补 NOTE-ID、Status、release 或 Related Notes 条目

## 最终检查

完成前确认：

- Bear 标题仍然存在
- 标签仍然正确
- 必需的 section 仍然存在
- `Related Notes` 仍然使用嵌套列表
- 如果是长期主笔记覆写，存在快照
