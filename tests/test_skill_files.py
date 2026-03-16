from pathlib import Path


def test_core_skill_files_exist() -> None:
    root = Path("skills/bearbrain")
    assert (root / "bear-editing" / "SKILL.md").exists()
    assert (root / "search-core" / "SKILL.md").exists()
