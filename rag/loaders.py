import json
import os
from pathlib import Path

from rag.html_text import extract_html_text
from rag.text import clean_text


TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv", ".tsv", ".log"}
HTML_EXTENSIONS = {".html", ".htm"}
JSON_EXTENSIONS = {".json", ".jsonl"}


def load_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF support needs pypdf installed.") from exc

    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"\n\n[Page {index}]\n{text}")
    return clean_text("\n".join(pages))


def load_docx(path):
    try:
        import docx
    except ImportError as exc:
        raise RuntimeError("DOCX support needs python-docx installed.") from exc

    document = docx.Document(str(path))
    return clean_text("\n".join(paragraph.text for paragraph in document.paragraphs))


def load_json_text(path):
    if path.suffix.lower() == ".jsonl":
        texts = []
        with open(path, "r", encoding="utf-8") as src:
            for line in src:
                if not line.strip():
                    continue
                item = json.loads(line)
                texts.append(item.get("text") or json.dumps(item, ensure_ascii=False))
        return clean_text("\n\n".join(texts))

    with open(path, "r", encoding="utf-8") as src:
        item = json.load(src)
    if isinstance(item, dict) and item.get("text"):
        return clean_text(item["text"])
    return clean_text(json.dumps(item, ensure_ascii=False, indent=2))


def load_document_file(path):
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in TEXT_EXTENSIONS:
        return path.stem, clean_text(path.read_text(encoding="utf-8", errors="replace"))
    if suffix in HTML_EXTENSIONS:
        title, text = extract_html_text(path.read_text(encoding="utf-8", errors="replace"))
        return title or path.stem, text
    if suffix in JSON_EXTENSIONS:
        return path.stem, load_json_text(path)
    if suffix == ".pdf":
        return path.stem, load_pdf(path)
    if suffix == ".docx":
        return path.stem, load_docx(path)

    raise ValueError(f"Unsupported file type: {path}")


def iter_supported_files(root):
    root = Path(root)
    supported = TEXT_EXTENSIONS | HTML_EXTENSIONS | JSON_EXTENSIONS | {".pdf", ".docx"}
    for current_root, _, files in os.walk(root):
        for file_name in files:
            path = Path(current_root) / file_name
            if path.suffix.lower() in supported:
                yield path
