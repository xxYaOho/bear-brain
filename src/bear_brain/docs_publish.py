from __future__ import annotations

from pathlib import Path

_DOC_TARGETS = {
    "spec": Path("docs/product/SPEC.md"),
    "guide": Path("docs/guide/GUIDE.md"),
    "changelog": Path("docs/CHANGELOG.md"),
    "completions": Path("docs/COMPLETIONS.md"),
    "decisions": Path("docs/DECISIONS.md"),
}


_DOC_SKELETONS = {
    "spec": (
        "# SPEC\n\n## Purpose\n\n## Scope\n\n## Behavior\n\n"
        "## Constraints\n\n## Acceptance\n\n## Notes\n"
    ),
    "guide": (
        "# GUIDE\n\n## Scope\n\n## Rules\n\n## Workflow\n\n"
        "## Exceptions\n\n## Examples\n\n## Maintenance\n"
    ),
    "changelog": (
        "# Changelog\n\n## [Unreleased]\n\n### Added\n"
        "### Changed\n### Fixed\n### Removed\n"
    ),
    "completions": (
        "# COMPLETIONS\n\n## Context\n\n## Completed\n\n"
        "## Not Completed\n\n## Impact\n\n## Next\n"
    ),
    "decisions": "# DECISIONS\n",
}


def classify_publish_target(doc_type: str) -> Path:
    try:
        return _DOC_TARGETS[doc_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported doc type: {doc_type}") from exc


def ensure_initial_docs(project_root: Path) -> None:
    for doc_type, relative_path in _DOC_TARGETS.items():
        path = project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(_DOC_SKELETONS[doc_type], encoding="utf-8")


def publish_doc(project_root: Path, doc_type: str) -> Path:
    ensure_initial_docs(project_root)
    return project_root / classify_publish_target(doc_type)
