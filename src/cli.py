import json
import click

from src.retrieve import DEFAULT_K, retrieve
from src.models import Hit
from src.ingest import load_documents
from src.chunk import chunk_documents
from src.index import get_client, build_index
from src.generate import generate


TRACE_PATH = "trace.jsonl"


# Log `trace.jsonl {query, chunk_ids, scores, answer}`
def append_trace(query: str, hits: list[Hit], answer: str, path: str = TRACE_PATH) -> None:
    with open(path, "a", encoding="utf-8") as f:
        data = {
            "query" : query,
            "chunk_ids" : [h.chunk_id for h in hits], 
            "scores" : [h.score for h in hits], 
            "answer" : answer
        }
        f.write(json.dumps(data) + "\n")



@click.group()
def main() -> None:
    pass

# load_docs() -> chunk_docs() -> get_client() -> build_index(chunks, client)
@main.command()
def ingest() -> None:
    docs = load_documents()
    chunks = chunk_documents(docs=docs)

    llm = get_client()
    total_chunks = build_index(chunks=chunks, client=llm)

    print(f"Total {len(docs)} documents and {total_chunks} chunks indexed")


@main.command() 
@click.argument("query")
@click.option("--k", default=DEFAULT_K, type=int)
def query(query: str, k: int) -> None:
    llm = get_client()
    results = retrieve(query=query, k=k)
    answer = generate(query=query, hits=results, client=llm)

    append_trace(query=query, hits=results, answer=answer)

    print(answer)
