"""Gate / Lint Module.

Enforces memory writing rules and validates note structure.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class GateLevel(Enum):
    """Gate enforcement levels."""

    FAIL = "fail"  # Block the operation
    WARN = "warn"  # Log warning but allow
    PASS = "pass"  # No issues


@dataclass(slots=True)
class GateResult:
    """Result of gate check."""

    level: GateLevel
    message: str
    rule: str


class MemoryGate:
    """Gate for memory operations.

    Enforces rules like:
    - No guessing note IDs
    - No guessing timestamps
    - Required fields must be present
    - Valid status values
    """

    # Valid status values
    VALID_STATUSES = {
        "pending",
        "done-promoted",
        "done-none",
        "processing",
        "failed",
        "max-retries",
    }

    # Patterns that indicate guessing
    GUESSING_PATTERNS = [
        r"假设",  # Assuming
        r"可能是",  # Maybe
        r"应该",  # Should be
        r"猜测",  # Guess
    ]

    def check_daily_structure(self, content: str) -> list[GateResult]:
        """Check daily note structure.

        Args:
            content: Daily note content.

        Returns:
            List of gate results.
        """
        results = []

        # Check for required sections
        if "## Promote Status" not in content:
            results.append(
                GateResult(
                    level=GateLevel.FAIL,
                    message="Missing ## Promote Status section",
                    rule="daily_required_sections",
                )
            )

        if "## Summary" not in content:
            results.append(
                GateResult(
                    level=GateLevel.WARN,
                    message="Missing ## Summary section",
                    rule="daily_required_sections",
                )
            )

        # Check status value
        status_match = re.search(r"- Status:\s*(\S+)", content)
        if status_match:
            status = status_match.group(1).lower()
            if status not in self.VALID_STATUSES:
                results.append(
                    GateResult(
                        level=GateLevel.FAIL,
                        message=f"Invalid status: {status}",
                        rule="valid_status_values",
                    )
                )
        else:
            results.append(
                GateResult(
                    level=GateLevel.FAIL,
                    message="Missing Status field",
                    rule="daily_required_fields",
                )
            )

        return results

    def check_memory_structure(self, content: str) -> list[GateResult]:
        """Check memory note structure.

        Args:
            content: Memory note content.

        Returns:
            List of gate results.
        """
        results = []

        # Check for Core Memory section
        if "## Core Memory" not in content:
            results.append(
                GateResult(
                    level=GateLevel.WARN,
                    message="Missing ## Core Memory section",
                    rule="memory_structure",
                )
            )

        return results

    def check_no_guessing(self, text: str, context: str = "") -> list[GateResult]:
        """Check for guessing language.

        Args:
            text: Text to check.
            context: Context for error messages.

        Returns:
            List of gate results.
        """
        results = []

        for pattern in self.GUESSING_PATTERNS:
            if re.search(pattern, text):
                results.append(
                    GateResult(
                        level=GateLevel.WARN,
                        message=f"Possible guessing detected: '{pattern}' in {context}",
                        rule="no_guessing",
                    )
                )

        return results

    def check_note_id(self, note_id: str, source: str) -> list[GateResult]:
        """Check if note ID looks valid.

        Args:
            note_id: The note ID to check.
            source: Where the ID came from.

        Returns:
            List of gate results.
        """
        results = []

        # Valid UUID or similar format
        if not re.match(r"^[A-F0-9-]{36,}$", note_id, re.IGNORECASE):
            results.append(
                GateResult(
                    level=GateLevel.FAIL,
                    message=f"Invalid note ID format: {note_id}",
                    rule="valid_note_id",
                )
            )

        if source == "guessed":
            results.append(
                GateResult(
                    level=GateLevel.FAIL,
                    message="Note ID should not be guessed",
                    rule="no_guessing_note_id",
                )
            )

        return results

    def run_all_checks(
        self,
        content: str,
        content_type: str = "daily",
        metadata: dict[str, Any] | None = None,
    ) -> list[GateResult]:
        """Run all applicable gate checks.

        Args:
            content: Content to check.
            content_type: "daily", "memory", or "workstream".
            metadata: Additional metadata for checks.

        Returns:
            List of all gate results.
        """
        results = []
        metadata = metadata or {}

        # Structure checks
        if content_type == "daily":
            results.extend(self.check_daily_structure(content))
        elif content_type == "memory":
            results.extend(self.check_memory_structure(content))

        # Guessing checks
        results.extend(self.check_no_guessing(content, context=content_type))

        # Note ID check if provided
        note_id = metadata.get("note_id")
        if note_id:
            source = metadata.get("note_id_source", "unknown")
            results.extend(self.check_note_id(note_id, source))

        return results

    def should_block(self, results: list[GateResult]) -> bool:
        """Check if any results indicate blocking.

        Args:
            results: List of gate results.

        Returns:
            True if any result is FAIL level.
        """
        return any(r.level == GateLevel.FAIL for r in results)


class LintService:
    """Lint service for checking note format.

    Provides higher-level linting than gate, focusing on
    style and format consistency.
    """

    def __init__(self) -> None:
        """Initialize lint service."""
        self._gate = MemoryGate()

    def lint_daily(self, content: str) -> dict[str, Any]:
        """Lint daily note.

        Args:
            content: Daily content.

        Returns:
            Lint report dict.
        """
        gate_results = self._gate.check_daily_structure(content)

        issues = []
        for result in gate_results:
            if result.level == GateLevel.FAIL:
                severity = "error"
            elif result.level == GateLevel.WARN:
                severity = "warning"
            else:
                severity = "info"

            issues.append(
                {
                    "severity": severity,
                    "message": result.message,
                    "rule": result.rule,
                }
            )

        # Check timestamp format
        timestamp_issues = self._check_timestamps(content)
        issues.extend(timestamp_issues)

        return {
            "valid": not any(i["severity"] == "error" for i in issues),
            "issues": issues,
            "error_count": sum(1 for i in issues if i["severity"] == "error"),
            "warning_count": sum(1 for i in issues if i["severity"] == "warning"),
        }

    def lint_memory(self, content: str) -> dict[str, Any]:
        """Lint memory note.

        Args:
            content: Memory content.

        Returns:
            Lint report dict.
        """
        gate_results = self._gate.check_memory_structure(content)

        issues = []
        for result in gate_results:
            if result.level == GateLevel.FAIL:
                severity = "error"
            elif result.level == GateLevel.WARN:
                severity = "warning"
            else:
                severity = "info"

            issues.append(
                {
                    "severity": severity,
                    "message": result.message,
                    "rule": result.rule,
                }
            )

        return {
            "valid": not any(i["severity"] == "error" for i in issues),
            "issues": issues,
            "error_count": sum(1 for i in issues if i["severity"] == "error"),
            "warning_count": sum(1 for i in issues if i["severity"] == "warning"),
        }

    def _check_timestamps(self, content: str) -> list[dict[str, Any]]:
        """Check timestamp format in content.

        Args:
            content: Content to check.

        Returns:
            List of timestamp issues.
        """
        issues = []

        # Check log timestamps
        for match in re.finditer(r"### (\d{4}-\d{2}-\d{2} \d{2}:\d{2})", content):
            ts = match.group(1)
            # Verify it's a valid datetime
            try:
                from datetime import datetime

                datetime.strptime(ts, "%Y-%m-%d %H:%M")
            except ValueError:
                issues.append(
                    {
                        "severity": "warning",
                        "message": f"Invalid timestamp format: {ts}",
                        "rule": "timestamp_format",
                    }
                )

        return issues


# Convenience functions
def run_gate_check(
    content: str,
    content_type: str = "daily",
    metadata: dict[str, Any] | None = None,
) -> list[GateResult]:
    """Run gate check on content.

    Args:
        content: Content to check.
        content_type: Type of content.
        metadata: Additional metadata.

    Returns:
        List of gate results.
    """
    gate = MemoryGate()
    return gate.run_all_checks(content, content_type, metadata)


def should_block_operation(results: list[GateResult]) -> bool:
    """Check if operation should be blocked.

    Args:
        results: Gate results.

    Returns:
        True if should block.
    """
    return any(r.level == GateLevel.FAIL for r in results)
