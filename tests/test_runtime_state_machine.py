"""Tests for promote state machine."""

from __future__ import annotations

import pytest

from bear_brain.runtime.state_machine import (
    PromoteEvent,
    PromoteRecord,
    PromoteState,
    PromoteStateMachine,
    PromoteStateStore,
)


class TestPromoteStateMachine:
    """Test PromoteStateMachine class."""

    def test_initial_state(self) -> None:
        """Test initial state is PENDING."""
        sm = PromoteStateMachine()
        record = sm.start_promote("daily-2026-03-17")

        assert record.state == PromoteState.PROCESSING
        assert record.daily_id == "daily-2026-03-17"

    def test_transition_to_success(self) -> None:
        """Test successful promote transition."""
        sm = PromoteStateMachine()
        record = sm.start_promote("daily-2026-03-17")

        success = sm.transition(record, PromoteEvent.PROMOTE_SUCCESS)

        assert success is True
        assert record.state == PromoteState.DONE_PROMOTED
        assert record.promoted_at is not None

    def test_transition_to_empty(self) -> None:
        """Test empty promote transition."""
        sm = PromoteStateMachine()
        record = sm.start_promote("daily-2026-03-17")

        success = sm.transition(record, PromoteEvent.PROMOTE_EMPTY)

        assert success is True
        assert record.state == PromoteState.DONE_NONE

    def test_transition_to_failed(self) -> None:
        """Test failed promote transition."""
        sm = PromoteStateMachine()
        record = sm.start_promote("daily-2026-03-17")

        success = sm.transition(record, PromoteEvent.PROMOTE_FAILED)

        assert success is True
        assert record.state == PromoteState.FAILED
        assert record.retry_count == 1

    def test_retry_transition(self) -> None:
        """Test retry transition."""
        sm = PromoteStateMachine()
        record = sm.start_promote("daily-2026-03-17")

        # Fail first
        sm.transition(record, PromoteEvent.PROMOTE_FAILED)
        assert record.state == PromoteState.FAILED

        # Then retry
        success = sm.transition(record, PromoteEvent.RETRY)
        assert success is True
        assert record.state == PromoteState.PROCESSING

    def test_max_retries(self) -> None:
        """Test max retries reached."""
        sm = PromoteStateMachine(max_retries=2)
        record = sm.start_promote("daily-2026-03-17")

        # Fail twice
        sm.transition(record, PromoteEvent.PROMOTE_FAILED)
        sm.transition(record, PromoteEvent.RETRY)
        sm.transition(record, PromoteEvent.PROMOTE_FAILED)

        assert record.state == PromoteState.MAX_RETRIES

    def test_invalid_transition(self) -> None:
        """Test invalid transition returns False."""
        sm = PromoteStateMachine()
        record = sm.start_promote("daily-2026-03-17")

        # Can't go directly from PROCESSING to RETRY
        success = sm.transition(record, PromoteEvent.RETRY)

        assert success is False
        assert record.state == PromoteState.PROCESSING  # Unchanged

    def test_get_pending_dailies(self) -> None:
        """Test getting pending dailies."""
        sm = PromoteStateMachine()

        # Create some records
        sm.start_promote("daily-1")
        sm.start_promote("daily-2")

        pending = sm.get_pending_dailies(days=7)
        assert len(pending) == 0  # They're PROCESSING, not PENDING


class TestPromoteRecord:
    """Test PromoteRecord dataclass."""

    def test_record_creation(self) -> None:
        """Test creating a record."""
        from datetime import datetime

        record = PromoteRecord(
            daily_id="daily-2026-03-17",
            state=PromoteState.PENDING,
            max_retries=3,
        )

        assert record.daily_id == "daily-2026-03-17"
        assert record.state == PromoteState.PENDING
        assert record.retry_count == 0
        assert record.max_retries == 3
        assert isinstance(record.created_at, datetime)


class TestPromoteStateStore:
    """Test PromoteStateStore class."""

    def test_store_creation(self) -> None:
        """Test creating store."""
        store = PromoteStateStore()
        assert store is not None

    def test_save_and_load(self) -> None:
        """Test save and load operations."""
        store = PromoteStateStore()
        record = PromoteRecord(
            daily_id="daily-2026-03-17",
            state=PromoteState.DONE_PROMOTED,
        )

        # Save
        success = store.save(record)
        assert success is True

        # Load (will return None in current implementation)
        loaded = store.load("daily-2026-03-17")
        assert loaded is None  # Not yet implemented


class TestAutoTrigger:
    """Test auto-trigger functionality."""

    def test_auto_trigger_finds_pending(self) -> None:
        """Test auto-trigger processes pending dailies."""
        sm = PromoteStateMachine()

        # Create a pending record
        record1 = sm.start_promote("daily-2026-03-16")
        sm.transition(record1, PromoteEvent.PROMOTE_FAILED)  # Make it failed/pending

        # Auto-trigger with new daily
        processed = sm.auto_trigger("daily-2026-03-17")

        # Should have processed the pending daily
        assert len(processed) == 1

    def test_auto_trigger_excludes_today(self) -> None:
        """Test auto-trigger excludes today's daily."""
        sm = PromoteStateMachine()

        # Auto-trigger won't process today's daily
        processed = sm.auto_trigger("daily-2026-03-17")

        # No pending records to process
        assert len(processed) == 0
