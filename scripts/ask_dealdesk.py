import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.answer import generate_grounded_answer
from rag.bm25 import search
from rag.retrievers import search_hybrid


def print_answer(payload):
    print(payload["answer"])
    print("\nConfidence:", payload["confidence"])
    if payload.get("warning"):
        print("Warning:", payload["warning"])
    print("\nCitations:")
    for citation in payload["citations"]:
        print(
            f"[{citation['id']}] {citation['vendor']} - {citation['title']} "
            f"({citation['source_url']}) score={citation['score']}"
        )


def main():
    parser = argparse.ArgumentParser(description="Ask DealDesk AI using retrieval plus optional Gemini generation.")
    parser.add_argument("question")
    parser.add_argument("--index", default="data/index/bm25_index.json")
    parser.add_argument("--vector-index", default="data/index/vector_index.json")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--retriever",
        choices=["bm25", "hybrid"],
        default="bm25",
    )
    parser.add_argument(
        "--mode",
        choices=["qa", "compare", "objection", "email", "recommend"],
        default="qa",
    )
    parser.add_argument("--no-gemini", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--vendor", help="Filter by vendor (e.g., Supabase)")
    args = parser.parse_args()

    filters = {}
    if args.vendor:
        filters["vendor"] = args.vendor

    with open(args.index, "r", encoding="utf-8") as src:
        index = json.load(src)

    if args.retriever == "hybrid":
        results = search_hybrid(index, args.vector_index, args.question, top_k=args.top_k, filters=filters, mode=args.mode)
    else:
        results = search(index, args.question, top_k=args.top_k, filters=filters)
    payload = generate_grounded_answer(
        args.question,
        results,
        mode=args.mode,
        use_gemini=not args.no_gemini,
    )

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_answer(payload)


if __name__ == "__main__":
    main()
