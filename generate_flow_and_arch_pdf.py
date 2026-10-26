import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

BASE_DIR = r"C:\Users\Abhiraj\.gemini\antigravity-ide\brain\531a1c6a-3ded-48c7-897c-0760e81bbfb0"
IMG_DOCS = os.path.join(BASE_DIR, "documents_page_1792779978247.png")
IMG_CHAT = os.path.join(BASE_DIR, "chat_page_1792782611081.png")
IMG_BLIND = os.path.join(BASE_DIR, "blind_spots_done_1792780383488.png")
IMG_DASH = os.path.join(BASE_DIR, "dashboard_page_1792782600524.png")

OUTPUT_PDF = r"d:\Legal Document Analyzer\LexAnalyzer_Architecture_and_Flow.pdf"

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
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(40, 755, "LexAnalyzer · End-to-End System Flow & Architecture Specification")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)
            
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 40, 572, 40)
        self.drawString(40, 28, "LexAnalyzer Legal AI · Architecture & Visual Walkthrough")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 28, page_str)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569")
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=6,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748B"),
        alignment=1,
        spaceAfter=6
    )

    story = []

    # ================= PAGE 1 =================
    # Hero Title Banner
    banner_data = [[
        Paragraph(
            "<b>LexAnalyzer · End-to-End System Flow & Architecture</b><br/>"
            "<font size=8.5 color='#93C5FD'>Complete Lifecycle: Ingestion → OCR → Dense Vector Indexing → AI Auditing → Interactive Q&A</font>",
            ParagraphStyle('Banner', parent=title_style, textColor=colors.white, fontSize=15, leading=19)
        )
    ]]
    banner_table = Table(banner_data, colWidths=[532])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))

    # Executive Overview
    story.append(Paragraph("1. Executive Overview", h1_style))
    story.append(Paragraph(
        "<b>LexAnalyzer</b> is an enterprise legal intelligence platform engineered for lawyers, legal auditors, and contract managers. "
        "It eliminates manual contract reviews by combining <b>optical character recognition (OCR)</b>, <b>retrieval-augmented generation (RAG)</b>, "
        "and <b>multi-tenant local vector stores</b> to uncover hidden risks, missing clauses, and ambiguous terms in seconds.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # End to End Flow
    story.append(Paragraph("2. End-to-End Project Workflow (Start to Finish)", h1_style))
    story.append(Paragraph("Every legal contract processed by LexAnalyzer flows through six deterministic stages:", body_style))
    story.append(Spacer(1, 4))

    flow_items = [
        ("Step 1: Secure Multi-Tenant Authentication",
         "Users register and log in via JWT authentication (RFC-7519) and bcrypt salt hashing. Every document, index, and audit query is strictly scoped to the authenticated user ID. Complete data privacy is enforced across tenants."),
        ("Step 2: Multi-Format Ingestion & Tesseract OCR",
         "Users upload native PDFs or scanned images (PNG, JPG, TIFF, WEBP, BMP). If an image or scanned document is detected, the automated OCR pipeline executes Tesseract OCR to extract high-accuracy text and wraps it into a standardized PDF."),
        ("Step 3: Document Chunking & Dense Vectorization",
         "PyMuPDF segments the document into semantic text chunks while preserving page numbers. Local HuggingFace Sentence-Transformers (<i>all-MiniLM-L6-v2</i>) generate 384-dimensional dense embeddings without transmitting confidential data to external vector APIs."),
        ("Step 4: Vector Index Creation (FAISS)",
         "Facebook AI Similarity Search (FAISS) builds a local on-disk index per document. This enables sub-millisecond nearest-neighbor search for precise clause retrieval."),
        ("Step 5: Multi-Engine Legal Auditing",
         "• <b>Contract Blind-Spot Detector:</b> Scans for omissions, ambiguous wording, missing exhibits, and undefined terms.<br/>"
         "• <b>Clause Risk Analyzer:</b> Classifies indemnification, liability, and termination clauses into Low, Medium, and High risk.<br/>"
         "• <b>Executive Summarizer:</b> Generates concise plain-English summaries and key business takeaways."),
        ("Step 6: Interactive Q&A & Audit Export",
         "Legal counsel asks natural language questions in Document Chat. The system retrieves exact context chunks with page citations. Findings and gap analyses can be exported to Markdown (.md) or printed as formal audit reports.")
    ]

    for title, desc in flow_items:
        story.append(Paragraph(f"• <b>{title}</b>", h2_style))
        story.append(Paragraph(desc, bullet_style))
        story.append(Spacer(1, 2))

    story.append(PageBreak())

    # ================= PAGE 2 =================
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. System Architecture & Component Design", h1_style))
    story.append(Paragraph(
        "LexAnalyzer is built on a modern decoupled architecture separating presentation, orchestration, AI retrieval, and isolated tenant storage.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Architecture Table
    arch_data = [
        [Paragraph("<b>Layer</b>", body_style), Paragraph("<b>Component / Tech</b>", body_style), Paragraph("<b>Function & Implementation Details</b>", body_style)],
        [
            Paragraph("<b>Frontend (Client)</b>", body_style),
            Paragraph("React 18 · Vite<br/>Vanilla CSS · Lucide", body_style),
            Paragraph("• Responsive single-page application with custom dark navy glassmorphic design.<br/>• Zero bulky CSS framework overhead; dynamic filtering, instant live search, and audit badges.", body_style)
        ],
        [
            Paragraph("<b>API Gateway & Security</b>", body_style),
            Paragraph("FastAPI · Uvicorn<br/>JWT · Bcrypt", body_style),
            Paragraph("• Asynchronous REST endpoints with strict Pydantic v2 validation.<br/>• Bearer JWT authorization middleware enforcing multi-tenant isolation on every document and query.", body_style)
        ],
        [
            Paragraph("<b>OCR & Parsing</b>", body_style),
            Paragraph("PyMuPDF (fitz)<br/>Tesseract OCR", body_style),
            Paragraph("• Dual-mode extractor: parses digital text streams with page bounding or invokes local Tesseract OCR on scanned contract images.", body_style)
        ],
        [
            Paragraph("<b>Embeddings & Search</b>", body_style),
            Paragraph("all-MiniLM-L6-v2<br/>FAISS Vector DB", body_style),
            Paragraph("• Local 384-dimensional dense semantic vectors. Fast L2/Inner Product search per tenant index without external third-party vector databases.", body_style)
        ],
        [
            Paragraph("<b>AI Intelligence</b>", body_style),
            Paragraph("LangChain · Groq<br/>OpenAI / Gemini / Heuristics", body_style),
            Paragraph("• High-speed inference using LLaMA-3.3-70B on Groq or OpenAI/Gemini.<br/>• Includes deterministic fallback heuristics ensuring 100% uptime even if API quotas expire.", body_style)
        ],
        [
            Paragraph("<b>Tenant Storage</b>", body_style),
            Paragraph("JSON Store · Disk<br/>Tenant Directories", body_style),
            Paragraph("• Directory isolation: <code>storage/documents/&lt;user_id&gt;/</code> and <code>storage/index/&lt;user_id&gt;/</code>.<br/>• Prevents cross-user data leakage at the operating system filesystem level.", body_style)
        ]
    ]

    arch_table = Table(arch_data, colWidths=[90, 115, 327])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 14))

    # Data Flow Pipeline Diagram (Table format)
    story.append(Paragraph("4. Technical Data Flow Pipeline", h1_style))
    story.append(Paragraph("Visual representation of data transformations from raw input to verified legal insights:", body_style))
    story.append(Spacer(1, 6))

    flow_box_data = [
        [
            Paragraph("<font color='#1E3A8A'><b>[1] Ingestion</b></font><br/>Upload PDF/Image<br/>Auto Tesseract OCR", body_style),
            Paragraph("➔", ParagraphStyle('Arrow', alignment=1, fontSize=12, textColor=colors.HexColor("#94A3B8"))),
            Paragraph("<font color='#1E3A8A'><b>[2] Indexing</b></font><br/>PyMuPDF Chunking<br/>FAISS Embeddings", body_style),
            Paragraph("➔", ParagraphStyle('Arrow', alignment=1, fontSize=12, textColor=colors.HexColor("#94A3B8"))),
            Paragraph("<font color='#1E3A8A'><b>[3] Verification</b></font><br/>Tenant Token Check<br/>Context Retrieval", body_style),
            Paragraph("➔", ParagraphStyle('Arrow', alignment=1, fontSize=12, textColor=colors.HexColor("#94A3B8"))),
            Paragraph("<font color='#1E3A8A'><b>[4] AI Auditing</b></font><br/>Blind-Spots / Risks<br/>Q&A + Page Citations", body_style)
        ]
    ]
    flow_box_table = Table(flow_box_data, colWidths=[110, 20, 110, 20, 110, 20, 142])
    flow_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#EFF6FF")),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor("#EFF6FF")),
        ('BACKGROUND', (4,0), (4,0), colors.HexColor("#EFF6FF")),
        ('BACKGROUND', (6,0), (6,0), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (0,0), 0.5, colors.HexColor("#3B82F6")),
        ('BOX', (2,0), (2,0), 0.5, colors.HexColor("#3B82F6")),
        ('BOX', (4,0), (4,0), 0.5, colors.HexColor("#3B82F6")),
        ('BOX', (6,0), (6,0), 0.5, colors.HexColor("#3B82F6")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(flow_box_table)

    story.append(PageBreak())

    # ================= PAGE 3 =================
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Visual Walkthrough & Interface Tour (Part 1)", h1_style))
    story.append(Paragraph(
        "Screenshots captured directly from the live LexAnalyzer environment showcasing core workflows:",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Screenshot 1: Documents & Ingestion
    story.append(Paragraph("Feature 1: Multi-Format Document Center & OCR Ingestion", h2_style))
    story.append(Paragraph(
        "• Drag-and-drop ingestion accepting digital PDFs and scanned images (PNG, JPG, TIFF, WEBP, BMP).<br/>"
        "• Auto-detects scanned documents, triggers OCR text extraction, and organizes indexes per tenant.",
        bullet_style
    ))
    story.append(Spacer(1, 4))
    if os.path.exists(IMG_DOCS):
        story.append(Image(IMG_DOCS, width=500, height=230))
        story.append(Paragraph("Figure 1: Document Upload & Ingestion Center with automatic OCR pipeline.", caption_style))
    story.append(Spacer(1, 10))

    # Screenshot 2: Chat & RAG
    story.append(Paragraph("Feature 2: Interactive Document Chat with Verifiable Citations", h2_style))
    story.append(Paragraph(
        "• Natural language conversational interface grounded in indexed contract text.<br/>"
        "• Exact page-numbered citations prevent LLM hallucination and facilitate instant human review.",
        bullet_style
    ))
    story.append(Spacer(1, 4))
    if os.path.exists(IMG_CHAT):
        story.append(Image(IMG_CHAT, width=500, height=230))
        story.append(Paragraph("Figure 2: Natural Language Document Chat powered by RAG vector search.", caption_style))

    story.append(PageBreak())

    # ================= PAGE 4 =================
    story.append(Spacer(1, 10))
    story.append(Paragraph("6. Visual Walkthrough & Interface Tour (Part 2)", h1_style))
    story.append(Spacer(1, 4))

    # Screenshot 3: Blind Spot Detector
    story.append(Paragraph("Feature 3: Contract Blind-Spot & Gap Detector", h2_style))
    story.append(Paragraph(
        "• Automatically uncovers what is <i>missing</i>: unattached exhibits, undefined terms, and vague deadlines.<br/>"
        "• Categorizes gaps by severity (High, Medium, Low) and suggests specific human review questions.",
        bullet_style
    ))
    story.append(Spacer(1, 4))
    if os.path.exists(IMG_BLIND):
        story.append(Image(IMG_BLIND, width=500, height=230))
        story.append(Paragraph("Figure 3: Contract Blind-Spot Detector identifying omissions, ambiguities, and missing exhibits.", caption_style))
    story.append(Spacer(1, 10))

    # Screenshot 4: Dashboard
    story.append(Paragraph("Feature 4: Unified Analytics & Quick Action Dashboard", h2_style))
    story.append(Paragraph(
        "• Real-time overview of indexed agreements, audited clauses, and detected risk distributions.<br/>"
        "• Fast shortcuts to summarize documents, audit blind-spots, or query specific clauses.",
        bullet_style
    ))
    story.append(Spacer(1, 4))
    if os.path.exists(IMG_DASH):
        story.append(Image(IMG_DASH, width=500, height=230))
        story.append(Paragraph("Figure 4: Executive Dashboard displaying document metrics, risk analytics, and quick links.", caption_style))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF generated successfully:", OUTPUT_PDF)

if __name__ == "__main__":
    build_pdf()
