import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import json
import os
import subprocess
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from mangum import Mangum

from rag.answer import generate_grounded_answer
from rag.bm25 import search
from rag.retrievers import search_hybrid
from api.database import log_chat, update_feedback

app = FastAPI(title="DealDesk AI API", description="RAG-powered SaaS sales backend")

# Enable CORS for the frontend React/Vite app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, change to the specific frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BM25_INDEX_PATH = "data/index/bm25_index.json"
VECTOR_INDEX_PATH = "data/index/vector_index.json"

bm25_index_cache = None

def get_bm25_index():
    global bm25_index_cache
    if bm25_index_cache is None:
        try:
            with open(BM25_INDEX_PATH, "r", encoding="utf-8") as src:
                bm25_index_cache = json.load(src)
        except Exception as e:
            print(f"Warning: Index not loaded. Error: {e}")
            bm25_index_cache = {"documents": [], "idf": {}}
    return bm25_index_cache


class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    retriever: str = "hybrid"  # "hybrid" or "bm25"
    mode: str = "qa" # qa, compare, objection, email, recommend
    vendor: Optional[str] = None
    use_gemini: bool = True

class Citation(BaseModel):
    id: int
    vendor: str
    title: str
    source_url: str
    score: float

class AskResponse(BaseModel):
    answer: str
    confidence: str
    warning: Optional[str] = None
    citations: List[Citation]
    log_id: int

class FeedbackRequest(BaseModel):
    log_id: int
    feedback: int # 1 for positive, -1 for negative

@app.post("/api/ask", response_model=AskResponse)
def ask_dealdesk(request: AskRequest):
    index = get_bm25_index()
    
    filters = {}
    if request.vendor:
        filters["vendor"] = request.vendor
        
    try:
        if request.retriever == "hybrid":
            results = search_hybrid(index, VECTOR_INDEX_PATH, request.question, top_k=request.top_k, filters=filters)
        else:
            results = search(index, request.question, top_k=request.top_k, filters=filters)
            
        payload = generate_grounded_answer(
            request.question,
            results,
            mode=request.mode,
            use_gemini=request.use_gemini,
        )
        
        # Log to local/sqlite DB
        log_id = log_chat(request.question, request.vendor, request.mode, payload["confidence"], payload["answer"])
        payload["log_id"] = log_id
        
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest):
    try:
        update_feedback(req.log_id, req.feedback)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), vendor: str = Form("Custom")):
    try:
        # Vercel checks: Vercel's root filesystem is read-only, except /tmp
        # But we default to local dev path 'data/inbox' if available
        inbox_dir = Path(ROOT) / "data" / "inbox"
        if not os.environ.get("VERCEL"):
            inbox_dir.mkdir(parents=True, exist_ok=True)
            file_path = inbox_dir / file.filename
        else:
            inbox_dir = Path("/tmp")
            file_path = inbox_dir / file.filename
            
        with open(file_path, "wb") as f:
            f.write(await file.read())
            
        # Trigger the pipeline if local (Vercel would fail trying to write to data/index unless we map it to /tmp)
        if not os.environ.get("VERCEL"):
            run_rag_script = ROOT / "scripts" / "run_rag_pipeline.py"
            subprocess.run([sys.executable, str(run_rag_script), "--source-dir", str(inbox_dir), "--vendor", vendor], check=True)
            
            # Reset cache so index reflects new uploaded doc
            global bm25_index_cache
            bm25_index_cache = None
            
        return {"message": "Document uploaded and pipeline triggered successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Vercel Serverless Hook
handler = Mangum(app)
