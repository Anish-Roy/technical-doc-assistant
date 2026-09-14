import tiktoken
from openai import OpenAI
from tenacity import retry, stop_after_attempt

from src.chunk import ENCODING_NAME
from src.models import Hit
from src.index import get_client

MODEL_CHAT = "gpt-4o-mini"
MAX_CONTEXT_TOKENS = 6000

SYSTEM_PROMPT = (
    "You answer questions about Pydantic using only the provided context. "
    "If the answer is not in the context, say you don't know."
)

def build_input(query: str, hits: list[Hit], max_tokens: int = MAX_CONTEXT_TOKENS) -> str:
    context = "\n\n".join([f"Document {i} : {doc.text}" for i, doc in enumerate(hits, start=1)])
    context = truncate_text(context, max_tokens)

    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

    return prompt


def truncate_text(text: str, max_tokens: int) -> str:
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return encoding.decode(tokens)


@retry(stop=stop_after_attempt(3))
def _create_response(client: OpenAI, model: str, input_text: str) -> str:
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=input_text,
    )
    return response.output_text


def generate(
    query: str,
    hits: list[Hit],
    client: OpenAI | None = None,
    model: str = MODEL_CHAT,
    max_tokens: int = MAX_CONTEXT_TOKENS,
) -> str:
    if not query or not query.strip():
        raise ValueError("Query is not valid")

    llm = client or get_client()
    input_text = build_input(query, hits, max_tokens)
    answer = _create_response(llm, model, input_text)
    if not answer:
        raise ValueError("Could not generate response")
    return answer


