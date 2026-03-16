from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path


@dataclass(slots=True)
class Settings:
    project_root: Path
    data_dir: Path
    cache_dir: Path
    state_dir: Path
    docs_dir: Path
    memory_db: Path
    ollama_base_url: str
    embedding_model: str


def load_settings(project_root: Path) -> Settings:
    data_dir = project_root / "data"
    return Settings(
        project_root=project_root,
        data_dir=data_dir,
        cache_dir=data_dir / "cache",
        state_dir=data_dir / "state",
        docs_dir=project_root / "docs",
        memory_db=data_dir / "db" / "memory.db",
        ollama_base_url=getenv("BEAR_BRAIN_OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        embedding_model=getenv("BEAR_BRAIN_EMBEDDING_MODEL", "qwen3-embedding:0.6b"),
    )
