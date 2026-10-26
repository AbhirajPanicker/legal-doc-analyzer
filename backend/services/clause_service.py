"""
Clause & Risk Detection Service.

Identifies, classifies, and risk-assesses legal clauses in uploaded documents.
Works in both LLM mode (Gemini / OpenAI) and offline fallback mode.
"""
from __future__ import annotations

from config import settings
from services.pdf_extractor import extract_text

# ── Clause type definitions ────────────────────────────────────────────────────

CLAUSE_TYPES = [
    {
        "id": "confidentiality",
        "name": "Confidentiality / NDA",
        "icon": "🔒",
        "keywords": ["confidential", "non-disclosure", "nda", "proprietary information", "trade secret", "disclosure"],
        "risk_indicators": {
            "high": ["perpetual confidentiality", "unlimited duration", "no exceptions"],
            "medium": ["all information is confidential"],
            "low": ["3 years", "5 years", "reasonable exceptions"],
        },
        "standard_note": "A balanced confidentiality clause includes clear definitions, reasonable duration (2–5 years), and carve-outs for publicly known or independently developed information.",
        "missing_risk": "medium",
    },
    {
        "id": "indemnification",
        "name": "Indemnification & Hold Harmless",
        "icon": "⚖️",
        "keywords": ["indemnif", "hold harmless", "defend and indemnify", "losses, damages", "costs and expenses"],
        "risk_indicators": {
            "high": ["unlimited indemnification", "indemnify for all", "sole indemnification"],
            "medium": ["one-sided indemnification", "broad indemnification"],
            "low": ["mutual indemnification", "proportionate", "cap on indemnification"],
        },
        "standard_note": "Balanced indemnification should be mutual or proportionate. Unlimited or one-sided indemnification is a high-risk red flag.",
        "missing_risk": "medium",
    },
    {
        "id": "liability",
        "name": "Limitation of Liability",
        "icon": "🛡️",
        "keywords": ["limitation of liability", "limit of liability", "cap on liability", "in no event shall", "maximum liability", "not be liable for", "consequential damages", "indirect damages"],
        "risk_indicators": {
            "high": ["no limitation on liability", "unlimited liability", "full liability"],
            "medium": ["excludes consequential damages only for one party"],
            "low": ["mutual cap", "cap equals fees paid"],
        },
        "standard_note": "A well-drafted agreement caps liability at a reasonable amount (e.g., fees paid in 12 months) and mutually excludes consequential damages.",
        "missing_risk": "high",
    },
    {
        "id": "termination",
        "name": "Termination & Default",
        "icon": "🚪",
        "keywords": ["terminat", "default", "cancell", "notice of termination", "right to terminate", "early termination", "upon termination", "for cause", "for convenience"],
        "risk_indicators": {
            "high": ["immediate termination", "terminate without cause", "no cure period", "unilateral termination"],
            "medium": ["termination for convenience by one party only", "short notice period"],
            "low": ["mutual termination rights", "reasonable cure period", "30 day notice"],
        },
        "standard_note": "Fair termination clauses are mutual, provide adequate notice (30–90 days), and include a cure period for material breaches.",
        "missing_risk": "medium",
    },
    {
        "id": "governing_law",
        "name": "Governing Law & Dispute Resolution",
        "icon": "🏛️",
        "keywords": ["governing law", "jurisdiction", "arbitration", "dispute resolution", "mediation", "courts of", "laws of", "venue", "shall be resolved"],
        "risk_indicators": {
            "high": ["exclusive jurisdiction in a foreign country", "binding arbitration with no appeal", "one-sided venue"],
            "medium": ["arbitration institution not named", "distant jurisdiction"],
            "low": ["neutral jurisdiction", "named arbitration institution", "mediation first"],
        },
        "standard_note": "Governing law clauses should specify a clear jurisdiction. Dispute resolution should be fair, named, and ideally include mediation before arbitration.",
        "missing_risk": "medium",
    },
    {
        "id": "non_compete",
        "name": "Non-Compete / Non-Solicitation",
        "icon": "🚫",
        "keywords": ["non-compete", "non compete", "noncompete", "non-solicitation", "restraint of trade", "competitive activity", "shall not engage", "soliciting employees"],
        "risk_indicators": {
            "high": ["indefinite non-compete", "worldwide non-compete", "very broad scope"],
            "medium": ["2+ year non-compete", "broad geographic scope"],
            "low": ["reasonable duration", "narrow geographic scope", "limited industry"],
        },
        "standard_note": "Non-compete clauses should be reasonable in scope, duration (typically under 1 year), and geography. Overly broad clauses may be unenforceable.",
        "missing_risk": "low",
    },
    {
        "id": "force_majeure",
        "name": "Force Majeure",
        "icon": "🌪️",
        "keywords": ["force majeure", "act of god", "unforeseen event", "beyond reasonable control", "pandemic", "natural disaster", "circumstances beyond"],
        "risk_indicators": {
            "high": ["overly narrow events"],
            "medium": ["no pandemic listed", "no government action listed"],
            "low": ["comprehensive list", "includes pandemic and government action"],
        },
        "standard_note": "Force majeure should cover natural disasters, government actions, and pandemics, with clear notice requirements and defined consequences.",
        "missing_risk": "medium",
    },
    {
        "id": "intellectual_property",
        "name": "Intellectual Property",
        "icon": "💡",
        "keywords": ["intellectual property", "ip rights", "copyright", "patent", "trademark", "work for hire", "work product", "assigns all rights", "proprietary rights"],
        "risk_indicators": {
            "high": ["assigns all ip to one party", "no license back", "perpetual irrevocable license"],
            "medium": ["work for hire with no carve-outs", "unclear IP ownership"],
            "low": ["mutual IP protection", "clear ownership", "limited license grants"],
        },
        "standard_note": "IP clauses should clearly define who owns created work, pre-existing IP, and license rights. Blanket IP assignment is a high-risk flag.",
        "missing_risk": "medium",
    },
    {
        "id": "payment",
        "name": "Payment Terms",
        "icon": "💰",
        "keywords": ["payment", "invoice", "fee", "compensation", "due date", "net 30", "net 60", "late payment", "shall pay", "monthly", "annual fee"],
        "risk_indicators": {
            "high": ["no payment terms defined", "payment on demand with no notice"],
            "medium": ["very short payment window", "high late payment interest"],
            "low": ["net 30 or net 60", "reasonable late fees", "clear invoicing terms"],
        },
        "standard_note": "Payment terms should clearly state amounts, due dates, acceptable payment methods, and consequences of late payment.",
        "missing_risk": "high",
    },
    {
        "id": "warranties",
        "name": "Warranties & Representations",
        "icon": "✅",
        "keywords": ["warrant", "warrants", "represent", "representation", "covenant", "as-is", "no warranty", "disclaimer of warranties", "merchantability"],
        "risk_indicators": {
            "high": ["full warranty without limitation", "warranty of fitness for all purposes"],
            "medium": ["one-sided warranty disclaimer", "as-is for one party only"],
            "low": ["mutual warranty disclaimers", "standard as-is clause", "limited warranty"],
        },
        "standard_note": "Warranties should be clearly scoped. At minimum, authority to enter the agreement should always be warranted by both parties.",
        "missing_risk": "low",
    },
]


# ── Offline helpers ────────────────────────────────────────────────────────────

def _find_excerpt(lines: list, keywords: list) -> str | None:
    for kw in keywords:
        for i, line in enumerate(lines):
            if kw in line.lower() and len(line.strip()) > 20:
                start = max(0, i - 1)
                end = min(len(lines), i + 3)
                excerpt = " ".join(l.strip() for l in lines[start:end] if l.strip())
                return excerpt[:500] + ("…" if len(excerpt) > 500 else "")
    return None


def _assess_risk_offline(text_lower: str, clause_def: dict) -> str:
    for indicator in clause_def["risk_indicators"].get("high", []):
        if indicator.lower() in text_lower:
            return "high"
    for indicator in clause_def["risk_indicators"].get("medium", []):
        if indicator.lower() in text_lower:
            return "medium"
    return "low"


def _offline_clause_analysis(full_text: str) -> dict:
    text_lower = full_text.lower()
    lines = full_text.splitlines()

    detected_clauses = []
    missing_clauses = []

    for cd in CLAUSE_TYPES:
        matched = [kw for kw in cd["keywords"] if kw in text_lower]

        if not matched:
            missing_clauses.append({
                "clause_id": cd["id"],
                "clause_name": cd["name"],
                "icon": cd["icon"],
                "missing": True,
                "risk": cd["missing_risk"],
                "description": f"No {cd['name']} clause was detected in this document. This absence carries {cd['missing_risk'].upper()} risk.",
                "standard_note": cd["standard_note"],
                "text_excerpt": None,
            })
        else:
            risk = _assess_risk_offline(text_lower, cd)
            risk_label = {"high": "⚠️ HIGH RISK", "medium": "🔶 MEDIUM RISK", "low": "✅ LOW RISK"}[risk]
            detected_clauses.append({
                "clause_id": cd["id"],
                "clause_name": cd["name"],
                "icon": cd["icon"],
                "missing": False,
                "risk": risk,
                "description": (
                    f"{risk_label} — {cd['name']} clause detected. "
                    f"Key terms found: {', '.join(matched[:4])}. Review carefully."
                ),
                "standard_note": cd["standard_note"],
                "text_excerpt": _find_excerpt(lines, matched[:3]),
            })

    all_clauses = detected_clauses + missing_clauses
    high_count = sum(1 for c in all_clauses if c["risk"] == "high")
    medium_count = sum(1 for c in all_clauses if c["risk"] == "medium")
    low_count = sum(1 for c in all_clauses if c["risk"] == "low")

    overall_risk = "high" if high_count >= 2 else ("medium" if high_count == 1 or medium_count >= 3 else "low")

    return {
        "detected_clauses": detected_clauses,
        "missing_clauses": missing_clauses,
        "overall_risk": overall_risk,
        "high_risk_count": high_count,
        "medium_risk_count": medium_count,
        "low_risk_count": low_count,
        "total_clauses_found": len(detected_clauses),
        "total_clauses_missing": len(missing_clauses),
        "llm_used": False,
        "analysis_note": (
            "This analysis used offline keyword extraction. "
            "Configure a Google or OpenAI API key for AI-powered analysis with deeper risk insights."
        ),
    }


# ── LLM mode ──────────────────────────────────────────────────────────────────

_CLAUSE_PROMPT = """You are a senior legal analyst specializing in contract review. Analyze the following legal document and identify all clauses present. For each clause type, provide a detailed risk assessment.

Return a JSON object with EXACTLY this structure:
{{
  "detected_clauses": [
    {{
      "clause_id": "string (one of: confidentiality|indemnification|liability|termination|governing_law|non_compete|force_majeure|intellectual_property|payment|warranties)",
      "clause_name": "string",
      "icon": "string emoji",
      "missing": false,
      "risk": "high|medium|low",
      "description": "string — 2-3 sentences explaining WHY this risk level, referencing actual contract language",
      "text_excerpt": "string — exact clause text from document (max 400 chars)"
    }}
  ],
  "missing_clauses": [
    {{
      "clause_id": "string",
      "clause_name": "string",
      "icon": "string emoji",
      "missing": true,
      "risk": "high|medium|low — risk of this clause being ABSENT",
      "description": "string — why the absence of this clause is risky",
      "text_excerpt": null
    }}
  ],
  "overall_risk": "high|medium|low",
  "high_risk_count": number,
  "medium_risk_count": number,
  "low_risk_count": number,
  "total_clauses_found": number,
  "total_clauses_missing": number,
  "analysis_note": "string — expert 1-2 sentence overview of this document's legal risk profile"
}}

Clause types to check: Confidentiality/NDA, Indemnification, Limitation of Liability, Termination & Default, Governing Law & Dispute Resolution, Non-Compete/Non-Solicitation, Force Majeure, Intellectual Property, Payment Terms, Warranties & Representations.

RULES:
- Base risk assessment on the ACTUAL language in the document, not generic observations.
- Mark clauses not found in the document as "missing" with appropriate risk level.
- Output ONLY the JSON object, no markdown fences, no extra text.

Legal document text:
{text}
"""


def _llm_clause_analysis(full_text: str) -> dict:
    import json

    capped_text = full_text[:14000]
    if len(full_text) > 14000:
        capped_text += "\n\n[... document truncated ...]"

    prompt = _CLAUSE_PROMPT.format(text=capped_text)

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
        data["llm_used"] = True

        # Inject standard_note from CLAUSE_TYPES definitions
        for clause in data.get("detected_clauses", []) + data.get("missing_clauses", []):
            cd = next((c for c in CLAUSE_TYPES if c["id"] == clause.get("clause_id", "")), None)
            clause["standard_note"] = cd["standard_note"] if cd else "Review with a qualified legal professional."

        return data

    except Exception as exc:
        print(f"[ClauseService] LLM error: {exc}. Falling back to offline analysis.")
        result = _offline_clause_analysis(full_text)
        result["llm_used"] = False
        return result


# ── Main entry point ──────────────────────────────────────────────────────────

def analyse_clauses(doc_id: str) -> dict:
    """Analyse clauses and risks in a legal document."""
    from config import settings as cfg
    from services import document_registry as registry

    pdf_path = cfg.UPLOAD_DIR / f"{doc_id}.pdf"
    if not pdf_path.exists():
        doc = registry.get_document(doc_id)
        if not doc:
            raise FileNotFoundError(f"Document {doc_id} not found.")
        pdf_path = cfg.UPLOAD_DIR / doc["filename"]

    result = extract_text(pdf_path)
    if result.error:
        raise ValueError(f"Text extraction failed: {result.error}")

    full_text = "\n\n".join(p.text for p in result.pages)

    if not settings.llm_configured:
        data = _offline_clause_analysis(full_text)
    else:
        data = _llm_clause_analysis(full_text)

    data["document_id"] = doc_id
    data["llm_configured"] = settings.llm_configured
    return data
