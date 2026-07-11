import argparse
import datetime as dt
import hashlib
import html.parser
import json
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import deque


SOURCE_CONFIG = [
    {
        "vendor": "Supabase",
        "domain": "supabase.com",
        "seeds": [
            "https://supabase.com/docs",
            "https://supabase.com/pricing",
            "https://supabase.com/docs/guides/auth",
            "https://supabase.com/docs/guides/database",
            "https://supabase.com/docs/guides/storage",
            "https://supabase.com/docs/guides/realtime",
            "https://supabase.com/docs/guides/functions",
            "https://supabase.com/docs/guides/ai",
        ],
        "allow_prefixes": ["https://supabase.com/docs", "https://supabase.com/pricing"],
    },
    {
        "vendor": "Firebase",
        "domain": "firebase.google.com",
        "seeds": [
            "https://firebase.google.com/docs",
            "https://firebase.google.com/pricing",
            "https://firebase.google.com/docs/auth",
            "https://firebase.google.com/docs/firestore",
            "https://firebase.google.com/docs/storage",
            "https://firebase.google.com/docs/hosting",
            "https://firebase.google.com/docs/functions",
            "https://firebase.google.com/docs/database",
        ],
        "allow_prefixes": ["https://firebase.google.com/docs", "https://firebase.google.com/pricing"],
    },
    {
        "vendor": "Vercel",
        "domain": "vercel.com",
        "seeds": [
            "https://vercel.com/docs",
            "https://vercel.com/pricing",
            "https://vercel.com/docs/deployments",
            "https://vercel.com/docs/functions",
            "https://vercel.com/docs/storage",
            "https://vercel.com/docs/security",
            "https://vercel.com/docs/frameworks",
            "https://vercel.com/docs/analytics",
        ],
        "allow_prefixes": ["https://vercel.com/docs", "https://vercel.com/pricing"],
    },
    {
        "vendor": "Render",
        "domain": "render.com",
        "seeds": [
            "https://render.com/docs",
            "https://render.com/pricing",
            "https://render.com/docs/web-services",
            "https://render.com/docs/postgresql-creating-connecting",
            "https://render.com/docs/deploy-node-express-app",
            "https://render.com/docs/deploy-django",
            "https://render.com/docs/blueprint-spec",
            "https://render.com/docs/free",
        ],
        "allow_prefixes": ["https://render.com/docs", "https://render.com/pricing"],
    },
]


class TextAndLinkExtractor(html.parser.HTMLParser):
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title = ""
        self.links = []
        self.text_parts = []
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "a" and attrs.get("href"):
            self.links.append(urllib.parse.urljoin(self.base_url, attrs["href"]))
        if tag in {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3", "h4", "tr"}:
            self.text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in {"p", "section", "article", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.text_parts.append("\n")

    def handle_data(self, data):
        if self._skip_depth:
            return
        clean = data.strip()
        if not clean:
            return
        if self._in_title:
            self.title += clean + " "
        self.text_parts.append(clean + " ")

    def text(self):
        text = "".join(self.text_parts)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def normalize_url(url):
    parsed = urllib.parse.urlparse(url)
    parsed = parsed._replace(fragment="", query="")
    path = parsed.path.rstrip("/") or "/"
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def is_allowed_doc_url(url, source):
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower() != source["domain"]:
        return False
    normalized = normalize_url(url)
    return any(normalized.startswith(prefix) for prefix in source["allow_prefixes"])


def robot_parser_for(source, user_agent):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"https://{source['domain']}/robots.txt")
    try:
        rp.read()
    except Exception:
        return None
    return rp


def fetch(url, user_agent, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return None
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def stable_id(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def crawl_source(source, max_pages, delay, timeout, out_dir, user_agent):
    os.makedirs(out_dir, exist_ok=True)
    raw_dir = os.path.join(out_dir, "raw_html")
    os.makedirs(raw_dir, exist_ok=True)
    rp = robot_parser_for(source, user_agent)
    queue = deque(normalize_url(url) for url in source["seeds"])
    seen = set()
    docs = []

    while queue and len(docs) < max_pages:
        url = queue.popleft()
        if url in seen or not is_allowed_doc_url(url, source):
            continue
        seen.add(url)

        if rp is not None and not rp.can_fetch(user_agent, url):
            print(f"SKIP robots.txt: {url}")
            continue

        try:
            html = fetch(url, user_agent, timeout)
            if not html:
                continue
            extractor = TextAndLinkExtractor(url)
            extractor.feed(html)
            text = extractor.text()
            if len(text) < 500:
                continue

            doc_id = stable_id(url)
            raw_path = os.path.join(raw_dir, f"{source['vendor'].lower()}_{doc_id}.html")
            with open(raw_path, "w", encoding="utf-8") as raw_file:
                raw_file.write(html)

            docs.append(
                {
                    "id": doc_id,
                    "vendor": source["vendor"],
                    "source_url": url,
                    "title": extractor.title.strip(),
                    "text": text,
                    "fetched_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                    "raw_html_path": raw_path.replace("\\", "/"),
                }
            )
            print(f"OK {source['vendor']}: {url}")

            for link in extractor.links:
                normalized = normalize_url(link)
                if normalized not in seen and is_allowed_doc_url(normalized, source):
                    queue.append(normalized)

            time.sleep(delay)
        except Exception as exc:
            print(f"ERR {url}: {exc}")

    return docs


def main():
    parser = argparse.ArgumentParser(description="Crawl public docs for DealDesk AI RAG dataset.")
    parser.add_argument("--out", default="data/public_docs", help="Output directory.")
    parser.add_argument("--max-pages-per-source", type=int, default=40)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--user-agent", default="DealDeskAI-RAG-StudentProject/0.1")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    output_path = os.path.join(args.out, "documents.jsonl")
    all_docs = []

    for source in SOURCE_CONFIG:
        docs = crawl_source(
            source=source,
            max_pages=args.max_pages_per_source,
            delay=args.delay,
            timeout=args.timeout,
            out_dir=args.out,
            user_agent=args.user_agent,
        )
        all_docs.extend(docs)

    with open(output_path, "w", encoding="utf-8") as output:
        for doc in all_docs:
            output.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"\nSaved {len(all_docs)} documents to {output_path}")


if __name__ == "__main__":
    main()
