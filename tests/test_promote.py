from pathlib import Path

from bear_brain.promote import apply_promote_to_files, promote_yesterday


def test_promote_yesterday_marks_done_none_when_nothing_reusable(sample_daily_text: str) -> None:
    result = promote_yesterday(sample_daily_text, existing_topics=[])
    assert result.status.state == "done-none"


def test_promote_yesterday_extracts_reusable_items(sample_reusable_daily_text: str) -> None:
    result = promote_yesterday(sample_reusable_daily_text, existing_topics=[])
    assert result.status.state == "done-promoted"
    assert result.promoted_items


def test_promote_yesterday_prefers_structured_signals(sample_reusable_daily_text: str) -> None:
    result = promote_yesterday(sample_reusable_daily_text, existing_topics=[])
    assert "rule:daily-before-new-day" in result.promoted_items
    assert "vector:512-dimension" in result.promoted_items


def test_apply_promote_to_files_appends_into_core_memory_section(tmp_path: Path) -> None:
    daily_path = tmp_path / "daily.md"
    memory_path = tmp_path / "memory.md"

    daily_path.write_text(
        "## Promote Status\n"
        "- Status: pending\n"
        "- Promoted At:\n"
        "- Promoted To:\n\n"
        "## Summary\n"
        "- 今日主线：验证 promote\n"
        "- 是否有值得提炼的内容：有\n\n"
        "## Log\n"
        "### 2026-03-15 11:00\n"
        "- 发现了什么：昨天先结账，今天再开工\n",
        encoding="utf-8",
    )
    memory_path.write_text(
        "## Position\n"
        "长期经验入口\n\n"
        "## Core Memory\n"
        "- 现有规则\n\n"
        "## Recall Keys\n"
        "- 检索 -> 本地优先\n",
        encoding="utf-8",
    )

    apply_promote_to_files(daily_path, memory_path)

    memory_text = memory_path.read_text(encoding="utf-8")
    assert (
        "## Core Memory\n- 现有规则\n- rule:daily-before-new-day\n\n## Recall Keys" in memory_text
    )
