---
name: admission
description: 当写入 Bear 内容但目标层不明确时使用本 skill。当用户要保存、记录、整理内容，却还没确定应写到 workstream、repo/*、book/*、#memory、#memory/daily 或 docs/* 时，用本 skill 判断去向。目标已明确时可跳过，直接进入对应 skill。
---

# Admission

`admission` 是写入前的前置闸门，不只是分类器。

**负责：** 判断内容去向 + 给出下一步动作建议
**不负责：** 真正写入、格式检查、内容提炼

## 何时必须使用

以下情况必须先过 `admission`：

- 用户要"记一下"、"保存一下"、"整理一下"，但没说清楚写到哪一层
- agent 识别出一段新内容值得写入 BB，但目标层仍有歧义
- 同一份内容可能落到多个层级，如 `repo/*` 和 `book/*`、或 `#memory` 和 `#memory/daily`

## 何时可以跳过

以下情况可以直接进入对应 skill：

- 目标笔记已明确，如"更新这条 workstream"、"追加到这条 memory 笔记"
- 目标层已明确，如"发布到 docs"、"写进 #memory"、"追加到 today daily"
- 用户已经给出 note ID、标题、或明确 section

也就是说，`admission` 负责**决策去向**，不是为所有写入重复做一次确认。

## 输出结构

每次判断输出最小结构：

```text
destination: repo/prd
reason: 这是当前项目的活文档草稿，尚未稳定
action: create-note
next: 挂到 workstream Related Notes；稳定后用 doc-publish 发布
```

字段说明：

- `destination`：目标层路径，如 `repo/*`、`workstream`、`book/knowledge`、`#memory`、`#memory/daily`、`docs/*`
- `reason`：一句话说明判断依据
- `action`：建议动作，如 `create-note`、`append`、`update-section`、`keep-draft`
- `next`：后续应触发哪个 skill 或动作

## 路由决策

### 第一步：看内容用途

| 内容用途                             | 候选目标层      |
| ------------------------------------ | --------------- |
| 当前工作的进展、状态、待办           | `workstream`    |
| 当前项目的活文档（PRD、QA、FT、FB）  | `repo/*`        |
| 跨项目的参考资料、知识点、指南、想法 | `book/*`        |
| 可复用的规则、方法、约束、判断依据   | `#memory`       |
| 今日工作过程记录                     | `#memory/daily` |
| 已稳定、可发布的文档                 | `docs/*`        |

### 第二步：看生命周期

| 生命周期           | 调整方向                                      |
| ------------------ | --------------------------------------------- |
| 活跃草稿、仍在变化 | 留在 Bear（`repo/*` 或 `workstream`），不发布 |
| 跨项目、长期有效   | `book/*` 或 `#memory`                         |
| 阶段收束、已稳定   | `docs/*`                                      |
| 今日过程、待提炼   | `#memory/daily`                               |

### 第三步：`#memory` 特殊链路

`#memory` 和 `#memory/daily` 是经验主轴，不走普通多标签归类逻辑：

- **不要**给一条普通 repo 笔记直接打 `#memory` 标签
- `#memory` 的内容来源是 `#memory/daily` 经过 `promote-memory` 提炼后的结果
- 如果内容是"今天发现的可复用规则"，先进 `#memory/daily`，次日由 `promote-memory` 提炼
- 如果内容已经是明确的长期规则（不需要再提炼），可以直接用 `bearbrain/memory` 写入

## 各目标层判断标准

### `workstream`

- 这是"一轮工作"的组织容器
- 适合：开启新工作、更新进度、关联相关笔记
- 不适合：存放活文档正文、跨项目资料

### `repo/*`

- 当前项目的活文档（PRD、QA、FT、FB、设计稿等）
- 适合：仍在迭代的草稿
- 不适合：已稳定可发布的内容（那应该去 `docs/*`）

### `book/*`

- 跨项目资料，按成熟度选子栏目：
  - `book/reference`：来源明确、偏回查
  - `book/knowledge`：已提炼、可复用
  - `book/guide`：规范、流程、指南
  - `book/idea`：未归属的想法

### `#memory`

- 已提炼的长期可复用规则、方法、约束
- 来源通常是 `promote-memory` 的输出
- 直接写入时使用 `bearbrain/memory`

### `#memory/daily`

- 今日工作过程记录
- 原料层，待次日 `promote-memory` 提炼

### `docs/*`

- 已稳定、阶段收束的发布文档
- 使用 `bearbrain/doc-publish` 发布

## 歧义与冲突处理

**多标签不是冲突：** 同一条 Bear 笔记可以同时有 `repo/*` 和 `workstream` 标签，这是正常的。

**边界模糊时：** 给出警告 + 推荐默认去向，不要阻止写入。格式：

```text
destination: book/knowledge (推荐，但有歧义)
reason: 内容已提炼，但也可能属于 repo/* 的项目规范
action: create-note
next: 如果只服务当前项目，改路由到 repo/*
```

**明显错误必须拦截：**

- 把 daily 日志直接写进 `#memory`（应先进 daily，再 promote）
- 把活跃草稿发布到 `docs/*`（应等阶段收束）
- 把强 repo 相关内容写进 `book/*`

## 下一步 skill 路由

| destination     | 下一步 skill                     |
| --------------- | -------------------------------- |
| `workstream`    | `bearbrain/workstream`           |
| `repo/*`        | `bearbrain/bear-editing`         |
| `book/*`        | `bearbrain/book-entry`           |
| `#memory`       | `bearbrain/memory`               |
| `#memory/daily` | `bearbrain/bear-editing`（追加） |
| `docs/*`        | `bearbrain/doc-publish`          |
