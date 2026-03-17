from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path


def _load_strict_bool_env(name: str, default: bool) -> bool:
    raw = getenv(name)
    if raw is None:
        return default
    if raw == "true":
        return True
    if raw == "false":
        return False
    raise ValueError(f"{name} must be 'true' or 'false'")


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
    daily_global: bool
    preload_enabled: bool
    preload_source: str
    preload_file_path: Path | None


def load_settings(project_root: Path) -> Settings:
    data_dir = project_root / "data"
    preload_file = getenv("BB_MEMORY_FILE")
    return Settings(
        project_root=project_root,
        data_dir=data_dir,
        cache_dir=data_dir / "cache",
        state_dir=data_dir / "state",
        docs_dir=project_root / "docs",
        memory_db=data_dir / "db" / "memory.db",
        ollama_base_url=getenv("BEAR_BRAIN_OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        embedding_model=getenv("BEAR_BRAIN_EMBEDDING_MODEL", "qwen3-embedding:0.6b"),
        daily_global=_load_strict_bool_env("BEAR_BRAIN_DAILY_GLOBAL", False),
        preload_enabled=_load_strict_bool_env("BB_PRELOAD_ENABLED", True),
        preload_source=getenv("BB_PRELOAD_SOURCE", "bear"),
        preload_file_path=Path(preload_file) if preload_file else None,
    )
