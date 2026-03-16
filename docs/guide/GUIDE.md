# GUIDE

## Scope
本指南约束 Bear-Brain 第一阶段开发与文档维护方式。

适用于：
- 本地原型开发
- Bear 计划与工作流维护
- `path/docs/*` 稳定文档发布

不适用于：
- 远程部署方案
- 多人协作流程
- 最终产品化运营规范

## Rules
- 活文档优先在 Bear 中维护
- `path/docs/*` 只收稳定快照
- `#memory` 是默认继承入口
- `#memory/daily` 是原料层，不等于长期经验
- 长期主笔记采用“快照 + 覆写”
- `Related Notes` 使用列表，不使用表格

## Workflow
1. 在 Bear 中讨论和整理活文档
2. 达到稳定状态后，再发布到 `path/docs/*`
3. daily 由 agent 追加记录
4. 次日先做 promote-memory，再开始新 daily
5. 代码实现始终以测试和 lint 结果为准

## Exceptions
- 讨论中的开发计划暂不进入 `path/docs/*`
- Bear `repo/*` 活文档不进入默认向量索引
- `book/reference -> book/knowledge` 采用新建知识笔记，不原地改造

## Examples
正例：
- 活 PRD 放在 Bear `repo/*`
- 稳定后的 SPEC 发布到 `docs/product/SPEC.md`
- 昨日 daily 提炼后，把状态写回 daily 正文顶部

反例：
- 讨论稿直接发到 `path/docs/*`
- 把 `#memory/daily` 直接当长期 memory 使用
- 在正文里维护 Bear 标签

## Maintenance
当以下任一情况出现时，应更新这份 guide：
- Bear 工作流规则变化
- docs 发布边界变化
- memory-first 检索策略变化
- CLI 或 skill 交互模式变化