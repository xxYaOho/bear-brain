---
name: promote-memory
description: 当用户要记录今日 daily 时，自动将最近的待处理 daily 提纯到 #memory。使用场景包括：用户说"开始今天的工作"、"整理一下记录"、或每次创建新 daily 时自动触发。
---

# Promote Memory

## 概述

当用户要记录今日 daily 时，自动将最近的 `#memory/daily` 提纯到 `#memory`。

本 skill 是全自动执行的提纯动作，用户无感知。目标是做到：每次记录 daily 时，自动检查并处理待提纯的历史 daily。

## 与 memory 的关系

- `bearbrain/memory`：面向长期经验层本身的维护
- `bearbrain/promote-memory`：负责从 `#memory/daily` 升级进 `#memory`

## 处理范围

- 自动查找最近的待处理 daily（从今日往前追溯，最多 7 天）
- 不按 workstream 切分
- 因为 `#memory` 是全局经验层，不是 workstream 经验层

## 使用场景

以下情况使用本 skill：

- hook 触发记录 daily 时，检查是否存在待 promote 的历史 daily
- 需要决定哪些内容值得升级进 memory

## 触发条件

以下情况自动触发本 skill：

- hook 触发记录 daily 时（自动触发，不是用户手动）
- hook 会先调用本 skill 检查是否需要 promote

## 流程步骤

### 1. 检查今日 daily 状态

使用 Bear 搜索检查今日 daily 是否存在：

```
bear-search-notes tag="memory/daily" term="<今日日期，如 2026-03-16>"
```

- **已存在** → 打开现有笔记，结束流程
- **不存在** → 继续 Step 2

### 2. 查找最近的待处理 daily

从今日往前追溯，查找最近的 pending daily：

```
bear-search-notes tag="memory/daily" term="2026-03-15"
bear-search-notes tag="memory/daily" term="2026-03-14"
bear-search-notes tag="memory/daily" term="2026-03-13"
...（最多追溯 7 天）
```

每找到一个就读取其 `## Promote Status` section 检查状态：

- `pending` → 找到目标，执行 Step 3
- `done-promoted` 或 `done-none` → 继续往前找更早的
- **未找到任何 pending** → 直接创建今日 daily（Step 5）

### 3. 执行 Promote（如找到 pending）

从目标 daily 的 Log 或 Summary 中识别可提炼内容：

| 类型         | 说明           |
| ------------ | -------------- |
| 可迁移方法   | 可以复用的做法 |
| 可复用约束   | 值得遵守的规则 |
| 重复出现的坑 | 需要避免的错误 |
| 明确判断依据 | 决策时的参考   |

如果没有可提炼内容，跳到 Step 4，状态设为 `done-none`。

### 4. 写入目标位置

| 情况                   | 目标                        |
| ---------------------- | --------------------------- |
| 最高优先级的可复用规则 | `#memory` 主文件            |
| 稳定主题且细节渐增     | 主题子笔记 `memory/<topic>` |

使用 `bearbrain/memory` skill 执行写入。

### 5. 更新 Promote Status

用 `bear-replace-text` 替换目标 daily 的 `## Promote Status` section 内容：

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

**注意：** 使用 section 替换（`bear-replace-text` 指定 header），不是追加到正文末尾。

### 6. 创建今日 daily

promote 完成后，创建今天的 `Memory Daily YYYY-MM-DD` 笔记，使用 `bearbrain/bear-editing/reference/daily-memory.md` 模板。

## 常见错误

- 把 daily 原文直接复制到 memory（应提炼后写入）
- 把原材料或文章摘要复制到 memory（应用 book-entry）
- 没有先检查今日 daily 是否存在就重复 promote
- 没有逐天往前查找就假设昨日才是待处理的
- 用追加代替 section 替换来更新 Promote Status
- 把经验写进 workstream 而不是 memory

## 最终检查

完成前确认：

- 目标 daily 的 Promote Status 已更新（section 替换，不是追加）
- 状态值正确（done-promoted 或 done-none）
- 提炼内容已写入正确目标位置（主文件或主题笔记）
- 写入内容已精简为可复用规则，不是原文复制
- 今日 daily 已创建
