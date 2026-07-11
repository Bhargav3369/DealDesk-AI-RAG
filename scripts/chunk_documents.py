import argparse
import json
import os
import re


def tokenizeish(text):
    return re.findall(r"\S+", text)


def chunk_text(text, chunk_words, overlap_words):
    words = tokenizeish(text)
    if not words:
        return []
    chunks = []
    step = max(1, chunk_words - overlap_words)
    for start in range(0, len(words), step):
        window = words[start : start + chunk_words]
        if len(window) < 80:
            continue
        chunks.append(" ".join(window))
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Chunk crawled documents into RAG-ready JSONL.")
    parser.add_argument("--input", default="data/public_docs/documents.jsonl")
    parser.add_argument("--output", default="data/public_docs/chunks.jsonl")
    parser.add_argument("--chunk-words", type=int, default=350)
    parser.add_argument("--overlap-words", type=int, default=60)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    total = 0
    with open(args.input, "r", encoding="utf-8") as src, open(args.output, "w", encoding="utf-8") as dst:
        for line in src:
            doc = json.loads(line)
            for index, chunk in enumerate(chunk_text(doc["text"], args.chunk_words, args.overlap_words)):
                record = {
                    "chunk_id": f"{doc['id']}-{index:04d}",
                    "doc_id": doc["id"],
                    "vendor": doc["vendor"],
                    "source_url": doc["source_url"],
                    "title": doc.get("title", ""),
                    "chunk_index": index,
                    "text": chunk,
                }
                dst.write(json.dumps(record, ensure_ascii=False) + "\n")
                total += 1

    print(f"Saved {total} chunks to {args.output}")


if __name__ == "__main__":
    main()
