from pathlib import Path

from bear_brain.config import load_settings


def test_load_settings_has_local_defaults(tmp_path: Path) -> None:
    settings = load_settings(project_root=tmp_path)
    assert settings.memory_db.name == "memory.db"
    assert settings.docs_dir.name == "docs"
