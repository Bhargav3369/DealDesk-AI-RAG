import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.text import chunk_text, tokenize
from rag.bm25 import build_index, search

def test_chunk_text():
    # Generate 100 dummy words
    text = " ".join([f"word{i}" for i in range(100)])
    # Chunk with max 40 words, overlap of 10
    chunks = list(chunk_text(text, chunk_words=40, overlap_words=10))
    # Should create multiple overlapping chunks
    assert len(chunks) >= 3
    assert len(chunks[0].split()) == 40
    assert len(chunks[1].split()) <= 40

def test_tokenization():
    text = "Supabase provides Postgres-powered real-time databases! Excellent."
    tokens = tokenize(text)
    assert "supabase" in tokens
    assert "postgres-powered" in tokens
    assert "!" not in tokens # Should be stripped of raw punctuations

def test_bm25_build_and_search():
    chunks = [
        {"text": "Firebase is a mobile backend platform by Google.", "vendor": "Firebase", "metadata": "platform"},
        {"text": "Supabase provides an open source Firebase alternative.", "vendor": "Supabase", "metadata": "database"},
        {"text": "Vercel is the platform for frontend frameworks, providing speed.", "vendor": "Vercel", "metadata": "hosting"}
    ]
    
    index = build_index(chunks)
    assert index["total_docs"] == 3
    assert len(index["documents"]) == 3
    
    # Search for "Firebase alternative"
    results = search(index, "Firebase alternative")
    assert len(results) > 0
    # "Supabase provides an open source Firebase alternative" matches completely
    assert results[0]["chunk"]["vendor"] == "Supabase"
    
    # Search for "Firebase", but explicitly filter vendor to only search within Vercel logs
    # Should probably return 0, but tests filtering directly.
    filter_results = search(index, "platform", filters={"vendor": "Vercel"})
    assert len(filter_results) == 1
    assert filter_results[0]["chunk"]["vendor"] == "Vercel"
