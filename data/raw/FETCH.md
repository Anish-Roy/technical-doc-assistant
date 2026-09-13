# Corpus fetch notes

- Source: `https://pydantic.dev/docs/validation/latest/llms.txt` index + per-page markdown fetched via `src/download.py` (links extracted from the index, saved as local `.md` files).
- Fetched: 2026-09-13. Files: 90 `.md` files under `data/raw/pydantic/`, every file nested as `<section>/.../index.md` (e.g. `concepts/models/index.md`).
- Each file starts with an agent preamble (documentation-index blockquote + `## Querying This Documentation` + `---` separator). The loader strips this
  preamble; it is not content.
- URL rule (approximate): `data/raw/pydantic/<page>/index.md` maps to `https://pydantic.dev/docs/validation/latest/<page>/`; a root `index.md` maps to the section root. Rule-based guess, not parsed from nav.

Reproduce:

```sh
uv run python -m src.download
# writes data/raw/pydantic/<section>/.../index.md (90 files)
```
