"""Bear-Brain: Memory Core Runtime.

Bear-Brain is a local-first memory infrastructure for agent collaboration.

Architecture:
    runtime/    - Core execution layer (preload, triggers, state machine, gates)
    services/   - Business logic layer (memory, daily, promote services)
    adapters/   - External integration layer (Bear, OpenCode)
    support/    - Auxiliary tools (CLI, legacy search)

Usage:
    from bear_brain import MemoryPreloader
    from bear_brain.services import DailyService
    from bear_brain.runtime import PromoteStateMachine
"""

from __future__ import annotations

# Runtime layer exports
from .runtime.preload import (
    MemoryPreloader,
    PreloadResult,
    get_preload_context,
    preload_memory,
)
from .runtime.state_machine import (
    PromoteEvent,
    PromoteRecord,
    PromoteState,
    PromoteStateMachine,
    PromoteStateStore,
)
from .runtime.gate import (
    GateLevel,
    GateResult,
    LintService,
    MemoryGate,
    run_gate_check,
    should_block_operation,
)
from .runtime.trigger import (
    DailyCreateTrigger,
    SessionStartTrigger,
    TriggerAction,
    TriggerConfig,
    TriggerEvent,
    TriggerManager,
    TriggerType,
    get_trigger_manager,
)

# Service layer exports
from .services.memory_service import (
    MemoryPreloadService,
    MemoryService,
    MemoryServiceResult,
)
from .services.daily_service import (
    DailyHookService,
    DailyService,
    DailyServiceResult,
)
from .services.promote_service import (
    PromoteService,
    PromoteServiceResult,
    promote_yesterday,
)

# Adapter layer exports
from .adapters.bear_adapter import (
    BearAdapter,
    BearNote,
)
from .adapters.opencode_adapter import (
    CommandRegistry,
    OpenCodeAdapter,
    OpenCodeEvent,
    get_opencode_adapter,
)

# Keep existing exports for backward compatibility
from .cli import main
from .config import load_settings, Settings
from .models import (
    DailyEntry,
    MemoryTopic,
    PromoteStatus,
    PublishedDoc,
    SearchHit,
)

__version__ = "0.2.0"

__all__ = [
    # Version
    "__version__",
    # Runtime
    "MemoryPreloader",
    "PreloadResult",
    "get_preload_context",
    "preload_memory",
    "PromoteEvent",
    "PromoteRecord",
    "PromoteState",
    "PromoteStateMachine",
    "PromoteStateStore",
    "GateLevel",
    "GateResult",
    "LintService",
    "MemoryGate",
    "run_gate_check",
    "should_block_operation",
    "DailyCreateTrigger",
    "SessionStartTrigger",
    "TriggerAction",
    "TriggerConfig",
    "TriggerEvent",
    "TriggerManager",
    "TriggerType",
    "get_trigger_manager",
    # Services
    "MemoryPreloadService",
    "MemoryService",
    "MemoryServiceResult",
    "DailyHookService",
    "DailyService",
    "DailyServiceResult",
    "PromoteService",
    "PromoteServiceResult",
    "promote_yesterday",
    # Adapters
    "BearAdapter",
    "BearNote",
    "CommandRegistry",
    "OpenCodeAdapter",
    "OpenCodeEvent",
    "get_opencode_adapter",
    # Legacy compatibility
    "main",
    "load_settings",
    "Settings",
    "DailyEntry",
    "MemoryTopic",
    "PromoteStatus",
    "PublishedDoc",
    "SearchHit",
]
