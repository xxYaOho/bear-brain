---
name: workstream
description: 创建或维护 workstream 笔记时使用。当用户说"开一个新项目"、"记录一下这轮工作"、"更新一下进度"、"把这个挂到 workstream"、"开始开发"、"招募团队"、或需要追踪一轮工作的状态和关联笔记时，必须使用本 skill。
---

# Workstream

## 概述

Workstream 是一轮工作的主容器笔记，由 User 和 Agent 共同主导。

**三种角色：**

- **User** — 方向决策、member 招募确认、Related Notes 维护
- **Agent** — 技术规划、Team 初始化、任务拆分、Work Notes 和 Summary 维护
- **Member（subagent）** — 在独立 git worktree 中执行任务，只维护自己的 Checkpoint

完整笔记结构参考：`bear-editing/reference/workstream.md`

---

## 生命周期

### 阶段一：规划（Phase: planning）

创建 workstream 笔记时进入此阶段。

**此阶段完成：**

- 初始化 Meta Card（Repo、Main Space、Goal、Scope、Phase=planning）
- Status 设为 `idea` 或 `active`
- Team 留空，不初始化

**不做：**

- 不拆任务
- 不招募 member
- 不初始化 Summary Tasks

---

### 阶段二：开发（Phase: implementation）

User 或 Agent 明确进入开发阶段时触发。

**此阶段完成：**

1. 更新 Meta Card Phase → `implementation`
2. 分析 Goal 和 Scope，制定任务清单
3. 按拆分原则决定 member 数量和任务边界
4. 初始化 Team section（每个 member 的 Ability + Task）
5. 初始化 Summary Tasks

---

### 阶段三：执行中

**Agent 持续维护：**

- Work Notes：每次有判断价值的发现追加一条（ISO-8601 时间戳）
- Summary Tasks：任务完成时打勾

**Member 维护：**

- 每个可独立验证的功能单元完成后追加 Checkpoint

**Agent 验收：**

- 读取 member 的 Checkpoint，对照 Task 要求验收
- 验收通过后更新 Summary Next

---

### 阶段四：完成（Phase: shipped / archived）

- 更新 Meta Card Status → `shipped`
- 填写 Actual release
- 更新 Summary Next 为空或后续方向

---

## Team 初始化

进入开发阶段时，Agent 负责决定 member 数量和任务分配。

### 拆分原则

**独立性优先**：每个 member 的任务必须可以在独立 worktree 中完成，不依赖其他 member 的未完成产出。

具体检查：

- 两个 member 是否会修改同一个文件？→ 合并为一个 member
- 一个 member 的输出是否是另一个 member 的输入？→ 串行执行，不并行分配
- 两个 member 是否需要实现同一个接口或数据结构？→ 先由一个 member 定义，另一个等待或合并

**粒度原则**：单个 member 的任务应该是一个可独立验证的功能单元，不要过细（每个函数一个 member）也不要过粗（整个模块一个 member）。

**数量原则**：member 数量由任务的并行度决定，没有上限。如果所有任务都有依赖关系，串行执行比强行并行更安全。

### Member 信息格式

```md
### <name>

Member: subagent
Ability: <这个 member 擅长什么 / 负责什么领域>
Task: <具体任务描述，明确边界和产出物>
```

Task 描述必须包含：

- 做什么
- 边界在哪里（不做什么）
- 产出物是什么（文件、接口、功能）

---

## 笔记操作规范

### 定位已有 workstream

操作前先确认是否已有对应 workstream：

```
bear-search-notes term="Workstream: <关键词>" tag="workstream"
```

已存在则更新，不重复创建。更新前必须先 `bear-open-note` 读取当前内容。

### 各 section 操作

| Section        | 操作                                         | 执行者       |
| -------------- | -------------------------------------------- | ------------ |
| Meta Card      | `bear-replace-text` scope=section            | Agent        |
| Related Notes  | 由 Agent 维护，User 辅助                     | Agent & User |
| Work Notes     | `bear-add-text` 插入末尾                     | Agent        |
| Team（初始化） | `bear-add-text` 插入末尾                     | Agent        |
| Checkpoint     | `bear-add-text` 插入对应 member section 末尾 | Member       |
| Summary        | `bear-replace-text` scope=section            | Agent        |

---

## 常见错误

- 创建时就初始化 Team（应等到进入开发阶段）
- 两个 member 任务存在文件级依赖（会导致 merge conflict 或重复实现）
- Task 描述没有明确边界，member 自行扩展范围
- Work Notes 写流水账而不是判断（"改了 X 文件"不如"发现 Y 模块有耦合问题，决定先拆"）
- 验收前没有读 Checkpoint，直接宣称完成
