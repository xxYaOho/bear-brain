"""Memory Service.

Business logic for managing long-term memory.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..adapters.bear_adapter import BearAdapter, BearNote
from ..memory_store import ensure_schema, upsert_document
from ..search import make_ollama_embedder, search_memory_db

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MemoryServiceResult:
    """Result of memory operation."""

    success: bool
    items_added: list[str]
    error: str | None = None


class MemoryService:
    """Service for managing long-term memory.

    Responsibilities:
    - Load and update memory content
    - Add new items to Core Memory
    - Sync with vector database
    - Coordinate with Bear notes
    """

    def __init__(
        self,
        memory_file: Path | None = None,
        project_root: Path | None = None,
    ) -> None:
        """Initialize service.

        Args:
            memory_file: Path to memory file (defaults to ./memory.md).
            project_root: Project root directory.
        """
        self._project_root = project_root or Path.cwd()
        self._memory_file = memory_file or self._project_root / "memory.md"
        self._bear = BearAdapter()

    def load_memory(self) -> str:
        """Load memory content.

        Returns:
            Memory content (empty string if not found).
        """
        if self._memory_file.exists():
            try:
                return self._memory_file.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
                return ""
        return ""

    def add_to_core(
        self,
        items: list[str],
        check_duplicates: bool = True,
    ) -> MemoryServiceResult:
        """Add items to Core Memory section.

        Args:
            items: Items to add.
            check_duplicates: Whether to check for duplicates.

        Returns:
            MemoryServiceResult.
        """
        if not items:
            return MemoryServiceResult(
                success=True,
                items_added=[],
                error=None,
            )

        try:
            memory_text = self.load_memory()

            # Check for existing items if requested
            if check_duplicates and "## Core Memory" in memory_text:
                existing_items = self._extract_core_items(memory_text)
                items = [item for item in items if item not in existing_items]

            if not items:
                return MemoryServiceResult(
                    success=True,
                    items_added=[],
                    error=None,
                )

            # Update memory content
            updated = self._add_items_to_core(memory_text, items)
            self._memory_file.write_text(updated, encoding="utf-8")

            logger.info(f"Added {len(items)} items to Core Memory")
            return MemoryServiceResult(
                success=True,
                items_added=items,
                error=None,
            )
        except Exception as e:
            logger.error(f"Failed to add to Core Memory: {e}")
            return MemoryServiceResult(
                success=False,
                items_added=[],
                error=str(e),
            )

    def sync_to_vector_db(
        self,
        db_path: Path,
        ollama_base_url: str = "http://127.0.0.1:11434",
        embedding_model: str = "qwen3-embedding:0.6b",
    ) -> bool:
        """Sync memory to vector database.

        Args:
            db_path: Path to SQLite database.
            ollama_base_url: Ollama server URL.
            embedding_model: Embedding model name.

        Returns:
            True if successful.
        """
        try:
            # Ensure schema
            ensure_schema(db_path, embedding_model=embedding_model)

            # Load memory content
            content = self.load_memory()
            if not content:
                logger.warning("No memory content to sync")
                return True

            # Get embedding
            try:
                embedder = make_ollama_embedder(
                    base_url=ollama_base_url,
                    model=embedding_model,
                    expected_dim=512,
                )
                embedding = embedder(content)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
                # Continue without embedding
                embedding = None

            # Upsert document
            from datetime import datetime, timezone

            updated_at = datetime.now(timezone.utc).isoformat()
            upsert_document(
                db_path,
                source="memory",
                source_id=str(self._memory_file),
                title=self._memory_file.stem,
                content=content,
                updated_at=updated_at,
                embedding=embedding,
            )

            logger.info(f"Synced memory to vector DB: {db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to sync to vector DB: {e}")
            return False

    def search(
        self,
        query: str,
        db_path: Path,
        limit: int = 10,
    ) -> list[Any]:
        """Search memory.

        Args:
            query: Search query.
            db_path: Path to database.
            limit: Max results.

        Returns:
            List of search hits.
        """
        try:
            return search_memory_db(db_path, query=query, limit=limit)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _extract_core_items(self, memory_text: str) -> set[str]:
        """Extract existing items from Core Memory section.

        Args:
            memory_text: Memory content.

        Returns:
            Set of item texts (normalized).
        """
        items = set()

        # Find Core Memory section
        match = re.search(
            r"## Core Memory\n(.*?)(?:\n## |\Z)",
            memory_text,
            re.DOTALL,
        )
        if match:
            body = match.group(1)
            for line in body.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    items.add(line[2:].strip())

        return items

    def _add_items_to_core(
        self,
        memory_text: str,
        items: list[str],
    ) -> str:
        """Add items to Core Memory section.

        Args:
            memory_text: Current memory content.
            items: Items to add.

        Returns:
            Updated memory content.
        """
        lines = [f"- {item}" for item in items]

        if "## Core Memory" in memory_text:
            # Insert after header
            pattern = r"(## Core Memory\n)(.*?)(\n## |\Z)"

            def _insert(match: re.Match[str]) -> str:
                body = match.group(2).rstrip()
                body_lines = [ln for ln in body.splitlines() if ln.strip()]
                body_lines.extend(lines)
                suffix = match.group(3) if match.group(3) else ""
                return f"## Core Memory\n{'\n'.join(body_lines)}{suffix}"

            return re.sub(pattern, _insert, memory_text, count=1, flags=re.DOTALL)
        else:
            # Create new section
            return (
                memory_text.rstrip()
                + "\n\n## Core Memory\n"
                + "\n".join(lines)
                + "\n"
            )


class MemoryPreloadService:
    """Service for preloading memory at session start.

    This service provides a clean interface for the runtime layer
to preload memory content.
    """

    def __init__(
        self,
        memory_file: Path | None = None,
        use_bear: bool = True,
    ) -> None:
        """Initialize service.

        Args:
            memory_file: Path to memory file.
            use_bear: Whether to try loading from Bear first.
        """
        self._memory_service = MemoryService(memory_file=memory_file)
        self._bear = BearAdapter() if use_bear else None

    def preload(self) -> dict[str, Any]:
        """Preload memory and return context.

        Returns:
            Dict with memory_content key if successful.
        """
        context: dict[str, Any] = {}

        # Try Bear first if enabled
        if self._bear and self._bear.is_available():
            note = self._bear.get_memory_note()
            if note:
                context["memory_content"] = note.text
                context["memory_source"] = "bear"
                return context

        # Fall back to file
        content = self._memory_service.load_memory()
        if content:
            context["memory_content"] = content
            context["memory_source"] = "file"

        return context
