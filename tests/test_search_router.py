from pathlib import Path

import pytest

from bear_brain.memory_store import ensure_schema, upsert_document
from bear_brain.router import choose_search_modes
from bear_brain.search import (
    make_ollama_embedder,
    search_docs_scope,
    search_memory_db,
)
from bear_brain.search_index import sync_local_sources


class _FakeEmbedResponse:
    def __init__(self, embeddings):
        self.embeddings = embeddings


class _FakeClient:
    def __init__(self, host: str):
        self.host = host
        self.calls = []

    def embed(self, *, model: str, input: str, dimensions: int):
        self.calls.append({"model": model, "input": input, "dimensions": dimensions})
        return _FakeEmbedResponse([[1.0] * dimensions])


def test_router_defaults_to_memory_first() -> None:
    modes = choose_search_modes(task_type="general", repo=None, explicit_refs=False)
    assert modes[0] == "memory_db"


def test_router_adds_docs_scope_for_repo_work() -> None:
    modes = choose_search_modes(task_type="implementation", repo="bear-brain", explicit_refs=False)
    assert "docs_scope" in modes


def test_router_adds_note_refs_when_explicit_refs_exist() -> None:
    modes = choose_search_modes(task_type="general", repo=None, explicit_refs=True)
    assert "note_refs" in modes


def test_make_ollama_embedder_uses_host_model_and_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    def _factory(host: str):
        client = _FakeClient(host)
        captured["client"] = client
        return client

    monkeypatch.setattr("bear_brain.search.ollama.Client", _factory)
    embed = make_ollama_embedder(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        expected_dim=512,
    )

    vector = embed("hello")
    assert len(vector) == 512
    assert captured["client"].host == "http://127.0.0.1:11434"
    assert captured["client"].calls[0] == {
        "model": "qwen3-embedding:0.6b",
        "input": "hello",
        "dimensions": 512,
    }


def test_make_ollama_embedder_rejects_wrong_dimension(monkeypatch: pytest.MonkeyPatch) -> None:
    class _WrongClient(_FakeClient):
        def embed(self, *, model: str, input: str, dimensions: int):
            return _FakeEmbedResponse([[1.0, 2.0]])

    monkeypatch.setattr("bear_brain.search.ollama.Client", lambda host: _WrongClient(host))
    embed = make_ollama_embedder(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        expected_dim=512,
    )

    with pytest.raises(ValueError, match="512"):
        embed("hello")


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


def test_sync_local_sources_indexes_memory_daily_and_docs(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "db" / "memory.db"
    memory_file = tmp_path / "memory.md"
    daily_dir = tmp_path / "daily"
    docs_dir = tmp_path / "docs"

    daily_dir.mkdir()
    (docs_dir / "product").mkdir(parents=True)

    memory_file.write_text(
        "## Position\n长期经验入口\n\n## Core Memory\n- 固定使用 512 维 embedding\n",
        encoding="utf-8",
    )
    (daily_dir / "2026-03-16.md").write_text(
        "## Summary\n- 今天确认 memory-first\n",
        encoding="utf-8",
    )
    (docs_dir / "product" / "SPEC.md").write_text(
        "# SPEC\n\n## Constraints\n\n默认使用本地搜索\n",
        encoding="utf-8",
    )

    count = sync_local_sources(
        db_path,
        memory_file=memory_file,
        daily_dir=daily_dir,
        docs_dir=docs_dir,
    )

    assert count == 3
    hits = search_memory_db(db_path, query="本地搜索", limit=5)
    assert hits
    assert hits[0].metadata["source_id"].endswith("SPEC.md")
