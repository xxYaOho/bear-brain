from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from .memory_store import upsert_document

_TITLE_RE = re.compile(r"^#\s+(?P<title>.+)$", re.MULTILINE)


def _read_markdown(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    title_match = _TITLE_RE.search(text)
    title = title_match.group("title").strip() if title_match else path.stem
    return title, text


def _iter_markdown_files(path: Path | None) -> Iterable[Path]:
    if path is None or not path.exists():
        return ()
    if path.is_file() and path.suffix == ".md":
        return (path,)
    return tuple(sorted(candidate for candidate in path.rglob("*.md") if candidate.is_file()))


def sync_local_sources(
    db_path: Path,
    *,
    memory_file: Path | None = None,
    daily_dir: Path | None = None,
    docs_dir: Path | None = None,
) -> int:
    indexed = 0
    source_specs = (
        ("memory", _iter_markdown_files(memory_file)),
        ("daily", _iter_markdown_files(daily_dir)),
        ("docs", _iter_markdown_files(docs_dir)),
    )

    for source, paths in source_specs:
        for path in paths:
            title, content = _read_markdown(path)
            updated_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
            upsert_document(
                db_path,
                source=source,
                source_id=str(path),
                title=title,
                content=content,
                updated_at=updated_at,
            )
            indexed += 1

    return indexed
