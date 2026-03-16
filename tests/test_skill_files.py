from pathlib import Path


def test_actual_skill_files_exist() -> None:
    root = Path("skills/bearbrain")
    expected = {
        "admission",
        "bear-editing",
        "book-entry",
        "context-router",
        "doc-publish",
        "memory",
        "note-lint",
        "promote-memory",
        "search",
        "workstream",
    }
    found = {path.name for path in root.iterdir() if path.is_dir()}
    assert expected.issubset(found)
    assert "write-core" not in found
    assert "governance-core" not in found
    assert "search-core" not in found

    for name in expected:
        assert (root / name / "SKILL.md").exists()


def test_bear_editing_uses_code_wrapped_tags_in_body_guidance() -> None:
    bear_editing = Path("skills/bearbrain/bear-editing/SKILL.md").read_text(encoding="utf-8")
    note_lint = Path("skills/bearbrain/note-lint/SKILL.md").read_text(encoding="utf-8")

    assert "`#memory`" in bear_editing
    assert "裸写 `#tag`" in bear_editing
    assert "代码包裹形式，如 `#memory`" in note_lint
