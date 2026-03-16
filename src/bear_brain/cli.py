from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_settings
from .docs_publish import publish_doc
from .memory_store import ensure_schema
from .promote import apply_promote_to_files
from .search import search_memory_db


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

    publish = subparsers.add_parser("publish-doc")
    publish.add_argument("--project-root", type=Path, default=Path.cwd())
    publish.add_argument("--doc-type", required=True)

    return parser


def _bootstrap(project_root: Path) -> int:
    settings = load_settings(project_root)
    settings.memory_db.parent.mkdir(parents=True, exist_ok=True)
    ensure_schema(settings.memory_db)
    return 0


def _publish_doc(project_root: Path, doc_type: str) -> int:
    publish_doc(project_root, doc_type)
    return 0


def _search(project_root: Path, query: str) -> int:
    settings = load_settings(project_root)
    hits = search_memory_db(settings.memory_db, query=query, limit=10)
    for hit in hits:
        print(hit.title)
    return 0


def _promote_yesterday(
    project_root: Path,
    daily_file: Path | None,
    memory_file: Path | None,
) -> int:
    if daily_file is None or memory_file is None:
        raise SystemExit("promote-yesterday requires --daily-file and --memory-file")
    apply_promote_to_files(daily_file, memory_file)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "bootstrap":
        return _bootstrap(args.project_root)
    if args.command == "promote-yesterday":
        return _promote_yesterday(args.project_root, args.daily_file, args.memory_file)
    if args.command == "search":
        return _search(args.project_root, args.query)
    if args.command == "publish-doc":
        return _publish_doc(args.project_root, args.doc_type)

    parser.print_help()
    return 0
