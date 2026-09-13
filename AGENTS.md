# AGENTS.md — Coding Style for This Project

Audience: entry-level AI engineer. Code must read like a competent junior wrote it, not a framework.
Goal: simple, explicit, production-honest. Show you understand the pipeline without hiding it behind abstractions.

## 1. Philosophy
- One pipeline stage = one file with plain functions. No cleverness.
- Explicit > magic. Prefer passing arguments over global state, singletons, registries.
- Only add complexity if it proves engineering familiarity: typed I/O, deterministic IDs, retries, token counting, trace logging.
- If a function needs a comment to explain *what* it does, split it. Comments explain *why* only.

## 2. Layout (flat, no deep packages)
```
src/
  models.py    # Pydantic schemas only: Document, Chunk, Hit, Trace
  ingest.py    # load md/html -> List[Document]
  chunk.py     # Document -> List[Chunk]
  index.py     # embed + Chroma upsert / load
  retrieve.py  # query -> List[Hit]
  generate.py  # query + hits -> answer
  cli.py       # Click commands: ingest, query
```

Do not create `base.py`, `interfaces.py`, `factories.py`, `utils/` grab-bag. If shared code exceeds ~20 lines, then and only then make `common.py`.

## 3. Functions
- Pure functions where possible: `def chunk_document(doc: Document, size: int = 512, overlap: int = 50) -> list[Chunk]`
- Max ~40 lines per function. More than that → split into two named steps.
- No classes except Pydantic models. No inheritance, no ABCs, no decorators except `@click` and `@retry`.
- No `*args, **kwargs` passthrough. List every parameter explicitly.
- Return dataclass/Pydantic objects, not dicts or tuples. Caller should do `hit.text`, not `hit[2]`.

Good:
```python
def retrieve(query: str, k: int = 5) -> list[Hit]:
    vec = embed_text(query)
    return collection.query(vec, k=k)
```

Bad:
```python
class RetrievalManagerFactory(BaseRetriever):  # over-engineered, do not do this
```

## 4. Types + Config
- Python 3.10+. Type-hint all function signatures. Run `ruff check` clean.
- Pydantic v2 for `models.py` only. No validation logic elsewhere.
- Config at top of file as constants or env: `MODEL_EMBED = "text-embedding-3-small"`, keys via `os.getenv("OPENAI_API_KEY")`. Never hardcode keys. Commit `.env.example`, never `.env`.
- IDs deterministic: `chunk_id = sha1(doc_id + str(offset))[:12]`. No `uuid4()` for chunks — breaks re-index determinism.

## 5. Production Patterns to Keep (minimal set)
- Batch OpenAI embedding calls (e.g. 100 texts/batch). Count tokens with `tiktoken` before calling.
- Retry only network/LLM calls: `@retry(stop_after_attempt(3))` via `tenacity`. No retry on file parsing.
- Log traces as JSONL: `trace.jsonl` with `{query, chunk_ids, scores, answer}`. `print()` for CLI is fine; no structlog/OTel.
- Fail fast: let exceptions raise in CLI during baseline. No silent `except: pass`.
- Pin deps in `pyproject.toml` / `requirements.txt`.

## 6. What to Avoid
- No LangChain / LlamaIndex. Raw `openai` SDK only — the point is to show retrieval internals.
- No async until latency proves you need it. Sync baseline first.
- No custom exception hierarchies, no plugin system, no YAML-driven pipelines.
- No notebooks importing private helpers with `sys.path` hacks — `pip install -e .` once.
- No premature optimization: full re-index is fine (per PLAN.md). Incremental indexing lives in EXTENSIONS.md.

## 7. Tests + Checks
- 3–5 unit tests max for baseline: chunk overlap math, deterministic IDs, prompt truncation.
- Smoke test is the gate: `python -m src ingest` + 5 sample queries return plausible answers.
- Before commit: `ruff check src/` passes, CLI runs from fresh env (`uv sync --extra dev`, then `uv run ...`).

## 8. Adding an Extension
New technique = new function + CLI flag, not a rewrite. Example: `def rrf_fuse(...)` in `retrieve.py`, enabled with `--hybrid`. Baseline path must keep working untouched.

## 9. Git Workflow (Mandatory — follow on every change)
- `main` is always runnable: `ruff check src/` passes, CLI smoke passes. Never push broken code to `main`.
- Never work directly on `main`. New task = new branch from up-to-date `main`:
  `git checkout main && git pull --rebase && git checkout -b feat/<short-name>`
- Branch names are short, lowercase: `feat/<what>`, `fix/<what>`, `docs/<what>`, `chore/<what>`. Example: `feat/chunking`, `fix/ingest-html`, `docs/git-workflow`.
- One branch = one task. If the task changes direction, make a new branch.
- Commit early and often. One commit = one logical step that still runs (e.g. add `chunk.py`, not half a file). Push the branch daily so work is never local-only.
- Commit messages use `type: short imperative summary`. Types: `feat`, `fix`, `docs`, `chore`, `test`. Examples: `feat: add fixed-size chunking`, `fix: strip nav from html`, `docs: add git workflow to AGENTS.md`. Add a body only if the *why* is not obvious.
- Before every commit, run: `git status`, `git diff`. Stage only intended files (`git add src/chunk.py`), never blind `git add -A`. Then run `ruff check src/` — it must pass.
- Never commit secrets or generated data: `.env`, `venv/`, `__pycache__/`, `*.pyc`, `trace.jsonl`, `data/index/`, `chroma_db/`. If `git status` shows one, stop and fix `.gitignore`.
- `AGENTS.md`, `PLAN.md`, `EXTENSIONS.md` are tracked. Changes to them follow the same branch + commit rules.
- Sync with `main` often: `git fetch origin && git rebase origin/main`. Resolve conflicts on your branch, never on `main`.
- Merge to `main` only when checks pass. Delete the branch after merge: `git branch -d feat/<short-name>`.
- Never `push --force` on `main` or any shared branch. Never amend a commit after push — make a new commit instead.
