"""Naive dense retrieval over Chroma."""

from openai import OpenAI
from tenacity import retry, stop_after_attempt

from src.index import (
    CHROMA_DIR,
    COLLECTION_NAME,
    MODEL_EMBED,
    embed_batch,
    get_client,
    load_collection,
)
from src.models import Hit

DEFAULT_K = 5


@retry(stop=stop_after_attempt(3))
def embed_query(query: str, client: OpenAI, model: str = MODEL_EMBED) -> list[float]:
    if not query or not query.strip():
        raise ValueError("query must be non-empty")
    return embed_batch([query], client, model)[0]


def retrieve(
    query: str,
    k: int = DEFAULT_K,
    client: OpenAI | None = None,
    path: str = CHROMA_DIR,
    name: str = COLLECTION_NAME,
) -> list[Hit]:
    if not query or not query.strip():
        raise ValueError("query must be non-empty")
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")
    active_client = client or get_client()
    vec = embed_query(query, active_client)
    coll = load_collection(path, name)
    result = coll.query(query_embeddings=[vec], n_results=k)

    # ChromaDB labels all 3 fields as Optional, however returns all 3 by default.
    # Fail fast if any is missing so Pylance and readers know they exist below.
    if result["documents"] is None or result["distances"] is None or result["metadatas"] is None:
        raise KeyError("Chroma query result is missing documents/distances/metadatas")
    ids = result["ids"][0]
    documents = result["documents"][0]
    distances = result["distances"][0]
    metadatas = result["metadatas"][0]
    hits: list[Hit] = []
    for chunk_id, text, distance, meta in zip(ids, documents, distances, metadatas):
        if meta is None or "doc_id" not in meta:
            raise KeyError(f"chunk {chunk_id} metadata is missing doc_id")
        doc_id = meta["doc_id"]
        # meta["doc_id"] has a Union type : 
        # str | int | float | bool | SparseVector | list[...] | None
        # Hit.doc_id is always a str, so Pylance safe check
        if not isinstance(doc_id, str):
            raise KeyError(f"chunk {chunk_id} doc_id is not a string: {doc_id!r}")
        hits.append(
            Hit(chunk_id=chunk_id, doc_id=doc_id, score=1.0 - distance, text=text)
        )
    return hits
