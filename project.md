### Production-Grade RAG System with Retrieval Diagnostics

Build a technical-documentation assistant, but make the project primarily about **retrieval engineering rather than the chatbot UI**.

The interesting part is a retrieval pipeline that supports:

`documents → parsing → structure-aware chunking → embeddings + BM25 → hybrid retrieval → reranking → context construction → generation`

Then build an evaluation/diagnostics layer around it.

Key engineering components:

- PDF/HTML/Markdown ingestion.
- Incremental indexing and document versioning.
- Structure-aware or parent-child chunking.
- Dense retrieval + BM25 hybrid retrieval.
- RRF fusion.
- Cross-encoder reranking.
- Metadata filtering.
- Context deduplication and token budgeting.
- Citation generation.
- Retrieval evaluation: Recall@K, MRR, nDCG.
- End-to-end answer evaluation.
- Query/chunk tracing.
- Failure classification.

The differentiator would be a small **RAG evaluation laboratory**. For example:
- “Does reranking actually improve answer quality?”
- "How does chunk size affect Recall@5?”
- “When does BM25 outperform dense retrieval?”
- “How much does query rewriting improve difficult queries?”

You can show experiments rather than merely claiming that the system works.

---

Include information that only exists in your corpus, like: 
official documentation + GitHub issues + release notes + pull requests + your own project-specific documents