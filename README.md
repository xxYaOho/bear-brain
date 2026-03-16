# bear-brain

Bear-Brain 是本地优先的 Bear 协作与记忆基础设施。

当前版本定位：`v0.2.0` 本地可用原型。

## 当前范围
- 本地 memory store
- `#memory/daily` 到 `#memory` 的提炼流程
- `path/docs/*` 的最小发布骨架
- memory-first 检索与路由
- OpenCode 项目级 daily hook 原型（当前仍写入本地 `daily/`）
- 仓库内维护的 BearBrain skill 源文件

## 当前状态
- 第一阶段本地原型目标已完成，仓库已具备建库、提炼、检索、发布文档、追加 daily 的最小闭环
- 全量测试当前通过，可作为后续真实使用与产品化收敛的基线
- 下一阶段主线转向 memory 主轴的全流程优化，重点收敛 daily 触发与 Bear 单一真源

## 检索模型
默认先查 `#memory`，不足时再查 `#memory/daily`，只有在明确 repo 或 workstream 上下文时再补 `path/docs/*`。

## Vector DB
- 本地 `ollama`
- 模型：`qwen3-embedding:0.6b`
- 第一阶段固定 512 维，并在启动时校验
- 数据库路径：`data/db/memory.db`

## 命令
```bash
uv run python memory_worker.py --help
```

当前可用命令：
- `bootstrap`
- `promote-yesterday`
- `search`
- `publish-doc`
- `append-daily`
