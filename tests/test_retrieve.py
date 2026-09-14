from types import SimpleNamespace
from typing import Any

import pytest

import src.retrieve as retrieve_mod
from src.retrieve import retrieve


def make_fake_collection() -> SimpleNamespace:
    ids = ["c1", "c2", "c3"]
    documents = ["text one", "text two", "text three"]
    distances = [0.1, 0.2, 0.35]
    metadatas = [{"doc_id": "d1"}, {"doc_id": "d2"}, {"doc_id": "d3"}]

    def query(query_embeddings: list[list[float]], n_results: int) -> dict[str, Any]:
        assert len(query_embeddings) == 1
        assert query_embeddings[0] == [0.5, 0.5]
        k = n_results
        return {
            "ids": [ids[:k]],
            "documents": [documents[:k]],
            "distances": [distances[:k]],
            "metadatas": [metadatas[:k]],
        }

    return SimpleNamespace(query=query)


def test_retrieve_maps_scores_and_order(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(retrieve_mod, "embed_query", lambda query, client: [0.5, 0.5])
    monkeypatch.setattr(
        retrieve_mod, "load_collection", lambda path, name: make_fake_collection()
    )
    stub_client: Any = object()

    hits = retrieve("some query", k=2, client=stub_client)

    assert [h.chunk_id for h in hits] == ["c1", "c2"]
    assert hits[0].score == pytest.approx(1.0 - 0.1)
    assert hits[1].score == pytest.approx(1.0 - 0.2)
    assert [h.score for h in hits] == sorted([h.score for h in hits], reverse=True)
    assert hits[0].doc_id == "d1"
    assert hits[0].text == "text one"

    all_hits = retrieve("some query", k=5, client=stub_client)
    assert len(all_hits) == 3


def test_retrieve_rejects_empty_query(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_embed(query: str, client: Any) -> list[float]:
        raise AssertionError("embed_query must not be called")

    def fail_load(path: str, name: str) -> Any:
        raise AssertionError("load_collection must not be called")

    def fail_client() -> Any:
        raise AssertionError("get_client must not be called")

    monkeypatch.setattr(retrieve_mod, "embed_query", fail_embed)
    monkeypatch.setattr(retrieve_mod, "load_collection", fail_load)
    monkeypatch.setattr(retrieve_mod, "get_client", fail_client)

    with pytest.raises(ValueError):
        retrieve("")
    with pytest.raises(ValueError):
        retrieve("   ")
    with pytest.raises(ValueError):
        retrieve("ok query", k=0)
