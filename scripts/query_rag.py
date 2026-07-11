import argparse
import json
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.bm25 import search


def make_answer(question, results):
    if not results:
        return "I could not find enough supporting information in the indexed documents."

    lines = [
        "Draft grounded answer:",
        "Use the cited snippets below to answer this question. If a fact is not supported, say so.",
        f"Question: {question}",
        "",
        "Most relevant sources:",
    ]
    for index, result in enumerate(results, start=1):
        chunk = result["chunk"]
        lines.append(f"[{index}] {chunk.get('vendor')} - {chunk.get('title')}")
        lines.append(f"    URL: {chunk.get('source_url')}")
        lines.append(f"    Score: {result['score']}")
        lines.append("    " + textwrap.shorten(chunk["text"].replace("\n", " "), width=650, placeholder="..."))
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Query the local RAG index and show cited retrieval context.")
    parser.add_argument("question")
    parser.add_argument("--index", default="data/index/bm25_index.json")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    with open(args.index, "r", encoding="utf-8") as src:
        index = json.load(src)

    results = search(index, args.question, args.top_k)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(make_answer(args.question, results))


if __name__ == "__main__":
    main()
