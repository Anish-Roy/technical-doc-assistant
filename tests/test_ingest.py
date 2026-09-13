from src.ingest import (
    build_doc_id,
    build_url,
    extract_title,
    strip_boilerplate,
    strip_frontmatter,
)


def test_doc_id_is_deterministic() -> None:
    assert build_doc_id("concepts/models/index.md") == build_doc_id("concepts/models/index.md")
    assert len(build_doc_id("concepts/models/index.md")) == 12


def test_title_prefers_first_h1_and_strips_frontmatter() -> None:
    text = "---\ndescription: Migrating from Pydantic V1.\n---\n\nIntro line.\n\n"
    text += "# Migration Guide\n"
    assert strip_frontmatter(text).startswith("\nIntro")
    assert extract_title(strip_frontmatter(text), "migration") == "Migration Guide"
    assert extract_title("no heading here", "fields") == "fields"


def test_boilerplate_stripped_before_title() -> None:
    text = (
        "> ## Documentation Index\n"
        "> Fetch the complete documentation index at: https://pydantic.dev/llms.txt\n"
        "\n"
        "## Querying This Documentation\n"
        "\n"
        "**success**: agent query parameters correctly provided.\n"
        "\n"
        "---\n"
        "\n"
        "# Models\n"
    )
    stripped = strip_boilerplate(text)
    assert "Querying This Documentation" not in stripped
    assert extract_title(stripped, "models") == "Models"
    assert strip_boilerplate("# Plain Title\n") == "# Plain Title\n"


def test_url_mapping() -> None:
    base = "https://pydantic.dev/docs/validation/latest"
    assert build_url("index.md") == f"{base}/"
    assert build_url("concepts/models/index.md") == f"{base}/concepts/models/"
    assert build_url("api/pydantic/aliases/index.md") == f"{base}/api/pydantic/aliases/"
