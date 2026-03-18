"""Legacy Search Support.

Backward-compatible search utilities.
Re-exports from search and search_index modules.
"""

from __future__ import annotations

# Re-export for backward compatibility
from ..search import (
    SearchHit,
    make_ollama_embedder,
    search_memory_db,
)
from ..search_index import (
    sync_local_sources,
)

__all__ = [
    "SearchHit",
    "make_ollama_embedder",
    "search_memory_db",
    "sync_local_sources",
]
