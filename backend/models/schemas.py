"""
Pydantic models (schemas) used for API request / response bodies.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ─── Document schemas ──────────────────────────────────────────────────────────

class DocumentBase(BaseModel):
    id: str
    filename: str
    original_name: str
    upload_time: datetime
    page_count: int
    file_size_bytes: int
    status: str          # "processing" | "ready" | "error"
    error_message: Optional[str] = None
    ocr_applied: bool = False
    scanned_pages: list[int] = []

    model_config = {"from_attributes": True}


class DocumentList(BaseModel):
    documents: list[DocumentBase]
    total: int


class DocumentDetail(DocumentBase):
    """Full document info including extracted text preview."""
    text_preview: Optional[str] = None   # first ~500 chars of extracted text


# ─── Chat / QA schemas ─────────────────────────────────────────────────────────

class SourceReference(BaseModel):
    page: int
    snippet: str


class QuestionRequest(BaseModel):
    question: str
    eli5: bool = False


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    document_id: str
    llm_configured: bool
    eli5: bool = False


# ─── Upload response ───────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    message: str
    document: DocumentBase


# ─── Summarisation schemas ───────────────────────────────────────────────────

class SummaryParty(BaseModel):
    role: str
    name: str


class SummaryDate(BaseModel):
    label: str
    date: str


class SummaryFinancialTerm(BaseModel):
    label: str
    value: str


class SummaryRiskFlag(BaseModel):
    severity: str   # "high" | "medium" | "low"
    description: str


class SummaryResponse(BaseModel):
    document_id: str
    document_type: Optional[str] = None
    parties: list[SummaryParty] = []
    key_dates: list[SummaryDate] = []
    obligations: list[str] = []
    financial_terms: list[SummaryFinancialTerm] = []
    risk_flags: list[SummaryRiskFlag] = []
    governing_law: Optional[str] = None
    termination_conditions: Optional[str] = None
    one_line_summary: Optional[str] = None
    llm_configured: bool = False
    llm_used: bool = False       # True only when LLM actually generated the response


# ─── Clause / Risk Detection schemas ──────────────────────────────────────────

class ClauseItem(BaseModel):
    clause_id: str
    clause_name: str
    icon: str
    missing: bool = False
    risk: str            # "high" | "medium" | "low"
    description: str
    text_excerpt: Optional[str] = None
    standard_note: Optional[str] = None


class ClauseAnalysisResponse(BaseModel):
    document_id: str
    overall_risk: str    # "high" | "medium" | "low"
    detected_clauses: list[ClauseItem] = []
    missing_clauses: list[ClauseItem] = []
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_clauses_found: int
    total_clauses_missing: int
    llm_configured: bool = False
    llm_used: bool = False
    analysis_note: Optional[str] = None



# --- Auth schemas ---

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = ''


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime
    is_active: bool

    model_config = {'from_attributes': True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserOut



# --- Blind-Spot Detector schemas ---

class BlindSpotFinding(BaseModel):
    id: str
    gap_type: str
    category: str
    severity: str
    title: str
    explanation: str
    evidence: str
    page_number: Optional[int] = None
    human_review_question: str


class BlindSpotResponse(BaseModel):
    document_id: str
    total_findings: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    categories_summary: dict[str, int] = {}
    findings: list[BlindSpotFinding] = []
    executive_takeaway: str
    has_gaps: bool = True
    evidence_sufficient: bool = True
    llm_configured: bool = False
    llm_used: bool = False
    disclaimer: str = (
        "All findings are preliminary automated observations and do not constitute formal legal counsel. "
        "Human legal review by qualified counsel is required."
    )
