import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.bm25 import build_index


def main():
    parser = argparse.ArgumentParser(description="Build a local BM25 retrieval index.")
    parser.add_argument("--chunks", default="data/rag/chunks.jsonl")
    parser.add_argument("--output", default="data/index/bm25_index.json")
    args = parser.parse_args()

    chunks = []
    with open(args.chunks, "r", encoding="utf-8") as src:
        for line in src:
            if line.strip():
                chunks.append(json.loads(line))

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    index = build_index(chunks)
    with open(args.output, "w", encoding="utf-8") as dst:
        json.dump(index, dst, ensure_ascii=False)

    print(f"Built BM25 index with {len(chunks)} chunks at {args.output}")


if __name__ == "__main__":
    main()
