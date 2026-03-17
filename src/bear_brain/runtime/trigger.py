"""Trigger Management Module.

Manages automated triggers for memory workflows.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

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

            logger.info(
                f"Trigger fired: {event.trigger_type.name} -> {config.action.name}"
            )

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
        from ..services.promote_service import PromoteService

        service = PromoteService()
        # Get pending dailies from event payload or check
        pending = event.payload.get("pending_dailies", [])

        for daily_id in pending:
            # Process each pending daily
            logger.info(f"Auto-promoting: {daily_id}")

        return True

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

    def on_daily_created(self, daily_id: str) -> list[TriggerAction]:
        """Handle daily creation.

        Args:
            daily_id: ID of created daily.

        Returns:
            List of executed actions.
        """
        event = TriggerEvent(
            trigger_type=TriggerType.DAILY_CREATED,
            payload={"daily_id": daily_id},
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
