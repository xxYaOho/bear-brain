# AGENTS

## About it (source of ideas)

Bear-Brain 是本地优先的 Bear 协作与记忆基础设施。

## Vision

## Dev Conventions

_底线：代码质量要能让你在三个月后还能接手。_

### 核心原则

按优先级排序，冲突时上层优先：

| 优先级 | 原则  | 说明                       |
| ------ | ----- | -------------------------- |
| 1      | KISS  | 代码要让一周后的自己能看懂 |
| 2      | YAGNI | 只写当前需要的功能         |
| 3      | DRY   | 重复三次以上再抽象         |
| 4      | SOLID | 等项目复杂到需要它时再说   |

**决策准则**：如果一个设计让你犹豫超过 5 分钟，选简单的那个。

### Git

#### 分支策略

main (稳定发布) ← dev (集成测试) ← feature/\* (功能开发)

- `main`：稳定版本，正式发布打 tag `vX.Y.Z`，**禁止直接 commit**
- `dev`：集成分支，可发布 `vX.Y.Z-beta.N`，测试通过后 merge 到 `main`
- `feature/<name>`：从 `dev` 创建，短横线命名如 `feature/add-auth`，临时分支

#### Workflow

```bash
# 1. 创建 feature
git checkout dev && git pull origin dev
git checkout -b feature/<name>

# 2. 开发完成 → 合入 dev（--no-ff 保留合并记录）
git checkout dev && git pull origin dev
git merge --no-ff feature/<name>

# 3. dev 测试通过 → 合入 main 并发布
git checkout main && git pull origin main
git merge --no-ff dev
git tag -a vX.Y.Z -m "release vX.Y.Z"
git push origin main --tags

# 4. 清理已完成的 feature 分支
git branch -d feature/<name>
git push origin --delete feature/<name>
```

#### Principle

1. 根据任务拆分（或按照计划书）创建 `feature/*` 分支，一个分支只做一件事
2. commit 遵循 Conventional Commits（`feat:` / `fix:` / `refactor:` / `docs:` / `chore:`）
3. 合并前必须 `git pull`，切换分支前必须 `git status` 确认工作区干净
4. 禁止跳过 dev 直接将 feature 合入 main
5. feature 分支在 dev 测试通过、合入 main 后再批量清理

> 如果是本地开发，还没建立远程仓库，pull 和 push 操作可以适当忽略。

#### 提交

| 前缀     | 说明                       |
| -------- | -------------------------- |
| feat     | 新增功能                   |
| fix      | 修复问题                   |
| refactor | 重构代码                   |
| docs     | 文档更新                   |
| chore    | 杂项（依赖升级、配置调整） |

要求：

- 首行简短说明（不超过 50 字符）
- 一个提交只做一件事
- 可以补充第二段详细说明（空一行后）

### 代码风格

#### 命名

- **变量/函数**：语言惯例（camelCase 或 snake_case）
- **常量**：UPPER_SNAKE_CASE
- **布尔值**：`isReady`, `hasError`, `shouldRetry`
- **禁止**：`data`, `temp`, `obj`, `x`, `y`（无意义命名）

| Don't    |  →  | To Do                          |
| -------- | :-: | ------------------------------ |
| data     |  →  | userProfile, orderItems        |
| temp     |  →  | rawInput, unvalidatedEmail     |
| handle() |  →  | parseCSVRow(), validateToken() |

#### 组织

- 函数不超过 50 行（超过就拆分）
- 嵌套不超过 3 层（用 early return）
- 魔法数字提取为常量
- 配置项集中管理（单独的 config 文件或环境变量）

#### 格式化

- 配置自动格式化（Prettier / Black / gofmt）
- 保存时自动执行
- 不手动调格式

### 原则 vs 速度的平衡

快速迭代，但不留坑。

| 类别              | 实践                                            |
| :---------------- | :---------------------------------------------- |
| **Good Practice** | 1. 跳过不必要的测试（UI 调整、配置修改）        |
|                   | 2. 简化流程（不搞复杂分支策略）                 |
|                   | 3. 延迟优化（先跑起来再说）                     |
| **Bad Practice**  | 1. 跳过错误处理                                 |
|                   | 2. 不写文档（至少 README 要有）                 |
|                   | 3. 提交明显的烂代码（命名混乱、硬编码敏感信息） |

## Reference
