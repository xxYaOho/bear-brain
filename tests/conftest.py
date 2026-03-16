from pathlib import Path

import pytest


@pytest.fixture
def sample_daily_text() -> str:
    path = Path(__file__).parent / "fixtures" / "daily" / "daily_memory_sample.md"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def sample_reusable_daily_text() -> str:
    path = Path(__file__).parent / "fixtures" / "daily" / "daily_memory_reusable.md"
    return path.read_text(encoding="utf-8")
