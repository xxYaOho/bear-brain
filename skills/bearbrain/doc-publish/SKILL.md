---
name: bearbrain/doc-publish
description: 将 Bear-Brain 活文档发布为稳定文档时使用。当用户说"这个可以定稿了"、"发布一下"、"写进文档"、"发布到 docs"、或阶段明确收束时，必须使用本 skill。即使用户没有说"doc-publish"，只要涉及从 Bear 发布到 docs/*，都应触发。
---

# Doc Publish

## 概述
使用本 skill 将 Bear 活文档发布为 `docs/*` 稳定文档。

**负责：** 发布稳定快照到 `docs/*`
**不负责：** 决定内容是否已稳定（那是用户判断）；写活文档正文

## 发布前检查

以下条件**全部满足**才能发布：

- [ ] 结构完整，不是残缺草稿
- [ ] 已不再是讨论稿（用户确认或阶段明确收束）
- [ ] 已确定目标类型（SPEC / GUIDE / CHANGELOG / COMPLETIONS / DECISIONS）
- [ ] 用户明确要求发布，或阶段已收束

如果条件不满足，告知用户哪个条件未达到，不要强行发布。

## 目标类型与路径

| 类型 | 路径 | 说明 |
| --- | --- | --- |
| `SPEC` | `docs/product/SPEC.md` | 系统规格定义 |
| `GUIDE` | `docs/guide/GUIDE.md` | 使用指南 |
| `CHANGELOG` | `docs/CHANGELOG.md` | 版本变更记录 |
| `COMPLETIONS` | `docs/COMPLETIONS.md` | 阶段完成总结 |
| `DECISIONS` | `docs/DECISIONS.md` | 关键决策记录 |

如果同类型有多个文档（如多个 GUIDE），使用描述性文件名：
- `docs/guide/GUIDE-search.md`
- `docs/guide/GUIDE-memory.md`

## 发布流程

### Step 1：确认目标类型和路径
根据内容判断类型，确认目标路径。如果不确定，询问用户。

### Step 2：清理 Bear 内部标记
发布内容中移除：
- Bear 内链（`[[笔记标题]]` 格式）
- `## Promote Status` 等 Bear-Brain 内部 section
- Bear tag（`#repo/bear-brain` 等）

保留：
- 正文结构和内容
- 代码块、表格、列表

### Step 3：写入目标路径
使用 `finder-write-file` 写入目标路径。

如果目标文件已存在：
- **CHANGELOG / COMPLETIONS / DECISIONS**：追加新内容，不覆盖历史
- **SPEC / GUIDE**：覆盖（这是稳定快照，旧版本由 git 保留）

### Step 4：更新来源笔记
在 Bear 来源笔记的 `## Notes` 中追加发布记录：
```text
- YYYY-MM-DD HH:MM 发布到 docs/[路径]
```

### Step 5：更新 workstream
如果有关联的 workstream，在其 `## Related Notes` 中记录发布产物。

## 规则

- 发布的是稳定快照，不是临时复制
- 不在发布文档中保留 Bear 源笔记回链（来源追溯通过 workstream 的 Related Notes 维护）
- plan 草稿先留 Bear，不直接发布到 `docs/*`
- CHANGELOG 和 COMPLETIONS 只追加，不覆盖历史记录

## 常见错误

- 把活跃草稿直接发布（应等阶段收束）
- 发布后没有更新来源笔记的 Notes
- CHANGELOG 覆盖了历史记录
- 发布文档中保留了 Bear 内链（会在 docs 中显示为无效链接）
