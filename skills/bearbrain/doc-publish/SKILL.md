---
name: bearbrain/doc-publish
description: Use when publishing a stable Bear-Brain Bear note into `path/docs/*`, especially when turning active repo notes into stable SPEC, GUIDE, CHANGELOG, COMPLETIONS, or DECISIONS docs.
---

`doc-publish` 处理的是：Bear 活文档 -> `path/docs/*` 稳定文档。

发布前至少检查：
- 结构完整
- 已不再是讨论稿
- 已有明确目标类型
- 用户明确要求发布，或阶段已收束

规则：
- 发布的是稳定快照，不是临时复制
- 不保留 Bear 源笔记回链
- plan 草稿先留 Bear，不直接发布到 `path/docs/*`
