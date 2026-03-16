---
name: bearbrain/workstream
description: "创建或维护 `Workstream: ...` 笔记时使用，包含 Meta、Related Notes、Notes、Task 等 section。"
---

# Workstream

## 概述

使用本 skill 来创建或维护工作容器主笔记。

`workstream` 只管理"一轮工作"的主笔记，不承载活文档正文。它的作用是：

- 描述一轮具体工作
- 关联本轮涉及的笔记
- 让 agent 通过一条入口笔记理解当前工作状态

## 使用场景

以下情况使用本 skill：

- 需要开启一轮新的工作时
- 需要更新 workstream 的状态（idea → active → shipped 等）
- 需要把相关笔记挂到 workstream 的 Related Notes
- 需要记录范围变化、卡点、或下一步计划
- 需要追踪版本发布信息

不要用本 skill 来写 PRD、QA、FT、FB 正文，那些是 repo 活文档的职责。

## 职责

### 维护 Meta 信息

使用表格格式，包含以下字段：

|                 字段 | 说明                                                         |
| -------------------: | ------------------------------------------------------------ |
|             **Repo** | 当前 workstream 的主 repo，一个 workstream 只应有一个主 repo |
|        **Workspace** | 工作空间路径，如 `~/bear-brain`                              |
|           **Status** | 状态值建议 `idea \ active \ blocked \ shipped \ archived`    |
|             **Goal** | 这一轮工作最终想达成什么，必须简洁明确                       |
|            **Scope** | 当前纳入的需求/问题范围，范围变化时只更新这里                |
|   **Target release** | 计划版本（可空）                                             |
|   **Actual release** | 实际版本（可空，用于跳版、补丁版、降版等情况）               |
| **Primary artifact** | 主要产出物                                                   |
|            **Phase** | 当前阶段，如 `development`                                   |

### 维护 Related Notes

每条关联笔记建议同时保留：

- Bear 内置链接 `[[<note title>]]`
  - 笔记 ID `id: <bear note id>`
  - 简单描述

原因：链接方便在 Bear 内跳转，ID 方便 agent 精确定位，简述方便 agent 快速判断要不要读该笔记。

### 维护 Notes

记录自然语言说明：

- 为什么会开启这轮 workstream
- 当前判断
- 范围变化原因
- 与版本计划的偏差
- 当前卡点与下一步

## 不负责

- 不写 PRD、QA、FT、FB 正文
- 不直接承担 memory 提炼
- 不发布到 `path/docs/*`
- 不作为 tag 容器存在（是"一条主笔记"，不是 tag 聚合）

## 推荐格式

```markdown
# Workstream: <name>

## Meta Card

|             Mate | Note                                         |
| ---------------: | -------------------------------------------- |
|             Repo | <primary repo>                               |
|        Workspace | `<workspace path>`                           |
|           Status | idea / active / blocked / shipped / archived |
|             Goal | <这一轮工作最终目标>                         |
|            Scope | <当前纳入范围>                               |
|   Target release | <计划版本，可空>                             |
|   Actual release | <实际版本，可空>                             |
| Primary artifact | <主要产出物>                                 |
|            Phase | <阶段>                                       |

## Related Notes

- [[<note title>]]

  - `NOTE-ID`
  - 简单描述

- ~~[[<旧笔记标题>]]~~
  - `NOTE-ID`
  - 已被新入口覆盖 / 历史参考

## Notes

这里写自然语言说明，例如：

- 为什么会开启这轮 workstream
- 当前判断
- 范围变化原因
- 与版本计划的偏差
- 当前卡点与下一步
```

## 工作流程

1. 确认是否需要新的 workstream（还是复用现有的）
2. 创建或更新 workstream 主笔记
3. 填写/更新 Meta 信息
4. 添加相关笔记到 Related Notes
5. 在 Notes 中记录当前状态和下一步

## 常见错误

- 把两个目标塞进同一个 workstream
- 用 workstream 来聚合同类任务（应该用 Related Notes 关联）
- 把活文档正文写在 workstream 里（应该写在 repo 里）
- Related Notes 只写链接不写 ID 和描述
- 范围变化时创建新的 workstream 而不是更新 Scope

## 最终检查

完成前确认：

- Meta 各字段已正确填写
- Related Notes 使用嵌套列表格式
- Related Notes 包含链接 + ID + 描述
- 状态值是有效建议值之一
- Notes 包含当前阶段的关键信息
- 没有把活文档正文写在 workstream 里
