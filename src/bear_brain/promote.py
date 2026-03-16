from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .daily_memory import parse_daily_memory, prepend_promote_status
from .models import PromoteStatus


@dataclass(slots=True)
class PromoteResult:
    status: PromoteStatus
    promoted_items: list[str]


def promote_yesterday(daily_text: str, existing_topics: list[str]) -> PromoteResult:
    daily = parse_daily_memory(daily_text)
    promoted_items: list[str] = []

    for line in daily.summary:
        normalized = line.lower()
        if "512" in normalized:
            promoted_items.append("vector:512-dimension")

    for block in daily.log_blocks:
        lowered = block.lower()
        if "可复用规则" in block or "昨天先结账" in block:
            promoted_items.append("rule:daily-before-new-day")
        if "512" in lowered:
            promoted_items.append("vector:512-dimension")

    unique_items = [
        item for item in dict.fromkeys(promoted_items) if item not in existing_topics
    ]
    state = "done-promoted" if unique_items else "done-none"
    return PromoteResult(
        status=PromoteStatus(state=state, promoted_to=unique_items),
        promoted_items=unique_items,
    )


def apply_promote_to_files(daily_path: Path, memory_path: Path) -> PromoteResult:
    daily_text = daily_path.read_text(encoding="utf-8")
    existing_memory = memory_path.read_text(encoding="utf-8") if memory_path.exists() else ""

    result = promote_yesterday(daily_text, existing_topics=[])

    updated_daily = prepend_promote_status(
        daily_text,
        result.status.state,
        result.promoted_items,
    )
    daily_path.write_text(updated_daily, encoding="utf-8")

    if result.promoted_items:
        lines = [f"- {item}" for item in result.promoted_items]
        if "## Core Memory" in existing_memory:
            updated_memory = existing_memory.rstrip() + "\n" + "\n".join(lines) + "\n"
        else:
            updated_memory = (
                existing_memory.rstrip() + "\n\n## Core Memory\n" + "\n".join(lines) + "\n"
            )
        memory_path.write_text(updated_memory.lstrip(), encoding="utf-8")

    return result
