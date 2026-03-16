from pathlib import Path


def test_opencode_daily_plugin_exists() -> None:
    plugin_path = Path(".opencode/plugins/bear-brain-daily.js")
    assert plugin_path.exists()

    text = plugin_path.read_text(encoding="utf-8")
    assert "session.idle" in text
    assert "tui.command.execute" in text
    assert "session.compact" in text
    assert "append-daily" in text


def test_opencode_daily_plugin_has_behavior_test() -> None:
    test_path = Path(".opencode/plugins/bear-brain-daily.test.js")
    assert test_path.exists()
