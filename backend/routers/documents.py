"""
Documents router — handles upload, list, detail, and delete endpoints.
All endpoints require a valid JWT; documents are scoped per user.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from config import settings
from dependencies import get_current_user
from models.schemas import DocumentBase, DocumentDetail, DocumentList, UploadResponse
from services import document_registry as registry
from services.pdf_extractor import extract_text, image_to_pdf, SUPPORTED_IMAGE_EXTENSIONS
from services.rag_service import build_index, delete_index

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ACCEPTED_EXTENSIONS = frozenset({".pdf"}) | SUPPORTED_IMAGE_EXTENSIONS

# Ensure upload dir exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a PDF or image, extract text, and build the RAG index.
    The document is tagged with the authenticated user's ID.
    """
    # ── Validate ──────────────────────────────────────────────────────────────
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")

    original_ext = Path(file.filename).suffix.lower()
    if original_ext not in ACCEPTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. Accepted formats: "
                "PDF, PNG, JPG, JPEG, TIFF, WEBP, BMP."
            ),
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {MAX_FILE_SIZE_MB} MB size limit.",
        )

    # ── Save raw file ─────────────────────────────────────────────────────────
    doc_id = str(uuid.uuid4())
    is_image_upload = original_ext in SUPPORTED_IMAGE_EXTENSIONS

    if is_image_upload:
        tmp_img_path = settings.UPLOAD_DIR / f"{doc_id}{original_ext}"
        tmp_img_path.write_bytes(content)

        try:
            pdf_bytes = image_to_pdf(tmp_img_path)
        except Exception as exc:
            tmp_img_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=422,
                detail=f"Could not convert image to PDF: {exc}",
            )
        finally:
            tmp_img_path.unlink(missing_ok=True)

        display_name = Path(file.filename).stem + ".pdf"
        safe_name = f"{doc_id}.pdf"
        save_path = settings.UPLOAD_DIR / safe_name
        save_path.write_bytes(pdf_bytes)
    else:
        display_name = file.filename
        safe_name = f"{doc_id}.pdf"
        save_path = settings.UPLOAD_DIR / safe_name
        save_path.write_bytes(content)

    # ── Register document (status=processing) ─────────────────────────────────
    doc_entry = registry.create_document(
        filename=safe_name,
        original_name=display_name,
        file_size_bytes=len(content),
        doc_id=doc_id,
        user_id=current_user["id"],
    )

    # ── Extract text ──────────────────────────────────────────────────────────
    try:
        result = extract_text(save_path)
    except Exception as exc:
        registry.update_document(doc_id, status="error", error_message=str(exc))
        doc_entry = registry.get_document(doc_id)
        return UploadResponse(
            message=f"Text extraction failed: {exc}",
            document=DocumentBase(**doc_entry),
        )

    if result.error:
        registry.update_document(doc_id, status="error", error_message=result.error)
        doc_entry = registry.get_document(doc_id)
        return UploadResponse(
            message=f"Upload succeeded but text extraction failed: {result.error}",
            document=DocumentBase(**doc_entry),
        )

    # ── Build FAISS index ─────────────────────────────────────────────────────
    try:
        build_index(doc_id, result.pages)
        registry.update_document(
            doc_id,
            page_count=result.page_count,
            status="ready",
            ocr_applied=result.ocr_applied,
            scanned_pages=result.scanned_pages,
        )
    except Exception as exc:
        registry.update_document(doc_id, status="error", error_message=str(exc))
        doc_entry = registry.get_document(doc_id)
        return UploadResponse(
            message=f"Text extracted but indexing failed: {exc}",
            document=DocumentBase(**doc_entry),
        )

    doc_entry = registry.get_document(doc_id)
    return UploadResponse(
        message="Document uploaded, extracted, and indexed successfully.",
        document=DocumentBase(**doc_entry),
    )


@router.get("", response_model=DocumentList)
def list_documents(current_user: dict = Depends(get_current_user)):
    """Return documents owned by the authenticated user, newest first."""
    docs = registry.list_documents_for_user(current_user["id"])
    return DocumentList(
        documents=[DocumentBase(**d) for d in docs],
        total=len(docs),
    )


def _assert_owner(doc_id: str, user_id: str) -> dict:
    """Load document, raise 404 if missing, 403 if owned by someone else."""
    doc = registry.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.get("user_id") != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to access this document.",
        )
    return doc


@router.get("/{doc_id}", response_model=DocumentDetail)
def get_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Return document metadata plus a short text preview."""
    doc = _assert_owner(doc_id, current_user["id"])

    text_preview: str | None = None
    pdf_path = settings.UPLOAD_DIR / doc["filename"]
    if pdf_path.exists() and doc["status"] == "ready":
        result = extract_text(pdf_path)
        if result.pages:
            combined = " ".join(p.text for p in result.pages[:2])
            text_preview = combined[:600] + ("…" if len(combined) > 600 else "")

    return DocumentDetail(**doc, text_preview=text_preview)


@router.delete("/{doc_id}", status_code=200)
def delete_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a document: registry entry, PDF file, and FAISS index."""
    doc = _assert_owner(doc_id, current_user["id"])

    # Remove PDF
    pdf_path = settings.UPLOAD_DIR / doc["filename"]
    if pdf_path.exists():
        pdf_path.unlink()

    # Remove FAISS index
    delete_index(doc_id)

    # Remove registry entry
    registry.delete_document(doc_id)

    return {"message": "Document deleted successfully.", "id": doc_id}
