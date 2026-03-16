from pathlib import Path

from bear_brain.config import load_settings
from bear_brain.memory_store import ensure_schema


def test_vector_baseline_bootstrap(tmp_path: Path) -> None:
    settings = load_settings(tmp_path)
    ensure_schema(settings.memory_db)
    assert settings.embedding_model == "qwen3-embedding:0.6b"
    assert settings.memory_db.exists()
