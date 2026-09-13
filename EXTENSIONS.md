# Extensions (Post-Baseline)

Advanced retrieval engineering + eval lab. Build only after `PLAN.md` baseline works. Each item is an isolated ablation on top of the naive pipeline.

## 1. Structure-Aware / Parent-Child Chunking
- Markdown header-aware splits; child chunks (256 tok) retrieve, parent (1024 tok) generates
- Ablation: fixed-512 vs header-aware vs parent-child on Recall@5

## 2. BM25 + Hybrid Retrieval + RRF
- Local BM25 (`tantivy` / `rank-bm25`) + dense fusion via RRF (k=60)
- Ablation: BM25-only vs dense-only vs hybrid; expect BM25 wins on symbol queries (`BaseSettings`, `model_validator`)

## 3. Cross-Encoder Reranking
- Local `MiniLM-L-6-v2`, top-20 → top-5
- Ablation: rerank on/off on nDCG@10 + latency cost

## 4. Metadata / Version Filtering
- Chunk fields: `version=[v1|v2|agnostic], source_type, url, header_path`
- Test v1/v2-sensitive queries with filter on/off; fixes wrong-version citations

## 5. Context Construction
- Dedup (cosine > 0.95), token budgeting (4k cap via `tiktoken`), citation enforcement (`[source] per claim`)

## 6. Incremental Indexing + Versioning
- `doc_id` + content hash, chunk lineage, tombstones; delta re-embed only
- Deferred: baseline uses full rebuild

## 7. Eval Lab
- 50–60 labeled Pydantic queries: v2-only, v1-only, migration, hard/ambiguous, unanswerable
- Metrics: Recall@5, nDCG@10, MRR + citation precision
- Notebooks: `01_retrieval.ipynb`, `02_experiments.ipynb` with 4 experiments (chunk size, retriever type, rerank, version filter)

## 8. Tracing + Failure Classification
- `trace.jsonl`: query → hits + scores → reranked → prompt → answer
- Manual buckets first: wrong-version, missing-context, bad-rerank; automate later

## 9. Query Rewriting (Stretch)
- LLM rewrite + HyDE for hard queries only; measure lift vs cost
