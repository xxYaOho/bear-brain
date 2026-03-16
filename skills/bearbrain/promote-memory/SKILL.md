---
name: bearbrain/promote-memory
description: Use when promoting yesterday's `#memory/daily` into long-term Bear-Brain memory, including reusable-rule extraction, destination choice, and promote-status updates.
---

只处理“昨天”的 daily，不按 workstream 切。

做法：
- 读取昨日 daily
- 识别可迁移的方法、可复用约束、重复出现的坑、明确判断依据
- 决定写入 `#memory` 主文件还是主题子笔记
- 回写 `Promote Status`

规则：
- 自动执行，但状态必须对用户可见
- 若无可提炼内容，写 `done-none`
- 若有提炼结果，写 `done-promoted`
