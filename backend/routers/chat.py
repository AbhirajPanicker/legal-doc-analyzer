"""
Chat router — handles question answering for a specific document.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from config import settings
from dependencies import get_current_user
from models.schemas import AnswerResponse, QuestionRequest, SourceReference
from services import document_registry as registry
from services.rag_service import query_document

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{doc_id}", response_model=AnswerResponse)
def ask_question(
    doc_id: str,
    body: QuestionRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Ask a question about a specific uploaded document.
    Only the document owner may query it.
    """
    doc = registry.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to query this document.",
        )

    if doc["status"] != "ready":
        raise HTTPException(
            status_code=422,
            detail=f"Document is not ready for questions (status: {doc['status']}).",
        )

    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if len(question) > 2000:
        raise HTTPException(status_code=400, detail="Question is too long (max 2000 characters).")

    result = query_document(doc_id, question, eli5=body.eli5)

    return AnswerResponse(
        answer=result["answer"],
        sources=[SourceReference(**s) for s in result["sources"]],
        document_id=doc_id,
        llm_configured=settings.llm_configured,
        eli5=body.eli5,
    )
