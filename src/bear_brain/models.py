from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class PromoteStatus:
    state: str = "pending"
    promoted_at: datetime | None = None
    promoted_to: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DailyEntry:
    promote: PromoteStatus
    summary: list[str]
    log_blocks: list[str]
    raw_text: str


@dataclass(slots=True)
class MemoryTopic:
    title: str
    path: Path | None = None
    summary: str = ""


@dataclass(slots=True)
class PublishedDoc:
    doc_type: str
    target_path: Path


@dataclass(slots=True)
class SearchHit:
    source: str
    title: str
    content: str
    score: float = 0.0
    metadata: dict[str, str] = field(default_factory=dict)
