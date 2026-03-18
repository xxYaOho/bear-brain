---
name: bear-editing
description: 编辑任何 Bear 笔记时必须使用本 skill。当用户要求创建、更新、追加、替换、清理任何 Bear 笔记内容时，本 skill 提供安全编辑协议。即使用户没有明确提到"结构"或"格式"，只要涉及 Bear 笔记写入操作，都应触发本 skill。包括：更新 workstream、写入 memory、追加日志、修改 Meta / Task / Related Notes 等所有场景。
---

# Bear 笔记编辑规范

## 概述

使用本 skill 来决定**如何安全地**编辑一条 Bear 笔记。

本 skill 不决定**内容应该放在哪里**。如果路由不明确，先运行 `admission`。

---

## MCP 工具速查

### bear-search-notes — 搜索

按关键词或 tag 搜索笔记，返回标题 + ID 列表。

```
bear-search-notes
  term:  <关键词>         # 可选
  tag:   <完整 tag 路径>  # 可选，如 memory/daily
  limit: 1000
```

> 写入前必须先搜索或打开目标笔记，拿到 NOTE-ID，禁止凭记忆填写。

---

### bear-open-note — 读取

按 ID 读取笔记全文，包含标题、正文、tag。

```
bear-open-note
  id: <NOTE-ID>
```

> 优先用 ID 定位，避免笔记改名导致找不到目标。

---

### bear-create-note — 创建

```
bear-create-note
  title: <笔记标题>   # 渲染为 H1，禁止在 text 中重复写 # 标题
  text:  <正文内容>   # 从正文第一行开始，不含 H1
  tags:  <tag1,tag2>  # Bear 原生标签，逗号分隔；禁止在 text 中裸写 #tag
```

**注意：**

- `title` 自动渲染为 H1，`text` 中禁止出现 `# <标题>`，否则产生双 H1
- 正文中若需提及 tag 名称作为说明文字，用 inline code 包裹：`` `#memory` ``，避免被 Bear 解析为真实 tag

---

### bear-add-text — 追加 / 插入 / 替换 section

Bear 官方 `/add-text` action 的封装，支持四种 mode。

```
bear-add-text
  id:       <NOTE-ID>
  text:     <内容>
  header:   <section 标题文字，不含 # 符号>  # 可选
  mode:     append | prepend | replace | replace_all
  new_line: yes | no                          # 可选，mode=append 时生效
```

**四种 mode：**

| mode          | 行为                                                    |
| ------------- | ------------------------------------------------------- |
| `append`      | 在 header 所在 section 末尾追加                         |
| `prepend`     | 在 header 所在 section 开头插入                         |
| `replace`     | 替换 header 所在 section 的内容，**保留 header 行本身** |
| `replace_all` | 替换整篇笔记正文（含标题），慎用                        |

**陷阱：**

- `header` 找不到时，内容追加到笔记末尾，**不报错**——写入前必须先 `bear-open-note` 确认 header 存在
- `mode` 必须显式指定，不可依赖默认值

---

### bear-replace-text — 精确文字替换

替换笔记中指定的文字片段，适合修改单个字段值而不影响周围内容。

```
bear-replace-text
  id:          <NOTE-ID>
  old_text:    <要替换的原始文字>  # 必须与笔记中完全一致
  replacement: <新内容>
```

**行为：**

- 替换第一个匹配的 `old_text`
- `old_text` 不存在时**静默失败**——写入前必须先 `bear-open-note` 确认原文

---

### bear-add-text vs bear-replace-text 选择原则

| 场景                                            | 工具                                    |
| ----------------------------------------------- | --------------------------------------- |
| 替换整个 section 内容（如刷新 Summary、Meta）   | `bear-add-text` mode=replace            |
| 修改 section 内某个具体字段值（如改 Status 值） | `bear-replace-text`                     |
| 追加新内容到 section 末尾                       | `bear-add-text` mode=append             |
| 置顶插入新内容                                  | `bear-add-text` mode=prepend            |
| 覆写整篇笔记                                    | 快照 + `bear-add-text` mode=replace_all |

---

## 强制写入流程

凡是 Bear 写入，必须按以下顺序执行：

1. **确认路由**：目标笔记类型不明确时，先运行 `admission`
2. **先查后写**：`bear-search-notes` 或 `bear-open-note` 拿到 NOTE-ID 和当前内容
3. **获取真实时间**：时间戳必须来自系统时间，禁止猜测或沿用对话时间
4. **选择操作**：按上方选择原则选择工具和 mode
5. **写入后自检**：运行 `bearbrain/note-lint` 做结构验证

缺少任一步骤，不得宣称「已记录」或「已更新」。

---

## 写入前证据清单

执行写入前，至少拿到：

- 目标笔记的 NOTE-ID（来自搜索或打开结果，不得凭记忆）
- 目标 header 是否存在（`bear-add-text` 场景）
- `bear-replace-text` 场景：old_text 的完整原文（来自 `bear-open-note`）
- 真实时间来源（用于时间戳字段）

---

## 快照 + 覆写

覆写长期主笔记前，必须先创建快照：

1. `bear-open-note` 读取原笔记全文
2. `bear-create-note` 新建快照笔记
   - 标题：`snapshot [原标题] (原版本)`
   - text：原笔记全文
3. `bear-add-text` mode=replace_all 覆写原笔记正文

---

## 正文中提及标签的规则

- ❌ 禁止裸写："#memory"、"#memory/daily"
- ✅ 允许 inline code："`#memory`"、"`#memory/daily`"

---

## Related Notes 格式

```md
[[笔记标题]]

- `NOTE-ID`
- 描述

~~[[旧笔记标题]]~~

- `NOTE-ID`
- - 描述
- 已过时 / 被替代原因
```

- 使用 `[[]]` 链接，不使用表格
- 过时条目用删除线标记，保留不删除

---

## 各笔记类型规范

### Workstream

Section：`## Meta Card` / `## Related Notes` / `## Work Notes` / `## Team` / `## Summary`

- **新建**：必须读 `reference/workstream.md`
- **Meta Card 单字段更新**：`bear-replace-text`，old_text 取字段当前值
- **Meta Card 整体刷新**：`bear-add-text` mode=replace，header=`Meta Card`
- **Related Notes**：由 User 维护，Partner 不得擅自修改
- **Work Notes 追加**：`bear-add-text` mode=append，header=`Work Notes`
- **Team / Checkpoint 追加**：`bear-add-text` mode=append，header=成员名
- **Summary 更新**：`bear-add-text` mode=replace，header=`Summary`

### Daily Memory

Section：`## Promote Status` / `## Summary` / `## Log`

- **新建**：必须读 `reference/daily-memory.md`
- **Log 追加**：`bear-add-text` mode=append，header=`Log`
- **Promote Status 更新**：`bear-add-text` mode=replace，header=`Promote Status`

### Memory

Section：`## Position` / `## Core Memory` / `## Recall Keys` / `## Related Notes`

- **新建**：必须读 `reference/memory.md`
- **新条目置顶**：`bear-add-text` mode=prepend，header=`Core Memory`

### Book

Section：`## Summary` / `## Content` / `## My Take`

- **新建**：必须读 `reference/book.md`

---

## 常见错误

- 在 `text` 中写 `# 标题`（双 H1）
- 在正文中裸写 "#tag"（被 Bear 解析为真实 tag）
- 凭记忆填写 NOTE-ID、Status、时间戳
- `bear-add-text` 前未确认 header 是否存在（header 不存在时静默追加到末尾）
- `bear-replace-text` 前未 `bear-open-note` 确认 old_text 原文
- 长期主笔记应覆写时却追加
- 覆写前未创建快照
