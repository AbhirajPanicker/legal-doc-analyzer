"""
Generate a professional, publication-grade 2-page PDF overview for LexAnalyzer.
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_PATH = Path("D:/Legal Document Analyzer/LexAnalyzer_Platform_Overview.pdf")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running header on page 2
        if self._pageNumber > 1:
            self.drawString(46, 752, "LexAnalyzer — Legal Document AI Platform | System & Features Specification")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(46, 744, 566, 744)

        # Footer
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(46, 38, 566, 38)

        self.drawString(46, 26, "LexAnalyzer Legal Intelligence · Enterprise Architecture & Feature Overview")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(566, 26, page_str)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=46,
        rightMargin=46,
        topMargin=40,
        bottomMargin=42,
    )

    styles = getSampleStyleSheet()

    c_navy_dark = colors.HexColor("#0f172a")
    c_navy_blue = colors.HexColor("#1e3a8a")
    c_primary = colors.HexColor("#2563eb")
    c_text_dark = colors.HexColor("#1e293b")
    c_text_muted = colors.HexColor("#475569")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_navy_dark,
        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_primary,
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=c_navy_dark,
        spaceBefore=10,
        spaceAfter=6,
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_navy_blue,
        spaceBefore=5,
        spaceAfter=2,
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=c_text_dark,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_text_dark,
        leftIndent=12,
        spaceAfter=2,
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#f8fafc"),
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=11,
        textColor=c_text_dark,
    )

    story = []

    # ═════════════════════════════════════════════════════════════════════════════
    # PAGE 1: Overview, Purpose, Core Value & Feature Highlights
    # ═════════════════════════════════════════════════════════════════════════════

    # Top Brand Bar
    story.append(Paragraph("LexAnalyzer", title_style))
    story.append(Paragraph("AI-Powered Legal Document Intelligence & Contract Analysis Platform", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=8))

    # Executive Hero Banner
    hero_text = (
        "<b>Executive Summary:</b> LexAnalyzer is an enterprise legal AI platform engineered to streamline contract "
        "review, risk identification, and interactive document exploration. Built on high-precision Retrieval-Augmented "
        "Generation (RAG), local dense vector embeddings, and rule-based legal audit heuristics, LexAnalyzer empowers legal "
        "counsel, compliance leads, and contract managers to rapidly assess agreements, uncover drafting blind spots, "
        "extract structured executive briefings, and query contracts with verifiable page-level citations."
    )
    hero_table = Table([[Paragraph(hero_text, callout_style)]], colWidths=[520])
    hero_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_navy_dark),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', (0, 0), (-1, -1), 4),
    ]))
    story.append(hero_table)
    story.append(Spacer(1, 8))

    # Section 1: What Does the Platform Do?
    story.append(Paragraph("1. What Does LexAnalyzer Do?", h1_style))
    story.append(Paragraph(
        "Reviewing complex commercial agreements, corporate disclosures, leases, and procurement contracts requires "
        "hours of manual analysis. LexAnalyzer automates this workflow by transforming static PDFs into structured, "
        "queryable legal intelligence:",
        body_style,
    ))

    story.append(Paragraph("• <b>Instant Contract Triage:</b> Extracts key parties, milestone dates, core obligations, and financial covenants in seconds.", bullet_style))
    story.append(Paragraph("• <b>Zero-Hallucination Q&A:</b> Direct semantic grounding via local FAISS indices. Answers reference exact document page numbers and quotations.", bullet_style))
    story.append(Paragraph("• <b>Contract Blind-Spot Detection:</b> Flags ambiguous effort standards ('best efforts'), indefinite deadlines ('promptly'), missing exhibits, and unassigned liabilities.", bullet_style))
    story.append(Paragraph("• <b>Automated Risk Assessment:</b> Evaluates 10 core commercial clause types against standard protective benchmarks, scoring severity (High/Med/Low).", bullet_style))
    story.append(Paragraph("• <b>Multi-Tenant Privacy:</b> Implements strict per-user document isolation, ensuring tenant files and chat logs are completely private.", bullet_style))

    story.append(Spacer(1, 6))

    # Section 2: Core Platform Capabilities
    story.append(Paragraph("2. Core Platform Capabilities & Modules", h1_style))

    features_p1 = [
        (
            "[Audit] Contract Blind-Spot Detector",
            "A proactive legal auditing engine that inspects agreements for hidden exposures and drafting omissions. Categorizes findings into <b>Potential Gaps</b> (absent liability caps, missing termination cure periods), <b>Ambiguity</b> (subjective standards like 'reasonable efforts' or vague deadlines like 'in due course'), <b>Missing References</b> (unattached exhibits/schedules, unfulfilled drafting placeholders like [TBD]), and <b>Needs Human Review</b> (unresolved contingencies and open assumptions). Each finding delivers supporting page citations and actionable questions for legal counsel."
        ),
        (
            "[Risk] Automated Clause & Risk Analysis",
            "Classifies and evaluates 10 foundational commercial clause types: Confidentiality/NDA, Indemnification & Hold Harmless, Limitation of Liability, Termination & Default, Governing Law & Jurisdiction, Non-Compete/Non-Solicitation, Force Majeure, Intellectual Property, Payment Terms, and Warranties. Identifies missing protections and computes an overall contract risk score."
        ),
        (
            "[Briefing] One-Click Executive Document Summarisation",
            "Generates instant structured contract briefings capturing contracting entities, execution/effective dates, key milestones, primary covenants, financial terms, and an executive one-line takeaway for rapid negotiation preparation."
        ),
        (
            "[Q&A] Document Chat with Verified Page Citations",
            "Interactive natural-language conversational interface grounded strictly in document content. Users can query specific terms (e.g., 'What remedies apply if delivery is delayed?'), receiving answers with precise page tags and verbatim supporting text excerpts."
        ),
    ]

    for title, desc in features_p1:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(desc, body_style))

    # ═════════════════════════════════════════════════════════════════════════════
    # PAGE 2: Ingestion, Architecture, Security, Export & Legal Notice
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    story.append(Paragraph("2. Core Platform Capabilities (Continued)", h1_style))

    features_p2 = [
        (
            "[Ingestion] Multi-Format Ingestion & Tesseract OCR Pipeline",
            "Handles digital PDFs as well as scanned contracts and image uploads (PNG, JPG, JPEG, TIFF, WEBP, BMP). Automatically detects scanned pages, invoking Tesseract OCR with bundled language models to ensure complete text extractability."
        ),
        (
            "[Security] Multi-Tenant User Authentication & Strict Data Isolation",
            "JWT-based security with native bcrypt salt hashing. Enforces strict per-user document isolation: User A cannot list, view, search, or query documents owned by User B. Chat histories are private and scoped strictly to the authenticated user session."
        ),
        (
            "[Reporting] Multi-Format Export & Compliance Reporting",
            "One-click generation of structured Markdown (.md) audit reports and print-ready PDF summaries for sharing with outside counsel, clients, and executive stakeholders."
        ),
    ]

    for title, desc in features_p2:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 4))

    # Section 3: Technical Architecture
    story.append(Paragraph("3. Technical Architecture & Technology Stack", h1_style))

    table_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Technology", table_header_style), Paragraph("Implementation & Capabilities", table_header_style)],
        [Paragraph("<b>Frontend UI</b>", table_body_style), Paragraph("React 18 · Vite · Vanilla CSS", table_body_style), Paragraph("Custom dark-navy design system, glassmorphism cards, dynamic filters, responsive layout, zero CSS framework bloat.", table_body_style)],
        [Paragraph("<b>API Layer</b>", table_body_style), Paragraph("FastAPI · Uvicorn · Python 3.10+", table_body_style), Paragraph("Asynchronous endpoints, strict Pydantic v2 schemas, JWT bearer authentication, multi-tenant middleware.", table_body_style)],
        [Paragraph("<b>PDF & OCR</b>", table_body_style), Paragraph("PyMuPDF (fitz) · Tesseract OCR", table_body_style), Paragraph("Preserves page metadata. Auto-converts images to PDF and extracts vector text or optical OCR text.", table_body_style)],
        [Paragraph("<b>Embeddings</b>", table_body_style), Paragraph("all-MiniLM-L6-v2 (Sentence-Transformers)", table_body_style), Paragraph("Dense 384-dimensional semantic vectors. Runs 100% locally with zero external API latency or cost.", table_body_style)],
        [Paragraph("<b>Vector Index</b>", table_body_style), Paragraph("FAISS (Facebook AI Similarity Search)", table_body_style), Paragraph("Local on-disk indexed vector stores per document. Modular for PostgreSQL/pgvector scaling.", table_body_style)],
        [Paragraph("<b>LLM Engine</b>", table_body_style), Paragraph("LangChain · Groq / Gemini / OpenAI", table_body_style), Paragraph("High-speed inference with deterministic keyword and regex heuristics fallback for complete offline resilience.", table_body_style)],
        [Paragraph("<b>Security</b>", table_body_style), Paragraph("Native Bcrypt · Python-Jose", table_body_style), Paragraph("RFC-compliant HS256 JWT tokens, bcrypt salt hashing, strict tenant ownership verification on all endpoints.", table_body_style)],
    ]

    tech_table = Table(table_data, colWidths=[90, 150, 280])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 8))

    # Section 4: Privacy & Legal Notice
    story.append(Paragraph("4. Data Privacy Guarantee & Legal Notice", h1_style))
    disclaimer_text = (
        "<b>Data Privacy & Security:</b> LexAnalyzer operates on a local-first vector architecture. "
        "Document indexes and registry metadata are maintained within isolated local directories and JSON stores. "
        "User accounts and uploaded files are strictly scoped; no tenant can inspect, query, or view another user's agreements.<br/><br/>"
        "<b>Legal Notice:</b> LexAnalyzer is an artificial intelligence assistance tool designed for informational, research, "
        "and auditing purposes. Outputs, including clause classifications and blind-spot observations, represent preliminary automated "
        "findings and do not constitute formal legal counsel. Qualified legal professionals should always review critical contractual obligations."
    )
    disc_table = Table([[Paragraph(disclaimer_text, body_style)]], colWidths=[520])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('PADDING', (0, 0), (-1, -1), 7),
        ('ROUNDEDCORNERS', (0, 0), (-1, -1), 4),
    ]))
    story.append(disc_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {PDF_PATH} ({PDF_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    build_pdf()
