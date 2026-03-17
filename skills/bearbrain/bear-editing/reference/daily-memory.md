# Daily Memory 模板

## 定位
`#memory/daily` 是过程原料层，用于 agent 自动记录每日工作。

## 推荐格式

```md
---
## Promote Status
- Status: pending | done-promoted | done-none
- Promoted At: <时间戳>
- Promoted To: <被提炼到的目标笔记，可空>

## Summary
- 今日主线：<一句话概括今天在做什么>
- 关键发现：<今天学到了什么、发现了什么>
- 是否值得提炼：<yes/no，简要说明>

## Log
### 2026-03-15 10:30
- 做了什么
- 发现了什么
- 当前判断是什么

### 2026-03-15 14:20
- 做了什么
- 遇到了什么异常
- 暂时结论是什么
```

## 各 Section 作用

### Promote Status
放在最前面，用于第二天快速判断昨天的 daily 是否已完成 promote。

状态值：
- `pending`：待提炼
- `done-promoted`：已提炼到 memory
- `done-none`：无可提炼内容

### Summary
快速回看，不替代完整日志。建议保留三个点：
- 今日主线
- 关键发现
- 是否值得提炼

### Log
作为主要追加区。规则：
- 每次记录以时间块追加
- 时间块标题必须来自真实系统时间或 Bear 当前返回值，不得猜测
- 内容重点：做什么、发现什么、判断是什么
- 允许冗余，不追求定稿

## 写前检查

追加 daily 前，先确认：

- 已搜索或打开目标 daily，确认 NOTE-ID 和 `## Log` section 存在
- 如需新建，日期标题与标签来自真实当天日期，而不是对话推断
- 当前时间块使用真实系统时间

## 与 promote-memory 的闭环

### 当天
- agent 向 `Log` 追加记录
- 视情况补 `Summary`
- `Promote Status` 默认保持 `pending`

### 次日
- 先看昨日 daily 的 `Promote Status`
- 若仍为 `pending`，执行 `promote-memory`
- 执行后回写状态块
- 之后才创建今天的 daily
