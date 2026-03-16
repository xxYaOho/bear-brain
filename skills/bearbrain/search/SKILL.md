---
name: bearbrain/search
description: 当需要在 memory、daily-memory、docs、显式笔记引用、本地向量搜索或多标签 AND 搜索中执行 Bear-Brain 检索时使用，且搜索目标和顺序已确定。
---

# Search

## 概述

使用本 skill 来执行搜索。

这是统一搜索执行器，负责"怎么查"。

## 模式总览

| 模式 | 说明 | 使用场景 |
| --- | --- | --- |
| `memory_db` | 本地 Vector DB 查询 | 语义相似度检索 |
| `note_refs` | 显式笔记引用 | 已知 note id 或内链 |
| `docs_scope` | path/docs/*.md 搜索 | 项目稳定文档检索 |
| `tags_and` | 多标签 AND 搜索 | 多标签交叉过滤 |
| `hybrid` | 组合模式 | 需要交叉验证 |

## 默认索引范围

- `#memory`
- `#memory/daily`
- `path/docs/*`

---

## 模式 1：memory_db

### 描述
本地 Vector DB 查询，使用 ollama embedding + sqlite-vec。

### 使用场景
- 需要语义相似度检索
- 模糊匹配而非精确匹配

### 实现
调用 `search_memory_db()` 函数，传入：
- query: 搜索文本
- limit: 返回数量

### 输出格式
```json
{
  "source": "memory",
  "title": "笔记标题",
  "content": "笔记内容",
  "score": 0.85,
  "metadata": {"source_id": "xxx", "updated_at": "2026-03-16"}
}
```

---

## 模式 2：note_refs

### 描述
显式笔记引用，根据 note ID 直接读取笔记内容。

### 使用场景
- 已知 note ID
- 通过内链直接引用

### 步骤
1. 接收 note ID（如 `61D32283-92E3-4EAB-B8A3-58C2A5EA1A5F`）
2. 调用 `bear-open-note` 获取笔记内容
3. 返回笔记详情

### 输出格式
```json
{
  "source": "note_refs",
  "title": "笔记标题",
  "content": "笔记全文",
  "score": 1.0,
  "metadata": {"id": "xxx"}
}
```

---

## 模式 3：docs_scope

### 描述
在 `path/docs/*.md` 目录中进行关键词搜索。

### 使用场景
- 检索项目稳定文档
- 已知需要查 docs 目录

### 步骤
1. 确定 docs 根目录（如 `~/bear-brain/docs/`）
2. 遍历所有 `*.md` 文件
3. 关键词匹配打分
4. 按 score 排序返回

### 实现
调用 `search_docs_scope()` 函数。

### 输出格式
```json
{
  "source": "docs",
  "title": "文档标题",
  "content": "文档内容",
  "score": 3.0,
  "metadata": {"path": "docs/product/SPEC.md"}
}
```

---

## 模式 4：tags_and

### 描述
多标签 AND 搜索，找出同时持有所有指定标签的笔记。

### 使用场景
- 需要多标签交叉过滤
- 如：同时有 `#repo/bear-brain` 和 `#webook/docs` 的笔记

### 辅助脚本
`script/intersect.py` — 计算多标签交集

### 完整工作流

#### Step 1: Resolve tags
调用 `bear-list-tags`，解析用户提供的 tag：
- **精确路径**（含 `/`）：验证存在后直接使用
- **简单名称**：查找所有以该名称结尾的路径
  - 1 个匹配 → 使用
  - 2+ 个匹配 → 显示选项，让用户选择
  - 0 个匹配 → 告知用户，停止

#### Step 2: Search each tag
对每个解析后的 tag，调用 `bear-search-notes`：
```bash
bear-search-notes tag="repo/bear-brain" limit=1000
bear-search-notes tag="webook/docs" limit=1000
```
收集每个调用的原始输出。

#### Step 3: Intersect
构建 stdin 格式：
```
tag:repo/bear-brain
<bear-search-notes 输出>
---
tag:webook/docs
<bear-search-notes 输出>
```

运行 intersect.py：
```bash
python3 skills/bearbrain/search/script/intersect.py << 'EOF'
tag:repo/bear-brain
<output1>
---
tag:webook/docs
<output2>
EOF
```

#### Step 4: Present results
格式化为 markdown table：

| Title | ID |
| ----- | --- |
| ... | ... |

显示每个 tag 的命中数作为上下文（如 "repo/bear-brain: 142 notes, webook/docs: 38 notes → 交集: 5 notes"）。

### 输出格式
```json
{
  "count": 5,
  "results": [
    {"id": "xxx", "title": "笔记标题"}
  ],
  "per_tag": [
    {"tag": "repo/bear-brain", "count": 142},
    {"tag": "webook/docs", "count": 38}
  ]
}
```

### 边界情况处理

| 情况 | 处理方式 |
| --- | --- |
| Tag 不在列表中 | 告知用户，停止 |
| Tag 名称模糊 | 显示所有匹配路径及笔记数，让用户选择 |
| 交集为空 | 告知用户"未找到同时持有这些标签的笔记" |
| 单个 tag | 直接返回该 tag 的笔记（无需交集） |
| per_tag 中 count=0 | 警告：该 tag 存在但无笔记 |

---

## 模式 5：hybrid

### 描述
组合多个模式的搜索结果，进行交叉验证。

### 使用场景
- 需要同时从多个来源获取结果
- 如：先查 memory_db，再查 docs_scope，合并去重

### 步骤
1. 依次调用各模式
2. 按 note ID 去重
3. 合并结果
4. 可选：按 score 加权排序

### 输出格式
与各模式一致，通过 `source` 字段区分来源。

---

## 规则

- Bear `repo/*` 不走默认向量索引，只做显式读取
- 统一输出结果结构
- 默认服务 `#memory` / `#memory/daily` / `path/docs/*`

## 与 context-router 协作

```
用户/Agent 发起搜索请求
        ↓
context-router: 决定用什么模式
        ↓
search: 执行对应模式的 workflow
```
