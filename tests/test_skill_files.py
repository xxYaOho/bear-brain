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


def test_bear_editing_requires_evidence_before_writing() -> None:
    bear_editing = Path("skills/bearbrain/bear-editing/SKILL.md").read_text(encoding="utf-8")
    daily_reference = Path("skills/bearbrain/bear-editing/reference/daily-memory.md").read_text(
        encoding="utf-8"
    )
    workstream = Path("skills/bearbrain/workstream/SKILL.md").read_text(encoding="utf-8")

    assert "先搜索或打开目标笔记" in bear_editing
    assert "真实系统时间" in bear_editing
    assert "禁止猜测" in bear_editing
    assert "不得凭记忆填写 NOTE-ID" in bear_editing
    assert "时间块标题必须来自真实系统时间" in daily_reference
    assert "不得凭记忆更新 Status、release、NOTE-ID" in workstream


def test_note_lint_requires_write_evidence_output() -> None:
    note_lint = Path("skills/bearbrain/note-lint/SKILL.md").read_text(encoding="utf-8")
    spec = Path("docs/product/SPEC.md").read_text(encoding="utf-8")

    assert "真实时间来源" in note_lint
    assert "写入前证据" in note_lint
    assert "先查后写" in spec
    assert "禁止猜测时间、NOTE-ID、Status" in spec
