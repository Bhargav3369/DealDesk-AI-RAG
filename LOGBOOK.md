# RAG Project Logbook

## Project Task List

- [x] Decide project concept and business use case: DealDesk AI, a RAG-powered SaaS sales/support intelligence copilot.
- [x] Choose public data sources so the project does not require private company documents.
- [x] Select initial vendors: Supabase, Firebase, Vercel, and Render.
- [x] Create a data source manifest with vendor URLs, allowed crawl prefixes, and dataset notes.
- [x] Build a public documentation crawler.
- [x] Crawl a starter public dataset.
- [x] Save raw HTML for traceability.
- [x] Convert crawled pages into structured `documents.jsonl`.
- [x] Build a document chunking script.
- [x] Generate the first RAG-ready chunk dataset.
- [x] Create a local document drop zone at `data/inbox`.
- [x] Add support for ingesting new local documents.
- [x] Support common local formats: Markdown, text, HTML, JSON, JSONL, PDF, and DOCX.
- [x] Combine public and local documents into one RAG corpus.
- [x] Build a local BM25 retrieval baseline.
- [x] Add a one-command RAG pipeline runner.
- [x] Test that a newly added document flows through ingestion, chunking, indexing, and retrieval.
- [x] Add README instructions for running the dataset and RAG pipeline.
- [x] Create and maintain this logbook.
- [x] Add Gemini API generation for final cited answers.
- [x] Add environment configuration for API keys and model settings.
- [x] Add stronger semantic retrieval with Gemini embeddings and a vector index.
- [x] Keep BM25 as a fallback or hybrid retrieval signal.
- [x] Add source-aware answer formatting with citations.
- [x] Add confidence scoring based on retrieval strength and source coverage.
- [x] Add "I do not know from the provided sources" behavior for weak retrieval.
- [x] Add DealDesk modes: comparison, objection handling, email draft, and product recommendation.
- [x] Add query filters by vendor, source type, and document category.
- [x] Add retrieval evaluation questions and expected source checks.
- [x] Add automated tests for ingestion, chunking, indexing, and querying.
- [x] Add a small backend API, likely FastAPI.
- [x] Add a frontend chatbot interface.
- [x] Show retrieved sources/snippets in the UI.
- [x] Add document upload from the UI.
- [x] Trigger the RAG pipeline after document upload.
- [x] Add chat history and user feedback storage.
- [x] Add analytics for unanswered questions, top topics, and weak knowledge areas.
- [x] Add Docker or simple setup scripts for easier local running.
- [x] Add deployment path using free/open Google-friendly tools where practical.
- [x] Polish README with architecture diagram, screenshots, demo questions, and resume bullets.
- [x] Record a clean demo workflow for portfolio/GitHub.

## Entry 1 - 2026-07-11

### GOAL:
Build a resume-worthy RAG side project named **DealDesk AI**, a SaaS sales/support intelligence copilot that uses public developer-platform documentation to answer business questions with citations, compare vendors, support objection handling, and draft grounded customer responses.

### Progress:
- Chose the project direction: **DealDesk AI: A RAG-Powered Sales Intelligence Copilot for SaaS Teams**.
- Selected a public-data strategy so the project does not depend on private company documents.
- Picked four high-value developer-platform sources:
  - Supabase
  - Firebase
  - Vercel
  - Render
- Created `data_sources.yaml` with source URLs, allowed crawl prefixes, vendor metadata, and dataset notes.
- Created `scripts/crawl_public_docs.py`, a polite public-docs crawler that:
  - Starts from curated seed URLs.
  - Restricts crawling to approved docs/pricing prefixes.
  - Checks `robots.txt`.
  - Extracts readable text and links from HTML.
  - Saves raw HTML for traceability.
  - Writes structured JSONL records with source metadata.
- Created `scripts/chunk_documents.py`, a RAG chunking script that:
  - Reads crawled documents from JSONL.
  - Splits text into overlapping chunks.
  - Preserves citation metadata such as vendor, title, URL, document ID, and chunk index.
- Created `README.md` with:
  - Dataset source summary.
  - Commands to crawl and chunk documents.
  - Recommended RAG metadata.
  - Demo questions for the future chatbot.
- Ran a small test crawl first:
  - 12 documents collected.
  - 85 chunks generated.
- Fixed a Python UTC datetime deprecation warning in the crawler.
- Improved HTML decoding by using the page's declared charset when available.
- Ran a larger starter crawl:
  - 100 public documents collected.
  - 25 documents each from Supabase, Firebase, Vercel, and Render.
  - 681 RAG-ready chunks generated.
  - 100 raw HTML files saved under `data/public_docs/raw_html`.
- Confirmed all generated files are already inside:
  - `C:\Users\DELL\Documents\coding\Sem-8\RAG_project`

### Problems:
- The normal `python` command was not available in the Windows shell.
- Used the bundled Codex Python runtime instead:
  - `C:\Users\DELL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
- The first crawler run failed because sandboxed network access blocked outbound sockets.
- Re-ran the crawl with approved network access.
- Terminal preview showed some punctuation encoding artifacts, so the crawler was updated to respect each page's declared charset.
- The `git` command was not available directly in the shell path.

### Used Tools:
- Web search/browsing for current public source validation and pricing/docs pages.
- PowerShell shell commands for folder inspection, running scripts, and checking generated outputs.
- Bundled Codex Python runtime for crawling and chunking.
- `apply_patch` for creating and editing project files.
- `load_workspace_dependencies` to locate the bundled Python runtime.
- Network-enabled shell execution after approval for crawling public documentation.

## Entry 2 - 2026-07-11

### GOAL:
Start the RAG implementation and make sure the project supports a repeatable pipeline where newly added documents can be ingested, chunked, indexed, and retrieved.

### Progress:
- Added a `rag` Python package with reusable text cleaning, tokenization, HTML extraction, local document loading, and BM25 retrieval logic.
- Added local document ingestion through `scripts/ingest_local_documents.py`.
- Added corpus preparation through `scripts/prepare_rag_corpus.py`.
- Added retriever index creation through `scripts/build_bm25_index.py`.
- Added query testing through `scripts/query_rag.py`.
- Added one-command pipeline execution through `scripts/run_rag_pipeline.py`.
- Added `data/inbox` as the drop zone for new documents.
- Added a fictional sample document at `data/inbox/AcmeCloud/pricing_and_objections.md` to verify new-document ingestion.
- Updated `README.md` with the new RAG pipeline commands and supported file formats.
- Ran the complete pipeline successfully:
  - 1 local document ingested.
  - 101 total documents processed.
  - 682 chunks indexed.
- Queried the retriever with an AcmeCloud objection-handling question and confirmed the newly added local document was retrieved as the top source.

### Problems:
- Running scripts from the `scripts` folder initially caused a `ModuleNotFoundError` for the local `rag` package.
- Fixed the issue by adding the project root to `sys.path` in the scripts that import `rag`.
- The first retriever is lexical BM25, so it is useful for a free local baseline but not yet as semantically strong as Gemini embeddings or FAISS.

### Used Tools:
- PowerShell shell commands for running the pipeline and testing retrieval.
- Bundled Codex Python runtime.
- `apply_patch` for adding and updating project files.

## Entry 3 - 2026-07-11

### GOAL:
Add the answer-generation layer so DealDesk AI can turn retrieved chunks into cited business answers, while still working without an API key.

### Progress:
- Checked the current Gemini API text-generation documentation.
- Added `.env.example` for `GEMINI_API_KEY` and `GEMINI_MODEL`.
- Added lightweight `.env` loading in `rag/config.py`.
- Added DealDesk system instructions and grounded prompt construction in `rag/prompts.py`.
- Added Gemini REST API support in `rag/gemini.py`.
- Added answer orchestration, confidence labels, citations, and no-key fallback behavior in `rag/answer.py`.
- Added `scripts/ask_dealdesk.py` for end-to-end retrieval plus optional Gemini generation.
- Updated `README.md` with ask commands and API key setup.
- Updated the task checklist to mark generation, config, citations, confidence, fallback behavior, and DealDesk modes as complete.

### Problems:
- Gemini generation cannot be fully live-tested until the user provides a Google AI Studio Gemini API key.
- Network access may require approval when calling Gemini from this sandboxed environment.
- A live test with `gemini-2.5-flash-lite` reached the Gemini API, but Google returned a model availability error saying the model is no longer available to new users. The project default was changed to `gemini-3.1-flash-lite`, the next cheapest current option from the pricing table.

### Used Tools:
- Official Gemini API documentation.
- `apply_patch` for adding and updating project files.

## Entry 4 - 2026-07-11

### GOAL:
Move from a lexical-only RAG baseline to semantic retrieval with Gemini embeddings while keeping BM25 as a fallback and hybrid signal.

### Progress:
- Live-tested Gemini generation with the configured API key.
- Confirmed `gemini-2.5-flash-lite` is unavailable for this account/API path despite appearing in pricing docs.
- Successfully tested generated cited answers with `gemini-3.1-flash-lite`.
- Updated project defaults and `.env` model setting to `gemini-3.1-flash-lite`.
- Checked the official Gemini embeddings documentation.
- Added `rag/embeddings.py` for Gemini embedding API calls, retries, normalization, and cosine similarity.
- Added `rag/vector_index.py` for loading and querying a JSON vector index.
- Added `rag/retrievers.py` with hybrid BM25 + vector retrieval.
- Added `scripts/build_vector_index.py` to build a Gemini embedding index from `data/rag/chunks.jsonl`.
- Added `scripts/query_vector.py` to inspect semantic retrieval results.
- Updated `scripts/ask_dealdesk.py` with `--retriever bm25|hybrid`.
- Updated `scripts/run_rag_pipeline.py` with optional vector index building.
- Updated `README.md`, `.env.example`, and this task checklist.
- Built a 20-chunk vector index smoke test successfully.
- Queried the vector index and confirmed it retrieved relevant Supabase auth/database chunks.
- Tested the full hybrid RAG flow with Gemini generation using `--retriever hybrid`.

### Problems:
- `gemini-2.5-flash-lite` returned a live Gemini API 404 model availability error for this account.
- Full semantic indexing will require many embedding API calls, so the vector builder supports `--limit` for smoke tests and `--resume` for continuing safely.
- The current vector index is only a 20-chunk smoke-test index. Full semantic retrieval quality requires embedding the remaining corpus chunks.
- Attempting the full vector index hit Gemini embedding quota/rate limits at chunk 153 with HTTP 429. The saved vector index currently contains 150 embeddings and can be resumed later.
- Updated the vector builder to save immediately and exit cleanly on embedding API errors, especially quota/rate-limit errors.

### Used Tools:
- Official Gemini pricing and embeddings documentation.
- PowerShell shell commands for live Gemini testing.
- Network-enabled shell execution after approval for API calls.
- `apply_patch` for adding and updating project files.

## Entry 5 - 2026-07-11

### GOAL:
Add query filters by vendor, source type, and document category in the backend retriever to constrain searches.

### Progress:
- Updated `rag/bm25.py`, `rag/vector_index.py`, and `rag/retrievers.py` to allow query filtering using metadata attached to chunks.
- Updated `scripts/ask_dealdesk.py` to accept arguments like `--vendor` to seamlessly filter semantic bounds.

### Used Tools:
- Replaced file contents to adjust retrieving logic directly based on chunks' metadata (`chunk.get(key)`).

## Entry 6 - 2026-07-11

### GOAL:
Set up a FastAPI backend to expose the DealDesk RAG engine over HTTP APIs.

### Progress:
- Created a `requirements.txt` incorporating dependencies like `fastapi`, `uvicorn`, and `pydantic`.
- Built `api/main.py` configuring a `/api/ask` endpoint using the `AskRequest` / `AskResponse` schema validations.
- Hooked up `search`, `search_hybrid` and `generate_grounded_answer` from the `rag` module. 
- Bound CORS for local frontend communication.

### Used Tools:
- `write_to_file` to bootstrap the initial `api/main.py` scaffolding inline with `.cursorrules`.

## Entry 7 - 2026-07-11

### GOAL:
Scaffold the React + Vite frontend for DealDesk AI featuring a modern dark-mode glassmorphism interface.

### Progress:
- Used `create-vite` to initialize a React 18 frontend template natively in the `frontend/` directory.
- Created CSS variable foundations (`variables.css`) and global styling (`index.css`) for dark mode, glassmorphism, and gradient text natively adhering to `.cursorrules`.
- Configured Axios interactions in `services/api.js` explicitly targeting `http://localhost:8000/api/ask`.
- Built the main `ChatInterface.jsx` featuring dynamic request handling, dropdown selects for vendor/modes, automatic scrolling, and markdown-like citation anchors.

### Used Tools:
- Scaffolded using native `run_command` Node CLI tooling.
- Populated structural components with `write_to_file` spanning layouts, styles, and data-fetching.

## Entry 8 - 2026-07-11

### GOAL:
Introduce Frontend document uploads that automatically trigger pipeline processing, mapping correctly into a Vercel-ready environment.

### Progress:
- Appended `python-multipart` and `mangum` to `requirements.txt` to cover Vercel Serverless architectures and file uploads.
- Modified `api/main.py` with an `/api/upload` endpoint: 
  - Conditionally saves local parsing documents into `/tmp` (Vercel) or `data/inbox` (Local).
  - Conditionally triggers the entire RAG pipeline (`run_rag_pipeline.py`) directly from Python using `subprocess.run()`.
  - Added the `handler = Mangum(app)` adapter at the root.
- Modified `ChatInterface.jsx` and added an aesthetic file upload interaction directly in the frontend header.
- Forged `vercel.json` root definition to bind Serverless builder to the `api/main.py` and Vite Builder to `frontend`.

### Used Tools:
- Replaced contents in the Frontend logic via `multi_replace_file_content` to gracefully incorporate uploading states and UI.

## Entry 9 - 2026-07-11

### GOAL:
Introduce Pytest automated regression testing covering semantic pipelines.

### Progress:
- Setup a `tests/test_rag.py` scaffold isolating core unit-tests!
- Included `test_chunk_text` accurately inspecting token offsets and overlap logic handling.
- Integrated `test_bm25_build_and_search` mapping the local search index and evaluating conditional filter flags directly.
- Added `pytest` dependencies to `requirements.txt`.
- Checked off Retrieval checks and Semantic testing trackers!

### Used Tools:
- Generated native structures leveraging `.cursorrules` structure matching through `write_to_file`.

## Entry 10 - 2026-07-11

### GOAL:
Finalize deployment scaling components including Docker configuration, Chat History Analytics tables, and polished README artifacts for portfolio display!

### Progress:
- Configured a local persistent Sqlite3 DB natively inside `api/database.py` capturing all metrics implicitly per query.
- Pushed thumbs-up/down interaction points into `ChatInterface.jsx` hitting the newly exposed `/api/feedback` parameter.
- Bundled complete portability with `Dockerfile` mapping Uvicorn, and `docker-compose.yml` natively mounting Vite and Python across synced volumes for frictionless local execution!
- Polished up README with bullet points to assist rendering on GitHub portfolios!

### Used Tools:
- Automated the remaining structure using precise file writers and Docker syntaxes.
