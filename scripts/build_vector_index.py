import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.config import get_setting
from rag.embeddings import DEFAULT_EMBEDDING_MODEL, EmbeddingError, embed_with_retries


def load_existing(path):
    if not Path(path).exists():
        return None
    with open(path, "r", encoding="utf-8") as src:
        return json.load(src)


def load_chunks(path):
    with open(path, "r", encoding="utf-8") as src:
        return [json.loads(line) for line in src if line.strip()]


def save_index(path, model, dimensions, items):
    with open(path, "w", encoding="utf-8") as dst:
        json.dump({"type": "gemini_vector", "model": model, "dimensions": dimensions, "items": items}, dst)


def main():
    parser = argparse.ArgumentParser(description="Build a Gemini embedding vector index for semantic retrieval.")
    parser.add_argument("--chunks", default="data/rag/chunks.jsonl")
    parser.add_argument("--output", default="data/index/vector_index.json")
    parser.add_argument("--model", default=None)
    parser.add_argument("--dimensions", type=int, default=768)
    parser.add_argument("--limit", type=int, default=None, help="Useful for smoke tests.")
    parser.add_argument("--delay", type=float, default=0.1)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    model = args.model or get_setting("GEMINI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    chunks = load_chunks(args.chunks)
    if args.limit:
        chunks = chunks[: args.limit]

    existing = load_existing(args.output) if args.resume else None
    items = []
    done = set()
    if existing and existing.get("model") == model and existing.get("dimensions") == args.dimensions:
        items = existing.get("items", [])
        done = {item["chunk"]["chunk_id"] for item in items}

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    for index, chunk in enumerate(chunks, start=1):
        if chunk["chunk_id"] in done:
            continue
        text = f"title: {chunk.get('title') or 'none'} | text: {chunk['text']}"
        try:
            embedding = embed_with_retries(
                text,
                task_type="RETRIEVAL_DOCUMENT",
                model=model,
                output_dimensionality=args.dimensions,
                retries=5,
                delay=2.0,
            )
        except EmbeddingError as exc:
            save_index(args.output, model, args.dimensions, items)
            print(f"Stopped after {len(items)} embeddings. Progress saved to {args.output}")
            print(f"Embedding error: {exc}")
            print("Run the same command later with --resume to continue.")
            return

        items.append({"chunk": chunk, "embedding": embedding})
        print(f"Embedded {index}/{len(chunks)}: {chunk['chunk_id']}")
        if args.delay:
            time.sleep(args.delay)

        if index % 25 == 0:
            save_index(args.output, model, args.dimensions, items)

    save_index(args.output, model, args.dimensions, items)

    print(f"Built vector index with {len(items)} embeddings at {args.output}")


if __name__ == "__main__":
    main()
