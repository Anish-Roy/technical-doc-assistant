"""Fixed-size token chunking for Documents."""

import hashlib

import tiktoken

from src.models import Chunk, Document

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
ENCODING_NAME = "cl100k_base"  # encoding for text-embedding-3-small


# offset is the token count from where the chunk starts, so it is a number unique to each chunk
def make_chunk_id(doc_id: str, offset: int) -> str:
    return hashlib.sha1(f"{doc_id}{offset}".encode("utf-8")).hexdigest()[:12]


def chunk_document(
    doc: Document, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[Chunk]:
    if overlap >= size:
        raise ValueError(f"overlap ({overlap}) must be smaller than size ({size})")
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    tokens = encoding.encode(doc.text)
    if not tokens:
        return []
    step = size - overlap
    chunks: list[Chunk] = []
    for offset in range(0, len(tokens), step):
        window = tokens[offset : offset + size]
        chunks.append(
            Chunk(
                chunk_id=make_chunk_id(doc.doc_id, offset),
                doc_id=doc.doc_id,
                text=encoding.decode(window),
                token_count=len(window),
            )
        )
    return chunks


def chunk_documents(
    docs: list[Document], size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in docs:
        chunks.extend(chunk_document(doc, size=size, overlap=overlap))
    return chunks
