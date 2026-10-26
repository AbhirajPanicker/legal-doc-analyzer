"""
Blind-Spots router — triggers Contract Blind-Spot Detection for a document.
POST /api/v1/blind-spots/{doc_id}
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user
from models.schemas import BlindSpotResponse
from services import document_registry as registry
from services.blind_spot_service import detect_blind_spots

router = APIRouter(prefix="/blind-spots", tags=["blind-spots"])


@router.post("/{doc_id}", response_model=BlindSpotResponse)
def analyse_document_blind_spots(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Run Contract Blind-Spot Detection on a specific document.
    Only the document owner or authorized user may trigger this.
    """
    doc = registry.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to audit this document.",
        )

    if doc["status"] != "ready":
        raise HTTPException(
            status_code=422,
            detail=f"Document is not ready for analysis (status: {doc['status']}).",
        )

    try:
        result = detect_blind_spots(doc_id)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Blind-spot analysis failed: {exc}")
