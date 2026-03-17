# SPEC

## Purpose
定义 Bear-Brain 第一阶段本地原型的系统行为边界，使开发实现始终对齐同一份稳定规格。

## Scope
当前覆盖：
- 本地 `#memory` / `#memory/daily` 解析与提炼
- 本地 SQLite memory store
- 本地 `ollama + sqlite-vec` 检索路径
- `path/docs/*` 最小发布骨架
- 本地 CLI：`bootstrap`、`promote-yesterday`、`search`、`publish-doc`、`append-daily`
- OpenCode 项目级 daily hook 原型

当前不覆盖：
- 远程服务
- 多设备同步
- Bear 内部数据库直连
- 完整产品级提炼策略
- Bear 作为 daily 唯一真源的自动写入链

## Behavior
- 默认继承入口始终是 `#memory`
- `#memory/daily` 是原料层，次日先 promote，再开始新一天
- 向量检索默认本地执行，模型固定为 `qwen3-embedding:0.6b`
- 向量维度固定为 `512`，启动时必须校验
- Bear `repo/*` 不进入默认向量索引，只做显式读取
- `path/docs/*` 只收稳定文档，不收讨论稿
- `append-daily` 当前追加到仓库内 `daily/*.md`，作为 OpenCode 集成的第一阶段原型路径
- Bear 写入协议采用先查后写：先定位目标 note 与现有结构，再执行追加或替换
- 禁止猜测时间、NOTE-ID、Status、Target release、Actual release 或 Related Notes 元数据
- daily log、Notes 时间块、Promoted At 等字段必须来自真实系统时间或 Bear 当前返回值

## Constraints
- 第一阶段保持本地优先
- 不强制 `.env`，仅开放两个环境变量覆盖：
  - `BEAR_BRAIN_OLLAMA_BASE_URL`
  - `BEAR_BRAIN_EMBEDDING_MODEL`
- `memory.db` 默认位于 `data/db/memory.db`
- 若 embedding 模型或维度与现有索引不一致，必须报错，不得隐式混用

## Acceptance
满足以下条件可视为第一阶段规格达成：
- 本地 CLI 可以建库、提炼、检索、发布文档、追加 daily
- `ollama` 真实 embed 调用成功
- `qwen3-embedding:0.6b` 返回维度实测为 `512`
- 全量测试与 lint 通过

## Notes
当前 SPEC 面向第一阶段本地原型。下一阶段将重点处理 memory 主轴全流程优化，并把 daily 自动记录从本地文件链收敛到 Bear 单一真源。
