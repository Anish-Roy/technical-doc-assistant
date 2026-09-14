from types import SimpleNamespace
from typing import Any

import pytest
import tiktoken

from src.chunk import ENCODING_NAME
from src.generate import SYSTEM_PROMPT, build_input, generate, truncate_text
from src.models import Hit


def make_hit(text: str, chunk_id: str = "abc123def456", doc_id: str = "doc001") -> Hit:
    return Hit(chunk_id=chunk_id, doc_id=doc_id, score=0.9, text=text)


def test_truncate_text_caps_tokens() -> None:
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    long_text = " hello" * 200
    assert len(encoding.encode(long_text)) == 200

    capped = truncate_text(long_text, 50)
    assert len(encoding.encode(capped)) == 50

    short = "hello world"
    assert truncate_text(short, 50) == short


def test_build_input_truncates_context_but_keeps_query() -> None:
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    hits = [make_hit(" hello" * 200, chunk_id=f"c{i}") for i in range(3)]
    query = "How to define a strict model?"

    prompt = build_input(query, hits, max_tokens=100)

    assert query in prompt
    context_part = prompt.split("Context:\n")[1].split("\n\nQuestion:")[0]
    assert len(encoding.encode(context_part)) <= 100


def test_build_input_keeps_hit_order() -> None:
    hits = [make_hit(f"marker-alpha-{i}", chunk_id=f"c{i}") for i in range(3)]

    prompt = build_input("some query?", hits)

    assert prompt.index("marker-alpha-0") < prompt.index("marker-alpha-1")
    assert prompt.index("marker-alpha-1") < prompt.index("marker-alpha-2")


def test_generate_returns_answer_with_stub_client() -> None:
    seen: dict[str, Any] = {}

    def fake_create(model: str, instructions: str, input: str) -> SimpleNamespace:
        seen["model"] = model
        seen["instructions"] = instructions
        seen["input"] = input
        return SimpleNamespace(output_text="strict models use ConfigDict")

    stub_client: Any = SimpleNamespace(responses=SimpleNamespace(create=fake_create))
    hits = [make_hit("strict model text", chunk_id="c1")]

    answer = generate("What is strict?", hits, client=stub_client)

    assert answer == "strict models use ConfigDict"
    assert seen["instructions"] == SYSTEM_PROMPT
    assert "strict model text" in seen["input"]
    assert "What is strict?" in seen["input"]


def test_generate_rejects_bad_input() -> None:
    stub_client: Any = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda model, instructions, input: SimpleNamespace(output_text="x")
        )
    )
    hits = [make_hit("some text")]

    with pytest.raises(ValueError):
        generate("", hits, client=stub_client)
    with pytest.raises(ValueError):
        generate("   ", hits, client=stub_client)

    empty_client: Any = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda model, instructions, input: SimpleNamespace(output_text="")
        )
    )
    with pytest.raises(ValueError):
        generate("ok query", hits, client=empty_client)
