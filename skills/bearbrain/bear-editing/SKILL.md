---
name: bear-editing
description: 编辑任何 Bear 笔记时必须使用本 skill。当用户要求创建、更新、追加、替换、清理任何 Bear 笔记内容时，本 skill 提供安全编辑协议。即使用户没有明确提到"结构"或"格式"，只要涉及 Bear 笔记写入操作，都应触发本 skill。包括：更新 workstream、写入 memory、追加日志、修改 Meta / Task / Related Notes 等所有场景。
---

# Bear 笔记编辑规范

## 概述

使用本 skill 来决定**如何安全地**编辑一条 Bear 笔记。

本 skill 不决定**内容应该放在哪里**。如果路由不明确，先运行 `admission`。

> 工具参数从 MCP schema 获取，本 skill 不维护参数列表。

---

## 工具职责

| 工具 | 职责 |
| --- | --- |
| `bear-search-notes` | 按关键词 / tag / 日期搜索，返回标题 + ID 列表 |
| `bear-open-note` | 按 ID 读取笔记全文（含 OCR 附件内容） |
| `bear-create-note` | 新建笔记，title 自动渲染为 H1 |
| `bear-add-text` | 在笔记或指定 section 内插入文本，不覆盖现有内容 |
| `bear-replace-text` | 覆写指定 section 或整篇正文（破坏性操作，见下方限制） |
| `bear-add-file` | 附加文件（base64 编码）到已有笔记 |
| `bear-add-tag` | 为笔记添加一个或多个 tag |
| `bear-list-tags` | 列出所有 tag 及层级结构 |
| `bear-find-untagged-notes` | 找出没有 tag 的笔记 |
| `bear-archive-note` | 归档笔记（不删除） |
| `bear-rename-tag` | 重命名 tag（影响所有含该 tag 的笔记） |
| `bear-delete-tag` | 删除 tag（笔记本身不受影响） |

---

## 工具选择原则

| 场景 | 工具 |
| --- | --- |
| 追加内容到 section 末尾 | `bear-add-text`，指定 header，插入位置为末尾 |
| 插入内容到 section 开头 | `bear-add-text`，指定 header，插入位置为开头 |
| 替换某个 section 的全部内容 | `bear-replace-text`，scope=section（见覆写限制） |
| 覆写整篇正文 | `bear-replace-text`，scope=full-note-body（需用户授权） |
| 新建笔记 | `bear-create-note` |

---

## 覆写限制

### section 替换

`bear-replace-text` 的 section 模式默认允许，用于刷新单个 section（如 Summary、Meta Card）。

**但如果替换范围实质上等同于全文覆写**——即笔记的绝大多数 section 都将被替换——必须停下来，向用户说明情况并请求授权，再决定是否继续。判断由 agent 自行评估，不依赖硬性数量规则。

### 全文覆写

`scope=full-note-body` **默认禁止**。执行前必须：

1. 向用户说明将覆写整篇正文
2. 获得明确授权
3. 先创建快照（见下方快照流程）

---

## 强制写入流程

凡是 Bear 写入，必须按以下顺序执行：

1. **确认路由**：目标笔记类型不明确时，先运行 `admission`
2. **先查后写**：`bear-search-notes` 或 `bear-open-note` 拿到 NOTE-ID 和当前内容
3. **获取真实时间**：时间戳必须来自系统时间，禁止猜测或沿用对话时间
4. **选择操作**：按上方选择原则选择工具
5. **写入后自检**：运行 `bearbrain/note-lint` 做结构验证

缺少任一步骤，不得宣称「已记录」或「已更新」。

---

## 写入前证据清单

执行写入前，至少拿到：

- 目标笔记的 NOTE-ID（来自搜索或打开结果，不得凭记忆）
- 目标 header 是否存在（`bear-add-text` 和 `bear-replace-text` scope=section 场景）
- 真实时间来源（用于时间戳字段）

---

## 快照流程

全文覆写前，必须先创建快照：

1. `bear-open-note` 读取原笔记全文
2. `bear-create-note` 新建快照笔记
   - 标题：`snapshot [原标题] (原版本)`
   - text：原笔记全文
3. 获得用户授权后，执行 `bear-replace-text` scope=full-note-body

---

## 陷阱

- **header 静默失败**：`bear-add-text` 指定 header 时，若 header 不存在，内容会追加到笔记末尾且不报错。写入前必须先 `bear-open-note` 确认 header 存在。
- **双 H1**：`bear-create-note` 的 title 自动渲染为 H1，text 中禁止再写 `# 标题`。
- **tag 被解析**：正文中若需提及 tag 名称作为说明文字，用 inline code 包裹（`` `#memory` ``），否则 Bear 会将其解析为真实 tag。

---

## 正文中提及标签的规则

- ❌ 禁止裸写：`#memory`、`#memory/daily`
- ✅ 允许 inline code：`` `#memory` ``、`` `#memory/daily` ``

---

## Related Notes 格式

```md
[[笔记标题]]

- `NOTE-ID`
- 描述

~~[[旧笔记标题]]~~

- `NOTE-ID`
- 描述
- 已过时 / 被替代原因
```

- 使用 `[[]]` 链接，不使用表格
- 过时条目用删除线标记，保留不删除

---

## 各笔记类型规范

### Workstream

Section：`## Meta Card` / `## Related Notes` / `## Work Notes` / `## Team` / `## Summary`

- **新建**：必须读 `reference/workstream.md`
- **Meta Card 更新**：`bear-replace-text` scope=section，header=`Meta Card`
- **Related Notes**：由 User 维护，Partner 不得擅自修改
- **Work Notes 追加**：`bear-add-text`，header=`Work Notes`，插入位置末尾
- **Team / Checkpoint 追加**：`bear-add-text`，header=成员名，插入位置末尾
- **Summary 更新**：`bear-replace-text` scope=section，header=`Summary`

### Daily Memory

Section：`## Promote Status` / `## Summary` / `## Log`

- **新建**：必须读 `reference/memory-daily.md`
- **Log 新增记录**：`bear-add-text`，header=`Log`，插入位置**开头**（倒叙）
- **Summary 更新**：`bear-replace-text` scope=section，header=`Summary`
- **Promote Status 更新**：`bear-replace-text` scope=section，header=`Promote Status`

### Memory

Section：`## Position` / `## Core Memory` / `## Recall Keys` / `## Related Notes`

- **新建**：必须读 `reference/memory.md`
- **Core Memory 新条目**：`bear-add-text`，header=`Core Memory`，插入位置开头
- **新建子主题后**：同步更新主文件 `## Recall Keys` 和 `## Related Notes`

### Book

Section：`## Summary` / `## Content` / `## My Take`

- **新建**：必须读 `reference/book.md`

---

## 常见错误

- 在 `text` 中写 `# 标题`（双 H1）
- 在正文中裸写 `#tag`（被 Bear 解析为真实 tag）
- 凭记忆填写 NOTE-ID、时间戳
- `bear-add-text` 前未确认 header 是否存在（header 不存在时静默追加到末尾）
- 替换范围实质等同全文覆写，却未请求用户授权
- 全文覆写前未创建快照
- Daily Memory Log 用末尾追加而非开头插入（破坏倒叙顺序）
