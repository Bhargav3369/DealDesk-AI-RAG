import re


def clean_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_+\-./]*", text.lower())


def chunk_text(text, chunk_words=350, overlap_words=60, min_words=80):
    words = re.findall(r"\S+", clean_text(text))
    if not words:
        return []

    chunks = []
    step = max(1, chunk_words - overlap_words)
    for start in range(0, len(words), step):
        window = words[start : start + chunk_words]
        if len(window) < min_words:
            continue
        chunks.append(" ".join(window))
    return chunks
