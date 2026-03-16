# DECISIONS

## 2026-03-15 Memory-first 作为默认继承路径

### Decision
Bear-Brain 的默认读取入口固定为 `#memory`，不足时再补 `#memory/daily`，只有在明确 repo 或 workstream 上下文时才引入 `path/docs/*`。

### Why
BB 的核心价值是可继承经验，而不是项目资料堆叠。将 memory 作为第一入口，可以保持协作主轴稳定。

### Alternatives Considered
- 让 `repo/*` 或 `path/docs/*` 成为默认入口：会弱化经验主轴
- 平铺读取所有层：上下文噪音过高

### Revisit Trigger
如果后续真实使用中发现 memory-first 导致召回明显不足，或者 docs 在多数任务中比 memory 更有价值，再重新评估。

## 2026-03-15 Vector DB 第一阶段固定 512 维

### Decision
第一阶段使用 `qwen3-embedding:0.6b`，向量维度固定为 `512`，并在运行时校验实际返回维度。

### Why
512 维已在设计阶段和真实 embed 调用中得到验证，先固定实现可以降低 schema 和检索链路的不确定性。

### Alternatives Considered
- 运行时动态确认维度：会让 schema 与测试边界变得模糊
- 先不做向量检索：不利于验证真实本地检索路径

### Revisit Trigger
如果后续切换 embedding 模型，或真实 benchmark 表明 512 维效果明显不足，再重新设计索引与迁移策略。

## 2026-03-15 计划文档草稿留在 Bear

### Decision
开发计划在草稿和试运行阶段优先留在 Bear 中维护，稳定后再发布到仓库中的 `docs/plans/*` 快照。

### Why
Bear 更适合多端查看、批注与快速微调；试运行阶段的 plan 变化频繁，不适合直接作为稳定 repo 文档。

### Alternatives Considered
- 直接以 repo 里的 plan 为主稿：更适合代码协作，但不适合当前多端阅读与快速微调需求

### Revisit Trigger
如果后续计划文档变得更稳定，或需要通过 PR 协作审阅，再考虑把 repo 版本提升为主维护面。