from bear_brain.daily_memory import parse_daily_memory, render_promote_status


def test_parse_daily_memory_extracts_promote_status(sample_daily_text: str) -> None:
    daily = parse_daily_memory(sample_daily_text)
    assert daily.promote.state == "pending"
    assert daily.summary


def test_render_promote_status_updates_block() -> None:
    text = render_promote_status("done-none", "2026-03-16 09:00", [])
    assert "done-none" in text
