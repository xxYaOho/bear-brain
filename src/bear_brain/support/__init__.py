"""Bear-Brain Support Layer.

Support layer contains auxiliary tools and CLI.
This layer is responsible for:
- CLI interface for manual operations
- Legacy search utilities
- Helper scripts

Note: This layer should depend on runtime/services layers,
but runtime/services should NOT depend on support.
"""

from __future__ import annotations

__all__ = [
    "cli",
    "search_legacy",
]
