# Book 模板

## 定位

`book/*` 是知识沉淀层，承载参考资料、知识整理、产品想法和正式文章。

有两种添加入口：

- **User 添加**：结构宽松，agent 不主动创建，不强制套模板
- **Agent 添加**：遵循规范结构，避免过度泛化

---

## book/reference — 参考资料

**由 Agent 添加**，外部资料、他人实现、分享笔记等。Agent 不主动创建。

```md
## Summary

一句话说明这份资料是什么

## Source

来源 / 链接 / 出处

## Notes（可选）

阅读笔记，由你自己添加

## Content

正文 / 摘录
```

`Notes` 和 `Content` 均可选，按实际情况填写。

---

## book/idea — 产品想法

**由 User 添加**，产品思路或想法。Agent 不主动创建。

```md
## Summary

一句话描述这个想法

## Content

详细说明
```

结构完全宽松，你怎么写都行。

---

## book/knowledge — 知识整理

**由 Agent 主导**，整理某个实现方法或解决途径。Agent 在判断有价值时会询问是否添加。

```md
## Summary

核心结论，一句话

## Context

适用场景 / 前提条件

## Content

具体方法 / 实现路径 / 关键点

## Cases（可选）

- <场景>：<做法 / 结论>

## References

来源笔记或资料的 NOTE-ID 列表

- <NOTE-ID>：<一句话描述>
```

`Cases` 可选，无案例时省略。`References` 用于追溯来源，至少填一条。

---

## book/blog — 正式文章

**协作产出**，可以是整理讨论、你给方向和资料由 agent 编写，或其他形式。达到可发布到 Medium / X / Blog 的质量。

```md
## Summary

文章核心观点，一句话

## Outline（可选）

写作前的提纲，完成后可删除

## Content

正文，markdown 格式

## Meta

- Status: draft | ready | published
- Target: <目标平台>
- Source: <来源笔记 NOTE-ID，可多条>
```

`Status` 由 agent 在每次编辑后更新。`Outline` 仅在起草阶段使用。

---

## Tag 规范

新建时 tags 对应子类型：

| 类型     | tag              |
| -------- | ---------------- |
| 参考资料 | `book/reference` |
| 产品想法 | `book/idea`      |
| 知识整理 | `book/knowledge` |
| 正式文章 | `book/blog`      |

---

## 写入规则

- `book/reference` / `book/idea`：user 主动添加，agent 不主动创建，不强制结构
- `book/knowledge`：agent 判断有价值时询问 user，确认后创建
- `book/blog`：需 user 明确发起或给出方向，agent 不自行决定创建
