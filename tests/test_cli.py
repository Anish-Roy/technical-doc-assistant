import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

import src.cli as cli_mod
from src.cli import append_trace, main
from src.models import Chunk, Document, Hit
from src.retrieve import DEFAULT_K


def make_doc(doc_id: str = "d1") -> Document:
    return Document(doc_id=doc_id, title="T", url="https://example.com/", text="hello")


def make_chunk(chunk_id: str = "c1", doc_id: str = "d1") -> Chunk:
    return Chunk(chunk_id=chunk_id, doc_id=doc_id, text="hello", token_count=1)


def make_hit(chunk_id: str = "c1", doc_id: str = "d1") -> Hit:
    return Hit(chunk_id=chunk_id, doc_id=doc_id, score=0.9, text="strict text")


def test_append_trace_writes_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    hits = [make_hit("c1", "d1"), make_hit("c2", "d2")]

    append_trace("what is strict?", hits, "use ConfigDict", path=str(path))

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["query"] == "what is strict?"
    assert data["chunk_ids"] == ["c1", "c2"]
    assert data["scores"] == [0.9, 0.9]
    assert data["answer"] == "use ConfigDict"


def test_ingest_runs_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    docs = [make_doc("d1"), make_doc("d2")]
    chunks = [make_chunk("c1", "d1"), make_chunk("c2", "d2")]
    seen: dict[str, Any] = {}
    sentinel = object()

    monkeypatch.setattr(cli_mod, "load_documents", lambda: docs)

    def fake_chunk(docs: list[Document]) -> list[Chunk]:
        seen["docs"] = docs
        return chunks

    monkeypatch.setattr(cli_mod, "chunk_documents", fake_chunk)
    monkeypatch.setattr(cli_mod, "get_client", lambda: sentinel)

    def fake_build(chunks: list[Chunk], client: Any) -> int:
        seen["chunks"] = chunks
        seen["client"] = client
        return len(chunks)

    monkeypatch.setattr(cli_mod, "build_index", fake_build)

    result = CliRunner().invoke(main, ["ingest"])

    assert result.exit_code == 0
    assert seen["docs"] == docs
    assert seen["chunks"] == chunks
    assert seen["client"] is sentinel
    assert "2 documents" in result.output
    assert "2 chunks" in result.output


def test_query_prints_answer_and_logs_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    hits = [make_hit("c1", "d1")]
    seen: dict[str, Any] = {}
    sentinel = object()

    monkeypatch.setattr(cli_mod, "get_client", lambda: sentinel)

    def fake_retrieve(query: str, k: int) -> list[Hit]:
        seen["query"] = query
        seen["k"] = k
        return hits

    monkeypatch.setattr(cli_mod, "retrieve", fake_retrieve)

    def fake_generate(query: str, hits: list[Hit], client: Any) -> str:
        seen["gen_query"] = query
        seen["gen_hits"] = hits
        seen["gen_client"] = client
        return "strict answer"

    monkeypatch.setattr(cli_mod, "generate", fake_generate)

    def fake_trace(query: str, hits: list[Hit], answer: str) -> None:
        seen["trace"] = (query, hits, answer)

    monkeypatch.setattr(cli_mod, "append_trace", fake_trace)

    result = CliRunner().invoke(main, ["query", "what is strict?"])

    assert result.exit_code == 0
    assert "strict answer" in result.output
    assert seen["query"] == "what is strict?"
    assert seen["k"] == DEFAULT_K
    assert seen["gen_query"] == "what is strict?"
    assert seen["gen_hits"] == hits
    assert seen["gen_client"] is sentinel
    assert seen["trace"] == ("what is strict?", hits, "strict answer")


def test_query_respects_k_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}

    monkeypatch.setattr(cli_mod, "get_client", lambda: object())

    def fake_retrieve(query: str, k: int) -> list[Hit]:
        seen["k"] = k
        return []

    monkeypatch.setattr(cli_mod, "retrieve", fake_retrieve)
    monkeypatch.setattr(cli_mod, "generate", lambda query, hits, client: "a")
    monkeypatch.setattr(cli_mod, "append_trace", lambda query, hits, answer: None)

    result = CliRunner().invoke(main, ["query", "hello", "--k", "2"])

    assert result.exit_code == 0
    assert seen["k"] == 2
