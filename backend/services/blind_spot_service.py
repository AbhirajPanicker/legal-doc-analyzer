"""
Contract Blind-Spot Detector Service.

Analyzes an indexed legal document to identify:
- Potential missing terms & protective gaps
- Ambiguous wording & undefined standards
- References to missing exhibits / attachments / placeholders
- Incomplete obligations & missing consequences for non-compliance
- Unresolved contingencies & unanswered contractual assumptions

Works in both LLM mode (Groq / Gemini / OpenAI via LangChain) and deterministic
offline fallback mode.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from config import settings
from services.pdf_extractor import extract_text, PageContent


# ── LLM Prompt ────────────────────────────────────────────────────────────────

_BLIND_SPOT_PROMPT = """You are a senior legal audit counsel and partner specializing in contract risk analysis.
Carefully inspect the legal agreement provided below (with explicit page markers).

Analyze the document to detect:
1. POTENTIAL GAPS:
   - Missing standard protective terms (e.g., liability caps, mutual indemnification boundaries, notice & cure periods, confidentiality exclusions, termination consequences, audit rights).
   - Missing consequences for non-compliance (an obligation is created, but no remedy, interest, or breach effect is stated).
2. AMBIGUITY:
   - Subjective standards of care ("best efforts", "commercially reasonable efforts", "reasonable endeavors") without objective benchmarks or expenditure limits.
   - Vague timelines ("from time to time", "promptly", "as soon as practicable", "reasonable notice", "timely manner") lacking calendar or business day definitions.
   - Unilateral discretion ("sole discretion", "absolute discretion") without reasonableness standards.
   - Undefined materiality thresholds ("material breach", "material adverse effect").
3. MISSING REFERENCES:
   - Citations to Exhibits, Schedules, Annexures, Appendices, or Statements of Work (SOWs) that are referenced in clauses but omitted, blank, or placeholder-only.
   - Drafting placeholders like [TBD], [INSERT...], blanks, or undefined schedules.
4. NEEDS HUMAN REVIEW:
   - Undefined capitalized terms used in operative obligations.
   - Incomplete obligations (promises without clear obligor, timeline, or scope).
   - Unresolved contingencies ("subject to mutual agreement", "to be negotiated in good faith", "pending board approval").
   - Unanswered questions and assumptions the agreement leaves open.

GROUNDING & INTEGRITY RULES:
- Only cite findings with genuine evidence from the text or genuine document-wide omissions.
- For every finding, provide the exact `evidence` quote and the exact `page_number` from the page marker where it occurs.
- If a finding is a document-wide omission (e.g. entire agreement lacks a liability cap), set `page_number` to null and set `evidence` to the closest related clause or state "[Document-wide omission]".
- Formulate a targeted, actionable `human_review_question` for legal counsel or negotiation teams.
- Categorize each finding into EXACTLY ONE of:
  - "Potential Gap"
  - "Ambiguity"
  - "Missing Reference"
  - "Needs Human Review"
- Assign severity: "High" | "Medium" | "Low".
- If no potential gaps or ambiguities are found, return "findings": [] and "has_gaps": false.
- Do NOT hallucinate sections that do not exist.

OUTPUT FORMAT:
Return ONLY valid JSON matching this exact structure:
{{
  "executive_takeaway": "2-3 sentences providing an executive summary of the document's hidden contractual risks and unaddressed assumptions.",
  "has_gaps": true,
  "evidence_sufficient": true,
  "findings": [
    {{
      "id": "bs_1",
      "gap_type": "Ambiguous Standard / Missing Consequence / Undefined Term / Incomplete Obligation / Unresolved Contingency / Unclear Deadline / Missing Attachment / Missing Protective Term",
      "category": "Potential Gap | Ambiguity | Missing Reference | Needs Human Review",
      "severity": "High | Medium | Low",
      "title": "Short descriptive title of the issue",
      "explanation": "Clear explanation of why this represents a blind spot or risk.",
      "evidence": "Direct quote or section reference from document",
      "page_number": 1,
      "human_review_question": "Targeted question requiring human counsel review."
    }}
  ]
}}

Document Text:
{text}
"""


# ── Offline Deterministic Fallback ────────────────────────────────────────────

def _extract_sentence(text: str, match_start: int, max_len: int = 240) -> str:
    """Extract a clean sentence or clause surrounding a match."""
    # Look back for punctuation or newline
    prev_period = max(text.rfind(".", 0, match_start), text.rfind("\n", 0, match_start))
    start = 0 if prev_period == -1 else prev_period + 1

    # Look forward for punctuation or newline
    next_period = text.find(".", match_start)
    next_nl = text.find("\n", match_start)
    candidates = [p for p in (next_period, next_nl) if p != -1]
    end = min(candidates) + 1 if candidates else len(text)

    snippet = text[start:end].strip()
    if len(snippet) > max_len:
        snippet = snippet[:max_len] + "..."
    return snippet or text[match_start:match_start + max_len].strip()


def _offline_blind_spot_analysis(pages: list[PageContent], original_name: str = "") -> dict:
    """
    Comprehensive rule-based legal audit engine for offline analysis or LLM fallback.
    """
    findings: list[dict] = []
    counter = 1

    full_text = "\n\n".join(p.text for p in pages)
    full_lower = full_text.lower()

    # 1. Ambiguity: Subjective standards of effort
    effort_pat = re.compile(
        r"\b(best\s+efforts?|commercially\s+reasonable\s+efforts?|reasonable\s+efforts?|reasonable\s+endeavors?)\b",
        re.IGNORECASE,
    )
    for p in pages:
        for m in effort_pat.finditer(p.text):
            evidence = _extract_sentence(p.text, m.start())
            matched_term = m.group(0)
            findings.append({
                "id": f"bs_{counter}",
                "gap_type": "Ambiguous Standard of Care",
                "category": "Ambiguity",
                "severity": "Medium",
                "title": f"Subjective Standard: '{matched_term}' Lacks Objective Benchmarks",
                "explanation": (
                    f"The contract imposes a '{matched_term}' standard without specifying expenditure caps, "
                    "milestone deadlines, or quantifiable criteria, leaving compliance vulnerable to dispute."
                ),
                "evidence": evidence,
                "page_number": p.page,
                "human_review_question": (
                    f"Should '{matched_term}' be defined with specific operational milestones or replaced with "
                    "measurable deliverables?"
                ),
            })
            counter += 1
            if counter > 5:
                break
        if counter > 5:
            break

    # 2. Ambiguity: Vague timelines / deadlines
    timeline_pat = re.compile(
        r"\b(from\s+time\s+to\s+time|as\s+soon\s+as\s+practicable|in\s+due\s+course|timely\s+manner|without\s+undue\s+delay)\b",
        re.IGNORECASE,
    )
    for p in pages:
        for m in timeline_pat.finditer(p.text):
            evidence = _extract_sentence(p.text, m.start())
            matched_term = m.group(0)
            findings.append({
                "id": f"bs_{counter}",
                "gap_type": "Unclear Deadline / Timeline",
                "category": "Ambiguity",
                "severity": "Medium",
                "title": f"Indefinite Timeline: '{matched_term}'",
                "explanation": (
                    f"The phrase '{matched_term}' does not provide a definite calendar or business day deadline, "
                    "making it difficult to establish default or delay damages."
                ),
                "evidence": evidence,
                "page_number": p.page,
                "human_review_question": (
                    "What specific number of business or calendar days should replace this indefinite deadline?"
                ),
            })
            counter += 1
            if counter > 8:
                break
        if counter > 8:
            break

    # 3. Ambiguity: Unilateral Discretion
    discretion_pat = re.compile(
        r"\b(sole\s+discretion|absolute\s+discretion|at\s+its\s+sole\s+option)\b",
        re.IGNORECASE,
    )
    for p in pages:
        for m in discretion_pat.finditer(p.text):
            evidence = _extract_sentence(p.text, m.start())
            findings.append({
                "id": f"bs_{counter}",
                "gap_type": "Unilateral Discretion",
                "category": "Ambiguity",
                "severity": "High",
                "title": f"Unilateral Right: '{m.group(0)}'",
                "explanation": (
                    "One party holds unilateral discretionary authority without a requirement of reasonableness, "
                    "commercial good faith, or bilateral consensus."
                ),
                "evidence": evidence,
                "page_number": p.page,
                "human_review_question": (
                    "Should this discretion be subject to 'reasonable and good-faith commercial judgment'?"
                ),
            })
            counter += 1
            if counter > 10:
                break
        if counter > 10:
            break

    # 4. Missing Reference: Exhibits / Schedules referenced but potentially missing
    ref_pat = re.compile(
        r"\b(Exhibit|Schedule|Appendix|Annex|Attachment)\s+([A-Z0-9]+|\b[I|V|X]+\b)",
        re.IGNORECASE,
    )
    found_refs = set()
    for p in pages:
        for m in ref_pat.finditer(p.text):
            ref_name = f"{m.group(1).title()} {m.group(2).upper()}"
            if ref_name not in found_refs:
                found_refs.add(ref_name)
                # Check if this exhibit has an actual section header or content
                has_body = bool(
                    re.search(rf"\b{re.escape(ref_name)}\b[\s\S]{{50,}}", full_text, re.IGNORECASE)
                )
                if not has_body:
                    findings.append({
                        "id": f"bs_{counter}",
                        "gap_type": "Missing Attachment / Exhibit",
                        "category": "Missing Reference",
                        "severity": "High",
                        "title": f"Referenced Attachment Omitted: {ref_name}",
                        "explanation": (
                            f"The agreement references '{ref_name}' in operative provisions, but the substantive content "
                            "or signed attachment does not appear in the document body."
                        ),
                        "evidence": _extract_sentence(p.text, m.start()),
                        "page_number": p.page,
                        "human_review_question": (
                            f"Has {ref_name} been finalized, countersigned, and formally annexed to this agreement?"
                        ),
                    })
                    counter += 1
            if counter > 13:
                break
        if counter > 13:
            break

    # 5. Missing Reference: Unfilled Drafting Placeholders
    placeholder_pat = re.compile(
        r"(\[TBD\]|\[INSERT[^\]]*\]|\[DATE\]|\[AMOUNT\]|\[PARTY[^\]]*\]|___+)",
        re.IGNORECASE,
    )
    for p in pages:
        for m in placeholder_pat.finditer(p.text):
            evidence = _extract_sentence(p.text, m.start())
            findings.append({
                "id": f"bs_{counter}",
                "gap_type": "Unfilled Drafting Placeholder",
                "category": "Missing Reference",
                "severity": "High",
                "title": f"Unfilled Placeholder: '{m.group(0)}'",
                "explanation": (
                    f"A drafting placeholder '{m.group(0)}' was left unfilled, indicating an incomplete contract term."
                ),
                "evidence": evidence,
                "page_number": p.page,
                "human_review_question": (
                    "What finalized value, date, or party information needs to replace this placeholder?"
                ),
            })
            counter += 1
            if counter > 15:
                break
        if counter > 15:
            break

    # 6. Needs Human Review: Unresolved Contingency / Agreement to Agree
    contingency_pat = re.compile(
        r"\b(subject\s+to\s+(?:further\s+)?(?:mutual\s+)?agreement|to\s+be\s+agreed\s+(?:upon\s+)?in\s+writing|good\s+faith\s+negotiation|pending\s+(?:written\s+)?approval|unless\s+otherwise\s+agreed)\b",
        re.IGNORECASE,
    )
    for p in pages:
        for m in contingency_pat.finditer(p.text):
            evidence = _extract_sentence(p.text, m.start())
            matched_term = m.group(0)
            findings.append({
                "id": f"bs_{counter}",
                "gap_type": "Unresolved Contingency",
                "category": "Needs Human Review",
                "severity": "High",
                "title": f"Agreement to Agree: '{matched_term}'",
                "explanation": (
                    f"The provision contains '{matched_term}', deferring a material term to future consensus without "
                    "a deadlock resolution mechanism if parties disagree."
                ),
                "evidence": evidence,
                "page_number": p.page,
                "human_review_question": (
                    "What fallback remedy or arbitration mechanism governs if the parties fail to reach mutual agreement?"
                ),
            })
            counter += 1
            if counter > 18:
                break
        if counter > 18:
            break

    # 7. Potential Gap: Document-wide protective omissions
    # Liability Cap
    has_liability_cap = any(
        term in full_lower
        for term in ["aggregate liability", "cap on liability", "liability shall not exceed", "maximum liability"]
    )
    if not has_liability_cap:
        findings.append({
            "id": f"bs_{counter}",
            "gap_type": "Missing Liability Cap",
            "category": "Potential Gap",
            "severity": "High",
            "title": "Absence of Express Aggregate Liability Cap",
            "explanation": (
                "The agreement does not contain an explicit monetary cap (e.g. fees paid over 12 months) on total "
                "aggregate damages, creating uncapped commercial liability exposure."
            ),
            "evidence": "[Document-wide omission: no aggregate liability cap detected]",
            "page_number": None,
            "human_review_question": (
                "Should an aggregate liability cap tied to trailing fees or a fixed monetary ceiling be negotiated?"
            ),
        })
        counter += 1

    # Termination Cure Period
    has_cure_period = any(
        term in full_lower
        for term in ["cure period", "days to cure", "opportunity to cure", "within 30 days of written notice"]
    )
    if not has_cure_period:
        findings.append({
            "id": f"bs_{counter}",
            "gap_type": "Missing Notice & Cure Period",
            "category": "Potential Gap",
            "severity": "Medium",
            "title": "Missing Breach Notice & Cure Window",
            "explanation": (
                "No clear notice and cure period (e.g. 30 days) is defined for curable contractual breaches prior to default."
            ),
            "evidence": "[Document-wide omission: termination terms lack formal cure window]",
            "page_number": None,
            "human_review_question": (
                "Should a standard 30-day written notice and cure period be inserted before termination for breach can occur?"
            ),
        })
        counter += 1

    # Audit & Inspection Rights
    has_audit = any(
        term in full_lower
        for term in ["audit right", "right to audit", "inspect books", "access to records", "accounting records"]
    )
    if not has_audit and any(k in full_lower for k in ["fee", "payment", "commission", "royalty", "affiliate"]):
        findings.append({
            "id": f"bs_{counter}",
            "gap_type": "Missing Audit & Inspection Rights",
            "category": "Potential Gap",
            "severity": "Medium",
            "title": "No Financial or Compliance Audit Rights",
            "explanation": (
                "While financial, fee, or commission obligations exist, the agreement lacks provisions allowing verification "
                "or inspection of underlying books and records."
            ),
            "evidence": "[Document-wide omission: fee terms exist without verification audit clause]",
            "page_number": None,
            "human_review_question": (
                "Should periodic audit rights and access to financial logs be included to verify calculations?"
            ),
        })
        counter += 1

    # Summary stats
    high_count = sum(1 for f in findings if f["severity"] == "High")
    med_count = sum(1 for f in findings if f["severity"] == "Medium")
    low_count = sum(1 for f in findings if f["severity"] == "Low")

    cat_summary = {}
    for f in findings:
        cat_summary[f["category"]] = cat_summary.get(f["category"], 0) + 1

    takeaway = (
        f"Automated offline audit identified {len(findings)} potential blind spots across {len(pages)} pages. "
        f"Key observations include {high_count} elevated severity issues including contractual ambiguities, "
        "missing consequences, and protective gap risks requiring human counsel review."
    )

    return {
        "executive_takeaway": takeaway,
        "has_gaps": len(findings) > 0,
        "evidence_sufficient": True,
        "findings": findings,
        "total_findings": len(findings),
        "high_severity_count": high_count,
        "medium_severity_count": med_count,
        "low_severity_count": low_count,
        "categories_summary": cat_summary,
        "llm_used": False,
    }


# ── LLM Analysis ─────────────────────────────────────────────────────────────

def _llm_blind_spot_analysis(pages: list[PageContent], original_name: str = "") -> dict:
    """
    Passes full page-indexed text to the configured LLM for deep blind-spot detection.
    """
    # Build text with explicit page markers
    doc_sections = []
    for p in pages:
        doc_sections.append(f"--- Page {p.page} ---\n{p.text.strip()}")
    full_indexed_text = "\n\n".join(doc_sections)

    # Cap to fit model context safely (~16k chars)
    capped_text = full_indexed_text[:16000]
    if len(full_indexed_text) > 16000:
        capped_text += "\n\n[... document truncated for model context ...]"

    prompt = _BLIND_SPOT_PROMPT.format(text=capped_text)

    try:
        if settings.LLM_PROVIDER == "openai":
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage
            llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0)
        elif settings.LLM_PROVIDER == "groq":
            from langchain_groq import ChatGroq
            from langchain.schema import HumanMessage
            llm = ChatGroq(model=settings.GROQ_MODEL, api_key=settings.GROQ_API_KEY, temperature=0, max_retries=1)
        else:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.schema import HumanMessage
            llm = ChatGoogleGenerativeAI(
                model=settings.GOOGLE_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0,
                max_retries=1,
            )

        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content if hasattr(response, "content") else str(response)

        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0].strip()

        data = json.loads(raw)
        findings = data.get("findings", [])

        # Validate and clean findings
        valid_findings = []
        for i, f in enumerate(findings, 1):
            category = f.get("category", "Potential Gap")
            if category not in ["Potential Gap", "Ambiguity", "Missing Reference", "Needs Human Review"]:
                category = "Needs Human Review"

            severity = f.get("severity", "Medium").title()
            if severity not in ["High", "Medium", "Low"]:
                severity = "Medium"

            page_num = f.get("page_number")
            if isinstance(page_num, str) and page_num.isdigit():
                page_num = int(page_num)
            elif not isinstance(page_num, int):
                page_num = None

            valid_findings.append({
                "id": f.get("id") or f"bs_{i}",
                "gap_type": f.get("gap_type", "Contract Gap"),
                "category": category,
                "severity": severity,
                "title": f.get("title", "Contract Observation"),
                "explanation": f.get("explanation", ""),
                "evidence": f.get("evidence", ""),
                "page_number": page_num,
                "human_review_question": f.get("human_review_question", "Review clause with legal counsel."),
            })

        high_count = sum(1 for f in valid_findings if f["severity"] == "High")
        med_count = sum(1 for f in valid_findings if f["severity"] == "Medium")
        low_count = sum(1 for f in valid_findings if f["severity"] == "Low")

        cat_summary = {}
        for f in valid_findings:
            cat_summary[f["category"]] = cat_summary.get(f["category"], 0) + 1

        return {
            "executive_takeaway": data.get("executive_takeaway", "Contract blind-spot analysis complete."),
            "has_gaps": len(valid_findings) > 0,
            "evidence_sufficient": data.get("evidence_sufficient", True),
            "findings": valid_findings,
            "total_findings": len(valid_findings),
            "high_severity_count": high_count,
            "medium_severity_count": med_count,
            "low_severity_count": low_count,
            "categories_summary": cat_summary,
            "llm_used": True,
        }

    except Exception as exc:
        print(f"[BlindSpotService] LLM analysis error: {exc}. Falling back to offline engine.")
        result = _offline_blind_spot_analysis(pages, original_name)
        result["llm_used"] = False
        return result


# ── Public Entrypoint ─────────────────────────────────────────────────────────

def detect_blind_spots(doc_id: str) -> dict:
    """
    Run the Contract Blind-Spot Detector on a specific document.
    """
    from config import settings as cfg
    from services import document_registry as registry

    doc = registry.get_document(doc_id)
    if not doc:
        raise FileNotFoundError(f"Document {doc_id} not found.")

    pdf_path = cfg.UPLOAD_DIR / f"{doc_id}.pdf"
    if not pdf_path.exists():
        pdf_path = cfg.UPLOAD_DIR / doc["filename"]
    if not pdf_path.exists():
        raise FileNotFoundError(f"Underlying PDF file for document {doc_id} not found.")

    extraction = extract_text(pdf_path)
    if extraction.error:
        raise ValueError(f"Text extraction failed: {extraction.error}")

    if not extraction.pages or extraction.total_chars < 50:
        return {
            "document_id": doc_id,
            "total_findings": 0,
            "high_severity_count": 0,
            "medium_severity_count": 0,
            "low_severity_count": 0,
            "categories_summary": {},
            "findings": [],
            "executive_takeaway": "The document contains insufficient extractable text to conduct a blind-spot audit.",
            "has_gaps": False,
            "evidence_sufficient": False,
            "llm_configured": settings.llm_configured,
            "llm_used": False,
            "disclaimer": (
                "All findings are preliminary automated observations and do not constitute formal legal counsel. "
                "Human legal review by qualified counsel is required."
            ),
        }

    if not settings.llm_configured:
        result = _offline_blind_spot_analysis(extraction.pages, doc.get("original_name", ""))
    else:
        result = _llm_blind_spot_analysis(extraction.pages, doc.get("original_name", ""))

    result["document_id"] = doc_id
    result["llm_configured"] = settings.llm_configured
    result["disclaimer"] = (
        "All findings are preliminary automated observations and do not constitute formal legal conclusions. "
        "Human legal review by qualified counsel is required."
    )
    return result
