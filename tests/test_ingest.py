from src.ingest import build_doc_id, build_url, extract_title, strip_frontmatter


def test_doc_id_is_deterministic() -> None:
    assert build_doc_id("concepts/models.md") == build_doc_id("concepts/models.md")
    assert len(build_doc_id("concepts/models.md")) == 12


def test_title_prefers_first_h1_and_strips_frontmatter() -> None:
    text = "---\ndescription: Migrating from Pydantic V1.\n---\n\nIntro line.\n\n# Migration Guide\n"
    assert strip_frontmatter(text).startswith("\nIntro")
    assert extract_title(strip_frontmatter(text), "migration") == "Migration Guide"
    assert extract_title("no heading here", "fields") == "fields"


def test_url_mapping() -> None:
    assert build_url("migration.md") == "https://docs.pydantic.dev/latest/migration/"
    assert build_url("index.md") == "https://docs.pydantic.dev/latest/"
    assert build_url("concepts/models.md") == "https://docs.pydantic.dev/latest/concepts/models/"
