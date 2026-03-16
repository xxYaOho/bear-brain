import sqlite3
from pathlib import Path

from bear_brain.memory_store import (
    ensure_schema,
    get_index_meta,
    list_vector_rowids,
    upsert_document,
)


def test_ensure_schema_creates_required_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "memory.db"
    ensure_schema(db_path)

    assert db_path.exists()

    with sqlite3.connect(db_path) as connection:
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }

    assert {"documents", "index_meta", "promote_runs", "documents_vec"}.issubset(names)


def test_ensure_schema_records_embedding_metadata(tmp_path: Path) -> None:
    db_path = tmp_path / "memory.db"
    ensure_schema(db_path, embedding_model="qwen3-embedding:0.6b", embedding_dim=512)

    meta = get_index_meta(db_path)
    assert meta["embedding_model"] == "qwen3-embedding:0.6b"
    assert meta["embedding_dim"] == "512"


def test_upsert_document_replaces_existing_source_entry(tmp_path: Path) -> None:
    db_path = tmp_path / "memory.db"
    ensure_schema(db_path)
    upsert_document(
        db_path,
        source="memory",
        source_id="root",
        title="Memory Root",
        content="first version",
        updated_at="2026-03-16T09:00:00Z",
    )
    upsert_document(
        db_path,
        source="memory",
        source_id="root",
        title="Memory Root",
        content="second version",
        updated_at="2026-03-16T10:00:00Z",
    )

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT content, updated_at FROM documents "
            "WHERE source = 'memory' AND source_id = 'root'"
        ).fetchall()

    assert rows == [("second version", "2026-03-16T10:00:00Z")]


def test_upsert_document_stores_embedding_vector(tmp_path: Path) -> None:
    db_path = tmp_path / "memory.db"
    ensure_schema(db_path, embedding_dim=3)
    upsert_document(
        db_path,
        source="memory",
        source_id="vector-topic",
        title="Vector Topic",
        content="semantic content",
        updated_at="2026-03-16T11:00:00Z",
        embedding=[1.0, 0.0, 0.0],
    )

    rows = list_vector_rowids(db_path)
    assert rows == [1]
