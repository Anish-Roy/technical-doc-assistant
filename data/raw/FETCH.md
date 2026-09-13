# Corpus fetch notes

- Source: https://github.com/pydantic/pydantic (sparse checkout of `docs/`)
- Ref: tag `v2.13.5` (latest stable v2 release on 2026-09-13)
- Commit: `001dea020e0809844e5b17666432c9135a976f46`
- Files: 88 `.md` files copied to `data/raw/pydantic/`, relative paths preserved.
  Assets (`img/`, `logos/`, `*.png/svg`) excluded.
- The 4 `.html` files under `docs/theme/` and `docs/plugins/` are MkDocs theme
  scaffolding, not content — excluded. The loader is `.md`-only (deliberate
  deviation from PLAN.md Phase 1's "`.md` / `.html`", verified against the corpus).
- URL rule (approximate): `data/raw/pydantic/<page>.md` maps to
  `https://docs.pydantic.dev/latest/<page>/`; `index.md` maps to the section root.
  Rule-based guess, not parsed from the `mkdocs.yml` nav.

Reproduce:

```sh
git clone --depth 1 --branch v2.13.5 --filter=blob:none --sparse \
  https://github.com/pydantic/pydantic.git pydantic-docs
git -C pydantic-docs sparse-checkout set docs
# copy *.md from pydantic-docs/docs to data/raw/pydantic, preserving relative paths
```
