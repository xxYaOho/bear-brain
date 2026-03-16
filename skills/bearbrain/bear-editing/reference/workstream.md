# Workstream 模板

## 推荐格式

```md
# Workstream: <name>

## Meta Card

|             Meta | Note                                           |
| ---------------: | ---------------------------------------------- |
|             Repo | <primary repo>                                 |
|           Status | idea / active / blocked / shipped / archived   |
|             Goal | <这一轮工作最终目标>                           |
|            Scope | <当前纳入范围>                                 |
|   Target release | <计划版本，可空>                               |
|   Actual release | <实际版本，可空>                               |
| Primary artifact | <主要产出物，可空>                             |
|            Phase | <当前阶段，如 planning/implementation/testing> |

## Related Notes

### Plan

- [[note title]]
  - `NOTE-ID`
  - 计划笔记描述

### 当前有效入口

- [[note title]]
  - `NOTE-ID`
  - 描述

### 当前细则

- [[note title]]
  - `NOTE-ID`
  - 描述

### 历史参考

- [[note title]]
  - `NOTE-ID`
  - 描述

### 已被覆盖的旧入口

- ~~[[note title]]~~
  - `NOTE-ID`
  - 描述

## Notes

- <timestamp>
  - 内容

## Task

- [ ] 待办事项
```

## 字段说明

### Status

- `idea`：构思中
- `active`：进行中
- `blocked`：受阻
- `shipped`：已发布
- `archived`：已归档

### Related Notes 结构

- Plan：计划类笔记
- 当前有效入口：正在使用的有效笔记
- 当前细则：具体的规则、设计文档
- 历史参考：仍有参考价值的旧笔记
- 已被覆盖的旧入口：已被新版本替代的笔记（用删除线）

### Notes 追加规则

- 每次追加以时间戳开头
- 记录：做什么、发现什么、判断是什么
