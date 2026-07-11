from rag.bm25 import search as search_bm25
from rag.vector_index import load_vector_index, search_vector_index


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


def search_hybrid(bm25_index, vector_index_path, query, top_k=5, filters=None):
    lexical = _normalize_scores(search_bm25(bm25_index, query, top_k=top_k * 2, filters=filters))
    vector = _normalize_scores(search_vector_index(load_vector_index(vector_index_path), query, top_k=top_k * 2, filters=filters))
    combined = {}

    for result in lexical:
        chunk_id = result["chunk"].get("chunk_id")
        combined.setdefault(chunk_id, {"score": 0, "chunk": result["chunk"]})
        combined[chunk_id]["score"] += 0.4 * result["score"]

    for result in vector:
        chunk_id = result["chunk"].get("chunk_id")
        combined.setdefault(chunk_id, {"score": 0, "chunk": result["chunk"]})
        combined[chunk_id]["score"] += 0.6 * result["score"]

    ranked = sorted(combined.values(), key=lambda result: result["score"], reverse=True)
    return [
        {
            "score": round(result["score"] * 100, 4),
            "chunk": result["chunk"],
        }
        for result in _dedupe(ranked)[:top_k]
    ]
