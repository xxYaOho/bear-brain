"""CLI Support Module.

Command-line interface for bear-brain operations.
This is the main CLI implementation moved to support layer.

Note: Import from bear_brain.cli for backward compatibility.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from ..config import load_settings
from ..daily_hook import DailyHookEntry, append_daily_entry, should_write_daily
from ..docs_publish import publish_doc
from ..memory_store import ensure_schema, upsert_document
from ..promote import apply_promote_to_files
from ..search import make_ollama_embedder, search_memory_db
from ..search_index import sync_local_sources


def _default_memory_file(project_root: Path) -> Path | None:
    candidate = project_root / "memory.md"
    return candidate if candidate.exists() else None


def _default_daily_dir(project_root: Path) -> Path | None:
    candidate = project_root / "daily"
    return candidate if candidate.exists() else None


def _default_docs_dir(project_root: Path) -> Path | None:
    candidate = project_root / "docs"
    return candidate if candidate.exists() else None


def _latest_daily_file(project_root: Path) -> Path | None:
    daily_dir = _default_daily_dir(project_root)
    if daily_dir is None:
        return None

    candidates = sorted(path for path in daily_dir.glob("*.md") if path.is_file())
    return candidates[-1] if candidates else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory_worker.py")
    subparsers = parser.add_subparsers(dest="command")

    bootstrap = subparsers.add_parser("bootstrap")
    bootstrap.add_argument("--project-root", type=Path, default=Path.cwd())

    promote = subparsers.add_parser("promote-yesterday")
    promote.add_argument("--project-root", type=Path, default=Path.cwd())
    promote.add_argument("--daily-file", type=Path)
    promote.add_argument("--memory-file", type=Path)

    search = subparsers.add_parser("search")
    search.add_argument("--project-root", type=Path, default=Path.cwd())
    search.add_argument("--query", required=False, default="")
    search.add_argument("--memory-file", type=Path)
    search.add_argument("--daily-dir", type=Path)
    search.add_argument("--docs-dir", type=Path)

    publish = subparsers.add_parser("publish-doc")
    publish.add_argument("--project-root", type=Path, default=Path.cwd())
    publish.add_argument("--doc-type", required=True)

    append_daily = subparsers.add_parser("append-daily")
    append_daily.add_argument("--project-root", type=Path, default=Path.cwd())
    append_daily.add_argument("--did", required=True)
    append_daily.add_argument("--found", required=True)
    append_daily.add_argument("--judgment", required=True)

    return parser


def _bootstrap(project_root: Path) -> int:
    settings = load_settings(project_root)
    settings.memory_db.parent.mkdir(parents=True, exist_ok=True)
    ensure_schema(settings.memory_db)
    return 0


def _publish_doc(project_root: Path, doc_type: str) -> int:
    publish_doc(project_root, doc_type)
    return 0


def _append_daily(project_root: Path, did: str, found: str, judgment: str) -> int:
    settings = load_settings(project_root)
    if not should_write_daily(project_root, settings.daily_global):
        return 0

    append_daily_entry(
        project_root,
        DailyHookEntry(did=did, found=found, judgment=judgment),
    )
    return 0


def _search(
    project_root: Path,
    query: str,
    memory_file: Path | None,
    daily_dir: Path | None,
    docs_dir: Path | None,
) -> int:
    settings = load_settings(project_root)
    memory_file = memory_file or _default_memory_file(project_root)
    daily_dir = daily_dir or _default_daily_dir(project_root)
    docs_dir = docs_dir or _default_docs_dir(project_root)
    sync_local_sources(
        settings.memory_db,
        memory_file=memory_file,
        daily_dir=daily_dir,
        docs_dir=docs_dir,
    )
    hits = search_memory_db(settings.memory_db, query=query, limit=10)
    for hit in hits:
        print(hit.title)
    return 0


def _promote_yesterday(
    project_root: Path,
    daily_file: Path | None,
    memory_file: Path | None,
) -> int:
    daily_file = daily_file or _latest_daily_file(project_root)
    memory_file = memory_file or _default_memory_file(project_root)
    if daily_file is None or memory_file is None:
        raise SystemExit("promote-yesterday requires --daily-file and --memory-file")
    apply_promote_to_files(daily_file, memory_file)
    _embed_memory_file(project_root, memory_file)
    return 0


def _embed_memory_file(project_root: Path, memory_file: Path) -> None:
    settings = load_settings(project_root)
    if not memory_file.exists():
        return

    try:
        embedder = make_ollama_embedder(
            base_url=settings.ollama_base_url,
            model=settings.embedding_model,
            expected_dim=512,
        )
    except Exception:
        return

    content = memory_file.read_text(encoding="utf-8")
    embedding = embedder(content)
    updated_at = datetime.now(timezone.utc).isoformat()

    upsert_document(
        settings.memory_db,
        source="memory",
        source_id=str(memory_file),
        title=memory_file.stem,
        content=content,
        updated_at=updated_at,
        embedding=embedding,
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "bootstrap":
        return _bootstrap(args.project_root)
    if args.command == "promote-yesterday":
        return _promote_yesterday(args.project_root, args.daily_file, args.memory_file)
    if args.command == "search":
        return _search(
            args.project_root,
            args.query,
            args.memory_file,
            args.daily_dir,
            args.docs_dir,
        )
    if args.command == "publish-doc":
        return _publish_doc(args.project_root, args.doc_type)
    if args.command == "append-daily":
        return _append_daily(args.project_root, args.did, args.found, args.judgment)

    parser.print_help()
    return 0
