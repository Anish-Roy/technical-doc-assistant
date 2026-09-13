import tiktoken

from src.chunk import CHUNK_OVERLAP, CHUNK_SIZE, chunk_document, make_chunk_id
from src.models import Document


def make_doc(text: str, doc_id: str = "abc123def456") -> Document:
    return Document(doc_id=doc_id, title="T", url="https://example.com/", text=text)


def test_chunk_overlap_math() -> None:
    encoding = tiktoken.get_encoding("cl100k_base")
    text = " hello" * 1200
    assert len(encoding.encode(text)) == 1200
    chunks = chunk_document(make_doc(text), size=512, overlap=50)
    assert [c.token_count for c in chunks] == [512, 512, 276]
    first = encoding.encode(chunks[0].text)
    second = encoding.encode(chunks[1].text)
    assert first[-CHUNK_OVERLAP:] == second[:CHUNK_OVERLAP]


def test_chunk_ids_are_deterministic() -> None:
    text = " hello" * 600
    first = chunk_document(make_doc(text))
    second = chunk_document(make_doc(text))
    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]
    assert all(len(c.chunk_id) == 12 for c in first)
    assert make_chunk_id("abc123def456", 0) == make_chunk_id("abc123def456", 0)
    assert first[0].chunk_id != first[1].chunk_id


def test_short_and_empty_docs() -> None:
    short = chunk_document(make_doc("hello world"), size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    assert len(short) == 1
    assert short[0].doc_id == "abc123def456"
    assert short[0].token_count == 2
    assert chunk_document(make_doc("")) == []
