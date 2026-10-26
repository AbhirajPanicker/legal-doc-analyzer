# LexAnalyzer — RAG-Based Legal Document Analyzer
### Intelligent Legal Document Analysis, Risk Detection & Q&A

> **Disclaimer:** This tool is intended for informational and research purposes. It is not a substitute for formal legal counsel.

---

## What This Does

LexAnalyzer lets you upload text-based legal PDFs (contracts, agreements, legal notices, property documents) and ask plain-language questions about their contents. Answers are grounded in the actual document — the system will tell you if it cannot find enough information.

**Technology stack:**
- **Frontend:** React 18 + Vite + Vanilla CSS design system
- **Backend:** Python 3.10+ · FastAPI · Uvicorn
- **PDF extraction:** PyMuPDF (fitz)
- **Embeddings:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key)
- **Vector store:** FAISS (local, on-disk) — modular for pgvector migration
- **LLM:** Google Gemini or OpenAI (configured via `.env`)
- **RAG framework:** LangChain

---

## Project Structure

```
Legal Document Analyzer/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings loaded from .env
│   ├── routers/
│   │   ├── documents.py         # Upload, list, detail, delete endpoints
│   │   ├── chat.py              # Q&A endpoint
│   │   ├── summarise.py         # Executive summary endpoint
│   │   └── clauses.py           # Clause & risk detection endpoint
│   ├── services/
│   │   ├── pdf_extractor.py     # PyMuPDF text extraction
│   │   ├── rag_service.py       # FAISS indexing + LangChain Q&A
│   │   ├── document_registry.py # JSON-file metadata store
│   │   ├── summarise_service.py # Executive summarisation service
│   │   └── clause_service.py    # Clause & risk assessment engine
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── uploads/                 # Uploaded PDF files (gitignored)
│   ├── vector_store/            # FAISS index files (gitignored)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/          # Sidebar, DocumentCard, UploadZone, StatusBanner
    │   ├── pages/               # Dashboard, Documents, Summarise, ClauseAnalysis, Chat
    │   ├── services/api.js      # Axios API client
    │   ├── App.jsx
    │   └── index.css            # Design system
    ├── index.html
    └── vite.config.js
```

---

## Setup & Running

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- A Google Gemini or OpenAI API key

---

### 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate

# Install dependencies (first run downloads the embedding model ~90 MB)
pip install -r requirements.txt

# Configure environment
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

# Edit .env and set your API key:
#   LLM_PROVIDER=google
#   GOOGLE_API_KEY=your_actual_key_here

# Start the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

---

### 2. Frontend Setup

Open a **new terminal window:**

```bash
cd frontend
npm install
npm run dev
```

The app will be available at **http://localhost:5173**

---

### 3. Getting a Free Google Gemini API Key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with a Google account
3. Click **Create API key**
4. Copy the key into `backend/.env` as `GOOGLE_API_KEY=...`
5. Restart the backend

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check + LLM status |
| `GET` | `/api/v1/status` | LLM configuration status |
| `POST` | `/api/v1/documents/upload` | Upload a PDF |
| `GET` | `/api/v1/documents` | List all documents |
| `GET` | `/api/v1/documents/{id}` | Document detail + text preview |
| `DELETE` | `/api/v1/documents/{id}` | Delete document + index |
| `POST` | `/api/v1/chat/{doc_id}` | Ask a question about a document |
| `POST` | `/api/v1/summarise/{doc_id}` | Generate structured executive summary |
| `POST` | `/api/v1/clauses/{doc_id}` | Detect legal clauses & assess contract risks |

---

## Features

- ✅ **Smart Document Ingestion** — PDF upload and auto-OCR for scanned documents/images (Tesseract OCR fallback)
- ✅ **FAISS Semantic Vector Indexing** — local sentence-transformers embeddings (`all-MiniLM-L6-v2`)
- ✅ **Grounded RAG Q&A** — plain-language questions answered with precise source citations & page references
- ✅ **Clause & Risk Detection** — identifies key legal clauses, flags missing protections, and calculates overall risk scores
- ✅ **Executive Summarisation** — structured briefings covering parties, dates, obligations, and financial terms
- ✅ **User Authentication & Multi-Tenancy** — JWT-based authentication with secure per-user document isolation
- ✅ **Report Export** — one-click Markdown and print-ready PDF export
- ✅ **Document Chat History** — conversation history saved with quick reset controls

---

## System Notes

| Item | Notes |
|---|---|
| Document Registry | JSON-file metadata store (`document_registry.json`) |
| Embeddings | `sentence-transformers` downloads ~90 MB model on first run |
| Storage | Vector index stored locally in `backend/vector_store/` |

---

## Troubleshooting

**Backend won't start:**
- Ensure the virtual environment is activated
- Check Python version: `python --version` (needs 3.10+)

**"LLM not configured" banner:**
- Copy `.env.example` to `.env` and add your API key
- Restart the backend with `uvicorn main:app --reload`

**Upload fails with "No extractable text":**
- Check that Tesseract OCR is installed and available if uploading scanned images or image-based PDFs.

**Frontend shows blank page:**
- Make sure the backend is running on port 8000
- Check browser console for errors

---

*LexAnalyzer — Intelligent Legal Document Understanding Platform.*
