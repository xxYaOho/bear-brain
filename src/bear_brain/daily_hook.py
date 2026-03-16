from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class DailyHookEntry:
    did: str
    found: str
    judgment: str


def should_write_daily(project_root: Path, daily_global: bool) -> bool:
    return daily_global or project_root.name == "bear-brain"


def append_daily_entry(
    project_root: Path,
    entry: DailyHookEntry,
    now: datetime | None = None,
) -> Path:
    current = now or datetime.now()
    daily_dir = project_root / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    daily_path = daily_dir / f"{current.date().isoformat()}.md"

    if not daily_path.exists():
        daily_path.write_text(
            "## Promote Status\n"
            "- Status: pending\n"
            "- Promoted At:\n"
            "- Promoted To:\n\n"
            "## Summary\n"
            "- 今日主线：\n"
            "- 关键发现：\n"
            "- 是否有值得提炼的内容：\n\n"
            "## Log\n",
            encoding="utf-8",
        )

    existing = daily_path.read_text(encoding="utf-8").rstrip()
    block = (
        f"### {current.strftime('%Y-%m-%d %H:%M')}\n"
        f"- 做了什么：{entry.did}\n"
        f"- 发现了什么：{entry.found}\n"
        f"- 当前判断是什么：{entry.judgment}\n"
    )
    daily_path.write_text(f"{existing}\n\n{block}", encoding="utf-8")
    return daily_path
