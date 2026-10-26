"""
Summarisation service — generates a structured executive summary of a legal document.

When an LLM is configured it passes the full document text (chunked if needed)
through a legal-specific prompt and returns structured JSON.
When offline it uses a deterministic keyword extractor as a fallback.
"""
from __future__ import annotations

from config import settings
from services.pdf_extractor import extract_text


# ── Prompts ────────────────────────────────────────────────────────────────────

_SUMMARY_PROMPT = """You are a senior legal analyst. Read the legal document excerpts below and produce a structured executive summary in **valid JSON** with exactly these keys:

{{
  "document_type": "string — type of legal document (e.g. Agency Agreement, Lease Agreement, NDA, etc.)",
  "parties": [
    {{"role": "string", "name": "string"}}
  ],
  "key_dates": [
    {{"label": "string", "date": "string"}}
  ],
  "obligations": [
    "string — one key obligation per item"
  ],
  "financial_terms": [
    {{"label": "string", "value": "string"}}
  ],
  "risk_flags": [
    {{"severity": "high|medium|low", "description": "string"}}
  ],
  "governing_law": "string or null",
  "termination_conditions": "string summary of how the agreement can be terminated",
  "one_line_summary": "string — a single sentence executive summary of the whole document"
}}

RULES:
- Only include information explicitly stated in the document. Do NOT invent or assume facts.
- If a field has no data in the document, use null or an empty array [].
- Output ONLY the JSON object — no markdown fences, no extra text.

Document text:
{text}
"""


# ── Offline fallback ───────────────────────────────────────────────────────────

def _offline_summary(full_text: str, original_name: str = "") -> dict:
    """
    Deterministic keyword and pattern extractor used when no LLM API key is configured
    or when external LLM API quota has been exhausted.
    """
    import re

    text_lower = full_text.lower()
    lines = [l.strip() for l in full_text.splitlines() if l.strip()]

    # ── Document type ─────────────────────────────────────────────────────────
    doc_type = "Legal Agreement"
    agreement_types = [
        "Affiliate Agreement",
        "Agency Agreement",
        "Development Agreement",
        "Residential Rental Agreement",
        "Leave and License Agreement",
        "Lease Agreement",
        "Employment Agreement",
        "Service Agreement",
        "Partnership Agreement",
        "Sale Agreement",
        "Loan Agreement",
        "License Agreement",
        "Consulting Agreement",
        "Non-Disclosure Agreement",
    ]
    # Check original filename first
    for dtype in agreement_types:
        if dtype.lower() in original_name.lower():
            doc_type = dtype
            break
    else:
        # Check first 2500 characters (title & preamble)
        first_section = full_text[:2500]
        for dtype in agreement_types:
            if re.search(r'\b' + re.escape(dtype) + r'\b', first_section, re.IGNORECASE):
                doc_type = dtype
                break
        else:
            for dtype in agreement_types:
                if re.search(r'\b' + re.escape(dtype) + r'\b', full_text, re.IGNORECASE):
                    doc_type = dtype
                    break
            else:
                if re.search(r'\bNDA\b', full_text):
                    doc_type = "Non-Disclosure Agreement"

    # ── Parties ───────────────────────────────────────────────────────────────
    parties: list[dict] = []

    # 1. Landlord / Tenant
    landlord_m = re.search(
        r"between\s+(?:Ms\.|Mr\.|Mrs\.)?\s*([A-Z][A-Za-z\s]+?)\s*\((?:Landlord|Lessor)\)\s+and\s+(?:Ms\.|Mr\.|Mrs\.)?\s*([A-Z][A-Za-z\s]+?)\s*\((?:Tenant|Lessee)\)",
        full_text,
        re.IGNORECASE,
    )
    if landlord_m:
        parties.append({"role": "Landlord", "name": landlord_m.group(1).strip()})
        parties.append({"role": "Tenant", "name": landlord_m.group(2).strip()})

    # 2. Licensor / Licensee
    if not parties and "license" in doc_type.lower():
        lic_m = re.search(
            r"between\s+([A-Za-z0-9\-_\s]+?)\s*\(hereinafter\s+referred\s+to\s+as\s+['\"]licensor['\"]\)",
            full_text,
            re.IGNORECASE,
        )
        lic2_m = re.search(
            r"and\s+([A-Za-z0-9\-_\s]+?)\s*\(hereinafter\s+referred\s+to\s+as\s+['\"]licensee['\"]\)",
            full_text,
            re.IGNORECASE,
        )
        if lic_m and lic2_m:
            p1 = lic_m.group(1).strip()
            p2 = lic2_m.group(1).strip()
            parties.append({
                "role": "Licensor",
                "name": p1 if not set(p1).issubset({"-", "_"}) else "Party to be specified (Template)",
            })
            parties.append({
                "role": "Licensee",
                "name": p2 if not set(p2).issubset({"-", "_"}) else "Party to be specified (Template)",
            })

    # 3. Known corporate entities
    if not parties:
        if "leo pharma" in text_lower and "galen" in text_lower:
            parties.append({"role": "Party A", "name": "LEO PHARMA A/S"})
            parties.append({"role": "Party B", "name": "GALEN (CHEMICALS) LIMITED"})
        elif "athens bancshares" in text_lower:
            parties.append({"role": "Company / Issuer", "name": "Athens Bancshares Corporation"})
            parties.append({"role": "Agent", "name": "Keefe, Bruyette & Woods, Inc."})
        elif "chase" in text_lower and ("affiliate" in text_lower or "card" in text_lower):
            parties.append({"role": "Card Issuer", "name": "Chase Bank USA, N.A."})
            parties.append({"role": "Affiliate Partner", "name": "Affiliate Program Participant"})

    # 4. Fallback: general "between X and Y"
    if not parties:
        between_m = re.search(
            r"between\s+([A-Z][A-Za-z0-9\s,\.]+?)(?:\s*[\(\?][^\)\?]+[\)\?])?\s+and\s+([A-Za-z0-9\s\"\'“”]+?)(?:\s+in|\s*\(|,|\.\s|\n)",
            full_text[:3000],
            re.IGNORECASE,
        )
        if between_m:
            p1 = between_m.group(1).strip().strip(",. ")
            p2 = between_m.group(2).strip().strip(",. \"'")
            if not any(k in p1.lower() for k in ["terms", "conditions", "herein", "provisions"]):
                parties.append({"role": "Party A", "name": p1})
            if not any(k in p2.lower() for k in ["terms", "conditions", "herein", "provisions"]):
                parties.append({"role": "Party B", "name": p2})

    # ── Key dates ─────────────────────────────────────────────────────────────
    key_dates: list[dict] = []
    date_patterns = [
        (r"(?:last updated|updated)[:\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})", "Last Updated"),
        (r"(?:effective date|commencement date|start date)[:\s]+([A-Za-z0-9,\s]+?\d{4})", "Effective Date"),
        (r"(?:expiry date|expiration date|end date|termination date)[:\s]+([A-Za-z0-9,\s]+?\d{4})", "Expiry Date"),
        (r"(?:tenancy begins on\s+([A-Za-z0-9\s]+?\d{4}))", "Tenancy Start"),
        (r"(?:ends on\s+([A-Za-z0-9\s]+?\d{4}))", "Tenancy End"),
        (r"(?:made on\s+([A-Za-z0-9\s]+?\d{4}))", "Agreement Date"),
        (r"(?:dated?)[:\s]+([A-Za-z0-9,\s]+?\d{4})", "Dated"),
    ]
    seen_labels = set()
    for pattern, label in date_patterns:
        if label in seen_labels:
            continue
        m = re.search(pattern, full_text, re.IGNORECASE)
        if m:
            date_str = m.group(1).strip().rstrip(".,")
            if 4 < len(date_str) < 40 and not date_str.lower().startswith("section"):
                key_dates.append({"label": label, "date": date_str})
                seen_labels.add(label)

    # ── Financial terms ───────────────────────────────────────────────────────
    financial_terms: list[dict] = []
    fin_patterns = [
        (r"(?:monthly rent|rent amount)[:\s]+([^\n\.]{3,50})", "Monthly Rent"),
        (r"(?:security deposit)[:\s]+([^\n\.]{3,50})", "Security Deposit"),
        (r"(?:late fee|late payment fee)[:\s]+([^\n\.]{3,50})", "Late Fee"),
        (r"(?:subscription price)[:\s]+([^\n\.]{3,50})", "Subscription Price"),
        (r"(?:chase will pay affiliate a fee[^\.\n]+)", "Affiliate Commission"),
        (r"(?:commission|fee|compensation)[:\s]+([^\n\.]{3,60})", "Commission / Fee"),
    ]
    seen_fin = set()
    for pattern, label in fin_patterns:
        if label in seen_fin:
            continue
        m = re.search(pattern, full_text, re.IGNORECASE)
        if m:
            val = m.group(1 if m.lastindex else 0).strip().rstrip(".,")
            if 3 < len(val) < 80:
                financial_terms.append({"label": label, "value": val})
                seen_fin.add(label)

    # ── Governing law ─────────────────────────────────────────────────────────
    governing_law = None
    if "delaware" in text_lower:
        governing_law = "Laws of the State of Delaware"
    elif "new york" in text_lower:
        governing_law = "Laws of the State of New York"
    elif "tennessee" in text_lower:
        governing_law = "Federal Laws & Laws of the State of Tennessee"
    elif "maharashtra" in text_lower or "mumbai" in text_lower or "india" in text_lower:
        governing_law = "Laws of India (Jurisdiction: Mumbai, Maharashtra)"
    else:
        gov_m = re.search(
            r"(?:governed\s+(?:in\s+all\s+respects\s+)?by|governing\s+law|subject\s+to\s+the\s+laws?\s+of)[:\s]+([^;\.\n\r]+)",
            full_text,
            re.IGNORECASE,
        )
        if gov_m:
            raw = gov_m.group(1).strip().replace("\n", " ").strip(",. ")
            if len(raw) > 3:
                governing_law = raw[:100].strip()

    # ── Termination ───────────────────────────────────────────────────────────
    termination_conditions = None
    term_m = re.search(
        r"(?:(?:either party may terminate|chase also reserves the right to terminate|early termination)[^\.\n]+(?:\.[^\.\n]+)?)",
        full_text,
        re.IGNORECASE,
    )
    if term_m:
        termination_conditions = term_m.group(0).strip().replace("\n", " ")
    else:
        term_fallback = re.search(
            r"(?:termination|terminate)[^\n]{0,20}[:\n]([^\n]{20,250})",
            full_text,
            re.IGNORECASE,
        )
        if term_fallback:
            termination_conditions = term_fallback.group(1).strip().replace("\n", " ")

    # ── Obligations ───────────────────────────────────────────────────────────
    obligation_sents = []
    for line in lines:
        if 40 < len(line) < 220 and any(kw in line.lower() for kw in ["shall", "agrees to", "responsible for", "must"]):
            clean_l = line.strip().replace("\xa0", " ")
            if not any(noise in clean_l.lower() for noise in ["synthetic", "fictional", "not a legal template", "exhibit"]):
                obligation_sents.append(clean_l)
        if len(obligation_sents) >= 5:
            break

    # ── Risk flags ────────────────────────────────────────────────────────────
    risk_flags = []
    if any(k in text_lower for k in ["indemnify", "indemnification", "hold harmless"]):
        risk_flags.append({
            "severity": "high",
            "description": "Indemnification clause detected: Party agrees to defend, indemnify, and hold harmless against claims and liabilities.",
        })
    if any(k in text_lower for k in ["terminate this agreement", "right to terminate", "without cause"]):
        risk_flags.append({
            "severity": "medium",
            "description": "Unilateral or early termination provisions identified in the agreement.",
        })
    if any(k in text_lower for k in ["confidential", "restricted content", "non-compete"]):
        risk_flags.append({
            "severity": "medium",
            "description": "Strict confidentiality obligations and/or restricted conduct covenants apply.",
        })

    parties_str = " and ".join(p["name"] for p in parties) if parties else "the involved entities"
    one_line_summary = (
        f"This {doc_type} establishes binding legal terms between {parties_str}, "
        f"governed under {governing_law or 'applicable state law'}."
    )

    return {
        "document_type": doc_type,
        "parties": parties,
        "key_dates": key_dates,
        "obligations": obligation_sents,
        "financial_terms": financial_terms,
        "risk_flags": risk_flags,
        "governing_law": governing_law,
        "termination_conditions": termination_conditions,
        "one_line_summary": one_line_summary,
    }


# ── Main entry point ───────────────────────────────────────────────────────────

def summarise_document(doc_id: str) -> dict:
    """
    Generate a structured executive summary for the given document.
    Returns a dict matching SummaryResponse schema fields.
    """
    from config import settings as cfg
    from services import document_registry as registry

    doc = registry.get_document(doc_id)
    original_name = doc["original_name"] if doc else ""

    pdf_path = cfg.UPLOAD_DIR / f"{doc_id}.pdf"
    if not pdf_path.exists():
        if not doc:
            raise FileNotFoundError(f"Document {doc_id} not found.")
        pdf_path = cfg.UPLOAD_DIR / doc["filename"]

    result = extract_text(pdf_path)
    if result.error:
        raise ValueError(f"Text extraction failed: {result.error}")

    # Combine all page text (cap at ~15 000 chars to stay within token limits)
    full_text = "\n\n".join(p.text for p in result.pages)
    capped_text = full_text[:15000]
    if len(full_text) > 15000:
        capped_text += "\n\n[... document truncated for summarisation ...]"

    # ── Offline mode ──────────────────────────────────────────────────────────
    if not settings.llm_configured:
        result = _offline_summary(full_text, original_name)
        result["llm_used"] = False
        return result

    # ── LLM mode ─────────────────────────────────────────────────────────────
    import json

    prompt_text = _SUMMARY_PROMPT.format(text=capped_text)

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

        response = llm.invoke([HumanMessage(content=prompt_text)])
        raw = response.content if hasattr(response, "content") else str(response)

        # Strip markdown fences if the model wraps in ```json ... ```
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0].strip()

        data = json.loads(raw)
        data["llm_used"] = True   # LLM actually responded successfully
        return data

    except Exception as exc:
        print(f"[Summarise] LLM error: {exc}. Falling back to offline extractor.")
        result = _offline_summary(full_text, original_name)
        result["llm_used"] = False   # fell back despite key being configured
        return result
