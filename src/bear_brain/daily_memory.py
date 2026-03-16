from __future__ import annotations

import re
from datetime import datetime

from .models import DailyEntry, PromoteStatus

_STATUS_RE = re.compile(r"^- Status:\s*(?P<value>.+)$", re.MULTILINE)
_SUMMARY_RE = re.compile(r"## Summary\n(?P<body>.*?)(?:\n## |\Z)", re.DOTALL)
_LOG_RE = re.compile(r"## Log\n(?P<body>.*)\Z", re.DOTALL)


def parse_daily_memory(text: str) -> DailyEntry:
    status_match = _STATUS_RE.search(text)
    summary_match = _SUMMARY_RE.search(text)
    log_match = _LOG_RE.search(text)

    status = status_match.group("value").strip() if status_match else "pending"
    summary_lines = []
    if summary_match:
        summary_lines = [
            line.strip()
            for line in summary_match.group("body").splitlines()
            if line.strip()
        ]

    log_blocks = []
    if log_match:
        log_blocks = [
            block.strip()
            for block in log_match.group("body").split("\n### ")
            if block.strip()
        ]

    return DailyEntry(
        promote=PromoteStatus(state=status),
        summary=summary_lines,
        log_blocks=log_blocks,
        raw_text=text,
    )


def render_promote_status(state: str, promoted_at: str, promoted_to: list[str]) -> str:
    promoted_to_text = ", ".join(promoted_to)
    lines = [
        "## Promote Status",
        f"- Status: {state}",
        f"- Promoted At: {promoted_at}",
        f"- Promoted To: {promoted_to_text}",
    ]
    return "\n".join(lines)


def prepend_promote_status(
    text: str,
    state: str,
    promoted_to: list[str],
    now: datetime | None = None,
) -> str:
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d %H:%M")
    block = render_promote_status(state, timestamp, promoted_to)
    if text.startswith("## Promote Status"):
        parts = text.split("## Summary", maxsplit=1)
        if len(parts) == 2:
            return f"{block}\n\n## Summary{parts[1]}"
    return f"{block}\n\n{text}"
