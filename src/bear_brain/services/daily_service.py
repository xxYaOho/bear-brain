"""Daily Service.

Business logic for managing daily notes.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.bear_adapter import BearAdapter
from ..daily_memory import parse_daily_memory, render_promote_status
from ..models import DailyEntry, PromoteStatus

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DailyServiceResult:
    """Result of daily operation."""

    success: bool
    daily_id: str | None
    error: str | None = None


class DailyService:
    """Service for managing daily notes.

    Responsibilities:
    - Create and append daily entries
    - Parse daily note structure
    - Track daily metadata
    - Coordinate with Bear notes
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize service.

        Args:
            project_root: Root directory for daily files.
        """
        self._project_root = project_root or Path.cwd()
        self._daily_dir = self._project_root / "daily"
        self._bear = BearAdapter()

    def create_daily(
        self,
        date: datetime | None = None,
        title: str | None = None,
        content: str | None = None,
    ) -> DailyServiceResult:
        """Create a new daily note.

        Args:
            date: Date for the daily (defaults to today).
            title: Optional custom title.
            content: Optional initial content.

        Returns:
            DailyServiceResult with daily ID.
        """
        date = date or datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        daily_id = f"memory-daily-{date_str}"

        # Ensure daily directory exists
        self._daily_dir.mkdir(parents=True, exist_ok=True)
        daily_path = self._daily_dir / f"{date_str}.md"

        if daily_path.exists():
            return DailyServiceResult(
                success=False,
                daily_id=daily_id,
                error=f"Daily already exists: {daily_path}",
            )

        # Generate content
        title = title or f"memory-daily-{date_str}"
        content = content or self._generate_daily_template(date)

        try:
            daily_path.write_text(content, encoding="utf-8")
            logger.info(f"Created daily: {daily_path}")
            return DailyServiceResult(
                success=True,
                daily_id=daily_id,
                error=None,
            )
        except Exception as e:
            logger.error(f"Failed to create daily: {e}")
            return DailyServiceResult(
                success=False,
                daily_id=daily_id,
                error=str(e),
            )

    def append_entry(
        self,
        entry_text: str,
        date: datetime | None = None,
    ) -> DailyServiceResult:
        """Append an entry to today's daily.

        Args:
            entry_text: Text to append.
            date: Date for the daily (defaults to today).

        Returns:
            DailyServiceResult.
        """
        date = date or datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        daily_id = f"memory-daily-{date_str}"

        daily_path = self._daily_dir / f"{date_str}.md"

        # Create if doesn't exist
        if not daily_path.exists():
            result = self.create_daily(date)
            if not result.success:
                return result

        try:
            # Read existing content
            existing = daily_path.read_text(encoding="utf-8")

            # Append new entry
            timestamp = date.strftime("%Y-%m-%d %H:%M")
            entry = f"\n### {timestamp}\n{entry_text}\n"

            # Find Log section and append
            if "## Log" in existing:
                updated = existing + entry
            else:
                updated = existing + f"\n## Log{entry}"

            daily_path.write_text(updated, encoding="utf-8")
            logger.info(f"Appended entry to daily: {daily_path}")

            return DailyServiceResult(
                success=True,
                daily_id=daily_id,
                error=None,
            )
        except Exception as e:
            logger.error(f"Failed to append entry: {e}")
            return DailyServiceResult(
                success=False,
                daily_id=daily_id,
                error=str(e),
            )

    def parse_daily(self, daily_id: str) -> DailyEntry | None:
        """Parse a daily note.

        Args:
            daily_id: Daily identifier (e.g., "memory-daily-2026-03-17").

        Returns:
            DailyEntry if found, None otherwise.
        """
        # Extract date from ID
        match = re.match(r"memory-daily-(\d{4}-\d{2}-\d{2})", daily_id)
        if not match:
            return None

        date_str = match.group(1)
        daily_path = self._daily_dir / f"{date_str}.md"

        if not daily_path.exists():
            return None

        try:
            text = daily_path.read_text(encoding="utf-8")
            return parse_daily_memory(text)
        except Exception as e:
            logger.error(f"Failed to parse daily: {e}")
            return None

    def list_dailies(self, days: int = 7) -> list[str]:
        """List recent daily IDs.

        Args:
            days: Number of days to look back.

        Returns:
            List of daily IDs (most recent first).
        """
        if not self._daily_dir.exists():
            return []

        dailies = []
        for path in sorted(self._daily_dir.glob("*.md"), reverse=True):
            if path.is_file():
                date_str = path.stem  # YYYY-MM-DD
                dailies.append(f"memory-daily-{date_str}")
                if len(dailies) >= days:
                    break

        return dailies

    def get_daily_path(self, daily_id: str) -> Path | None:
        """Get file path for a daily ID.

        Args:
            daily_id: Daily identifier.

        Returns:
            Path if exists, None otherwise.
        """
        match = re.match(r"memory-daily-(\d{4}-\d{2}-\d{2})", daily_id)
        if not match:
            return None

        date_str = match.group(1)
        daily_path = self._daily_dir / f"{date_str}.md"

        return daily_path if daily_path.exists() else None

    def _generate_daily_template(self, date: datetime) -> str:
        """Generate default daily template.

        Args:
            date: Date for the daily.

        Returns:
            Template content.
        """
        date_str = date.strftime("%Y-%m-%d")
        return f"""# memory-daily-{date_str}
---

## Promote Status
- Status: pending
- Promoted At: -
- Promoted To: -

## Summary
- 今日主线：
- 关键发现：
- 是否值得提炼：

## Log
"""


class DailyHookService:
    """Service for handling daily hook operations.

    This service integrates with OpenCode hooks to automatically
    append entries to daily notes.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize service."""
        self._daily_service = DailyService(project_root)

    def should_write_daily(self, project_root: Path) -> bool:
        """Check if daily should be written for this project.

        Args:
            project_root: Project root directory.

        Returns:
            True if daily should be written.
        """
        import os

        # Check if this is the bear-brain project
        if (project_root / "memory_worker.py").exists():
            return True

        # Check global setting
        if os.environ.get("BEAR_BRAIN_DAILY_GLOBAL", "").lower() == "true":
            return True

        return False

    def append_hook_entry(
        self,
        did: str,
        found: str,
        judgment: str,
    ) -> DailyServiceResult:
        """Append an entry from hook.

        Args:
            did: What was done.
            found: What was discovered.
            judgment: Current judgment.

        Returns:
            DailyServiceResult.
        """
        entry = f"- 做了什么：{did}\n- 发现了什么：{found}\n- 当前判断是什么：{judgment}"
        return self._daily_service.append_entry(entry)
