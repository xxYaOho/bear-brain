"""CLI Entry Point.

Backward-compatible CLI entry point.
Actual implementation moved to support.cli module.
"""

from __future__ import annotations

# Re-export from support layer for backward compatibility
from .support.cli import (
    _append_daily,
    _bootstrap,
    _default_daily_dir,
    _default_docs_dir,
    _default_memory_file,
    _embed_memory_file,
    _latest_daily_file,
    _promote_yesterday,
    _publish_doc,
    _search,
    build_parser,
    main,
)

__all__ = [
    "main",
    "build_parser",
    "_bootstrap",
    "_promote_yesterday",
    "_search",
    "_publish_doc",
    "_append_daily",
    "_default_memory_file",
    "_default_daily_dir",
    "_default_docs_dir",
    "_latest_daily_file",
    "_embed_memory_file",
]
