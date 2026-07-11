from rag.bm25 import search as search_bm25
from rag.vector_index import load_vector_index, search_vector_index


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _dedupe(results):
    seen = set()
    deduped = []
    for result in results:
        chunk_id = result["chunk"].get("chunk_id")
        if chunk_id in seen:
            continue
        seen.add(chunk_id)
        deduped.append(result)
    return deduped


def _normalize_scores(results):
    if not results:
        return []
    max_score = max(result["score"] for result in results) or 1
    return [
        {
            "score": result["score"] / max_score,
            "chunk": result["chunk"],
        }
        for result in results
    ]


def _get_vendors(bm25_index):
    """Return sorted list of unique vendors from the BM25 index."""
    vendors = set()
    for doc in bm25_index.get("documents", []):
        v = doc["chunk"].get("vendor")
        if v:
            vendors.add(v)
    return sorted(vendors)


# ─────────────────────────────────────────────────────────────────────
# Balanced retrieval  (used by compare / recommend modes)
# ─────────────────────────────────────────────────────────────────────

def search_balanced(bm25_index, query, top_k=5, slots_per_vendor=2):
    """
    Pull the best `slots_per_vendor` BM25 hits per vendor, then merge
    and deduplicate so the final result set spans multiple vendors.
    Falls back to standard search when only one vendor is present.
    """
    vendors = _get_vendors(bm25_index)
    if len(vendors) <= 1:
        return search_bm25(bm25_index, query, top_k=top_k)

    per_vendor_results = []
    for vendor in vendors:
        hits = search_bm25(
            bm25_index, query,
            top_k=slots_per_vendor,
            filters={"vendor": vendor}
        )
        per_vendor_results.extend(hits)

    # Re-sort by score, dedupe, trim to top_k
    ranked = sorted(per_vendor_results, key=lambda r: r["score"], reverse=True)
    return _dedupe(ranked)[:top_k]


# ─────────────────────────────────────────────────────────────────────
# Hybrid retrieval  (BM25 + Vector)
# ─────────────────────────────────────────────────────────────────────

def search_hybrid(bm25_index, vector_index_path, query, top_k=5, filters=None, mode=None):
    """
    Hybrid BM25 + semantic search with optional vendor-balanced retrieval.
    If mode is 'compare' or 'recommend' and no explicit vendor filter is set,
    use balanced multi-vendor retrieval so each vendor gets fair representation.
    """
    use_balanced = mode in ("compare", "recommend") and not filters

    if use_balanced:
        # Balanced BM25: best N chunks per vendor
        slots_per_vendor = max(2, top_k // max(1, len(_get_vendors(bm25_index))))
        lexical_raw = search_balanced(bm25_index, query, top_k=top_k * 2, slots_per_vendor=slots_per_vendor)
    else:
        lexical_raw = search_bm25(bm25_index, query, top_k=top_k * 2, filters=filters)

    # Vector search (always standard — embedding space is already vendor-agnostic)
    try:
        vector_raw = search_vector_index(
            load_vector_index(vector_index_path), query,
            top_k=top_k * 2,
            filters=filters
        )
    except Exception:
        vector_raw = []

    lexical = _normalize_scores(lexical_raw)
    vector  = _normalize_scores(vector_raw)

    combined = {}
    for result in lexical:
        chunk_id = result["chunk"].get("chunk_id")
        combined.setdefault(chunk_id, {"score": 0, "chunk": result["chunk"]})
        combined[chunk_id]["score"] += 0.4 * result["score"]

    for result in vector:
        chunk_id = result["chunk"].get("chunk_id")
        combined.setdefault(chunk_id, {"score": 0, "chunk": result["chunk"]})
        combined[chunk_id]["score"] += 0.6 * result["score"]

    ranked = sorted(combined.values(), key=lambda r: r["score"], reverse=True)
    return [
        {
            "score": round(r["score"] * 100, 4),
            "chunk": r["chunk"],
        }
        for r in _dedupe(ranked)[:top_k]
    ]
