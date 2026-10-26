"""
Clauses router — triggers clause detection and risk analysis for a document.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user
from models.schemas import ClauseAnalysisResponse
from services import document_registry as registry
from services.clause_service import analyse_clauses

router = APIRouter(prefix="/clauses", tags=["clauses"])


@router.post("/{doc_id}", response_model=ClauseAnalysisResponse)
def analyse_document_clauses(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Run clause detection and risk analysis on a specific document.
    Only the document owner may trigger this.
    """
    doc = registry.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to analyse this document.",
        )

    if doc["status"] != "ready":
        raise HTTPException(
            status_code=422,
            detail=f"Document is not ready for analysis (status: {doc['status']}).",
        )

    try:
        result = analyse_clauses(doc_id)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Clause analysis failed: {exc}")
