import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

OUTPUT_PDF = r"d:\Legal Document Analyzer\LexAnalyzer_How_AI_Works.pdf"
PUBLIC_PDF = r"d:\Legal Document Analyzer\frontend\public\LexAnalyzer_How_AI_Works.pdf"

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
        self.setFont("Helvetica-Bold", 8.5)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(40, 755, "LexAnalyzer · How AI Delivers Answers, Summaries & Audits")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)
            
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 42, 572, 42)
        self.setFont("Helvetica", 9)
        self.drawString(40, 28, "LexAnalyzer Legal AI · AI Functionality Guide")
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
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Larger fonts as requested by user
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=25,
        textColor=colors.white
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#93C5FD")
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=5
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=6,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E3A8A")
    )

    story = []

    # ================= PAGE 1 =================
    # Hero Title Banner
    banner_data = [[
        Paragraph(
            "<b>How AI Works in LexAnalyzer</b><br/>"
            "<font size=10.5 color='#93C5FD'>Plain-English Guide: Document Q&amp;A, Summaries, Clause Risk &amp; Blind-Spot Detection</font>",
            title_style
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

    # SECTION 1: DOCUMENT Q&A (RAG)
    story.append(Paragraph("1. How AI Answers Your Questions (Document Chat)", h1_style))
    story.append(Paragraph(
        "LexAnalyzer uses <b>Retrieval-Augmented Generation (RAG)</b>. Instead of guessing, the AI answers strictly from your uploaded contract:",
        body_style
    ))
    
    qna_points = [
        "<b>1. Vector Matching:</b> When you type a question, local AI models (<i>all-MiniLM-L6-v2</i>) convert your question into a mathematical search vector.",
        "<b>2. FAISS Semantic Search:</b> The system scans the document's local vector index and retrieves the top 4 exact paragraphs that match your question conceptually.",
        "<b>3. Strict Grounding:</b> The retrieved contract text is fed to the LLM with strict instructions: <i>'Only answer using this text. Do not make anything up.'</i>",
        "<b>4. Verified Citations:</b> The AI provides a clear plain-English answer and attaches exact page numbers so you can verify the clause in the PDF."
    ]
    for pt in qna_points:
        story.append(Paragraph(f"• {pt}", bullet_style))
    
    story.append(Spacer(1, 12))

    # SECTION 2: DOCUMENT SUMMARY
    story.append(Paragraph("2. How Document Summaries are Generated", h1_style))
    story.append(Paragraph(
        "Instead of reading 50 pages of legal jargon, the AI distills the agreement into executive-ready takeaways:",
        body_style
    ))
    
    summary_points = [
        "<b>1. Structure Parsing:</b> The AI scans key anchors across all pages (Recitals, Scope, Financial Terms, Term & Termination).",
        "<b>2. Commercial Extraction:</b> It identifies the core business deal: Who is paying whom? What are the deliverables? What are the key milestones?",
        "<b>3. Four-Pillar Summary:</b> The output is organized into crisp sections: <i>Executive Overview</i>, <i>Key Obligations</i>, <i>Liabilities & Deadlines</i>, and <i>Practical Takeaways</i>.",
        "<b>4. Plain-English Translation:</b> Archaic legal phrases (e.g., <i>'heretofore'</i>, <i>'indemnify and hold harmless'</i>) are translated into clear business language."
    ]
    for pt in summary_points:
        story.append(Paragraph(f"• {pt}", bullet_style))

    story.append(PageBreak())

    # ================= PAGE 2 =================
    story.append(Spacer(1, 10))

    # SECTION 3: CLAUSE ANALYSIS
    story.append(Paragraph("3. How Clause Analysis & Risk Profiling Works", h1_style))
    story.append(Paragraph(
        "The AI systematically reviews the agreement to identify legal commitments and assess their risk level:",
        body_style
    ))
    
    clause_points = [
        "<b>1. Clause Classification:</b> Automatically identifies key clause types: Indemnification, Governing Law, Limitation of Liability, Termination, Confidentiality, and Dispute Resolution.",
        "<b>2. Balance Assessment:</b> The AI checks whether obligations are mutual or heavily one-sided favoring the other party.",
        "<b>3. Risk Grading:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <font color='#DC2626'><b>HIGH RISK:</b></font> Unlimited liability, one-sided indemnities, automatic renewal with short opt-out windows.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <font color='#D97706'><b>MEDIUM RISK:</b></font> Ambiguous termination triggers or unfamiliar foreign governing jurisdictions.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <font color='#16A34A'><b>LOW RISK:</b></font> Standard bilateral confidentiality and mutual dispute resolution terms.",
        "<b>4. Actionable Advice:</b> For every flagged risk, the AI explains <i>why</i> it is dangerous and suggests amendment language."
    ]
    for pt in clause_points:
        story.append(Paragraph(f"• {pt}", bullet_style))

    story.append(Spacer(1, 12))

    # SECTION 4: BLIND-SPOT DETECTOR
    story.append(Paragraph("4. How the Contract Blind-Spot Detector Works", h1_style))
    story.append(Paragraph(
        "Traditional tools only review what is written. The <b>Blind-Spot Detector</b> scans for what is <b>MISSING, VAGUE, or UNRESOLVED</b>:",
        body_style
    ))
    
    blind_points = [
        "<b>1. Potential Gaps:</b> Detects missing protective clauses that should be in the contract (e.g., missing cap on damages, missing audit rights, no force majeure).",
        "<b>2. Ambiguity Detection:</b> Highlights vague wording like <i>'reasonable efforts'</i>, <i>'timely manner'</i>, or <i>'to the satisfaction of'</i> that lead to costly disputes.",
        "<b>3. Missing References:</b> Flags references to unattached documents (e.g., contract says <i>'as defined in Exhibit B'</i>, but Exhibit B is missing from the upload).",
        "<b>4. Questions for Human Counsel:</b> Generates targeted legal questions to ask the counterparty during negotiation."
    ]
    for pt in blind_points:
        story.append(Paragraph(f"• {pt}", bullet_style))

    story.append(Spacer(1, 14))

    # Summary Callout Table
    summary_box_data = [[
        Paragraph(
            "<b>Key Takeaway:</b> LexAnalyzer combines local vector search (FAISS) with high-speed LLM reasoning. "
            "It never relies on blind AI hallucination — every answer, risk score, and detected blind spot is anchored "
            "directly in verifiable text with page references.",
            callout_style
        )
    ]]
    summary_box_table = Table(summary_box_data, colWidths=[532])
    summary_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3B82F6")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_box_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF generated successfully:", OUTPUT_PDF)

if __name__ == "__main__":
    build_pdf()
