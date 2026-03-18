"""Bear Data Adapter.

Data transformation and parsing for Bear notes.
Does NOT make MCP calls - expects data from host layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class BearNote:
    """Represents a Bear note."""

    id: str
    title: str
    text: str
    tags: list[str]
    created: str | None = None
    modified: str | None = None


class BearAdapter:
    """Adapter for Bear note data transformation.

    This class does NOT make MCP calls.
    It receives note data from host layer and provides:
    - Data parsing and validation
    - Content extraction
    - Format conversion
    """

    @staticmethod
    def is_available() -> bool:
        """Check if Bear MCP is available (host layer responsibility)."""
        import os

        return os.environ.get("OPENCODE_WORKSPACE") is not None

    @staticmethod
    def parse_note_data(data: dict[str, Any]) -> BearNote | None:
        """Parse raw note data into BearNote.

        Args:
            data: Raw note data from Bear MCP.

        Returns:
            BearNote if valid, None otherwise.
        """
        if not data:
            return None

        note_id = data.get("id")
        title = data.get("title", "Untitled")
        text = data.get("text", "")
        tags = data.get("tags", [])

        if not note_id:
            return None

        return BearNote(
            id=note_id,
            title=title,
            text=text,
            tags=tags if isinstance(tags, list) else [],
            created=data.get("created"),
            modified=data.get("modified"),
        )

    @staticmethod
    def extract_daily_date(title: str) -> str | None:
        """Extract date from daily note title.

        Args:
            title: Note title.

        Returns:
            Date string (YYYY-MM-DD) if found, None otherwise.
        """
        import re

        match = re.search(r"(\d{4}-\d{2}-\d{2})", title)
        return match.group(1) if match else None

    @staticmethod
    def is_memory_note(title: str) -> bool:
        """Check if title indicates a memory note (not daily).

        Args:
            title: Note title.

        Returns:
            True if it's a memory note, False if daily/workstream.
        """
        lowered = title.lower()
        return "daily" not in lowered and "workstream" not in lowered

    @staticmethod
    def is_pending_daily(text: str) -> bool:
        """Check if daily note has pending status.

        Args:
            text: Note content.

        Returns:
            True if pending, False otherwise.
        """
        lowered = text.lower()
        return "pending" in lowered or "status: pending" in lowered
