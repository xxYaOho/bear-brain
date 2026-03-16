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
