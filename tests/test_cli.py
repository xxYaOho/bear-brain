from datetime import date
from pathlib import Path
from subprocess import run


def test_cli_help_runs() -> None:
    result = run(
        ["uv", "run", "python", "memory_worker.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "promote-yesterday" in result.stdout


def test_cli_bootstrap_creates_db(tmp_path: Path) -> None:
    result = run(
        ["uv", "run", "python", "memory_worker.py", "bootstrap", "--project-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (tmp_path / "data" / "db" / "memory.db").exists()


def test_cli_publish_doc_creates_spec(tmp_path: Path) -> None:
    result = run(
        [
            "uv",
            "run",
            "python",
            "memory_worker.py",
            "publish-doc",
            "--project-root",
            str(tmp_path),
            "--doc-type",
            "spec",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (tmp_path / "docs" / "product" / "SPEC.md").exists()


def test_cli_search_returns_matching_hit(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "db" / "memory.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    bootstrap = run(
        ["uv", "run", "python", "memory_worker.py", "bootstrap", "--project-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert bootstrap.returncode == 0

    seed = run(
        [
            "uv",
            "run",
            "python",
            "-c",
            (
                "from pathlib import Path; "
                "from bear_brain.memory_store import upsert_document; "
                f"upsert_document(Path(r'{db_path}'), source='memory', source_id='root', "
                "title='Memory Root', content='固定使用 512 维 embedding', "
                "updated_at='2026-03-16T10:00:00Z')"
            ),
        ],
        capture_output=True,
        text=True,
    )
    assert seed.returncode == 0

    result = run(
        [
            "uv",
            "run",
            "python",
            "memory_worker.py",
            "search",
            "--project-root",
            str(tmp_path),
            "--query",
            "512 维",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Memory Root" in result.stdout


def test_cli_search_can_index_local_markdown_sources(tmp_path: Path) -> None:
    memory_file = tmp_path / "memory.md"
    daily_dir = tmp_path / "daily"
    docs_dir = tmp_path / "docs"

    daily_dir.mkdir()
    (docs_dir / "product").mkdir(parents=True)

    memory_file.write_text(
        "## Position\n长期经验入口\n\n## Core Memory\n- 固定使用 512 维 embedding\n",
        encoding="utf-8",
    )
    (daily_dir / "2026-03-16.md").write_text(
        "## Summary\n- 今日继续打磨 BB\n",
        encoding="utf-8",
    )
    (docs_dir / "product" / "SPEC.md").write_text(
        "# SPEC\n\n## Constraints\n\n默认使用本地搜索\n",
        encoding="utf-8",
    )

    result = run(
        [
            "uv",
            "run",
            "python",
            "memory_worker.py",
            "search",
            "--project-root",
            str(tmp_path),
            "--query",
            "本地搜索",
            "--memory-file",
            str(memory_file),
            "--daily-dir",
            str(daily_dir),
            "--docs-dir",
            str(docs_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "SPEC" in result.stdout


def test_cli_search_discovers_default_local_sources(tmp_path: Path) -> None:
    (tmp_path / "daily").mkdir()
    (tmp_path / "docs" / "product").mkdir(parents=True)

    (tmp_path / "memory.md").write_text(
        "## Core Memory\n- 默认检索 memory\n",
        encoding="utf-8",
    )
    (tmp_path / "daily" / "2026-03-16.md").write_text(
        "## Summary\n- 今天确认默认索引\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "product" / "SPEC.md").write_text(
        "# SPEC\n\n## Notes\n\n默认使用本地搜索\n",
        encoding="utf-8",
    )

    result = run(
        [
            "uv",
            "run",
            "python",
            "memory_worker.py",
            "search",
            "--project-root",
            str(tmp_path),
            "--query",
            "本地搜索",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "SPEC" in result.stdout


def test_cli_search_uses_ollama_env_vars(tmp_path: Path) -> None:
    result = run(
        [
            "uv",
            "run",
            "python",
            "-c",
            (
                "from pathlib import Path; "
                "from bear_brain.config import load_settings; "
                f"s=load_settings(Path(r'{tmp_path}')); "
                "print(s.ollama_base_url); "
                "print(s.embedding_model)"
            ),
        ],
        capture_output=True,
        text=True,
        env={
            "PATH": __import__("os").environ["PATH"],
            "HOME": __import__("os").environ.get("HOME", ""),
            "BEAR_BRAIN_OLLAMA_BASE_URL": "http://localhost:9999",
            "BEAR_BRAIN_EMBEDDING_MODEL": "custom-model",
        },
    )
    assert result.returncode == 0
    assert "http://localhost:9999" in result.stdout
    assert "custom-model" in result.stdout


def test_cli_promote_yesterday_updates_daily_and_memory(tmp_path: Path) -> None:
    daily_path = tmp_path / "Memory Daily 2026-03-15.md"
    memory_path = tmp_path / "memory.md"
    daily_path.write_text(
        "## Promote Status\n"
        "- Status: pending\n"
        "- Promoted At:\n"
        "- Promoted To:\n\n"
        "## Summary\n"
        "- 今日主线：打磨 memory 设计\n"
        "- 关键发现：需要固定 512 维 embedding\n"
        "- 是否有值得提炼的内容：有\n\n"
        "## Log\n"
        "### 2026-03-15 11:00\n"
        "- 做了什么：整理向量检索方案\n"
        "- 发现了什么：第一阶段应固定 512 维并在启动时校验\n"
        "- 当前判断是什么：把这条写入长期 memory\n",
        encoding="utf-8",
    )
    memory_path.write_text(
        "## Position\n长期经验入口\n\n## Core Memory\n- 现有规则\n",
        encoding="utf-8",
    )

    result = run(
        [
            "uv",
            "run",
            "python",
            "memory_worker.py",
            "promote-yesterday",
            "--daily-file",
            str(daily_path),
            "--memory-file",
            str(memory_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "done-promoted" in daily_path.read_text(encoding="utf-8")
    assert "vector:512-dimension" in memory_path.read_text(encoding="utf-8")


def test_cli_promote_yesterday_discovers_latest_daily_and_memory(tmp_path: Path) -> None:
    (tmp_path / "daily").mkdir()
    (tmp_path / "daily" / "2026-03-15.md").write_text(
        "## Promote Status\n"
        "- Status: pending\n"
        "- Promoted At:\n"
        "- Promoted To:\n\n"
        "## Summary\n"
        "- 今日主线：旧数据\n"
        "- 是否有值得提炼的内容：无\n\n"
        "## Log\n"
        "### 2026-03-15 09:00\n"
        "- 做了什么：旧记录\n",
        encoding="utf-8",
    )
    latest_daily = tmp_path / "daily" / "2026-03-16.md"
    latest_daily.write_text(
        "## Promote Status\n"
        "- Status: pending\n"
        "- Promoted At:\n"
        "- Promoted To:\n\n"
        "## Summary\n"
        "- 今日主线：验证默认发现\n"
        "- 是否有值得提炼的内容：有\n\n"
        "## Log\n"
        "### 2026-03-16 09:00\n"
        "- 发现了什么：昨天先结账，今天再开工\n",
        encoding="utf-8",
    )
    memory_path = tmp_path / "memory.md"
    memory_path.write_text(
        "## Position\n长期经验入口\n\n## Core Memory\n- 现有规则\n",
        encoding="utf-8",
    )

    result = run(
        [
            "uv",
            "run",
            "python",
            "memory_worker.py",
            "promote-yesterday",
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "done-promoted" in latest_daily.read_text(encoding="utf-8")
    assert "rule:daily-before-new-day" in memory_path.read_text(encoding="utf-8")


def test_cli_append_daily_skips_non_bear_brain_project_by_default(tmp_path: Path) -> None:
    result = run(
        [
            "uv",
            "run",
            "python",
            "memory_worker.py",
            "append-daily",
            "--project-root",
            str(tmp_path),
            "--did",
            "完成代码实现",
            "--found",
            "发现默认路径还不够顺手",
            "--judgment",
            "需要继续收敛 hook",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert not (tmp_path / "daily").exists()


def test_cli_append_daily_uses_global_flag_for_any_project(tmp_path: Path) -> None:
    result = run(
        [
            "uv",
            "run",
            "python",
            "memory_worker.py",
            "append-daily",
            "--project-root",
            str(tmp_path),
            "--did",
            "完成代码实现",
            "--found",
            "发现默认路径还不够顺手",
            "--judgment",
            "需要继续收敛 hook",
        ],
        capture_output=True,
        text=True,
        env={
            "PATH": __import__("os").environ["PATH"],
            "HOME": __import__("os").environ.get("HOME", ""),
            "BEAR_BRAIN_DAILY_GLOBAL": "true",
        },
    )

    assert result.returncode == 0
    daily_path = tmp_path / "daily" / f"{date.today().isoformat()}.md"
    assert daily_path.exists()
    daily_text = daily_path.read_text(encoding="utf-8")
    assert "完成代码实现" in daily_text
    assert "发现默认路径还不够顺手" in daily_text
    assert "需要继续收敛 hook" in daily_text
