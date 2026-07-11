import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.text import chunk_text


def iter_documents(paths):
    for path in paths:
        path = Path(path)
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as src:
            for line in src:
                if line.strip():
                    yield json.loads(line)


def main():
    parser = argparse.ArgumentParser(description="Combine and chunk all documents for retrieval.")
    parser.add_argument(
        "--inputs",
        nargs="+",
        default=["data/public_docs/documents.jsonl", "data/local_docs/documents.jsonl"],
    )
    parser.add_argument("--output", default="data/rag/chunks.jsonl")
    parser.add_argument("--chunk-words", type=int, default=350)
    parser.add_argument("--overlap-words", type=int, default=60)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    total_docs = 0
    total_chunks = 0

    with open(args.output, "w", encoding="utf-8") as dst:
        for doc in iter_documents(args.inputs):
            total_docs += 1
            chunks = chunk_text(doc.get("text", ""), args.chunk_words, args.overlap_words)
            for index, text in enumerate(chunks):
                record = {
                    "chunk_id": f"{doc['id']}-{index:04d}",
                    "doc_id": doc["id"],
                    "vendor": doc.get("vendor", "Unknown"),
                    "source_url": doc.get("source_url", ""),
                    "title": doc.get("title", ""),
                    "chunk_index": index,
                    "text": text,
                }
                dst.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_chunks += 1

    print(f"Processed {total_docs} documents into {total_chunks} chunks at {args.output}")


if __name__ == "__main__":
    main()
