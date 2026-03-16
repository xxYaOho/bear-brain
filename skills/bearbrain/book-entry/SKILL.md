---
name: bearbrain/book-entry
description: 当需要在 Bear-Brain `book/*` 中添加或完善跨项目材料时使用，包括 reference、knowledge、guide、idea 等需要共享 book 笔记结构的笔记。
---

# Book Entry

## 概述
使用本 skill 将跨项目资料写入 `book/*`。

## 栏目选择
先判断内容成熟度，再决定去向：

| 栏目 | 适用场景 |
| --- | --- |
| `book/reference` | 来源明确、偏回查 |
| `book/knowledge` | 已提炼、可复用 |
| `book/guide` | 规范、流程、指南 |
| `book/idea` | 未归属到具体 repo/workstream 的想法 |

## 结构基线
- Summary（描述）
- Take（脚注）
- Content（正文）

## 规则
- `reference -> knowledge` 时新建知识笔记，保留原 reference 作为来源
- 强 repo 相关材料不进 `book/*`，应回到 `repo/*` 或 workstream
