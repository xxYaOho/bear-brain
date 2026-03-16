---
name: bearbrain/note-lint
description: 写完或更新任何 Bear-Brain 笔记后使用本 skill 校验结构。当用户说"检查一下这条笔记"、"确认格式对不对"、或 agent 完成写入后自检时，必须触发本 skill。即使用户没有明确说"lint"，只要涉及笔记结构验证，都应使用。
---

# Note Lint

## 概述
`note-lint` 是写后结构校验器。

**负责：** 检查笔记结构是否符合目标层规范
**不负责：** 决定内容去哪一层（那是 `admission` 的职责）；大规模重写正文

## 输出格式

每个问题输出一条记录：

```text
[fail] workstream > Meta: 缺少 Status 字段
  位置: ## Meta Card 表格
  原因: Status 是必填字段，agent 需要它判断当前工作状态
  建议: 在 Meta 表格中补充 Status: active

[warn] workstream > Related Notes: 条目缺少 NOTE-ID
  位置: ## Related Notes > [[bear-brain spec]]
  原因: 没有 ID 时 agent 无法精确定位笔记
  建议: 补充 NOTE-ID，格式为 `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

[pass] workstream > Task: section 存在且格式正确
```

状态说明：
- `pass`：通过
- `warn`：非致命，建议修正
- `fail`：必须修正

## 各笔记类型检查清单

### Workstream

**必须存在（fail if missing）：**
- `## Meta` 或 `## Meta Card` section
- Meta 中包含 `Status` 字段
- Meta 中包含 `Goal` 字段
- `## Related Notes` section
- `## Notes` section

**建议存在（warn if missing）：**
- Meta 中包含 `Repo` 字段
- Meta 中包含 `Scope` 字段
- `## Task` section
- Related Notes 每条包含 NOTE-ID

**格式规则（fail if violated）：**
- Related Notes 使用嵌套列表，不使用表格
- 无效入口使用删除线标记，不直接删除
- 正文中不出现 H1（标题由 Bear 标题字段承载）

---

### `#memory/daily`

**必须存在（fail if missing）：**
- `## Promote Status` section（且在正文最前面）
- `## Summary` section
- `## Log` section

**Promote Status 字段检查（fail if missing）：**
- `Status:` 字段，值为 `pending` / `done-promoted` / `done-none`

**建议存在（warn if missing）：**
- Summary 中包含"今日主线"
- Log 中至少有一条时间块记录

---

### `#memory` 主笔记

**必须存在（fail if missing）：**
- `## Position` 或 `## Core Memory` section
- `## Recall Keys` section

**建议存在（warn if missing）：**
- `## Related Notes` section（当有主题笔记时）
- Recall Keys 中有指向主题笔记的链接

**内容规则（warn if violated）：**
- 主笔记不应包含大段原文摘录（应提炼为规则）
- 主笔记不应包含 daily 日志原文

---

### Memory 主题笔记（`memory/*`）

**必须存在（fail if missing）：**
- `## Summary` 或 `## Position` section
- `## Rules` 或 `## Core` section

**建议存在（warn if missing）：**
- `## Cases` section
- `## Notes` section（边界条件）

---

### `book/*`

**必须存在（fail if missing）：**
- `## Summary` 或描述块
- 正文内容区（`## Content` / `## 摘录` / 正文等）

**建议存在（warn if missing）：**
- `## My Take` 或脚注 (Take) 块

**内容规则（warn if violated）：**
- Take 不应只是复述原文，应有判断或提炼

---

### `docs/*`

**必须存在（fail if missing）：**
- 文档类型标识（SPEC / GUIDE / CHANGELOG / COMPLETIONS / DECISIONS）
- 正文内容

**内容规则（fail if violated）：**
- 不应包含 Bear 内链（`[[...]]` 格式）
- 不应包含 `## Promote Status` 等 Bear-Brain 内部 section

---

## 通用规则（所有类型）

**fail if violated：**
- 正文中出现 H1（`# 标题`）——标题由 Bear 标题字段承载
- 正文中裸写标签（如 `#memory`、`#repo/bear-brain`）

**pass 的例外：**
- 正文中以代码包裹形式提及标签，如 `#memory`、`#memory/daily`

也就是说，代码包裹形式，如 `#memory`，不算正文里的裸标签。

**warn if violated：**
- Related Notes 使用表格而非嵌套列表

## 模板强度说明

| 笔记类型 | 模板强度 |
| --- | --- |
| `workstream` | 强模板（结构固定，字段必填） |
| `#memory/daily` | 强模板（三 section 必须存在） |
| `#memory` 主笔记 | 强模板（Position + Recall Keys 必须存在） |
| `memory/*` 主题笔记 | 中模板（Summary + Rules 必须存在） |
| `book/*` | 中模板（Summary + 正文必须存在，Take 建议） |
| `docs/*` | 弱模板 + 强规则（结构自由，但不能有 Bear 内链） |
| `repo/*` | 弱模板（结构自由，无强制 section） |
