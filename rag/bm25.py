import math
from collections import Counter, defaultdict

from rag.text import tokenize


def build_index(chunks):
    tokenized = []
    doc_freq = Counter()

    for chunk in chunks:
        tokens = tokenize(chunk["text"])
        counts = Counter(tokens)
        tokenized.append({"counts": counts, "length": len(tokens)})
        doc_freq.update(counts.keys())

    total_docs = len(chunks)
    avgdl = sum(item["length"] for item in tokenized) / max(1, total_docs)
    idf = {
        term: math.log(1 + (total_docs - freq + 0.5) / (freq + 0.5))
        for term, freq in doc_freq.items()
    }

    return {
        "type": "bm25",
        "version": 1,
        "total_docs": total_docs,
        "avgdl": avgdl,
        "idf": idf,
        "documents": [
            {
                "chunk": chunk,
                "term_counts": dict(tokenized[index]["counts"]),
                "length": tokenized[index]["length"],
            }
            for index, chunk in enumerate(chunks)
        ],
    }


def check_filters(chunk, filters):
    if not filters:
        return True
    for key, value in filters.items():
        if chunk.get(key) != value: # Depending on where metadata is. Usually chunk has top level metadata like chunk["vendor"]
            return False
    return True

def search(index, query, top_k=5, filters=None):
    query_terms = tokenize(query)
    if not query_terms:
        return []

    k1 = 1.5
    b = 0.75
    avgdl = index.get("avgdl") or 1
    idf = index["idf"]
    scores = defaultdict(float)

    for term in query_terms:
        if term not in idf:
            continue
        for doc_index, doc in enumerate(index["documents"]):
            if filters and not check_filters(doc["chunk"], filters):
                continue
            freq = doc["term_counts"].get(term, 0)
            if not freq:
                continue
            dl = doc["length"] or 1
            numerator = freq * (k1 + 1)
            denominator = freq + k1 * (1 - b + b * dl / avgdl)
            scores[doc_index] += idf[term] * numerator / denominator

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
    return [
        {
            "score": round(score, 4),
            "chunk": index["documents"][doc_index]["chunk"],
        }
        for doc_index, score in ranked
    ]
