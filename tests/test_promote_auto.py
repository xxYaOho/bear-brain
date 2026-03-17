"""Tests for promote auto-trigger functionality."""

from __future__ import annotations

from pathlib import Path

from bear_brain.runtime.state_machine import (
    PromoteEvent,
    PromoteState,
    PromoteStateMachine,
)
from bear_brain.services.promote_service import PromoteService, PromoteServiceResult


class TestPromoteAutoTrigger:
    """Test automatic promote triggering."""

    def test_auto_trigger_on_daily_create(self, tmp_path: Path) -> None:
        """Test auto-trigger when new daily is created."""
        from bear_brain.runtime.trigger import DailyCreateTrigger

        trigger = DailyCreateTrigger()

        # Simulate creating a new daily
        actions = trigger.on_daily_created("memory-daily-2026-03-17")

        # Should have triggered check and possibly auto-promote
        assert len(actions) >= 1

    def test_state_machine_auto_trigger(self) -> None:
        """Test state machine auto-trigger functionality."""
        sm = PromoteStateMachine()

        # Create a failed record (would be pending retry)
        record1 = sm.start_promote("daily-2026-03-15")
        sm.transition(record1, PromoteEvent.PROMOTE_FAILED)

        # Create another pending record
        record2 = sm.start_promote("daily-2026-03-16")
        sm.transition(record2, PromoteEvent.PROMOTE_FAILED)

        # Auto-trigger with new daily
        processed = sm.auto_trigger("daily-2026-03-17")

        # Should process both pending dailies
        assert len(processed) == 2
        assert all(r.state == PromoteState.PROCESSING for r in processed)

    def test_auto_trigger_excludes_today(self) -> None:
        """Test auto-trigger doesn't include today's daily."""
        sm = PromoteStateMachine()

        # Start a record that stays pending
        sm.start_promote("daily-2026-03-17")
        # Don't transition - it's now PROCESSING

        # Auto-trigger for today shouldn't find anything
        # (it's in PROCESSING, not PENDING)
        processed = sm.auto_trigger("daily-2026-03-17")
        assert len(processed) == 0


class TestPromoteService:
    """Test PromoteService business logic."""

    def test_promote_daily_with_items(self) -> None:
        """Test promoting daily with extractable items."""
        service = PromoteService()

        daily_text = """## Promote Status
- Status: pending

## Summary
- 发现 512 维是最佳维度
- 可复用规则：每天先完成前一天的总结

## Log
### 2026-03-17 10:00
- 确定了 vector:512-dimension
"""
        result = service.promote_daily(daily_text, "daily-2026-03-17")

        assert result.success is True
        assert len(result.promoted_items) > 0
        assert "vector:512-dimension" in result.promoted_items

    def test_promote_daily_empty(self) -> None:
        """Test promoting daily with no extractable items."""
        service = PromoteService()

        daily_text = """## Promote Status
- Status: pending

## Summary
- 普通工作记录

## Log
### 2026-03-17 10:00
- 做了一些事情
"""
        result = service.promote_daily(daily_text, "daily-2026-03-17")

        assert result.success is True
        assert len(result.promoted_items) == 0

    def test_categorize_item(self) -> None:
        """Test item categorization."""
        service = PromoteService()

        assert service._categorize_item("512 维度") == "vector:512-dimension"
        assert service._categorize_item("可复用规则") == "rule:daily-before-new-day"
        assert service._categorize_item("TDD 模式") == "practice:tdd-pattern"
        assert service._categorize_item("项目收尾流程") == "process:project-completion"

    def test_apply_to_files(self, tmp_path: Path) -> None:
        """Test apply promote to files."""
        service = PromoteService()

        # Create test files
        daily_path = tmp_path / "daily.md"
        memory_path = tmp_path / "memory.md"

        daily_path.write_text(
            "## Promote Status\n- Status: pending\n\n## Summary\n- 512 维\n",
            encoding="utf-8",
        )
        memory_path.write_text("# Memory\n\n## Core Memory\n- existing\n", encoding="utf-8")

        service.apply_to_files(daily_path, memory_path, "daily-test")

        # Verify daily was updated
        updated_daily = daily_path.read_text(encoding="utf-8")
        assert "done" in updated_daily.lower() or "promoted" in updated_daily.lower()


class TestPromoteIntegration:
    """Integration tests for promote workflow."""

    def test_full_promote_workflow(self, tmp_path: Path) -> None:
        """Test complete promote workflow."""
        from bear_brain.services.daily_service import DailyService
        from bear_brain.services.promote_service import PromoteService

        # Create a daily
        daily_service = DailyService(project_root=tmp_path)
        daily_result = daily_service.create_daily()
        assert daily_result.success is True

        # Add content to daily
        daily_path = daily_service.get_daily_path(daily_result.daily_id)
        assert daily_path is not None

        # Append promotable content
        daily_service._daily_service = daily_service  # Use same instance

        # Create memory file
        memory_path = tmp_path / "memory.md"
        memory_path.write_text("# Memory\n\n## Core Memory\n", encoding="utf-8")

        # Promote
        promote_service = PromoteService()
        result = promote_service.apply_to_files(daily_path, memory_path, daily_result.daily_id)

        assert result.success is True


class TestPromoteServiceResult:
    """Test PromoteServiceResult dataclass."""

    def test_result_creation(self) -> None:
        """Test creating result."""
        result = PromoteServiceResult(
            success=True,
            record=None,
            promoted_items=["item1", "item2"],
            error=None,
        )

        assert result.success is True
        assert result.promoted_items == ["item1", "item2"]
        assert result.error is None
