import json
import urllib.error
import urllib.request

from rag.config import get_setting


DEFAULT_MODEL = "gemini-3.1-flash-lite"
INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


class GeminiError(RuntimeError):
    pass


def _extract_output_text(payload):
    if isinstance(payload, dict):
        if isinstance(payload.get("output_text"), str):
            return payload["output_text"].strip()

        texts = []
        for step in payload.get("steps", []) or []:
            for key in ("content", "contents", "output"):
                value = step.get(key)
                if isinstance(value, str):
                    texts.append(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and isinstance(item.get("text"), str):
                            texts.append(item["text"])
        if texts:
            return "\n".join(texts).strip()

    return ""


def generate_text(prompt, system_instruction, model=None, temperature=0.2, timeout=60):
    api_key = get_setting("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not set.")

    body = {
        "model": model or get_setting("GEMINI_MODEL", DEFAULT_MODEL),
        "system_instruction": system_instruction,
        "input": prompt,
        "generation_config": {
            "temperature": temperature,
            "thinking_level": "low",
        },
    }
    request = urllib.request.Request(
        INTERACTIONS_URL,
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
        raise GeminiError(f"Gemini API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise GeminiError(f"Gemini API request failed: {exc}") from exc

    text = _extract_output_text(payload)
    if not text:
        raise GeminiError(f"Gemini API returned no text: {json.dumps(payload)[:1000]}")
    return text
