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
