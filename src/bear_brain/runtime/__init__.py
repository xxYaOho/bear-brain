"""Bear-Brain Runtime Layer.

Runtime layer provides the core execution environment for memory operations.
This layer is responsible for:
- Memory preloading at session start
- Trigger management for automated workflows
- State machine for promote operations
- Gate/lint enforcement
"""

from __future__ import annotations

__all__ = [
    "preload",
    "trigger",
    "state_machine",
    "gate",
]
