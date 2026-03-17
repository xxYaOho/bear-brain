"""OpenCode Adapter.

Provides integration with OpenCode platform for event handling.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..runtime.trigger import TriggerEvent, TriggerManager, TriggerType

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class OpenCodeEvent:
    """Represents an OpenCode event."""

    event_type: str
    session_id: str | None
    payload: dict[str, Any]


class OpenCodeAdapter:
    """Adapter for OpenCode platform integration.

    This adapter handles:
    - Session start events
    - Command invocations (/bb-*)
    - Hook callbacks
    - Event routing to triggers
    """

    def __init__(self) -> None:
        """Initialize adapter."""
        self._trigger_manager = TriggerManager()
        self._command_handlers: dict[str, Callable[..., Any]] = {}
        self._session_id: str | None = None

    def initialize(self) -> bool:
        """Initialize OpenCode integration.

        Returns:
            True if OpenCode environment detected.
        """
        self._session_id = os.environ.get("OPENCODE_SESSION_ID")
        is_opencode = os.environ.get("OPENCODE_WORKSPACE") is not None

        if is_opencode:
            logger.info(f"OpenCode adapter initialized: session={self._session_id}")
        else:
            logger.debug("Not in OpenCode environment")

        return is_opencode

    def on_session_start(self) -> dict[str, Any]:
        """Handle new session start.

        Returns:
            Context dict for the session.
        """
        logger.info("Session start detected")

        # Fire trigger
        event = TriggerEvent(
            trigger_type=TriggerType.SESSION_START,
            payload={"session_id": self._session_id},
        )
        self._trigger_manager.fire(event)

        # Preload memory
        from ..runtime.preload import get_preload_context

        context = get_preload_context()

        if context.get("memory_content"):
            logger.info(f"Memory preloaded from {context.get('memory_source')}")

        return context

    def register_command(self, command: str, handler: Callable[..., Any]) -> None:
        """Register a command handler.

        Args:
            command: Command name (e.g., "/bb-memory-status").
            handler: Handler function.
        """
        self._command_handlers[command] = handler
        logger.info(f"Registered command: {command}")

    def handle_command(self, command: str, args: dict[str, Any]) -> Any:
        """Handle a command invocation.

        Args:
            command: Command name.
            args: Command arguments.

        Returns:
            Command result.
        """
        handler = self._command_handlers.get(command)
        if handler:
            try:
                return handler(**args)
            except Exception as e:
                logger.error(f"Command {command} failed: {e}")
                return {"error": str(e)}
        else:
            logger.warning(f"Unknown command: {command}")
            return {"error": f"Unknown command: {command}"}

    def is_opencode(self) -> bool:
        """Check if running in OpenCode environment.

        Returns:
            True if in OpenCode.
        """
        return os.environ.get("OPENCODE_WORKSPACE") is not None

    def get_session_context(self) -> dict[str, Any]:
        """Get current session context.

        Returns:
            Context information.
        """
        return {
            "session_id": self._session_id,
            "is_opencode": self.is_opencode(),
            "workspace": os.environ.get("OPENCODE_WORKSPACE"),
        }


class CommandRegistry:
    """Registry for /bb-* commands.

    Implements the 4 command specifications from v0.2:
    - /bb-memory-daily: Create new daily note
    - /bb-promote: Manually trigger promote
    - /bb-memory-status: Show memory system status
    - /bb-memory-lint: Run lint checks
    """

    def __init__(self) -> None:
        """Initialize registry."""
        self._adapter = OpenCodeAdapter()
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        """Register default command handlers."""
        self._adapter.register_command("/bb-memory-daily", self._cmd_memory_daily)
        self._adapter.register_command("/bb-promote", self._cmd_promote)
        self._adapter.register_command("/bb-memory-status", self._cmd_memory_status)
        self._adapter.register_command("/bb-memory-lint", self._cmd_memory_lint)

    def _cmd_memory_daily(self) -> dict[str, Any]:
        """Handle /bb-memory-daily command.

        Creates a new daily note for today.
        """
        from ..services.daily_service import DailyService

        service = DailyService()
        result = service.create_daily()

        if result.success:
            return {
                "success": True,
                "message": f"Created daily: {result.daily_id}",
                "daily_id": result.daily_id,
            }
        else:
            return {
                "success": False,
                "error": result.error,
            }

    def _cmd_promote(self, daily_id: str | None = None) -> dict[str, Any]:
        """Handle /bb-promote command.

        Manually trigger promote for a daily note and persist results to files.

        Args:
            daily_id: Optional daily ID (defaults to yesterday).
        """
        from datetime import datetime, timedelta
        from pathlib import Path

        from ..runtime.state_machine import PromoteStateStore
        from ..services.daily_service import DailyService
        from ..services.promote_service import PromoteService

        if daily_id is None:
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")
            daily_id = f"memory-daily-{date_str}"

        daily_service = DailyService()
        daily_path = daily_service.get_daily_path(daily_id)

        if daily_path is None:
            return {
                "success": False,
                "promoted_items": [],
                "state": "failed",
                "error": f"Daily not found: {daily_id}",
            }

        # Determine memory file path
        memory_path = Path("memory.md")
        if not memory_path.exists():
            # Try to find memory file in project root
            memory_path = Path.cwd() / "memory.md"

        promote_service = PromoteService()

        # Use apply_to_files to update both daily and memory files
        result = promote_service.apply_to_files(daily_path, memory_path, daily_id)

        # Persist state to store
        state_store = PromoteStateStore()
        if result.record:
            state_store.save(result.record)

        if result.record:
            state = result.record.state.name.lower().replace("_", "-")
        else:
            state = "failed"

        return {
            "success": result.success,
            "promoted_items": result.promoted_items,
            "state": state,
            "daily_updated": result.success,
            "memory_updated": result.success and len(result.promoted_items) > 0,
            "error": result.error,
        }

    def _cmd_memory_status(self) -> dict[str, Any]:
        """Handle /bb-memory-status command.

        Show memory system status.
        """
        from ..runtime.preload import preload_memory
        from ..runtime.state_machine import PromoteStateStore
        from ..services.daily_service import DailyService

        daily_service = DailyService()
        dailies = daily_service.list_dailies(days=30)

        state_store = PromoteStateStore()
        pending_records = state_store.list_pending(days=30)

        preload_result = preload_memory()

        last_promote = None
        for record in state_store.list_pending(days=365):
            if record.promoted_at:
                last_promote = record.promoted_at.isoformat()
                break

        return {
            "success": True,
            "preload_status": {
                "loaded": preload_result.success and bool(preload_result.content),
                "source": preload_result.source,
            },
            "promote_status": {
                "pending_count": len(pending_records),
                "last_promote": last_promote,
            },
            "session_id": self._adapter._session_id,
            "dailies_count": len(dailies),
        }

    def _cmd_memory_lint(self, content: str | None = None) -> dict[str, Any]:
        """Handle /bb-memory-lint command.

        Run lint checks on content.

        Args:
            content: Optional content to lint.
        """
        from ..runtime.gate import LintService

        service = LintService()

        if content:
            result = service.lint_daily(content)
        else:
            result = {"message": "No content provided for lint"}

        return {
            "success": True,
            "lint_result": result,
        }

    def handle(self, command: str, **kwargs: Any) -> dict[str, Any]:
        """Handle a command.

        Args:
            command: Command name.
            **kwargs: Command arguments.

        Returns:
            Command result.
        """
        return self._adapter.handle_command(command, kwargs)


# Global adapter instance
def get_opencode_adapter() -> OpenCodeAdapter:
    """Get global OpenCode adapter instance."""
    return OpenCodeAdapter()
