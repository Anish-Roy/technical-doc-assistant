"""Load Markdown docs from data/raw/pydantic into Document objects."""

import hashlib
from pathlib import Path

from src.models import Document

DOCS_ROOT = Path("data/raw/pydantic")
DOCS_BASE_URL = "https://docs.pydantic.dev/latest"


def iter_source_files(root: Path = DOCS_ROOT) -> list[Path]:
    return sorted(root.rglob("*.md"))


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[i + 1 :])
    return text


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_doc_id(rel_path: str) -> str:
    return hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:12]


def build_url(rel_path: str) -> str:
    page = rel_path[: -len(".md")] if rel_path.endswith(".md") else rel_path
    if page == "index":
        return DOCS_BASE_URL + "/"
    if page.endswith("/index"):
        page = page[: -len("/index")]
    return f"{DOCS_BASE_URL}/{page}/"


def load_markdown(path: Path, rel_path: str) -> Document:
    raw = path.read_text(encoding="utf-8")
    text = strip_frontmatter(raw)
    return Document(
        doc_id=build_doc_id(rel_path),
        title=extract_title(text, path.stem),
        url=build_url(rel_path),
        text=text,
    )


def load_documents(root: Path = DOCS_ROOT) -> list[Document]:
    root = Path(root)
    paths = iter_source_files(root)
    return [load_markdown(path, path.relative_to(root).as_posix()) for path in paths]
