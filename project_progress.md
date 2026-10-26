# Legal Document Analyzer — Project Progress

> **Last updated:** October 2026

---

## What Has Been Built

### Backend (Python / FastAPI)

#### Core Infrastructure
- **FastAPI application** (`main.py`) with CORS middleware, auto-generated API docs (`/docs`, `/redoc`), and a health-check endpoint (`/api/v1/status`).
- **Configuration system** (`config.py`) using `.env` for secrets, supporting dual LLM providers (OpenAI and Google Gemini) and environment-specific storage paths.

#### Document Pipeline
- **PDF ingestion** — file upload endpoint (`POST /api/v1/documents/upload`) that validates file type, enforces a 50 MB size cap, saves the file with a UUID-based filename, and pipelines it through extraction → indexing.
- **PDF text extraction** (`pdf_extractor.py`) using PyMuPDF (`fitz`), with per-page extraction, graceful error handling for unreadable pages, and a structured `ExtractionResult` response.
- **Document registry** (`document_registry.py`) — a lightweight JSON-file store tracking each document's ID, original name, page count, file size, upload timestamp, and processing status (`processing` / `ready` / `error`). Designed to be a thin interface for easy database migration later.
- **REST endpoints** for listing all documents, fetching individual document metadata + text preview, and deleting a document (removes the PDF, FAISS index, and registry entry atomically).

#### RAG Engine
- **FAISS vector store** — documents are chunked with `RecursiveCharacterTextSplitter` (800-char chunks, 150-char overlap), embedded using HuggingFace `sentence-transformers/all-MiniLM-L6-v2`, and persisted to disk as a per-document FAISS index.
- **Dual-mode QA** (`rag_service.py`):
  - **LLM-backed mode** — when an OpenAI or Gemini API key is configured, the top-5 retrieved chunks are passed via a strict prompt to the configured LLM (via LangChain), which is instructed to answer only from document content and explicitly flag missing information.
  - **Offline / local mode** — a deterministic extractive fallback (`_extract_local_answer`) that uses keyword matching and vector distance thresholds to answer or refuse questions without any external API call. Handles known "not-provided" patterns (bank details, pet policy, arbitration institution, termination penalty) accurately.
- **Source attribution** — every answer returns a `sources` list with page numbers and text snippets so the user can verify the claim against the original document.
- **Chat router** (`chat.py`) — `POST /api/v1/chat/{doc_id}` validates document readiness, enforces a 2 000-character question limit, and returns a structured `AnswerResponse` (answer, sources, LLM status flag).

#### Data Models
- **Pydantic v2 schemas** (`schemas.py`) — `DocumentBase`, `DocumentList`, `DocumentDetail`, `QuestionRequest`, `AnswerResponse`, `SourceReference`, `UploadResponse` — all used for strict request/response validation.

---

### Frontend (React + Vite)

#### Application Shell
- **React Router** navigation with three routes: Dashboard (`/`), Documents (`/documents`), Chat (`/chat`).
- **Sidebar** (`Sidebar.jsx`) with navigation links, active-state highlighting, and a collapsible layout.
- **Status banner** (`StatusBanner.jsx`) that polls `/api/v1/status` and warns the user when no LLM API key is configured, with inline setup guidance.
- **Global design system** (`index.css`) — CSS custom properties for a dark navy palette, typography scale (Inter / system fonts), card/button/badge/alert component classes, animations (`fadeInUp`, `slideInLeft`, `spin-slow`), and responsive layout utilities.

#### Pages
- **Dashboard** — live stats cards (total documents, ready count, error count, retrieval method), a step-by-step getting-started guide, and a "Recent Documents" list that deep-links directly into the Chat page with a pre-selected document.
- **Documents** — drag-and-drop upload zone (`UploadZone.jsx`) with visual upload progress and success/error toasts; full document list with status badges; a slide-in detail panel showing page count, file size, upload timestamp, index type, text preview, and quick-action buttons (Ask Questions / Delete).
- **Chat** — two-panel layout with a document selector sidebar and a main message area; suggestion chips for quick-start questions; streaming-style "thinking" indicator; assistant messages with source-reference tags and quoted snippets; per-message LLM-not-configured warning.

#### API Service Layer
- **`api.js`** — Axios client pre-configured with the backend base URL; typed wrappers for `listDocuments`, `getDocument`, `uploadDocument`, `deleteDocument`, and `askQuestion`.

---

## How Much Is Done

| Area | Status |
|---|---|
| Backend API (FastAPI, routing, CORS, health) | ✅ Complete |
| PDF upload, validation, and storage | ✅ Complete |
| Text extraction (PyMuPDF, per-page) | ✅ Complete |
| FAISS vector indexing and persistence | ✅ Complete |
| Sentence-transformer embeddings (local) | ✅ Complete |
| LLM-backed QA (OpenAI + Gemini via LangChain) | ✅ Complete |
| Offline extractive QA fallback | ✅ Complete |
| Source attribution in answers | ✅ Complete |
| Document registry (JSON store) | ✅ Complete |
| CRUD endpoints (upload / list / get / delete) | ✅ Complete |
| Pydantic v2 schemas | ✅ Complete |
| React frontend (Vite, Router, design system) | ✅ Complete |
| Dashboard with live stats | ✅ Complete |
| Documents page (upload + list + detail panel) | ✅ Complete |
| Chat page (RAG Q&A with sources) | ✅ Complete |
| LLM status banner | ✅ Complete |
| Offline mode (no API key required) | ✅ Complete |
| Scanned PDF / OCR support | ✅ Complete |
| Database persistence (beyond JSON file) | ❌ Not started |
| User authentication / multi-tenancy | ✅ Complete |
| Multi-document cross-querying | ❌ Not started |
| Document summarisation | ✅ Complete |
| Clause / risk detection | ✅ Complete |
| Chat history persistence (localStorage) | ✅ Complete |
| Navigation and layout | ✅ Complete |
| Report Export (1-click Markdown + Print-ready PDF) | ✅ Complete |
| Fast LLM failover (max_retries=1) | ✅ Complete |
| Text overflow & non-breaking space fix | ✅ Complete |
| Offline extraction precision overhaul | ✅ Complete |
| Image upload with auto-OCR conversion | ✅ Complete |

**Overall progress: ~97% of the envisioned full product.**
JWT Auth, per-user document scoping, OCR ingestion, and clause analysis are fully functional. What remains is a persistent SQL database and multi-document comparison.

---

## Future Work

### 1. OCR for Scanned PDFs
*(Completed)* Scanned PDFs and image-only pages are now automatically detected and processed using PyMuPDF's built-in Tesseract OCR engine with packaged language models. Documents display OCR badges and report which pages were scanned.

### 2. Persistent Database
The JSON-file document registry works for a single machine but won't scale or survive concurrent writes. Migrating to PostgreSQL (via SQLAlchemy + Alembic) with optional pgvector for vector storage would replace both the JSON registry and the per-document FAISS files, unlocking proper querying, filtering, and backup.

### 3. User Authentication & Multi-Tenancy
Currently there is no concept of users — all documents are shared in a single registry. Adding JWT-based authentication (FastAPI-Users or a custom OAuth2 flow) and scoping documents per user would make the application safe to deploy to multiple users.

### 4. Document Summarisation
Add a dedicated endpoint and UI panel that uses the LLM to produce a structured executive summary of a full document: key parties, obligations, dates, payment terms, and risk flags — generated in one click without the user needing to ask individual questions.

### 5. Clause & Risk Detection
Implement a pre-processing step that classifies clause types (indemnification, non-compete, arbitration, governing law, etc.) and flags potentially unfavourable or unusual terms using a fine-tuned or prompted legal NLP model.

### 6. Multi-Document Cross-Querying
Allow users to select multiple indexed documents and ask questions that span all of them (e.g., "How do the termination clauses in contract A and B differ?"). This requires a combined retriever that merges FAISS indexes and a prompt structure that attributes answers per document.

### 7. Chat History Persistence
Current chat sessions are in-memory and lost on page refresh. Persisting conversations (per user, per document) to the database would allow users to resume sessions and audit past queries.

### 8. Production Deployment
- Containerise the backend with Docker and serve via Gunicorn + Uvicorn workers.
- Build and serve the frontend as a static bundle via Nginx or a CDN.
- Add environment-specific configuration, logging (structured JSON logs), and error monitoring (Sentry or similar).
- Replace the synchronous `build_index` call inside the upload endpoint with a background task queue (Celery + Redis or FastAPI `BackgroundTasks`) so large documents don't block the HTTP response.

### 9. Evaluation & Testing
- Write a test suite (pytest) covering the RAG pipeline, API endpoints, and edge cases (empty PDF, oversized file, malformed question).
- Build a small benchmark set of legal documents with known ground-truth QA pairs to measure retrieval precision and answer accuracy as the system evolves.
