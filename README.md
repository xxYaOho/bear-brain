# bear-brain

Bear-Brain 是本地优先的 Bear 协作与记忆基础设施。

## 当前范围
- 本地 memory store
- `#memory/daily` 到 `#memory` 的提炼流程
- `path/docs/*` 的最小发布骨架
- memory-first 检索与路由
- 仓库内维护的 BearBrain skill 源文件

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
