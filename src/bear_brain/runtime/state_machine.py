"""Promote State Machine.

Manages the lifecycle of promote operations with proper state transitions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from ..adapters.bear_adapter import BearAdapter, BearNote
from ..models import PromoteStatus

__all__ = [
    "PromoteState",
    "PromoteEvent",
    "StateTransition",
    "PromoteRecord",
    "PromoteStateMachine",
    "PromoteStateStore",
]

logger = logging.getLogger(__name__)


class PromoteState(Enum):
    """States in the promote lifecycle."""

    PENDING = auto()  # Daily created, not yet processed
    PROCESSING = auto()  # Currently being promoted
    DONE_PROMOTED = auto()  # Successfully promoted with items
    DONE_NONE = auto()  # Processed, nothing to promote
    FAILED = auto()  # Failed, will retry
    MAX_RETRIES = auto()  # Failed after max retries


class PromoteEvent(Enum):
    """Events that trigger state transitions."""

    START_PROMOTE = auto()
    PROMOTE_SUCCESS = auto()
    PROMOTE_EMPTY = auto()
    PROMOTE_FAILED = auto()
    RETRY = auto()


@dataclass(slots=True)
class StateTransition:
    """Represents a state transition."""

    from_state: PromoteState
    event: PromoteEvent
    to_state: PromoteState
    action: str | None = None


# Define valid state transitions
TRANSITIONS: list[StateTransition] = [
    # From PENDING
    StateTransition(PromoteState.PENDING, PromoteEvent.START_PROMOTE, PromoteState.PROCESSING, "begin_promote"),
    # From PROCESSING
    StateTransition(PromoteState.PROCESSING, PromoteEvent.PROMOTE_SUCCESS, PromoteState.DONE_PROMOTED, "record_success"),
    StateTransition(PromoteState.PROCESSING, PromoteEvent.PROMOTE_EMPTY, PromoteState.DONE_NONE, "record_empty"),
    StateTransition(PromoteState.PROCESSING, PromoteEvent.PROMOTE_FAILED, PromoteState.FAILED, "record_failure"),
    # From FAILED
    StateTransition(PromoteState.FAILED, PromoteEvent.RETRY, PromoteState.PROCESSING, "begin_retry"),
    StateTransition(PromoteState.FAILED, PromoteEvent.PROMOTE_FAILED, PromoteState.MAX_RETRIES, "max_retries_reached"),
]


@dataclass(slots=True)
class PromoteRecord:
    """Record of a promote operation."""

    daily_id: str
    state: PromoteState
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    promoted_at: datetime | None = None
    promoted_to: list[str] = field(default_factory=list)
    error_message: str | None = None


class PromoteStateMachine:
    """State machine for managing promote lifecycle.

    Usage:
        sm = PromoteStateMachine()
        record = sm.start_promote("daily-2026-03-17")
        # ... do promote work ...
        sm.transition(record, PromoteEvent.PROMOTE_SUCCESS)
    """

    def __init__(self, max_retries: int = 3) -> None:
        """Initialize state machine.

        Args:
            max_retries: Maximum retry attempts for failed promotes.
        """
        self._max_retries = max_retries
        self._records: dict[str, PromoteRecord] = {}
        self._bear = BearAdapter()

    def start_promote(self, daily_id: str) -> PromoteRecord:
        """Start promote process for a daily note.

        Args:
            daily_id: Identifier for the daily note.

        Returns:
            PromoteRecord with state PROCESSING.
        """
        record = PromoteRecord(
            daily_id=daily_id,
            state=PromoteState.PENDING,
            max_retries=self._max_retries,
        )
        self._records[daily_id] = record

        self._transition(record, PromoteEvent.START_PROMOTE)
        return record

    def transition(self, record: PromoteRecord, event: PromoteEvent) -> bool:
        """Execute state transition.

        Args:
            record: The record to transition.
            event: The event triggering the transition.

        Returns:
            True if transition succeeded, False otherwise.
        """
        # Find valid transition
        transition = None
        for t in TRANSITIONS:
            if t.from_state == record.state and t.event == event:
                transition = t
                break

        if transition is None:
            logger.warning(
                f"Invalid transition: {record.state.name} + {event.name}"
            )
            return False

        # Execute transition
        old_state = record.state
        record.state = transition.to_state
        record.updated_at = datetime.now()

        # Execute action if defined
        if transition.action:
            self._execute_action(record, transition.action)

        logger.info(
            f"Promote {record.daily_id}: {old_state.name} -> {transition.to_state.name}"
        )
        return True

    def _execute_action(self, record: PromoteRecord, action: str) -> None:
        """Execute side effects for state transitions."""
        if action == "record_success":
            record.promoted_at = datetime.now()
        elif action == "record_failure":
            record.retry_count += 1
            if record.retry_count >= record.max_retries:
                self.transition(record, PromoteEvent.PROMOTE_FAILED)
        elif action == "begin_retry":
            logger.info(f"Retrying promote for {record.daily_id}")

    def get_pending_dailies(self, days: int = 7) -> list[str]:
        """Get list of daily IDs that need promotion.

        Args:
            days: Number of days to look back.

        Returns:
            List of daily IDs in pending or failed state.
        """
        # In real implementation, this would query Bear or database
        # For now, return empty list
        pending = [
            r.daily_id
            for r in self._records.values()
            if r.state in (PromoteState.PENDING, PromoteState.FAILED)
        ]
        return pending

    def auto_trigger(self, new_daily_id: str) -> list[PromoteRecord]:
        """Auto-trigger promote when new daily is created.

        This implements the automatic promote trigger:
        1. Check for pending dailies in last N days
        2. For each pending, attempt promote
        3. Return list of processed records

        Args:
            new_daily_id: ID of the newly created daily.

        Returns:
            List of PromoteRecords that were processed.
        """
        pending = self.get_pending_dailies(days=7)
        processed: list[PromoteRecord] = []

        for daily_id in pending:
            if daily_id == new_daily_id:
                continue  # Don't promote today's daily

            record = self.start_promote(daily_id)
            processed.append(record)
            # Actual promote work would be done by caller or service layer

        return processed


class PromoteStateStore:
    """Persistent storage for promote records.

    This would typically use Bear notes or local database.
    """

    def __init__(self) -> None:
        self._bear = BearAdapter()

    def save(self, record: PromoteRecord) -> bool:
        """Save record to persistent storage."""
        # Implementation would save to Bear or SQLite
        return True

    def load(self, daily_id: str) -> PromoteRecord | None:
        """Load record from persistent storage."""
        # Implementation would load from Bear or SQLite
        return None

    def list_pending(self, days: int = 7) -> list[PromoteRecord]:
        """List all pending records."""
        return []
