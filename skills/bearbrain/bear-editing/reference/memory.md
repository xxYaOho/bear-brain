# Memory 模板

## 定位

`#memory` 是长期经验层，用于沉淀可复用知识、方法和判断依据。只有经过 `promote-memory` 提炼的内容才能进入，不直接手写。

---

## 主文件结构

```md
# memory

## Position

长期经验入口，索引所有子主题。

## Core Memory

- <可复用的核心原则、方法、约束>

## Recall Keys

- <可以回忆的内容描述>
  - 关键词: <keyword-1>, <keyword-2>, <keyword-3>

## Related Notes (subnote)

- <NOTE-ID>：<子主题一句话描述>
```

**新建时**：title=`memory`，tags=`memory`，text 从 `## Position` 开始。

---

## 子主题笔记结构

```md
# memory/<topic>

## Position

本主题在 memory 中的定位，一句话。

## Core

- <核心方法 / 原则>
- <适用条件>
- <边界 / 例外>

## Cases（可选）

### 成功

- <场景>：<做法>

### 失败

- <场景>：<教训>

## Related Notes

- <NOTE-ID>：<关联主题一句话描述>
```

**Cases 为可选 section**，无案例时省略，不写空壳。

---

## 写入规则

1. 只有经过 promote 提炼的内容才能进入 memory
2. 内容强调精炼、可复用、可追溯
3. **新建子主题后，必须同步更新主文件**：
   - `## Recall Keys`：添加内容描述 + 关键词
   - `## Related Notes`：添加 NOTE-ID + 一句话描述
4. 定期回顾，合并相似主题，删除过时内容

---

## Recall Keys 格式

每条记录以内容描述为主体，关键词作为检索入口附在下方：

```
- Bear 笔记编辑的工具选择与写入流程
  - 关键词: bear-editing, MCP, add-text, replace-text
- 每日记忆的倒叙追加与 promote 闭环
  - 关键词: memory-daily, promote, log
```

关键词应贴近实际搜索习惯，辅助 embedding 检索。同一条内容可列多个关键词。
