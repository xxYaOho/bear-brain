# Workstream 模板

## 结构

```md
# Workstream: <name>

## Meta Card

|           字段 | 信息                                               |
| -------------: | -------------------------------------------------- |
|           Repo | <primary repo>                                     |
|     Main Space | `~/path`                                           |
|         Status | idea / active / blocked / shipped / archived       |
|           Goal | <这一轮工作最终目标>                               |
|          Scope | <当前纳入范围>                                     |
| Target release | <计划版本，可空>                                   |
| Actual release | <实际版本，可空>                                   |
|          Phase | <当前阶段，如 planning / implementation / testing> |

## Related Notes

[[note-title]]

- `NOTE-ID`
- 摘要描述

~~[[note-title]]~~

- `NOTE-ID`
- 摘要描述
- 已过时 / 被替代原因

## Work Notes

### <ISO-8601>

<过程记录：做了什么、发现什么、当前判断。由 Partner 维护。>

## Team

### <name>
```

Name:
Ability:
Task:

```

#### Checkpoint — <ISO-8601>

**完成**：<这个功能单元做了什么，一句话>

**对齐检查**：
- Task 要求：<原始 Task 的核心要求>
- 实际产出：<实际做了什么>
- 偏差：<有 / 无，有则说明>

**遗留**：<未完成或刻意跳过的，无则填「无」>
**下一步**：<下一个功能单元是什么>

## Summary

### Tasks

- [x] 已完成的任务
- [ ] 进行中或待做的任务

### Next

<当前阶段结束后的下一步工作方向，由 Partner 在每次验收通过后更新>
```

---

## 字段说明

### Meta Card

- `Status` 值：`idea` 构思中 / `active` 进行中 / `blocked` 受阻 / `shipped` 已发布 / `archived` 已归档
- `Phase` 随工作推进由 Partner 更新

### Related Notes

- 每条一个 `[[note-title]]`，下方缩进 `NOTE-ID` 和摘要
- 过时或被替代的条目用 `~~[[note-title]]~~` 标记，保留不删除
- 由 User 负责添加、删除、编辑；Partner 不得擅自修改

### Work Notes

- 由 Partner 在 workstream 期间追加，记录过程、发现、判断
- 每条以 ISO-8601 时间戳作为 H3 标题
- 目的是方便回溯，不是流水账——只记有判断价值的内容

### Team

- Partner 在招募阶段写入每个成员的 `Ability / Task`
- 成员只能维护自己 section 下的 `Checkpoint`，不得修改其他成员 section
- 每个成员在独立的 git worktree 中完成任务

### Checkpoint

- 由成员在每个可独立验证的功能单元完成后追加
- 目的是暴露漂移，不是记录流水账
- `对齐检查` 必须显式对照原始 Task，偏差字段不可省略（无偏差填「无」）

### Summary

- `Tasks`：workstream 全部任务清单，`- [x]` 已完成，`- [ ]` 待做或进行中，由 Partner 维护
- `Next`：每次验收通过后由 Partner 更新，记录下一步方向
