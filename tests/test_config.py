from pathlib import Path

import pytest

from bear_brain.config import load_settings


def test_load_settings_has_local_defaults(tmp_path: Path) -> None:
    settings = load_settings(project_root=tmp_path)
    assert settings.memory_db.name == "memory.db"
    assert settings.docs_dir.name == "docs"
    assert settings.daily_global is False


def test_load_settings_rejects_invalid_daily_global(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("BEAR_BRAIN_DAILY_GLOBAL", "yes")

    with pytest.raises(ValueError, match="BEAR_BRAIN_DAILY_GLOBAL"):
        load_settings(project_root=tmp_path)
