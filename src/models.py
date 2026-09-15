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


class EvalQuery(BaseModel):
    query_id: str
    query: str
    category: str   # v2-only | v1-only | migration | hard/ambiguous | unanswerable
    relevant_chunk_ids: list[str]  # empty iff unanswerable
    relevant_doc_ids: list[str]    # stable truth - survives re-chunking
    expected_claims: list[str]    # empty iff unanswerable
    chunking_version: str    # "baseline-512/50"


class EvalScore(BaseModel):
    query_id: str
    recall_at_5: float
    rr: float
    ndcg_at_10: float
    claims_hit: int
    claims_total: int
    abstained_correctly: bool | None