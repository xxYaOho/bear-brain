"""Bear-Brain Services Layer.

Services layer contains business logic for memory operations.
This layer is responsible for:
- Memory service: CRUD operations for memory
- Promote service: Logic for promoting daily to memory
- Daily service: Daily note management
"""

from __future__ import annotations

__all__ = [
    "memory_service",
    "promote_service",
    "daily_service",
]
