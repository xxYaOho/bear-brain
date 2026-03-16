from pathlib import Path

from bear_brain.memory_store import ensure_schema, upsert_document
from bear_brain.router import choose_search_modes
from bear_brain.search import search_docs_scope, search_memory_db


def test_router_defaults_to_memory_first() -> None:
    modes = choose_search_modes(task_type="general", repo=None, explicit_refs=False)
    assert modes[0] == "memory_db"


def test_router_adds_docs_scope_for_repo_work() -> None:
    modes = choose_search_modes(task_type="implementation", repo="bear-brain", explicit_refs=False)
    assert "docs_scope" in modes


def test_router_adds_note_refs_when_explicit_refs_exist() -> None:
    modes = choose_search_modes(task_type="general", repo=None, explicit_refs=True)
    assert "note_refs" in modes


def test_search_memory_db_returns_matching_document(tmp_path: Path) -> None:
    db_path = tmp_path / "memory.db"
    ensure_schema(db_path)
    upsert_document(
        db_path,
        source="memory",
        source_id="topic-vector",
        title="Vector Memory",
        content="固定使用 512 维 embedding",
        updated_at="2026-03-16T10:00:00Z",
    )

    hits = search_memory_db(db_path, query="512 维", limit=5)
    assert hits
    assert hits[0].title == "Vector Memory"


def test_search_memory_db_can_use_vector_similarity(tmp_path: Path) -> None:
    db_path = tmp_path / "memory.db"
    ensure_schema(db_path, embedding_dim=3)
    upsert_document(
        db_path,
        source="memory",
        source_id="vector-a",
        title="Semantic A",
        content="alpha",
        updated_at="2026-03-16T10:00:00Z",
        embedding=[1.0, 0.0, 0.0],
    )
    upsert_document(
        db_path,
        source="memory",
        source_id="vector-b",
        title="Semantic B",
        content="beta",
        updated_at="2026-03-16T10:00:00Z",
        embedding=[0.0, 1.0, 0.0],
    )

    hits = search_memory_db(
        db_path,
        query="semantic query",
        limit=5,
        embedder=lambda _query: [1.0, 0.0, 0.0],
    )
    assert hits
    assert hits[0].title == "Semantic A"


def test_search_docs_scope_returns_matching_doc(tmp_path: Path) -> None:
    docs_root = tmp_path / "docs"
    (docs_root / "product").mkdir(parents=True)
    spec_path = docs_root / "product" / "SPEC.md"
    spec_path.write_text(
        "# SPEC\n\n## Constraints\n\n固定使用 512 维 embedding\n",
        encoding="utf-8",
    )

    hits = search_docs_scope(docs_root, query="512 维", limit=5)
    assert hits
    assert hits[0].metadata["path"].endswith("SPEC.md")
