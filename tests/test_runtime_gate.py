"""Tests for gate/lint functionality."""

from __future__ import annotations

import pytest

from bear_brain.runtime.gate import (
    GateLevel,
    GateResult,
    LintService,
    MemoryGate,
    run_gate_check,
    should_block_operation,
)


class TestMemoryGate:
    """Test MemoryGate class."""

    def test_check_daily_structure_valid(self) -> None:
        """Test valid daily structure passes."""
        gate = MemoryGate()
        content = """## Promote Status
- Status: pending

## Summary
Test summary
"""
        results = gate.check_daily_structure(content)
        assert len(results) == 0

    def test_check_daily_structure_missing_promote_status(self) -> None:
        """Test missing promote status fails."""
        gate = MemoryGate()
        content = """## Summary
Test summary
"""
        results = gate.check_daily_structure(content)
        assert any(r.level == GateLevel.FAIL for r in results)
        assert any("Promote Status" in r.message for r in results)

    def test_check_daily_structure_invalid_status(self) -> None:
        """Test invalid status fails."""
        gate = MemoryGate()
        content = """## Promote Status
- Status: invalid-status

## Summary
Test
"""
        results = gate.check_daily_structure(content)
        assert any(r.level == GateLevel.FAIL for r in results)

    def test_check_memory_structure_missing_core(self) -> None:
        """Test missing Core Memory warns."""
        gate = MemoryGate()
        content = "# Memory\n\nSome content"
        results = gate.check_memory_structure(content)
        assert any(r.level == GateLevel.WARN for r in results)

    def test_check_no_guessing_detects_keywords(self) -> None:
        """Test guessing detection."""
        gate = MemoryGate()
        text = "我猜测这可能是正确的"
        results = gate.check_no_guessing(text, context="test")
        assert len(results) > 0
        assert all(r.level == GateLevel.WARN for r in results)

    def test_check_note_id_valid(self) -> None:
        """Test valid note ID passes."""
        gate = MemoryGate()
        results = gate.check_note_id("ABC12345-1234-1234-1234-123456789ABC", "api")
        assert len(results) == 0

    def test_check_note_id_invalid_format(self) -> None:
        """Test invalid note ID fails."""
        gate = MemoryGate()
        results = gate.check_note_id("invalid-id", "api")
        assert any(r.level == GateLevel.FAIL for r in results)

    def test_check_note_id_guessed(self) -> None:
        """Test guessed note ID fails."""
        gate = MemoryGate()
        results = gate.check_note_id("ABC12345-1234-1234-1234-123456789ABC", "guessed")
        assert any(r.level == GateLevel.FAIL for r in results)
        assert any("guessed" in r.message for r in results)

    def test_should_block_with_fail(self) -> None:
        """Test should_block detects FAIL level."""
        gate = MemoryGate()
        results = [
            GateResult(GateLevel.WARN, "warning", "test"),
            GateResult(GateLevel.FAIL, "error", "test"),
        ]
        assert gate.should_block(results) is True

    def test_should_not_block_with_only_warn(self) -> None:
        """Test should_block with only WARN doesn't block."""
        gate = MemoryGate()
        results = [
            GateResult(GateLevel.WARN, "warning", "test"),
            GateResult(GateLevel.WARN, "another warning", "test"),
        ]
        assert gate.should_block(results) is False


class TestLintService:
    """Test LintService class."""

    def test_lint_daily_valid(self) -> None:
        """Test linting valid daily."""
        service = LintService()
        content = """## Promote Status
- Status: pending

## Summary
Test

## Log
### 2026-03-17 10:00
Test entry
"""
        result = service.lint_daily(content)
        assert result["valid"] is True
        assert result["error_count"] == 0

    def test_lint_daily_with_errors(self) -> None:
        """Test linting daily with errors."""
        service = LintService()
        content = """## Summary
Missing Promote Status
"""
        result = service.lint_daily(content)
        assert result["valid"] is False
        assert result["error_count"] > 0

    def test_lint_memory_valid(self) -> None:
        """Test linting valid memory."""
        service = LintService()
        content = """# Memory

## Core Memory
- Item 1
"""
        result = service.lint_memory(content)
        assert result["valid"] is True

    def test_lint_memory_with_warnings(self) -> None:
        """Test linting memory with warnings."""
        service = LintService()
        content = "# Memory\n\nNo Core Memory section"
        result = service.lint_memory(content)
        assert result["warning_count"] > 0

    def test_check_timestamps_valid(self) -> None:
        """Test valid timestamp format."""
        service = LintService()
        content = "### 2026-03-17 10:00\nEntry"
        result = service.lint_daily(content)
        # Should not have timestamp issues
        timestamp_issues = [i for i in result["issues"] if i.get("rule") == "timestamp_format"]
        assert len(timestamp_issues) == 0


class TestGateConvenienceFunctions:
    """Test convenience functions."""

    def test_run_gate_check(self) -> None:
        """Test run_gate_check function."""
        content = """## Promote Status
- Status: pending
"""
        results = run_gate_check(content, content_type="daily")
        # Should pass basic checks
        assert all(r.level != GateLevel.FAIL for r in results)

    def test_should_block_operation_with_fail(self) -> None:
        """Test should_block_operation with fail."""
        results = [
            GateResult(GateLevel.FAIL, "error", "test"),
        ]
        assert should_block_operation(results) is True

    def test_should_block_operation_without_fail(self) -> None:
        """Test should_block_operation without fail."""
        results = [
            GateResult(GateLevel.WARN, "warning", "test"),
        ]
        assert should_block_operation(results) is False
