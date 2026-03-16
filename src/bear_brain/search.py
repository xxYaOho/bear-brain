from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from pathlib import Path

import ollama
import sqlite_vec

from .models import SearchHit

Embedder = Callable[[str], Sequence[float]]


def normalize_hits(hits: list[SearchHit]) -> list[SearchHit]:
    return hits


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.enable_load_extension(True)
    sqlite_vec.load(connection)
    return connection


def make_ollama_embedder(
    *,
    base_url: str,
    model: str,
    expected_dim: int,
) -> Embedder:
    client = ollama.Client(host=base_url)

    def _embed(query: str) -> Sequence[float]:
        response = client.embed(model=model, input=query, dimensions=expected_dim)
        vector = response.embeddings[0]
        if len(vector) != expected_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {expected_dim}, got {len(vector)}"
            )
        return vector

    return _embed


def search_memory_db(
    db_path: Path,
    query: str,
    limit: int = 10,
    embedder: Embedder | None = None,
) -> list[SearchHit]:
    if embedder is not None:
        query_vector = list(embedder(query))
        with _connect(db_path) as connection:
            rows = connection.execute(
                """
                SELECT documents.source, documents.source_id, documents.title, documents.content,
                       documents.updated_at, documents_vec.distance
                FROM documents_vec
                JOIN documents ON documents.id = documents_vec.rowid
                WHERE documents_vec.embedding MATCH ? AND k = ?
                ORDER BY documents_vec.distance ASC
                """,
                (sqlite_vec.serialize_float32(query_vector), limit),
            ).fetchall()
        hits = [
            SearchHit(
                source=source,
                title=title,
                content=content,
                score=float(1 / (1 + distance)),
                metadata={"source_id": source_id, "updated_at": updated_at or ""},
            )
            for source, source_id, title, content, updated_at, distance in rows
        ]
        return normalize_hits(hits)

    tokens = [token for token in query.split() if token]
    if not tokens:
        return []

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT source, source_id, title, content, updated_at "
            "FROM documents ORDER BY updated_at DESC"
        ).fetchall()

    hits: list[SearchHit] = []
    for source, source_id, title, content, updated_at in rows:
        score = sum(token in content or token in title for token in tokens)
        if score:
            hits.append(
                SearchHit(
                    source=source,
                    title=title,
                    content=content,
                    score=float(score),
                    metadata={"source_id": source_id, "updated_at": updated_at or ""},
                )
            )
    hits.sort(key=lambda hit: hit.score, reverse=True)
    return normalize_hits(hits[:limit])


def search_docs_scope(docs_root: Path, query: str, limit: int = 10) -> list[SearchHit]:
    tokens = [token for token in query.split() if token]
    if not docs_root.exists() or not tokens:
        return []

    hits: list[SearchHit] = []
    for path in sorted(docs_root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        score = sum(token in text or token in path.name for token in tokens)
        if score:
            hits.append(
                SearchHit(
                    source="docs",
                    title=path.stem,
                    content=text,
                    score=float(score),
                    metadata={"path": str(path)},
                )
            )
    hits.sort(key=lambda hit: hit.score, reverse=True)
    return normalize_hits(hits[:limit])
