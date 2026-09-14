from pydantic import BaseModel


class Document(BaseModel):
    doc_id: str
    title: str
    url: str
    text: str


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    token_count: int


class Hit(BaseModel):
    chunk_id: str
    doc_id: str
    score: float
    text: str
