from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from pathlib import Path

import sqlite_vec

SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        source TEXT NOT NULL,
        source_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        updated_at TEXT,
        UNIQUE(source, source_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS index_meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS promote_runs (
        daily_id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        promoted_at TEXT,
        promoted_to TEXT NOT NULL DEFAULT ''
    )
    """,
)


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.enable_load_extension(True)
    sqlite_vec.load(connection)
    return connection


def ensure_schema(
    db_path: Path,
    embedding_model: str = "qwen3-embedding:0.6b",
    embedding_dim: int = 512,
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as connection:
        for statement in SCHEMA:
            connection.execute(statement)

        existing_meta = dict(connection.execute("SELECT key, value FROM index_meta").fetchall())
        existing_model = existing_meta.get("embedding_model")
        existing_dim = existing_meta.get("embedding_dim")

        if existing_model and existing_model != embedding_model:
            raise ValueError("Embedding model mismatch with existing index")
        if existing_dim and int(existing_dim) != embedding_dim:
            raise ValueError("Embedding dimension mismatch with existing index")

        connection.execute(
            "INSERT OR REPLACE INTO index_meta(key, value) VALUES (?, ?)",
            ("embedding_model", embedding_model),
        )
        connection.execute(
            "INSERT OR REPLACE INTO index_meta(key, value) VALUES (?, ?)",
            ("embedding_dim", str(embedding_dim)),
        )

        vec_exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE name = 'documents_vec'"
        ).fetchone()
        if not vec_exists:
            connection.execute(
                f"CREATE VIRTUAL TABLE documents_vec USING vec0(embedding float[{embedding_dim}])"
            )
        connection.commit()


def get_index_meta(db_path: Path) -> dict[str, str]:
    ensure_schema(db_path)
    with _connect(db_path) as connection:
        rows = connection.execute("SELECT key, value FROM index_meta").fetchall()
    return {key: value for key, value in rows}


def upsert_document(
    db_path: Path,
    *,
    source: str,
    source_id: str,
    title: str,
    content: str,
    updated_at: str,
    embedding: Sequence[float] | None = None,
) -> None:
    embedding_dim = len(embedding) if embedding is not None else 512
    ensure_schema(db_path, embedding_dim=embedding_dim)
    with _connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO documents(source, source_id, title, content, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(source, source_id)
            DO UPDATE SET
                title = excluded.title,
                content = excluded.content,
                updated_at = excluded.updated_at
            """,
            (source, source_id, title, content, updated_at),
        )
        row = connection.execute(
            "SELECT id FROM documents WHERE source = ? AND source_id = ?",
            (source, source_id),
        ).fetchone()
        if row and embedding is not None:
            connection.execute(
                "INSERT OR REPLACE INTO documents_vec(rowid, embedding) VALUES (?, ?)",
                (row[0], sqlite_vec.serialize_float32(list(embedding))),
            )
        connection.commit()


def list_vector_rowids(db_path: Path) -> list[int]:
    with _connect(db_path) as connection:
        rows = connection.execute("SELECT rowid FROM documents_vec ORDER BY rowid").fetchall()
    return [row[0] for row in rows]


def list_unpromoted_days(db_path: Path) -> list[str]:
    ensure_schema(db_path)
    with _connect(db_path) as connection:
        rows = connection.execute(
            "SELECT daily_id FROM promote_runs WHERE status = 'pending' ORDER BY daily_id"
        ).fetchall()
    return [row[0] for row in rows]
