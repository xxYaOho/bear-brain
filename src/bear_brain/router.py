from __future__ import annotations


def choose_search_modes(task_type: str, repo: str | None, explicit_refs: bool) -> list[str]:
    modes = ["memory_db"]
    if explicit_refs:
        modes.append("note_refs")
    if repo and task_type in {"implementation", "bugfix", "review", "docs"}:
        modes.append("docs_scope")
    return modes
