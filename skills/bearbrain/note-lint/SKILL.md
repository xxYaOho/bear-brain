---
name: bearbrain/note-lint
description: Use when validating that a Bear-Brain note matches the expected structure after writing, including sections, anchors, status blocks, template strength, and target-layer rules.
---

`note-lint` 是写后校验器。

检查内容：
- 标题与 section 是否齐全
- 是否符合强模板 / 中模板 / 弱模板 + 强规则
- `Promote Status`、`Related Notes`、锚点、任务区是否完整
- 是否把活文档误写进 `path/docs/*`
- 是否把原始资料误写成 `#memory`

输出：
- `pass`
- `warn`
- `fail`

并附：问题位置、原因、修正建议。
