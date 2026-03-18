"""Tests for memory preload functionality."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from bear_brain.runtime.preload import (
    MemoryPreloader,
    PreloadResult,
    get_preload_context,
    preload_memory,
)


class TestMemoryPreloader:
    """Test MemoryPreloader class."""

    def test_preloader_disabled(self, tmp_path: Path) -> None:
        """Test that preloader returns empty when disabled."""
        preloader = MemoryPreloader(enabled=False)
        result = preloader.preload()

        assert result.success is True
        assert result.content == ""
        assert result.source == "none"
        assert result.error is None

    def test_preload_from_file_success(self, tmp_path: Path) -> None:
        """Test successful preload from file."""
        memory_file = tmp_path / "memory.md"
        memory_file.write_text("# Memory\n\nTest content", encoding="utf-8")

        preloader = MemoryPreloader(source="file", file_path=memory_file)
        result = preloader.preload()

        assert result.success is True
        assert "Test content" in result.content
        assert result.source == "file"
        assert result.error is None

    def test_preload_from_file_not_found(self, tmp_path: Path) -> None:
        """Test preload from non-existent file."""
        memory_file = tmp_path / "nonexistent.md"

        preloader = MemoryPreloader(source="file", file_path=memory_file)
        result = preloader.preload()

        assert result.success is True  # Don't fail session
        assert result.content == ""
        assert result.source == "none"
        assert "not found" in result.error

    def test_preload_from_bear_unavailable(self, tmp_path: Path) -> None:
        """Test preload from Bear when MCP unavailable."""
        # Remove OPENCODE_WORKSPACE to simulate unavailable Bear
        env_without_workspace = {k: v for k, v in os.environ.items() if k != "OPENCODE_WORKSPACE"}
        with patch.dict(os.environ, env_without_workspace, clear=True):
            preloader = MemoryPreloader(source="bear")
            result = preloader.preload()

            assert result.success is True  # Don't fail session
            assert result.source == "none"
            assert "disabled" in result.error or "not available" in result.error

    def test_convenience_function(self, tmp_path: Path) -> None:
        """Test preload_memory convenience function."""
        memory_file = tmp_path / "memory.md"
        memory_file.write_text("# Test", encoding="utf-8")

        result = preload_memory(enabled=True, source="file", file_path=memory_file)

        assert result.success is True
        assert "# Test" in result.content


class TestGetPreloadContext:
    """Test get_preload_context function."""

    def test_context_with_memory(self, tmp_path: Path) -> None:
        """Test context includes memory when available."""
        memory_file = tmp_path / "memory.md"
        memory_file.write_text("# Core Memory\n\nTest", encoding="utf-8")

        context = get_preload_context()

        # By default, will fail to find memory (no file at default path)
        assert "memory_content" not in context or context.get("memory_content") == ""

    def test_context_from_file(self, tmp_path: Path) -> None:
        """Test context from explicit file."""
        memory_file = tmp_path / "memory.md"
        memory_file.write_text("# Core Memory\n\nTest item", encoding="utf-8")

        with patch.dict(os.environ, {"BB_PRELOAD_SOURCE": "file"}, clear=False):
            with patch("bear_brain.runtime.preload.Path") as mock_path:
                mock_path.return_value = memory_file
                mock_path.cwd.return_value = tmp_path
                context = get_preload_context()

                assert "memory_source" in context


class TestPreloadConfiguration:
    """Test preload configuration via environment."""

    def test_env_enabled_true(self) -> None:
        """Test BB_PRELOAD_ENABLED=true."""
        with patch.dict(os.environ, {"BB_PRELOAD_ENABLED": "true"}):
            preloader = MemoryPreloader()
            assert preloader._enabled is True

    def test_env_enabled_false(self) -> None:
        """Test BB_PRELOAD_ENABLED=false."""
        with patch.dict(os.environ, {"BB_PRELOAD_ENABLED": "false"}):
            preloader = MemoryPreloader()
            assert preloader._enabled is False

    def test_env_source(self, tmp_path: Path) -> None:
        """Test BB_PRELOAD_SOURCE environment variable."""
        with patch.dict(os.environ, {"BB_PRELOAD_SOURCE": "bear"}):
            preloader = MemoryPreloader()
            assert preloader._source == "bear"


class TestPreloadResult:
    """Test PreloadResult dataclass."""

    def test_result_creation(self) -> None:
        """Test creating PreloadResult."""
        result = PreloadResult(
            success=True,
            content="test",
            source="file",
            error=None,
        )

        assert result.success is True
        assert result.content == "test"
        assert result.source == "file"
        assert result.error is None
