"""
ELI5 (Explain Like I'm 5) Router — Plain-English Legal Jargon Decoder
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dependencies import get_current_user
from services.eli5_service import decode_legal_jargon, get_preset_terms

router = APIRouter(prefix="/eli5", tags=["eli5"])

class DecodeRequest(BaseModel):
    text: str

class ELI5Response(BaseModel):
    term: str
    category: str
    plain_english: str
    real_life_analogy: str
    why_it_matters: str
    hidden_trap: str
    snippet_matched: str | None = None

@router.get("/presets")
def list_presets():
    """List common legal terms available in the ELI5 database."""
    return {"presets": get_preset_terms()}

@router.post("/decode", response_model=ELI5Response)
def decode_text(
    body: DecodeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Translates any legal term, phrase, or clause snippet into crystal-clear
    plain English with real-life analogies and negotiation tips.
    """
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if len(text) > 4000:
        raise HTTPException(status_code=400, detail="Text is too long (max 4000 chars).")

    result = decode_legal_jargon(text)
    return ELI5Response(**result)
