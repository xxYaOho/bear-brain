---
name: book-entry
description: 保存跨项目资料到 Bear-Brain book/* 时使用。当用户说"保存这篇文章"、"记录一下这个知识点"、"把这个想法存下来"、"归档一下这个资料"、或内容是跨项目可复用的参考/知识/指南/想法时，必须使用本 skill。不适用于当前项目活文档或 memory 经验层。
---

# Book Entry

## 概述

使用本 skill 将跨项目资料写入 `book/*`。

`book/*` 是跨项目资料库，使用中模板：不像 `workstream`、`#memory` 那样强结构化，也不完全自由。核心要求是：人好读，agent 也能稳定理解。

## 使用场景

以下情况使用本 skill：

- 需要保存跨项目的参考资料
- 需要沉淀可复用的知识点
- 需要记录规范、流程、指南
- 需要暂存未归属的想法
- 需要将 reference 升级为 knowledge

不要用本 skill 来写：

- 强 repo 相关的材料（应回到 `repo/*`）
- 当前工作的进展和状态（应用 workstream）
- 需要提炼进 memory 的经验（应用 memory 或 promote-memory）

## 定位已有笔记

操作前先确认是否已有同主题笔记：

```
bear-search-notes tag="book/<栏目>" term="<关键词>"
```

- 已存在且内容相关 → 更新已有笔记，不新建
- 已存在但成熟度不同（如 reference → knowledge）→ 新建新栏目笔记，保留原笔记

## 栏目选择

先判断内容成熟度，再决定去向。

| 栏目             | 适用场景                   |
| ---------------- | -------------------------- |
| `book/reference` | 来源明确、偏回查的外部资料 |
| `book/knowledge` | 已提炼、可复用的知识点     |
| `book/guide`     | 规范、流程、指南           |
| `book/idea`      | 未归属的想法               |

### 栏目微调说明

**book/reference**：强调来源材料、摘录、回查价值。适合外部文章、资料卡、工具说明等。

**book/knowledge**：强调已吸收、已提炼的知识点。正文可能不是原文摘录，而是提炼后的结论。

**book/guide**：强调规则、流程、方法、约定。Take 可用于说明适用边界。

**book/idea**：强调想法本身、方向、观察。Take 可用于说明为什么值得暂时保留。

## 结构基线

完整模板参考：`bearbrain/bear-editing/reference/book.md`

```md
---

**描述 (Summary)**

一句话或一段文字说明这条笔记是什么

**脚注 (Take)**

判断、提炼、为什么值得保留

---

正文（原文/内容/规范/想法）
```

### 字段说明

**描述 (Summary)**：告诉读者这条笔记是什么，提供快速理解入口。

**脚注 (Take)**：解释为什么值得保留，表达判断、提炼、取舍。不只是复述原文，应有自己的理解。

**正文**：保存主要内容，作为原始材料或主要表达区。

## reference → knowledge 升级流程

当 `book/reference` 的内容成熟到足以升级时：

1. 新建一条 `book/knowledge` 笔记
2. 原 `reference` 笔记保留，作为来源材料
3. 在新 knowledge 笔记的 Summary 或 Take 中注明来源 reference 的 NOTE-ID
4. 不做原地改造

## 规则

- 强 repo 相关材料不进 `book/*`，应回到 `repo/*` 或 workstream
- 升级时新建笔记，原笔记保留

## 工作流程

1. 确认内容是跨项目资料（不是强 repo 相关）
2. 搜索是否已有同主题笔记
3. 判断内容成熟度，选择合适栏目
4. 按栏目模板创建或更新笔记
5. 填写 Summary、Take、正文

## 常见错误

- 把强 repo 相关材料放进 book/_（应回到 repo/_）
- 用 book/\* 来记录工作状态（应用 workstream）
- 把 daily 日志复制到 book/\*（应用 promote-memory）
- reference 升级时做原地改造（应新建 knowledge，保留原 reference）
- Summary 写得过长（应简洁，快速说明主题）
- Take 只复述原文，没有自己的判断
- 没有先搜索就直接新建，导致重复

## 最终检查

完成前确认：

- 内容确实是跨项目资料
- 栏目选择符合成熟度判断
- Summary 简洁明了
- Take 包含判断和提炼，不只是复述
- 正文内容与栏目定位匹配
- 如果是 reference → knowledge 升级，已保留原 reference
