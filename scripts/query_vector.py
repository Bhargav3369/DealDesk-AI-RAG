import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.vector_index import load_vector_index, search_vector_index


def main():
    parser = argparse.ArgumentParser(description="Query the Gemini embedding vector index.")
    parser.add_argument("question")
    parser.add_argument("--index", default="data/index/vector_index.json")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    index = load_vector_index(args.index)
    results = search_vector_index(index, args.question, top_k=args.top_k)
    for rank, result in enumerate(results, start=1):
        chunk = result["chunk"]
        print(f"[{rank}] score={result['score']} {chunk.get('vendor')} - {chunk.get('title')}")
        print(f"    {chunk.get('source_url')}")
        print(f"    {chunk.get('text')[:400].replace(chr(10), ' ')}")
        print()


if __name__ == "__main__":
    main()
