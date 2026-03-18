# Memory Daily 模板

## 定位

`#memory/daily` 是过程原料层，用于 agent 流水式记录每日工作。内容允许冗余，不追求定稿。

每日结束或次日开始时，由 `promote-memory` skill 判断是否值得提炼到 `#memory`。单日无有价值内容时，Status 标记为 `done-none` 即可，不强制提炼。

---

## 结构

```md
# <YYYY-MM-DD>

## Promote Status

Status: pending | done-promoted | done-none

## Summary

- 今日主线：
- 关键发现：
- 是否值得提炼：yes / no

## Log

### <HH:MM>

- 做了什么
- 发现了什么
- 当前判断是什么
```

---

## 各 Section 说明

### Promote Status

状态值：
- `pending` — 待判断，默认值
- `done-promoted` — 已提炼到 memory
- `done-none` — 无可提炼内容，跳过

### Summary

当天结束时由 agent 填写，或 promote 时顺带补全。不替代 Log，只做快速回看用。

### Log

**倒叙**：新记录插入到 `## Log` section 开头（`bear-add-text` position=beginning + header=`Log`）。

每条记录以时间戳作为 H3 标题，时间必须来自真实系统时间，不得猜测。

---

## 写前检查

- 已搜索或打开目标 daily，确认 NOTE-ID 存在
- 如需新建，标题和 tag 来自真实当天日期
- 时间戳来自真实系统时间

---

## 与 promote-memory 的闭环

**当天**：agent 向 Log 插入记录（倒叙），视情况补 Summary，Status 保持 `pending`。

**次日**：先检查昨日 daily 的 Promote Status，若为 `pending`，执行 `promote-memory`，完成后将 Status 更新为 `done-promoted` 或 `done-none`，再创建今天的 daily。
