# Naive RAG Baseline — Phased Plan

Goal: Build a minimal end-to-end RAG over Pydantic docs to establish a working baseline before any retrieval engineering.

Stack: Python + OpenAI SDK (`text-embedding-3-small`, `gpt-4o-mini`) + Chroma + tiktoken + Pydantic + Click.

Scope: Markdown/HTML ingestion → fixed chunking → dense-only top-k → single-prompt generation → CLI query. No special techniques.

## Phase 0 — Repo Setup
- `pyproject.toml`, `venv`, `.env` (`OPENAI_API_KEY`)
- Layout: `src/`, `data/raw/`, `data/index/`
- Deps: `openai, chromadb, tiktoken, pydantic, click, python-dotenv`

## Phase 1 — Ingestion + Parsing
- Load `.md` / `.html` from `data/raw/pydantic/`
- Strip nav/boilerplate, keep `title, url, text`
- Output: `Document{doc_id, title, url, text}`

## Phase 2 — Chunking (Naive)
- Fixed 512 tokens, 50 token overlap via `tiktoken`
- No structure-aware / parent-child logic
- Output: `Chunk{chunk_id, doc_id, text, token_count}`

## Phase 3 — Embed + Index
- Batch embed with `text-embedding-3-small`
- Persist in Chroma collection `pydantic_baseline`
- Full re-index only (delete + rebuild), no incremental / versioning

## Phase 4 — Retrieval (Naive)
- Cosine similarity, top-k=5
- No BM25, RRF, rerank, or metadata filtering
- Output: `Hit{chunk_id, score, text}`

## Phase 5 — Generation (Naive)
- Fixed prompt: `system + top-5 chunks + question`
- Truncate to fit context, no dedup / token budgeting
- Model: `gpt-4o-mini`, plain answer, no citation enforcement
- Output: `answer: str`

## Phase 6 — CLI + Smoke Test
- `python -m src ingest`
- `python -m src query "How to define a strict model in Pydantic v2?"`
- Log `trace.jsonl {query, chunk_ids, scores, answer}`
- Done when: 5 sample Pydantic queries return plausible answers

## Non-Goals (see EXTENSIONS.md)
BM25, RRF, cross-encoder rerank, metadata/version filtering, parent-child chunking, incremental indexing, dedup/token budgeting, citations, Recall/nDCG eval, notebooks/plots, query rewriting, failure classification.
