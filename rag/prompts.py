SYSTEM_INSTRUCTION = """You are DealDesk AI, a sales and support intelligence copilot.

Use only the supplied source snippets. If the sources do not support the answer, say that the indexed documents do not contain enough information.

Rules:
- Be concise and business-focused.
- Cite sources inline using bracket numbers like [1] or [2].
- Do not invent prices, limits, SLAs, features, or legal claims.
- If sources conflict or are incomplete, call that out.
- End with a short "Recommended next step" when useful.
"""


def build_grounded_prompt(question, retrieved_sources, mode="qa"):
    mode_hint = {
        "qa": "Answer the user's question.",
        "compare": "Compare the options in a compact table followed by a recommendation.",
        "objection": "Draft an objection-handling response a sales/support teammate can send.",
        "email": "Draft a professional customer email using only supported facts.",
        "recommend": "Recommend the best-fit option and explain tradeoffs.",
    }.get(mode, "Answer the user's question.")

    source_blocks = []
    for index, result in enumerate(retrieved_sources, start=1):
        chunk = result["chunk"]
        source_blocks.append(
            "\n".join(
                [
                    f"[{index}] Vendor: {chunk.get('vendor', 'Unknown')}",
                    f"Title: {chunk.get('title', '')}",
                    f"URL: {chunk.get('source_url', '')}",
                    f"Retrieval score: {result.get('score')}",
                    "Snippet:",
                    chunk.get("text", ""),
                ]
            )
        )

    return "\n\n".join(
        [
            f"Task mode: {mode}",
            mode_hint,
            f"Question: {question}",
            "Sources:",
            "\n\n---\n\n".join(source_blocks),
        ]
    )
