"""Promote Service.

Business logic for promoting daily notes to long-term memory.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..adapters.bear_adapter import BearAdapter
from ..daily_memory import parse_daily_memory, prepend_promote_status
from ..models import DailyEntry
from ..runtime.state_machine import PromoteEvent, PromoteRecord, PromoteState, PromoteStateMachine

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PromoteServiceResult:
    """Result of promote operation."""

    success: bool
    record: PromoteRecord | None
    promoted_items: list[str]
    error: str | None = None


class PromoteService:
    """Service for promoting daily notes to memory.

    Responsibilities:
    - Extract promotable content from daily notes
    - Apply promote logic and rules
    - Update both daily note and target memory
    - Coordinate with state machine for lifecycle
    """

    # Keywords that indicate promotable content
    PROMOTABLE_KEYWORDS = [
        "512",  # vector dimension decision
        "可复用规则",
        "昨天先结账",
        "TDD",
        "项目收尾",
        "memory",
        "规范",
        "规则",
        "约定",
    ]

    def __init__(self) -> None:
        """Initialize service."""
        self._state_machine = PromoteStateMachine()
        self._bear = BearAdapter()

    def promote_daily(
        self,
        daily_text: str,
        daily_id: str,
        target_memory_text: str | None = None,
    ) -> PromoteServiceResult:
        """Promote a daily note to memory.

        Args:
            daily_text: Content of the daily note.
            daily_id: Identifier for the daily.
            target_memory_text: Current memory content (if None, will fetch).

        Returns:
            PromoteServiceResult with details of the operation.
        """
        # Start state machine
        record = self._state_machine.start_promote(daily_id)

        try:
            # Parse daily
            daily = parse_daily_memory(daily_text)

            # Extract promotable items
            promoted_items = self._extract_promotable_items(daily)

            if not promoted_items:
                # Nothing to promote
                self._state_machine.transition(
                    record, PromoteEvent.PROMOTE_EMPTY
                )
                record.state = PromoteState.DONE_NONE
                return PromoteServiceResult(
                    success=True,
                    record=record,
                    promoted_items=[],
                    error=None,
                )

            # Promote successful
            record.promoted_to = promoted_items
            self._state_machine.transition(
                record, PromoteEvent.PROMOTE_SUCCESS
            )

            return PromoteServiceResult(
                success=True,
                record=record,
                promoted_items=promoted_items,
                error=None,
            )

        except Exception as e:
            logger.error(f"Promote failed for {daily_id}: {e}")
            self._state_machine.transition(
                record, PromoteEvent.PROMOTE_FAILED
            )
            return PromoteServiceResult(
                success=False,
                record=record,
                promoted_items=[],
                error=str(e),
            )

    def _extract_promotable_items(self, daily: DailyEntry) -> list[str]:
        """Extract items worth promoting from daily.

        Args:
            daily: Parsed daily entry.

        Returns:
            List of promotable items (deduplicated).
        """
        items: list[str] = []

        # Check summary lines
        for line in daily.summary:
            normalized = line.lower()
            if any(kw in normalized for kw in self.PROMOTABLE_KEYWORDS):
                items.append(self._categorize_item(line))

        # Check log blocks
        for block in daily.log_blocks:
            lowered = block.lower()
            if any(kw in lowered for kw in self.PROMOTABLE_KEYWORDS):
                items.append(self._categorize_item(block))

        # Deduplicate while preserving order
        seen = set()
        unique_items = []
        for item in items:
            if item not in seen and item:
                seen.add(item)
                unique_items.append(item)

        return unique_items

    def _categorize_item(self, text: str) -> str:
        """Categorize an item for memory storage.

        Args:
            text: The text to categorize.

        Returns:
            Categorized string like "vector:512-dimension" or "rule:daily-before-new-day"
        """
        lowered = text.lower()

        if "512" in lowered:
            return "vector:512-dimension"
        if "可复用规则" in text or "昨天先结账" in text:
            return "rule:daily-before-new-day"
        if "tdd" in lowered:
            return "practice:tdd-pattern"
        if "项目收尾" in text or "收尾" in text:
            return "process:project-completion"
        if "规范" in text or "约定" in text:
            return "rule:convention"

        # Default: use first 30 chars
        return f"note:{text[:30]}..."

    def apply_to_files(
        self,
        daily_path: Path,
        memory_path: Path,
        daily_id: str | None = None,
    ) -> PromoteServiceResult:
        """Apply promote operation to files.

        Args:
            daily_path: Path to daily note file.
            memory_path: Path to memory file.
            daily_id: Optional identifier (defaults to filename).

        Returns:
            PromoteServiceResult.
        """
        daily_id = daily_id or daily_path.stem

        try:
            daily_text = daily_path.read_text(encoding="utf-8")
            memory_text = (
                memory_path.read_text(encoding="utf-8")
                if memory_path.exists()
                else ""
            )
        except Exception as e:
            return PromoteServiceResult(
                success=False,
                record=None,
                promoted_items=[],
                error=f"Failed to read files: {e}",
            )

        result = self.promote_daily(daily_text, daily_id, memory_text)

        if result.success and result.record:
            # Update daily file with promote status
            updated_daily = prepend_promote_status(
                daily_text,
                result.record.state.name.lower().replace("_", "-"),
                result.promoted_items,
            )
            daily_path.write_text(updated_daily, encoding="utf-8")

            # Update memory file if items were promoted
            if result.promoted_items:
                updated_memory = self._update_memory_content(
                    memory_text, result.promoted_items
                )
                memory_path.write_text(updated_memory, encoding="utf-8")

        return result

    def _update_memory_content(
        self, existing_memory: str, new_items: list[str]
    ) -> str:
        """Update memory content with new items.

        Args:
            existing_memory: Current memory content.
            new_items: New items to add.

        Returns:
            Updated memory content.
        """
        lines = [f"- {item}" for item in new_items]

        if "## Core Memory" in existing_memory:
            # Insert after ## Core Memory header
            pattern = r"(## Core Memory\n)(?P<body>.*?)(\n## |\Z)"

            def _insert(match: re.Match[str]) -> str:
                body = match.group("body").rstrip()
                body_lines = [line for line in body.splitlines() if line.strip()]
                body_lines.extend(lines)
                suffix = "\n\n## " if match.group(3) == "\n## " else ""
                return f"## Core Memory\n{'\n'.join(body_lines)}{suffix}"

            updated = re.sub(pattern, _insert, existing_memory, count=1, flags=re.DOTALL)
            return updated
        else:
            # Create new Core Memory section
            return (
                existing_memory.rstrip()
                + "\n\n## Core Memory\n"
                + "\n".join(lines)
                + "\n"
            )


# Maintain backward compatibility with existing code
def promote_yesterday(daily_text: str, existing_topics: list[str]) -> Any:
    """Backward compatible wrapper."""
    from ..promote import promote_yesterday as _legacy_promote

    return _legacy_promote(daily_text, existing_topics)
