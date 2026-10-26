"""
Summarisation router — POST /api/v1/summarise/{doc_id}
Returns a structured executive summary of the specified legal document.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from config import settings
from dependencies import get_current_user
from models.schemas import SummaryResponse
from services import document_registry as registry
from services.summarise_service import summarise_document

router = APIRouter(prefix="/summarise", tags=["summarise"])


@router.post("/{doc_id}", response_model=SummaryResponse)
def summarise(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a structured executive summary for a ready document.
    Only the document owner may request this.
    """
    doc = registry.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to summarise this document.",
        )

    if doc["status"] != "ready":
        raise HTTPException(
            status_code=422,
            detail=f"Document is not ready for summarisation (status: {doc['status']}).",
        )

    try:
        data = summarise_document(doc_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summarisation failed: {exc}")

    # llm_used comes from the service (True only if LLM actually responded)
    # llm_configured reflects whether a key is present in .env
    llm_used = data.pop("llm_used", False)
    return SummaryResponse(
        document_id=doc_id,
        llm_configured=settings.llm_configured,
        llm_used=llm_used,
        **{k: v for k, v in data.items() if k not in ("document_id", "llm_configured", "llm_used")},
    )
