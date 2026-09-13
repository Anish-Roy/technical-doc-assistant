from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
import re

INDEX_URL = "https://pydantic.dev/docs/validation/latest/llms.txt"
OUTPUT_DIR = Path("data/raw/pydantic")

# Parameters requested by the Pydantic documentation.
QUERY_PARAMS = {
    "intent": "download the Pydantic documentation as local Markdown files",
    "stack": "Python",
    "harness": "OpenCode-MuseSpark1.3",
}


def fetch(url: str) -> str:
    response = requests.get(
        url,
        params=QUERY_PARAMS,
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def extract_links(text: str, base_url: str) -> list[str]:
    """
    Extract Markdown links from llms.txt.

    Handles links such as:
        [Models](./concepts/models/index.md)
        [Models](/docs/validation/latest/concepts/models/index.md)
    """
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)

    urls = []
    for link in links:
        if link.startswith(("http://", "https://")):
            urls.append(link)
        else:
            urls.append(urljoin(base_url, link))

    return urls


def local_path(url: str) -> Path:
    """
    Convert the documentation URL into a local filesystem path.

    Example:
        https://pydantic.dev/docs/validation/latest/concepts/models/index.md

    becomes:
        pydantic/concepts/models/index.md
    """
    path = urlparse(url).path.lstrip("/").split("/")
    index = path.index("latest")
    path = "/".join(path[index+1:])

    # Ensure files without .md are still represented sensibly.
    if not path.endswith(".md"):
        path += ".md"

    return OUTPUT_DIR / path


def main():
    print("Fetching documentation index...")

    index = fetch(INDEX_URL)
    links = extract_links(index, INDEX_URL)

    # Remove duplicates while preserving order.
    links = list(dict.fromkeys(links))

    print(f"Found {len(links)} documentation pages.")

    for i, url in enumerate(links, 1):
        destination = local_path(url)
        destination.parent.mkdir(parents=True, exist_ok=True)

        print(f"[{i}/{len(links)}] {url}")

        try:
            content = fetch(url)
            destination.write_text(content, encoding="utf-8")
        except requests.RequestException as e:
            print(f"  ERROR: {e}")

    print(f"\nDocumentation saved to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()