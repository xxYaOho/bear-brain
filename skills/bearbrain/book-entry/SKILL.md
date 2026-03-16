---
name: bearbrain/book-entry
description: Use when adding or refining cross-project material in Bear-Brain `book/*`, including reference, knowledge, guide, and idea notes that need the shared book note structure.
---

先判断内容成熟度，再决定去向：
- `book/reference`：来源明确、偏回查
- `book/knowledge`：已提炼、可复用
- `book/guide`：规范、流程、指南
- `book/idea`：未归属到具体 repo/workstream 的想法

结构基线：
- 描述（Summary）
- 脚注（Take）
- 正文

规则：
- `reference -> knowledge` 时新建知识笔记，保留原 reference 作为来源
- 强 repo 相关材料不进 `book/*`，应回到 `repo/*` 或 workstream
