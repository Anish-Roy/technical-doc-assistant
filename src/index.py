"""Embed chunks with OpenAI and persist them in Chroma."""

import os

import tiktoken
from chromadb.api.models.Collection import Collection
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, stop_after_attempt

import chromadb

from src.chunk import ENCODING_NAME
from src.models import Chunk

MODEL_EMBED = "text-embedding-3-small"
CHROMA_DIR = "data/index"
COLLECTION_NAME = "pydantic_baseline"
EMBED_BATCH_SIZE = 100


def get_client(api_key: str | None = None) -> OpenAI:
    load_dotenv()
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is not set (pass api_key or use .env)")
    return OpenAI(api_key=key)


def count_tokens(texts: list[str]) -> int:
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    return sum(len(encoding.encode(text)) for text in texts)


@retry(stop=stop_after_attempt(3))
def embed_batch(
    texts: list[str], client: OpenAI, model: str = MODEL_EMBED
) -> list[list[float]]:
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]


def embed_texts(
    texts: list[str],
    client: OpenAI,
    model: str = MODEL_EMBED,
    batch_size: int = EMBED_BATCH_SIZE,
) -> list[list[float]]:
    if not texts:
        return []
    print(f"Embedding {len(texts)} texts (~{count_tokens(texts)} tokens) with {model}")
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        embeddings.extend(embed_batch(texts[start : start + batch_size], client, model))
    return embeddings


def get_collection(path: str = CHROMA_DIR, name: str = COLLECTION_NAME) -> Collection:
    db = chromadb.PersistentClient(path=path)
    return db.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def load_collection(path: str = CHROMA_DIR, name: str = COLLECTION_NAME) -> Collection:
    db = chromadb.PersistentClient(path=path)
    return db.get_collection(name=name)


def build_index(
    chunks: list[Chunk],
    client: OpenAI,
    path: str = CHROMA_DIR,
    name: str = COLLECTION_NAME,
) -> int:
    if not chunks:
        return 0
    embeddings = embed_texts([chunk.text for chunk in chunks], client)
    db = chromadb.PersistentClient(path=path)
    if name in [collection.name for collection in db.list_collections()]:
        db.delete_collection(name)
    collection = db.create_collection(name=name, metadata={"hnsw:space": "cosine"})
    collection.add(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        embeddings=embeddings,
        metadatas=[{"doc_id": chunk.doc_id, "token_count": chunk.token_count} for chunk in chunks],
    )
    return len(chunks)
