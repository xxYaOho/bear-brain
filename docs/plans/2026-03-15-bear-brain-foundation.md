# Bear-Brain 基础实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建 Bear-Brain 的第一版本地基础能力：本地 memory store、daily 到 memory 的提炼流程、文档发布、memory-first 检索，以及纳入仓库管理的 skill 源文件。

**Architecture:** Bear 继续作为编辑界面与活文档来源。仓库内部用 Python 实现本地执行核心：解析 Bear 风格笔记结构、维护本地 SQLite memory store、把 `#memory/daily` 提炼进 `#memory`，并以 memory-first 路由搜索 `#memory`、`#memory/daily` 与 `path/docs/*`。skill 定义以源码形式保存在仓库中，作为后续打包与实现的真实来源。

**Tech Stack:** Python 3.12+、`sqlite3`、`sqlite-vec`、`ollama`、`pytest`、`ruff`、位于 `skills/bearbrain/` 下的 Markdown skill 源文件。

---

## 建议的仓库结构

```text
src/bear_brain/
  __init__.py
  config.py
  models.py
  paths.py
  daily_memory.py
  memory_store.py
  promote.py
  docs_publish.py
  search.py
  router.py
  cli.py
memory_worker.py
data/
  db/
    memory.db
  cache/
  state/
skills/bearbrain/
  bear-editing/SKILL.md
  write-core/SKILL.md
  governance-core/SKILL.md
  search-core/SKILL.md
  promote-memory/SKILL.md
  doc-publish/SKILL.md
  workstream/SKILL.md
  memory/SKILL.md
  book-entry/SKILL.md
  admission/SKILL.md
  note-lint/SKILL.md
tests/
  test_config.py
  test_models.py
  test_daily_memory.py
  test_memory_store.py
  test_promote.py
  test_docs_publish.py
  test_search_router.py
  test_cli.py
  test_skill_files.py
  test_end_to_end.py
  fixtures/
    daily/
    memory/
    docs/
    book/
    search/
docs/
  product/SPEC.md
  guide/GUIDE.md
  CHANGELOG.md
  COMPLETIONS.md
  DECISIONS.md
  plans/2026-03-15-bear-brain-foundation.md

# PRD 快照、额外 guide 文档、releases 文档等，等项目真正需要时再扩展。
```

## 实现原则

- 优先实现最小可用的本地系统，不提前泛化基础设施。
- 始终把 `#memory` 视为默认继承入口，把 `#memory/daily` 视为原料层。
- Bear 特定的编辑行为应收敛在 skill 文档与解析模块中，不要散落成临时脚本。
- 未经用户明确要求，不要创建 git commit。

## Vector DB 设计方案（第一阶段）

### 目标
- 在本地提供稳定、可重建的语义检索层。
- 优先服务 `#memory` 与 `#memory/daily`，并在存在明确 repo / workstream 上下文时补充 `path/docs/*`。
- 不做远程服务，不做 Bear 全库镜像。

### 组成
- `ollama`：本地 embedding 服务。
- 模型：`qwen3-embedding:0.6b`。
- 向量维度：第一阶段按 **512** 固定实现，并在启动时用实际 embedding 返回值做一次校验；若返回维度不是 512，则报错并停止。
- 存储：`sqlite3` + `sqlite-vec`，与本地 `memory.db` 共存。

### 第一阶段索引范围
- `#memory`
- `#memory/daily`
- `path/docs/*`

### 不进入默认索引的内容
- Bear `repo/*`
- `book/*`

### 检索顺序
1. 默认先查 `#memory`
2. 不足时再查 `#memory/daily`
3. 只有在明确 repo / workstream 上下文时，再把 `path/docs/*` 纳入检索
4. Bear `repo/*` 只做显式读取，不做默认向量召回

### 工程约束
- embedding 模型名必须写入配置，默认值为 `qwen3-embedding:0.6b`。
- embedding 维度第一阶段固定为 `512`。
- schema 初始化时要记录模型名与维度（第一阶段固定为 `512`），避免后续模型切换导致向量不兼容。
- 若模型名或维度与既有库不一致，优先报错并要求显式重建索引，不做隐式混用。
- 检索层输出统一的 `SearchHit` 结构，屏蔽 Bear 搜索、docs 搜索、向量搜索之间的差异。
- `memory.db` 默认放在 `data/db/memory.db`，不再放在仓库根目录。
- 第一阶段不额外建立本地状态库，daily promote 状态仍以 Bear daily 笔记正文状态块为准。
- 第一阶段不强制引入 `.env` 文件；默认使用代码内稳定配置，只允许通过环境变量做少量覆盖。
- 当前仅开放两个环境变量覆盖项：`BEAR_BRAIN_OLLAMA_BASE_URL`、`BEAR_BRAIN_EMBEDDING_MODEL`。

### Bear 集成边界
- 第一阶段不直接依赖 Bear 内部数据库。
- 解析层优先处理 Bear 导出的 Markdown 或从 Bear 复制出的文本内容。
- 也就是说，核心模块要兼容 Bear 风格结构，但不把 Bear 私有数据库当成第一版实现前提。

### Benchmark 基线（第一阶段必须具备）
- 目标：给本地 `ollama + sqlite-vec` 检索一个可比较的基线，而不是等优化阶段再补。
- 最小基线内容：
  - 索引规模：30 / 100 / 300 条 mock note 的建索引耗时
  - 查询性能：单次查询延迟、批量查询平均延迟
  - 召回质量：10~20 条手工 query 的 top-3 / top-5 命中情况
  - 模型记录：固定 `qwen3-embedding:0.6b`，记录模型名、维度（512）、测试时间
- 产物形式：先以测试报告或仓库内基准文件存在，不要求第一阶段做复杂 benchmark 系统。

### 任务 1：搭建仓库基础骨架

**Files:**
- Create: `pyproject.toml`
- Create: `src/bear_brain/__init__.py`
- Create: `src/bear_brain/config.py`
- Create: `src/bear_brain/paths.py`
- Create: `memory_worker.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
from bear_brain.config import load_settings


def test_load_settings_has_local_defaults(tmp_path):
    settings = load_settings(project_root=tmp_path)
    assert settings.memory_db.name == "memory.db"
    assert settings.docs_dir.name == "docs"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py -q`
Expected: FAIL，因为 package 与 settings loader 还不存在。

**Step 3: Write minimal implementation**

实现一个最小的 `Settings` dataclass 与 `load_settings()`，从 `project_root` 推导本地默认路径，并补上 Vector DB 与数据目录配置：
- `memory_db`（默认 `data/db/memory.db`）
- `data_dir`
- `cache_dir`
- `state_dir`
- `ollama_base_url`（可由 `BEAR_BRAIN_OLLAMA_BASE_URL` 覆盖）
- `embedding_model`（默认 `qwen3-embedding:0.6b`，可由 `BEAR_BRAIN_EMBEDDING_MODEL` 覆盖）
- `docs_dir`

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(slots=True)
class Settings:
    project_root: Path
    docs_dir: Path
    memory_db: Path


def load_settings(project_root: Path) -> Settings:
    return Settings(
        project_root=project_root,
        docs_dir=project_root / "docs",
        memory_db=project_root / "memory.db",
    )
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py -q`
Expected: PASS.

### 任务 2：定义核心数据模型

**Files:**
- Create: `src/bear_brain/models.py`
- Create: `tests/test_models.py`

**Step 1: Write the failing test**

```python
from bear_brain.models import DailyEntry, PromoteStatus


def test_promote_status_defaults_to_pending():
    status = PromoteStatus()
    assert status.state == "pending"
    assert status.promoted_to == []
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_models.py -q`
Expected: FAIL，因为模型类型还不存在。

**Step 3: Write minimal implementation**

先用 Python dataclass 定义这些类型：
- `PromoteStatus`
- `DailyEntry`
- `MemoryTopic`
- `PublishedDoc`
- `SearchHit`

先避免引入过重的验证框架。

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_models.py -q`
Expected: PASS.

### 任务 3：解析并更新 `#memory/daily`

**Files:**
- Create: `src/bear_brain/daily_memory.py`
- Create: `tests/test_daily_memory.py`
- Create: `tests/fixtures/daily/daily_memory_sample.md`
- Create: `tests/fixtures/daily/daily_memory_reusable.md`

**Step 1: Write the failing test**

```python
from bear_brain.daily_memory import parse_daily_memory, render_promote_status


def test_parse_daily_memory_extracts_promote_status(sample_daily_text):
    daily = parse_daily_memory(sample_daily_text)
    assert daily.promote.state == "pending"
    assert daily.summary


def test_render_promote_status_updates_block():
    text = render_promote_status("done-none", "2026-03-16 09:00", [])
    assert "done-none" in text
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_daily_memory.py -q`
Expected: FAIL，因为解析器与状态块渲染器还不存在。

**Step 3: Write minimal implementation**

实现以下能力：
- 解析 `## Promote Status`、`## Summary`、`## Log` 三个 section
- 只更新状态块文本
- 兼容 Bear 导出的 Markdown / 复制文本
- 避免把整篇重写逻辑散落到其他模块

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_daily_memory.py -q`
Expected: PASS.

### 任务 4：实现本地 memory store 与 schema 初始化

**Files:**
- Create: `src/bear_brain/memory_store.py`
- Create: `tests/test_memory_store.py`

**Step 1: Write the failing test**

```python
from bear_brain.memory_store import ensure_schema, list_unpromoted_days


def test_ensure_schema_creates_required_tables(tmp_path):
    db_path = tmp_path / "memory.db"
    ensure_schema(db_path)
    assert db_path.exists()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_memory_store.py -q`
Expected: FAIL，因为 schema bootstrap 还不存在。

**Step 3: Write minimal implementation**

用最小 SQLite helper 建表，覆盖：
- 文档索引行
- 搜索元数据
- 向量索引元数据（至少包含 embedding 模型名、维度、更新时间）
- 后续可能需要的 promote bookkeeping

同时补上第一阶段的向量设计：
- 通过 `ollama` 调用 `qwen3-embedding:0.6b`
- 把 512 维 embedding 结果写入 `sqlite-vec`
- 初始化时校验当前模型与已存在索引的模型/维度是否一致
- 若实际返回维度不是 512，立即报错并停止初始化
- 把数据库默认落到 `data/db/memory.db`

不要过早引入通用 ORM。

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_memory_store.py -q`
Expected: PASS.

### 任务 5：实现 `promote-memory`

**Files:**
- Create: `src/bear_brain/promote.py`
- Create: `tests/test_promote.py`
- Modify: `src/bear_brain/daily_memory.py`
- Modify: `src/bear_brain/models.py`

**Step 1: Write the failing test**

```python
from bear_brain.promote import promote_yesterday


def test_promote_yesterday_marks_done_none_when_nothing_reusable(sample_daily_text):
    result = promote_yesterday(sample_daily_text, existing_topics=[])
    assert result.status.state == "done-none"


def test_promote_yesterday_extracts_reusable_items(sample_reusable_daily_text):
    result = promote_yesterday(sample_reusable_daily_text, existing_topics=[])
    assert result.status.state == "done-promoted"
    assert result.promoted_items
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_promote.py -q`
Expected: FAIL，因为提炼流程还不存在。

**Step 3: Write minimal implementation**

实现提炼流程：
- 读取一篇 daily
- 识别可复用规则、约束、方法
- 判断应写入 memory 主文件还是某个主题子笔记
- 返回可写回 daily 的状态块更新结果

最低可用提炼标准至少覆盖：
- 可迁移的方法
- 可复用的约束
- 重复出现的坑
- 明确的判断依据

提取规则要明确且保守，不要做黑箱式“聪明判断”。

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_promote.py -q`
Expected: PASS.

### 任务 6：实现 `doc-publish`

**Files:**
- Create: `src/bear_brain/docs_publish.py`
- Create: `tests/test_docs_publish.py`
- Create: `docs/product/SPEC.md`
- Create: `docs/guide/GUIDE.md`
- Create: `docs/CHANGELOG.md`
- Create: `docs/COMPLETIONS.md`
- Create: `docs/DECISIONS.md`

**Step 1: Write the failing test**

```python
from bear_brain.docs_publish import classify_publish_target


def test_spec_goes_to_product_spec():
    target = classify_publish_target(doc_type="spec")
    assert target.as_posix().endswith("docs/product/SPEC.md")
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_docs_publish.py -q`
Expected: FAIL，因为发布路由还不存在。

**Step 3: Write minimal implementation**

实现：
- 将稳定文档类型映射到目标路径
- 为第一阶段的 5 个 docs 文件生成最小骨架
- 最终发布文档中不保留源 Bear 笔记回链（按当前设计决定）

发布前最小门槛至少检查：
- 结构完整
- 已不再是讨论稿
- 已有明确目标类型（SPEC / GUIDE / CHANGELOG / COMPLETIONS / DECISIONS）
- 用户明确要求发布，或阶段已明确收束

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_docs_publish.py -q`
Expected: PASS.

### 任务 7：实现本地搜索与路由

**Files:**
- Create: `src/bear_brain/search.py`
- Create: `src/bear_brain/router.py`
- Create: `tests/test_search_router.py`
- Modify: `src/bear_brain/memory_store.py`

**Step 1: Write the failing test**

```python
from bear_brain.router import choose_search_modes


def test_router_defaults_to_memory_first():
    modes = choose_search_modes(task_type="general", repo=None, explicit_refs=False)
    assert modes[0] == "memory_db"


def test_router_adds_docs_scope_for_repo_work():
    modes = choose_search_modes(task_type="implementation", repo="bear-brain", explicit_refs=False)
    assert "docs_scope" in modes
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_search_router.py -q`
Expected: FAIL，因为 router 与 search 逻辑还不存在。

**Step 3: Write minimal implementation**

实现：
- `memory_db` 作为默认搜索模式
- `docs_scope`、`note_refs`、`tags_and`、`hybrid` 的路由逻辑
- 不同模式统一返回同一个 `SearchHit` 结构
- `memory_db` 内部通过 `ollama` + `qwen3-embedding:0.6b` 生成查询向量，并在本地 `sqlite-vec` 中检索

保持 Bear `repo/*` 不进入默认索引，只作为显式读取内容。

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_search_router.py -q`
Expected: PASS.

### 任务 8：给核心流程加一个小型 CLI

**Files:**
- Create: `src/bear_brain/cli.py`
- Modify: `memory_worker.py`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
from subprocess import run


def test_cli_help_runs():
    result = run(["python", "memory_worker.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "promote" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli.py -q`
Expected: FAIL，因为 CLI 入口还不存在。

**Step 3: Write minimal implementation**

暴露这些明确命令：
- `bootstrap`
- `promote-yesterday`
- `search`
- `publish-doc`

命令名保持朴素、直接。

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli.py -q`
Expected: PASS.

### 任务 9：把 skill 规划转成仓库内的源文件

**Files:**
- Create: `skills/bearbrain/bear-editing/SKILL.md`
- Create: `skills/bearbrain/write-core/SKILL.md`
- Create: `skills/bearbrain/governance-core/SKILL.md`
- Create: `skills/bearbrain/search-core/SKILL.md`
- Create: `skills/bearbrain/promote-memory/SKILL.md`
- Create: `skills/bearbrain/doc-publish/SKILL.md`
- Create: `tests/test_skill_files.py`

> `workstream`、`memory`、`book-entry`、`admission`、`note-lint` 等对象级 skill 第一阶段可先以轻量 stub 或引用 core skill 的方式存在，不要求全部一次写满。

**Step 1: Write the failing verification step**

```python
from pathlib import Path


def test_core_skill_files_exist():
    root = Path("skills/bearbrain")
    assert (root / "bear-editing" / "SKILL.md").exists()
    assert (root / "search-core" / "SKILL.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_skill_files.py -q`
Expected: FAIL，因为 skill 源文件还不存在。

**Step 3: Write minimal implementation**

把当前 Bear 里的规划转成 repo 内的 SKILL 源：
- metadata 保持精简
- 共性逻辑尽量收在三条 core skill 中
- 对象级 skill 保持轻量，必要时引用 core skill 中的规则

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_skill_files.py -q`
Expected: PASS.

### 任务 10：补充 mock-data 与 benchmark 基线

**Files:**
- Create: `tests/fixtures/daily/*.md`
- Create: `tests/fixtures/memory/*.md`
- Create: `tests/fixtures/docs/*.md`
- Create: `tests/fixtures/book/*.md`
- Create: `tests/fixtures/search/queries.json`
- Create: `tests/benchmark/test_vector_baseline.py`

**Step 1: Write the fixture set**

构建两层测试数据：
- 纯仓库 fixture：完全手写、稳定可控
- 半真实 seed：从 Bear `#inbox` 挑选少量代表性内容，脱敏后固化进 fixture

**Step 2: Run the benchmark baseline**

Run: `python -m pytest tests/benchmark/test_vector_baseline.py -q`
Expected: PASS，并输出第一阶段 baseline 结果。

**Step 3: Record baseline assumptions**

至少记录：
- mock note 数量
- 模型名
- 实际向量维度
- 建索引耗时
- 单次查询耗时
- top-k 命中情况

### 任务 11：跑通完整校验

**Files:**
- Modify: `README.md`
- Modify: `docs/CHANGELOG.md`
- Create: `tests/test_end_to_end.py`

**Step 1: Write the failing end-to-end test**

```python
from bear_brain.router import choose_search_modes


def test_memory_is_default_entry_point():
    assert choose_search_modes(task_type="general", repo=None, explicit_refs=False)[0] == "memory_db"
```

**Step 2: Run targeted tests, then the full suite**

Run: `python -m pytest tests/test_end_to_end.py -q`
Expected: PASS after implementation.

Run: `python -m pytest -q`
Expected: PASS.

**Step 3: Run lint**

Run: `python -m ruff check src tests`
Expected: PASS.

**Step 4: Update the top-level README**

补充说明：
- Bear-Brain 是什么
- v1 的本地优先范围
- memory-first 检索模型
- 第一阶段 `path/docs/*` 结构
- 如何运行 `memory_worker.py --help`

## Handoff notes

- Do not commit unless the user explicitly asks.
- Keep the first implementation local-only; do not reintroduce remote sync or service deployment.
- If the skill source files prove too large, split references into `references/` subfiles instead of bloating `SKILL.md`.