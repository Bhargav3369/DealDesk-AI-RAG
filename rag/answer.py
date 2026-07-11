from rag.gemini import GeminiError, generate_text
from rag.prompts import SYSTEM_INSTRUCTION, build_grounded_prompt


def retrieval_confidence(results):
    if not results:
        return "low"
    top = results[0]["score"]
    if top >= 25:
        return "high"
    if top >= 10:
        return "medium"
    return "low"


def format_citations(results):
    citations = []
    for index, result in enumerate(results, start=1):
        chunk = result["chunk"]
        citations.append(
            {
                "id": index,
                "vendor": chunk.get("vendor", "Unknown"),
                "title": chunk.get("title", ""),
                "source_url": chunk.get("source_url", ""),
                "score": result.get("score"),
            }
        )
    return citations


def fallback_answer(question, results):
    if not results:
        return "I do not have enough indexed source material to answer that question."

    lines = [
        "I found relevant sources, but Gemini generation is not configured yet.",
        "",
        "Use these citations as grounded context:",
    ]
    for index, result in enumerate(results, start=1):
        chunk = result["chunk"]
        lines.append(f"[{index}] {chunk.get('vendor')} - {chunk.get('title')}")
        lines.append(f"    {chunk.get('source_url')}")
        lines.append(f"    Score: {result.get('score')}")
    lines.append("")
    lines.append(f"Question: {question}")
    lines.append("Set GEMINI_API_KEY in `.env` to generate the final natural-language answer.")
    return "\n".join(lines)


def generate_grounded_answer(question, results, mode="qa", use_gemini=True):
    confidence = retrieval_confidence(results)
    citations = format_citations(results)

    if not use_gemini:
        return {
            "answer": fallback_answer(question, results),
            "confidence": confidence,
            "citations": citations,
            "used_model": None,
        }

    try:
        prompt = build_grounded_prompt(question, results, mode=mode)
        answer = generate_text(prompt, SYSTEM_INSTRUCTION)
        return {
            "answer": answer,
            "confidence": confidence,
            "citations": citations,
            "used_model": "gemini",
        }
    except GeminiError as exc:
        return {
            "answer": fallback_answer(question, results),
            "confidence": confidence,
            "citations": citations,
            "used_model": None,
            "warning": str(exc),
        }
