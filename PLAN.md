# Naive RAG Baseline — Phased Plan

Goal: Build a minimal end-to-end RAG over Pydantic docs to establish a working baseline before any retrieval engineering.

Stack: Python + OpenAI SDK (`text-embedding-3-small`, `gpt-4o-mini`) + Chroma + tiktoken + Pydantic + Click.

Scope: Markdown/HTML ingestion → fixed chunking → dense-only top-k → single-prompt generation → CLI query → baseline eval. No special techniques.

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

## Phase 7 — Baseline Eval
Build the complete evaluation pipeline alongside the naive RAG system, so later modifications can be re-tested with one command and compared against recorded baseline scores.

- Golden set `data/eval/golden.jsonl` (~15 hand-labeled queries, tracked in git), one JSON object per line:
  `{query_id, query, category, relevant_chunk_ids, expected_claims[], must_cite}`
- Categories: `v2-only`, `migration`, `hard/ambiguous`, `unanswerable`. Unanswerable rows carry empty `expected_claims` and grade on correct abstention.
- `relevant_chunk_ids` label against baseline chunking (deterministic `sha1` IDs). `expected_claims` are short atomic facts for the judge, not full reference answers.
- `src/eval.py` (pure functions, each ≤~40 lines, no new abstractions):
  - `recall_at_k(hits, relevant, k)`, `reciprocal_rank(...)`, `ndcg_at_k(...)` over existing `retrieve()` hits — deterministic, unit-testable.
  - `grade_answer(query, answer, expected_claims)` — single fixed rubric prompt to `gpt-4o-mini` at `temperature=0`; returns per-claim hit/miss + citation-present flag. Retry via existing `tenacity` pattern (network/LLM calls only).
  - `run_eval(k=5)` — runs the golden set through existing `retrieve()` + `generate()`, aggregates retrieval means (Recall@5, MRR, nDCG@10) + judge means, writes `evals/baseline.json`.
- `models.py`: add `EvalQuery`, `EvalScore` schemas only. `cli.py`: add `eval` command. No changes to Phase 1–5 functions.
- Record `evals/baseline.json` (tracked in git — JSON stays committable under the `*.md` ignore): holds `git_sha`, timestamp, model names/versions, per-query scores + aggregate means.
- Gate: baseline runs green and `baseline.json` is merged to `main` before any EXTENSIONS.md work. Every later modification re-runs the same `python -m src eval` on the same golden set and reports delta-vs-baseline.
- Cost note: one run ≈ 15 generations + 15 judge calls; judge scores may wobble run-to-run — mitigate with `temperature=0` and the recorded model version.
- Tests: 2 unit tests (metric math on a toy ranking, `baseline.json` schema round-trip).
- Done when: `python -m src eval` completes and retrieval means + judge means are recorded in `evals/baseline.json`.

## Non-Goals (see EXTENSIONS.md)
BM25, RRF, cross-encoder rerank, metadata/version filtering, parent-child chunking, incremental indexing, dedup/token budgeting, citations, eval scale-up (50–60 queries, ablation notebooks/plots), query rewriting, failure classification.
