import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(script, *args):
    command = [sys.executable, str(ROOT / "scripts" / script), *args]
    print("\n> " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description="Run the complete local RAG ingestion pipeline.")
    parser.add_argument("--source-dir", default="data/inbox")
    parser.add_argument("--vendor", default="Custom")
    parser.add_argument("--with-vector", action="store_true")
    parser.add_argument("--vector-limit", default=None)
    parser.add_argument("--top-level-only", action="store_true", help="Reserved for future use.")
    args = parser.parse_args()

    run("ingest_local_documents.py", "--source-dir", args.source_dir, "--vendor", args.vendor)
    run("prepare_rag_corpus.py")
    run("build_bm25_index.py")
    if args.with_vector:
        command_args = ["--resume"]
        if args.vector_limit:
            command_args.extend(["--limit", args.vector_limit])
        run("build_vector_index.py", *command_args)
    print("\nRAG pipeline complete. Query with: python scripts/query_rag.py \"your question\"")


if __name__ == "__main__":
    main()
