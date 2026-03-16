---
name: bearbrain/promote-memory
description: 将昨日 #memory/daily 提炼进长期 memory 时使用。当用户说"开始今天的工作"、"整理一下昨天的记录"、"promote 一下"、或每天工作开始前自动检查时，必须触发本 skill。即使用户没有说"promote"，只要是每日开工前的第一步，都应先检查昨日 daily 是否已处理。
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

使用 Bear 搜索查询昨日的 daily，tag 和 term 分开传：

```
bear-search-notes tag="memory/daily" term="<昨天日期，如 2026-03-15>"
```

**如果昨日 daily 不存在**（如周末没工作、节假日等）：跳过 promote，直接创建今天的 daily。

### 2. 检查 Promote Status

读取昨日 daily，检查 `## Promote Status` section：

- `pending` → 需要执行 promote
- `done-promoted` 或 `done-none` → 已处理，跳过

### 3. 识别可提炼内容

从昨日 daily 的 Log 或 Summary 中识别：

| 类型 | 说明 |
| --- | --- |
| 可迁移方法 | 可以复用的做法 |
| 可复用约束 | 值得遵守的规则 |
| 重复出现的坑 | 需要避免的错误 |
| 明确判断依据 | 决策时的参考 |

如果没有可提炼内容，直接跳到 Step 5，状态设为 `done-none`。

### 4. 决定目标位置

| 情况 | 目标 |
| --- | --- |
| 最高优先级的可复用规则 | `#memory` 主文件 |
| 稳定主题且细节渐增 | 主题子笔记 `memory/<topic>` |

使用 `bearbrain/memory` skill 执行写入。

### 5. 更新 Promote Status

用 `bear-replace-text` 替换昨日 daily 的 `## Promote Status` section 内容：

```md
- Status: done-promoted
- Promoted At: 2026-03-16 09:20
- Promoted To: [[memory]], [[memory/xxx]]
```

或无可提炼内容时：

```md
- Status: done-none
- Promoted At: 2026-03-16 09:20
- Promoted To:
```

**注意：** 使用 section 替换（`bear-replace-text` 指定 header），不是追加到正文末尾。`## Promote Status` 是 daily 的固定 section，应原地更新。

### 6. 创建今天的 daily

promote 完成后，创建今天的 `Memory Daily YYYY-MM-DD` 笔记，使用 `bearbrain/bear-editing/reference/daily-memory.md` 模板。

## 自动执行逻辑

1. 检查今天是否已存在 `Memory Daily YYYY-MM-DD`
2. 如果今天的 daily 不存在，则先检查昨日 daily 是否已完成 promote
3. 若昨日未完成 promote，则自动执行本 skill
4. promote 完成后，再创建今天的 daily

## 常见错误

- 把 daily 原文直接复制到 memory（应提炼后写入）
- 把原材料或文章摘要复制到 memory（应用 book-entry）
- 没有先检查 Promote Status 就重复 promote
- 用追加代替 section 替换来更新 Promote Status
- 把经验写进 workstream 而不是 memory
- 昨日 daily 不存在时报错而不是跳过

## 最终检查

完成前确认：

- 昨日 daily 的 Promote Status 已更新（section 替换，不是追加）
- 状态值正确（done-promoted 或 done-none）
- 提炼内容已写入正确目标位置（主文件或主题笔记）
- 写入内容已精简为可复用规则，不是原文复制
- 今天可以开始新的 daily
