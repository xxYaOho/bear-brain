from bear_brain.promote import promote_yesterday


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
