---
name: bearbrain/workstream
description: Use when creating or maintaining a `Workstream: ...` note for one active Bear-Brain work container, including Meta, Related Notes, Notes, and Task sections.
---

`workstream` 只管理“一轮工作”的主笔记，不承载活文档正文。

职责：
- 维护 `Meta / Related Notes / Notes / Task`
- 把相关笔记挂进 `Related Notes`
- 记录当前阶段状态与下一步

不要做：
- 不写 PRD、QA、FT、FB 正文
- 不直接承担 memory 提炼
- 不发布到 `path/docs/*`

写入前先经过 `bearbrain/admission`，写入时遵守 `bearbrain/bear-editing`。
