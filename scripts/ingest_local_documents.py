import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.loaders import iter_supported_files, load_document_file


def stable_id(path, text):
    fingerprint = f"{Path(path).as_posix()}\n{text[:2000]}".encode("utf-8")
    return hashlib.sha256(fingerprint).hexdigest()[:16]


def infer_vendor(path, source_dir, default_vendor):
    try:
        relative = Path(path).relative_to(source_dir)
    except ValueError:
        return default_vendor
    if len(relative.parts) > 1:
        return relative.parts[0]
    return default_vendor


def main():
    parser = argparse.ArgumentParser(description="Ingest new local files into normalized RAG documents.")
    parser.add_argument("--source-dir", default="data/inbox")
    parser.add_argument("--output", default="data/local_docs/documents.jsonl")
    parser.add_argument("--vendor", default="Custom")
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    records = []
    for path in iter_supported_files(source_dir):
        title, text = load_document_file(path)
        if len(text.split()) < 40:
            print(f"SKIP short document: {path}")
            continue

        doc_id = stable_id(path, text)
        records.append(
            {
                "id": doc_id,
                "vendor": infer_vendor(path, source_dir, args.vendor),
                "source_url": Path(path).as_posix(),
                "title": title,
                "text": text,
                "fetched_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "source_type": "local_file",
            }
        )
        print(f"OK local: {path}")

    with open(args.output, "w", encoding="utf-8") as dst:
        for record in records:
            dst.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Saved {len(records)} local documents to {args.output}")


if __name__ == "__main__":
    main()
