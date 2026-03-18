"""Promote State Machine.

Manages the lifecycle of promote operations with proper state transitions.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path

from ..adapters.bear_adapter import BearAdapter

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
    StateTransition(
        PromoteState.PENDING,
        PromoteEvent.START_PROMOTE,
        PromoteState.PROCESSING,
        "begin_promote",
    ),
    # From PROCESSING
    StateTransition(
        PromoteState.PROCESSING,
        PromoteEvent.PROMOTE_SUCCESS,
        PromoteState.DONE_PROMOTED,
        "record_success",
    ),
    StateTransition(
        PromoteState.PROCESSING,
        PromoteEvent.PROMOTE_EMPTY,
        PromoteState.DONE_NONE,
        "record_empty",
    ),
    StateTransition(
        PromoteState.PROCESSING,
        PromoteEvent.PROMOTE_FAILED,
        PromoteState.FAILED,
        "record_failure",
    ),
    # From FAILED
    StateTransition(
        PromoteState.FAILED,
        PromoteEvent.RETRY,
        PromoteState.PROCESSING,
        "begin_retry",
    ),
    StateTransition(
        PromoteState.FAILED,
        PromoteEvent.PROMOTE_FAILED,
        PromoteState.MAX_RETRIES,
        "max_retries_reached",
    ),
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

    def __init__(
        self,
        max_retries: int = 3,
        state_store: PromoteStateStore | None = None,
    ) -> None:
        """Initialize state machine.

        Args:
            max_retries: Maximum retry attempts for failed promotes.
            state_store: Optional persistent storage for records.
        """
        self._max_retries = max_retries
        self._records: dict[str, PromoteRecord] = {}
        self._store = state_store or PromoteStateStore()
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

        self.transition(record, PromoteEvent.START_PROMOTE)
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
            logger.warning(f"Invalid transition: {record.state.name} + {event.name}")
            return False

        # Execute transition
        old_state = record.state
        record.state = transition.to_state
        record.updated_at = datetime.now()

        # Execute action if defined
        if transition.action:
            self._execute_action(record, transition.action)

        # Persist to store
        self._store.save(record)

        logger.info(f"Promote {record.daily_id}: {old_state.name} -> {transition.to_state.name}")
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
        records = self._store.list_pending(days=days)
        return [r.daily_id for r in records]

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
    """Persistent storage for promote records using SQLite.

    Stores promote state with full durability across restarts.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        """Initialize storage with SQLite backend.

        Args:
            db_path: Path to SQLite database. Defaults to data/db/state.db.
        """
        if db_path is None:
            db_path = Path("data/db/state.db")
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS promote_records (
                    daily_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    promoted_at TEXT,
                    promoted_to TEXT,
                    error_message TEXT
                )
            """)
            conn.commit()

    def _serialize_datetime(self, dt: datetime | None) -> str | None:
        """Serialize datetime to ISO format string."""
        return dt.isoformat() if dt else None

    def _deserialize_datetime(self, s: str | None) -> datetime | None:
        """Deserialize ISO format string to datetime."""
        return datetime.fromisoformat(s) if s else None

    def save(self, record: PromoteRecord) -> bool:
        """Save record to persistent storage.

        Args:
            record: The promote record to save.

        Returns:
            True if save succeeded.
        """
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO promote_records
                    (daily_id, state, retry_count, max_retries, created_at,
                     updated_at, promoted_at, promoted_to, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(daily_id) DO UPDATE SET
                        state=excluded.state,
                        retry_count=excluded.retry_count,
                        max_retries=excluded.max_retries,
                        updated_at=excluded.updated_at,
                        promoted_at=excluded.promoted_at,
                        promoted_to=excluded.promoted_to,
                        error_message=excluded.error_message
                    """,
                    (
                        record.daily_id,
                        record.state.name,
                        record.retry_count,
                        record.max_retries,
                        self._serialize_datetime(record.created_at),
                        self._serialize_datetime(record.updated_at),
                        self._serialize_datetime(record.promoted_at),
                        json.dumps(record.promoted_to),
                        record.error_message,
                    ),
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to save promote record {record.daily_id}: {e}")
            return False

    def load(self, daily_id: str) -> PromoteRecord | None:
        """Load record from persistent storage.

        Args:
            daily_id: The daily ID to load.

        Returns:
            PromoteRecord if found, None otherwise.
        """
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT * FROM promote_records WHERE daily_id = ?",
                    (daily_id,),
                ).fetchone()

                if row is None:
                    return None

                return self._row_to_record(row)
        except sqlite3.Error as e:
            logger.error(f"Failed to load promote record {daily_id}: {e}")
            return None

    def _row_to_record(self, row: sqlite3.Row) -> PromoteRecord:
        """Convert database row to PromoteRecord."""
        return PromoteRecord(
            daily_id=row["daily_id"],
            state=PromoteState[row["state"]],
            retry_count=row["retry_count"],
            max_retries=row["max_retries"],
            created_at=self._deserialize_datetime(row["created_at"]) or datetime.now(),
            updated_at=self._deserialize_datetime(row["updated_at"]) or datetime.now(),
            promoted_at=self._deserialize_datetime(row["promoted_at"]),
            promoted_to=json.loads(row["promoted_to"]) if row["promoted_to"] else [],
            error_message=row["error_message"],
        )

    def list_pending(self, days: int = 7) -> list[PromoteRecord]:
        """List all pending records from last N days.

        Args:
            days: Number of days to look back.

        Returns:
            List of records in pending or failed state.
        """
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                cutoff = cutoff - timedelta(days=days)

                rows = conn.execute(
                    """
                    SELECT * FROM promote_records
                    WHERE state IN (?, ?)
                    AND created_at >= ?
                    ORDER BY created_at DESC
                    """,
                    (
                        PromoteState.PENDING.name,
                        PromoteState.FAILED.name,
                        self._serialize_datetime(cutoff),
                    ),
                ).fetchall()

                return [self._row_to_record(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to list pending records: {e}")
            return []
