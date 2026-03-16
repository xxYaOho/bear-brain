---
name: bearbrain/admission
description: Use when deciding where new Bear-Brain content should go before writing, especially when routing content across repo notes, workstream, docs, book, memory, or daily-memory and suggesting the next action.
---

`admission` 是前置闸门，不只是分类器。

输出最小结构：
- `destination`
- `reason`
- `action`
- `next`

规则：
- 先看内容用途，再看生命周期
- 多标签不是冲突，同一条 Bear 笔记可有多个空间/类型标签
- `#memory` / `#memory/daily` 是特殊链路，不走普通多标签归类逻辑
- 明显错误必须拦截
- 边界模糊时，给警告与默认建议
