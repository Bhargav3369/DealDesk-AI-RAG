import json

from rag.embeddings import cosine_similarity, embed_with_retries


def load_vector_index(path):
    with open(path, "r", encoding="utf-8") as src:
        return json.load(src)


def check_filters(chunk, filters):
    if not filters:
        return True
    for key, value in filters.items():
        if chunk.get(key) != value:
            return False
    return True

def search_vector_index(index, query, top_k=5, filters=None):
    query_vector = embed_with_retries(
        query,
        task_type="RETRIEVAL_QUERY",
        model=index.get("model"),
        output_dimensionality=index.get("dimensions", 768),
    )
    results = []
    for item in index["items"]:
        if filters and not check_filters(item["chunk"], filters):
            continue
        score = cosine_similarity(query_vector, item["embedding"])
        results.append({"score": round(score, 4), "chunk": item["chunk"]})
    return sorted(results, key=lambda result: result["score"], reverse=True)[:top_k]
