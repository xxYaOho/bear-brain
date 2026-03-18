"""Trigger Management Module.

Manages automated triggers for memory workflows.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of triggers."""

    SESSION_START = auto()  # New agent session started
    DAILY_CREATED = auto()  # New daily note created
    PROMOTE_CHECK = auto()  # Scheduled promote check
    MEMORY_UPDATE = auto()  # Memory content updated


class TriggerAction(Enum):
    """Actions that can be triggered."""

    PRELOAD_MEMORY = auto()
    CHECK_PENDING_PROMOTE = auto()
    AUTO_PROMOTE = auto()
    SYNC_TO_VECTOR = auto()


@dataclass(slots=True)
class TriggerEvent:
    """Represents a trigger event."""

    trigger_type: TriggerType
    timestamp: datetime = field(default_factory=datetime.now)
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TriggerConfig:
    """Configuration for a trigger."""

    trigger_type: TriggerType
    action: TriggerAction
    enabled: bool = True
    condition: Callable[[TriggerEvent], bool] | None = None


class TriggerManager:
    """Manages and executes triggers.

    Usage:
        manager = TriggerManager()
        manager.register(TriggerConfig(
            TriggerType.SESSION_START,
            TriggerAction.PRELOAD_MEMORY
        ))
        manager.fire(TriggerEvent(TriggerType.SESSION_START))
    """

    def __init__(self) -> None:
        """Initialize trigger manager."""
        self._handlers: dict[TriggerType, list[TriggerConfig]] = {}
        self._history: list[tuple[datetime, TriggerType, bool]] = []

    def register(self, config: TriggerConfig) -> None:
        """Register a trigger configuration.

        Args:
            config: Trigger configuration.
        """
        if config.trigger_type not in self._handlers:
            self._handlers[config.trigger_type] = []
        self._handlers[config.trigger_type].append(config)
        logger.info(f"Registered trigger: {config.trigger_type.name} -> {config.action.name}")

    def fire(self, event: TriggerEvent) -> list[TriggerAction]:
        """Fire a trigger event.

        Args:
            event: The trigger event.

        Returns:
            List of actions that were executed.
        """
        actions_executed: list[TriggerAction] = []

        handlers = self._handlers.get(event.trigger_type, [])
        for config in handlers:
            if not config.enabled:
                continue

            # Check condition if present
            if config.condition and not config.condition(event):
                continue

            # Execute action
            success = self._execute_action(config.action, event)
            actions_executed.append(config.action)
            self._history.append((datetime.now(), event.trigger_type, success))

            logger.info(f"Trigger fired: {event.trigger_type.name} -> {config.action.name}")

        return actions_executed

    def _execute_action(self, action: TriggerAction, event: TriggerEvent) -> bool:
        """Execute a trigger action.

        Args:
            action: Action to execute.
            event: Trigger event context.

        Returns:
            True if successful.
        """
        try:
            if action == TriggerAction.PRELOAD_MEMORY:
                return self._action_preload_memory(event)
            elif action == TriggerAction.CHECK_PENDING_PROMOTE:
                return self._action_check_pending(event)
            elif action == TriggerAction.AUTO_PROMOTE:
                return self._action_auto_promote(event)
            elif action == TriggerAction.SYNC_TO_VECTOR:
                return self._action_sync_to_vector(event)
            else:
                logger.warning(f"Unknown action: {action}")
                return False
        except Exception as e:
            logger.error(f"Action {action.name} failed: {e}")
            return False

    def _action_preload_memory(self, event: TriggerEvent) -> bool:
        """Execute preload memory action."""
        from .preload import preload_memory

        result = preload_memory()
        return result.success

    def _action_check_pending(self, event: TriggerEvent) -> bool:
        """Execute check pending promote action."""
        # This would check for pending dailies
        logger.info("Checking for pending promotes")
        return True

    def _action_auto_promote(self, event: TriggerEvent) -> bool:
        """Execute auto promote action."""
        import re
        from pathlib import Path

        from ..runtime.state_machine import PromoteEvent, PromoteStateMachine
        from ..services.promote_service import PromoteService

        pending = event.payload.get("pending_dailies", [])
        daily_contents = event.payload.get("daily_contents", {})

        if not pending:
            state_machine = PromoteStateMachine()
            pending = state_machine.get_pending_dailies(days=7)

        if not pending:
            logger.info("No pending dailies to auto-promote")
            return True

        service = PromoteService()
        state_machine = PromoteStateMachine()
        all_success = True

        for daily_id in pending:
            logger.info(f"Auto-promoting: {daily_id}")

            try:
                record = state_machine.start_promote(daily_id)

                # Get daily content from payload or local file
                if daily_id in daily_contents:
                    daily_text = daily_contents[daily_id]
                else:
                    # Fallback: load from local daily file
                    match = re.match(r"memory-daily-(\d{4}-\d{2}-\d{2})", daily_id)
                    if not match:
                        logger.warning(f"Invalid daily_id format: {daily_id}")
                        continue
                    date_str = match.group(1)
                    daily_path = Path(f"daily/{date_str}.md")
                    if daily_path.exists():
                        daily_text = daily_path.read_text(encoding="utf-8")
                    else:
                        logger.warning(f"Daily file not found: {daily_path}")
                        state_machine.transition(record, PromoteEvent.PROMOTE_FAILED)
                        all_success = False
                        continue

                result = service.promote_daily(
                    daily_text=daily_text, daily_id=daily_id, target_memory_text=None
                )

                if result.success:
                    if result.promoted_items:
                        state_machine.transition(record, PromoteEvent.PROMOTE_SUCCESS)
                        logger.info(f"Successfully promoted {daily_id}: {result.promoted_items}")
                    else:
                        state_machine.transition(record, PromoteEvent.PROMOTE_EMPTY)
                        logger.info(f"No items to promote for {daily_id}")
                else:
                    state_machine.transition(record, PromoteEvent.PROMOTE_FAILED)
                    logger.error(f"Failed to promote {daily_id}: {result.error}")
                    all_success = False

            except Exception as e:
                logger.error(f"Error auto-promoting {daily_id}: {e}")
                all_success = False

        return all_success

    def _action_sync_to_vector(self, event: TriggerEvent) -> bool:
        """Execute sync to vector DB action."""
        # This would sync memory to vector DB
        logger.info("Syncing to vector DB")
        return True

    def get_history(self, limit: int = 10) -> list[tuple[datetime, TriggerType, bool]]:
        """Get trigger execution history.

        Args:
            limit: Max number of history entries.

        Returns:
            List of (timestamp, trigger_type, success) tuples.
        """
        return self._history[-limit:]


class DailyCreateTrigger:
    """Specialized trigger for daily creation.

    Automatically triggers promote check when new daily is created.
    """

    def __init__(self) -> None:
        """Initialize trigger."""
        self._manager = TriggerManager()
        self._setup_triggers()

    def _setup_triggers(self) -> None:
        """Set up default triggers."""
        # When daily is created, check for pending promotes
        self._manager.register(
            TriggerConfig(
                trigger_type=TriggerType.DAILY_CREATED,
                action=TriggerAction.CHECK_PENDING_PROMOTE,
            )
        )

        # When daily is created, auto-promote pending
        self._manager.register(
            TriggerConfig(
                trigger_type=TriggerType.DAILY_CREATED,
                action=TriggerAction.AUTO_PROMOTE,
                condition=self._should_auto_promote,
            )
        )

    def _should_auto_promote(self, event: TriggerEvent) -> bool:
        """Check if auto-promote should run.

        Args:
            event: Trigger event.

        Returns:
            True if should auto-promote.
        """
        # Only auto-promote if explicitly enabled
        return event.payload.get("auto_promote", False)

    def on_daily_created(self, daily_id: str, auto_promote: bool = True) -> list[TriggerAction]:
        """Handle daily creation.

        Args:
            daily_id: ID of created daily.
            auto_promote: Whether to auto-promote pending dailies.

        Returns:
            List of executed actions.
        """
        event = TriggerEvent(
            trigger_type=TriggerType.DAILY_CREATED,
            payload={"daily_id": daily_id, "auto_promote": auto_promote},
        )
        return self._manager.fire(event)


class SessionStartTrigger:
    """Specialized trigger for session start.

    Automatically preloads memory when new agent session starts.
    """

    def __init__(self) -> None:
        """Initialize trigger."""
        self._manager = TriggerManager()
        self._setup_triggers()

    def _setup_triggers(self) -> None:
        """Set up default triggers."""
        self._manager.register(
            TriggerConfig(
                trigger_type=TriggerType.SESSION_START,
                action=TriggerAction.PRELOAD_MEMORY,
            )
        )

    def on_session_start(self) -> list[TriggerAction]:
        """Handle session start.

        Returns:
            List of executed actions.
        """
        event = TriggerEvent(trigger_type=TriggerType.SESSION_START)
        return self._manager.fire(event)


# Global trigger instance
def get_trigger_manager() -> TriggerManager:
    """Get global trigger manager instance."""
    return TriggerManager()
