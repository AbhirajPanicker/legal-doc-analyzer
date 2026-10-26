"""
FastAPI application entry point for the Legal Document Analyzer backend.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import auth, documents, chat, summarise, clauses, blind_spots, eli5

app = FastAPI(
    title="Legal Document Analyzer API",
    description=(
        "RAG-based API for uploading legal PDFs, extracting text, "
        "and answering questions grounded in document content."
    ),
    version="1.1.0-auth",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "https://legal-doc-analyzer-gray.vercel.app,http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(summarise.router, prefix="/api/v1")
app.include_router(clauses.router, prefix="/api/v1")
app.include_router(blind_spots.router, prefix="/api/v1")
app.include_router(eli5.router, prefix="/api/v1")


# ── Health / status ────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def root():
    return {
        "service": "Legal Document Analyzer API",
        "version": "1.1.0-auth",
        "status": "running",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": settings.llm_configured,
        "ocr_available": settings.ocr_available,
        "ocr_enabled": settings.OCR_ENABLED,
        "docs": "/docs",
    }


@app.get("/healthz", tags=["health"])
def healthz():
    """Standard health check endpoint for cloud platforms like Render / Kubernetes."""
    return {"status": "ok"}


@app.get("/api/v1/status", tags=["health"])
def api_status():
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": settings.llm_configured,
        "embedding_model": settings.EMBEDDING_MODEL,
        "ocr_available": settings.ocr_available,
        "ocr_enabled": settings.OCR_ENABLED,
    }
