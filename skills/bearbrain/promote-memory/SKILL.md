---
name: bearbrain/promote-memory
description: 当需要将昨日的 #memory/daily 提纯到长期 Bear-Brain memory 时使用，包括可复用规则提取、目标选择、promote-status 更新。
---

# Promote Memory

## 概述
使用本 skill 将 `#memory/daily` 提纯到 `#memory`。

## 处理范围
只处理"昨天"的 daily，不按 workstream 切。

## 流程步骤
1. 读取昨日 daily
2. 识别可迁移的方法、可复用约束、重复出现的坑、明确判断依据
3. 决定写入 `#memory` 主文件还是主题子笔记
4. 回写 `Promote Status`

## 规则
- 自动执行，但状态必须对用户可见
- 若无可提炼内容，写 `done-none`
- 若有提炼结果，写 `done-promoted`

## 可提炼内容类型
| 类型 | 说明 |
| --- | --- |
| 可迁移方法 | 可以复用的做法 |
| 可复用约束 | 值得遵守的规则 |
| 重复出现的坑 | 需要避免的错误 |
| 明确判断依据 | 决策时的参考 |

## 目标选择
| 情况 | 目标 |
| --- | --- |
| 最高优先级的可复用规则 | `#memory` 主文件 |
| 稳定主题且细节渐增 | 主题子笔记 |
