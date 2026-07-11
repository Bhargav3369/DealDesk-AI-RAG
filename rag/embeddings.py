import json
import math
import time
import urllib.error
import urllib.request

from rag.config import get_setting


DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"


class EmbeddingError(RuntimeError):
    pass


def normalize(values):
    magnitude = math.sqrt(sum(value * value for value in values))
    if magnitude == 0:
        return values
    return [value / magnitude for value in values]


def cosine_similarity(left, right):
    return sum(a * b for a, b in zip(left, right))


def _extract_embedding(payload):
    if "embedding" in payload and "values" in payload["embedding"]:
        return payload["embedding"]["values"]
    embeddings = payload.get("embeddings") or []
    if embeddings and "values" in embeddings[0]:
        return embeddings[0]["values"]
    raise EmbeddingError(f"Gemini embedding response did not include values: {json.dumps(payload)[:1000]}")


def embed_text(text, task_type="RETRIEVAL_DOCUMENT", model=None, output_dimensionality=768, timeout=60):
    api_key = get_setting("GEMINI_API_KEY")
    if not api_key:
        raise EmbeddingError("GEMINI_API_KEY is not set.")

    selected_model = model or get_setting("GEMINI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    body = {
        "taskType": task_type,
        "content": {
            "parts": [
                {
                    "text": text,
                }
            ]
        },
        "output_dimensionality": output_dimensionality,
    }
    request = urllib.request.Request(
        EMBEDDING_URL_TEMPLATE.format(model=selected_model),
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise EmbeddingError(f"Gemini embedding API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise EmbeddingError(f"Gemini embedding API request failed: {exc}") from exc

    return normalize(_extract_embedding(payload))


def embed_with_retries(text, task_type, retries=3, delay=1.0, **kwargs):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return embed_text(text, task_type=task_type, **kwargs)
        except EmbeddingError as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(delay * attempt)
    raise last_error
