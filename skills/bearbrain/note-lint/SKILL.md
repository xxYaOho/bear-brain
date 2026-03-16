---
name: bearbrain/note-lint
description: 当需要验证 Bear-Brain 笔记是否符合预期结构时使用，包括 section、锚点、状态块、模板强度和目标层规则。
---

# Note Lint

## 概述
使用本 skill 来校验笔记是否符合目标层的结构规范。

`note-lint` 是写后校验器。

## 检查内容
- 标题与 section 是否齐全
- 是否符合强模板 / 中模板 / 弱模板 + 强规则
- `Promote Status`、`Related Notes`、锚点、任务区是否完整
- 是否把活文档误写进 `path/docs/*`
- 是否把原始资料误写成 `#memory`
- `#memory/daily` 是否具备 `Promote Status + Summary + Log` 的基本闭环

## 输出结果
| 状态 | 说明 |
| --- | --- |
| `pass` | 通过校验 |
| `warn` | 警告，非致命问题 |
| `fail` | 失败，必须修正 |

## 输出格式
每个结果应附：
- 问题位置
- 不合规原因
- 修正建议
