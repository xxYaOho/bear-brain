"""Memory Preload Module.

Provides automatic loading of #memory content at session start.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..adapters.bear_adapter import BearAdapter, BearNote

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class PreloadResult:
    """Result of memory preload operation."""

    success: bool
    content: str
    source: str  # "bear", "file", "none"
    error: str | None = None


class MemoryPreloader:
    """Handles preloading of memory content.

    Configuration:
        - BB_PRELOAD_ENABLED: "true" (default) or "false"
        - BB_PRELOAD_SOURCE: "bear" (default) or "file"
        - BB_MEMORY_FILE: Path to memory file (if source="file")
    """

    def __init__(
        self,
        enabled: bool | None = None,
        source: str | None = None,
        file_path: Path | str | None = None,
    ) -> None:
        """Initialize preloader.

        Args:
            enabled: Whether preload is enabled (defaults from env)
            source: Source type "bear" or "file" (defaults from env)
            file_path: Path to memory file if source="file"
        """
        self._enabled = (
            enabled
            if enabled is not None
            else os.environ.get("BB_PRELOAD_ENABLED", "true").lower() == "true"
        )
        self._source = source or os.environ.get("BB_PRELOAD_SOURCE", "bear")
        self._file_path = Path(file_path) if file_path else None
        self._bear = BearAdapter()

    def preload(self) -> PreloadResult:
        """Execute preload and return result.

        Returns:
            PreloadResult with content and status.
        """
        if not self._enabled:
            logger.info("Memory preload disabled")
            return PreloadResult(
                success=True,
                content="",
                source="none",
                error=None,
            )

        if self._source == "bear":
            return self._preload_from_bear()
        elif self._source == "file":
            return self._preload_from_file()
        else:
            return PreloadResult(
                success=False,
                content="",
                source="none",
                error=f"Unknown source: {self._source}",
            )

    def _preload_from_bear(self) -> PreloadResult:
        """Load memory from Bear note."""
        if not self._bear.is_available():
            logger.warning("Bear MCP not available, skipping preload")
            return PreloadResult(
                success=True,  # Don't fail session if Bear unavailable
                content="",
                source="none",
                error="Bear MCP not available",
            )

        note = self._bear.get_memory_note()
        if note is None:
            logger.warning("#memory note not found")
            return PreloadResult(
                success=True,
                content="",
                source="none",
                error="#memory note not found",
            )

        logger.info(f"Loaded #memory from Bear: {note.title}")
        return PreloadResult(
            success=True,
            content=note.text,
            source="bear",
            error=None,
        )

    def _preload_from_file(self) -> PreloadResult:
        """Load memory from local file."""
        file_path = self._file_path or Path("memory.md")

        if not file_path.exists():
            logger.warning(f"Memory file not found: {file_path}")
            return PreloadResult(
                success=True,
                content="",
                source="none",
                error=f"Memory file not found: {file_path}",
            )

        try:
            content = file_path.read_text(encoding="utf-8")
            logger.info(f"Loaded memory from file: {file_path}")
            return PreloadResult(
                success=True,
                content=content,
                source="file",
                error=None,
            )
        except Exception as e:
            logger.error(f"Failed to read memory file: {e}")
            return PreloadResult(
                success=False,
                content="",
                source="none",
                error=str(e),
            )


def preload_memory(
    enabled: bool | None = None,
    source: str | None = None,
    file_path: Path | str | None = None,
) -> PreloadResult:
    """Convenience function to preload memory.

    Args:
        enabled: Whether preload is enabled
        source: Source type "bear" or "file"
        file_path: Path to memory file

    Returns:
        PreloadResult with content and status.
    """
    preloader = MemoryPreloader(
        enabled=enabled,
        source=source,
        file_path=file_path,
    )
    return preloader.preload()


def get_preload_context() -> dict[str, Any]:
    """Get context dict for injection into agent session.

    Returns:
        Dict with "memory_content" key if successful.
    """
    result = preload_memory()
    context: dict[str, Any] = {}

    if result.success and result.content:
        context["memory_content"] = result.content
        context["memory_source"] = result.source

    return context
