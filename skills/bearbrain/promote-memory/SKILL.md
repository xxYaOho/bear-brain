---
name: bearbrain/promote-memory
description: 当需要将昨日的 #memory/daily 提纯到长期 Bear-Brain memory 时使用，包括可复用规则提取、目标选择、promote-status 更新。
---

# Promote Memory

## 概述

使用本 skill 将 `#memory/daily` 提纯到 `#memory`。

本 skill 是自动执行的提纯动作，但状态对用户可见。目标是做到：昨天先结账，今天再开工。

## 与 memory 的关系

- `bearbrain/memory`：面向长期经验层本身的维护
- `bearbrain/promote-memory`：负责从 `#memory/daily` 升级进 `#memory`

## 处理范围

- 默认只处理"昨天"的一篇 daily
- 不按 workstream 切分
- 因为 `#memory` 是全局经验层，不是 workstream 经验层

## 使用场景

以下情况使用本 skill：

- 每天工作开始前，检查昨日 daily 是否已 promote
- 昨日 daily 尚未处理，需要执行 promote
- 需要决定哪些内容值得升级

## 流程步骤

### 1. 查询昨日 daily

使用 Bear 搜索查询昨日的 daily：

```
#memory/daily 昨天日期
```

例如：`#memory/daily 2026-03-15`

### 2. 检查 Promote Status

读取昨日 daily，检查是否已有 Promote Status：

- 如果是 `pending`，需要执行 promote
- 如果是 `done-promoted` 或 `done-none`，跳过

### 3. 识别可提炼内容

从昨日 daily 的 Log 或 Summary 中识别：

- **可迁移方法**：可以复用的做法
- **可复用约束**：值得遵守的规则
- **重复出现的坑**：需要避免的错误
- **明确判断依据**：决策时的参考

### 4. 决定目标位置

| 情况                   | 目标                        |
| ---------------------- | --------------------------- |
| 最高优先级的可复用规则 | `#memory` 主文件            |
| 稳定主题且细节渐增     | 主题子笔记 `memory/<topic>` |

### 5. 执行写入

- 使用 `bearbrain/bear-editing` 的快照 + 覆写方式
- 写入时保持简洁，优先使用指针和提炼后的规则

### 6. 更新 Promote Status

在昨日 daily 正文最前面写入状态块：

```md
## Promote Status

- Status: done-promoted
- Promoted At: 2026-03-16 09:20
- Promoted To: [[memory]], [[memory/xxx]]
```

状态值说明：

- `pending`：尚未处理
- `done-promoted`：已完成提炼，并升级到 `#memory`
- `done-none`：已检查，但没有值得升级的内容

## 自动执行逻辑

1. 检查今天是否已存在 `Memory Daily YYYY-MM-DD`
2. 如果今天的 daily 不存在，则先检查昨日 daily 是否已完成 promote
3. 若昨日未完成 promote，则自动执行本 skill
4. promote 完成后，再创建今天的 daily

## 可提炼内容类型

| 类型         | 说明           |
| ------------ | -------------- |
| 可迁移方法   | 可以复用的做法 |
| 可复用约束   | 值得遵守的规则 |
| 重复出现的坑 | 需要避免的错误 |
| 明确判断依据 | 决策时的参考   |

## 常见错误

- 把 daily 原文直接复制到 memory（应提炼后写入）
- 把原材料或文章摘要复制到 memory（应用 book-entry）
- 没有先检查 Promote Status 就重复 promote
- 状态块没有写在正文最前面
- 把经验写进 workstream 而不是 memory

## 最终检查

完成前确认：

- 昨日 daily 的 Promote Status 已更新
- 状态值正确（done-promoted 或 done-none）
- 提炼内容已写入正确目标位置（主文件或主题笔记）
- 写入内容已精简为可复用规则，不是原文复制
- 今天可以开始新的 daily
