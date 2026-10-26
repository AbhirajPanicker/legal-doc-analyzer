import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

OUTPUT_PDF = r"d:\Legal Document Analyzer\LexAnalyzer_AI_Pipelines_Explained.pdf"
PUBLIC_PDF = r"d:\Legal Document Analyzer\frontend\public\LexAnalyzer_AI_Pipelines_Explained.pdf"

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
            self.drawString(40, 755, "LexAnalyzer · Step-by-Step AI Execution Pipelines")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)
            
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 38, 572, 38)
        self.setFont("Helvetica", 9)
        self.drawString(40, 26, "LexAnalyzer AI Engine · Pipeline Flow Guide")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 26, page_str)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=38,
        rightMargin=38,
        topMargin=42,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.white
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=4
    )

    subhead_style = ParagraphStyle(
        'SubHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2563EB"),
        spaceBefore=4,
        spaceAfter=2
    )

    flow_box_style = ParagraphStyle(
        'FlowBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B")
    )

    flow_code_style = ParagraphStyle(
        'FlowCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0F172A")
    )

    arrow_style = ParagraphStyle(
        'Arrow',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=15,
        textColor=colors.HexColor("#3B82F6"),
        alignment=0,
        leftIndent=16
    )

    divider_style = ParagraphStyle(
        'Divider',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceBefore=4,
        spaceAfter=4
    )

    key_point_style = ParagraphStyle(
        'KeyPoint',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1E3A8A")
    )

    def make_pipeline_step(text, is_code=False):
        style = flow_code_style if is_code else flow_box_style
        t = Table([[Paragraph(text, style)]], colWidths=[536])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#CBD5E1")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        return t

    def make_key_point(text):
        t = Table([[Paragraph(f"<b>Key Point:</b> {text}", key_point_style)]], colWidths=[536])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3B82F6")),
            ('PADDING', (0,0), (-1,-1), 7),
        ]))
        return t

    story = []

    # ================= PAGE 1 =================
    banner_data = [[
        Paragraph(
            "<b>How the AI Works: Step-by-Step Execution Pipelines</b><br/>"
            "<font size=10 color='#93C5FD'>Exact flow of Q&amp;A (RAG), Document Summaries, Clause Analysis &amp; Blind-Spot Detection</font>",
            title_style
        )
    ]]
    banner_table = Table(banner_data, colWidths=[536])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 8))

    # 1. Q&A (RAG PIPELINE)
    story.append(Paragraph("1. How Q&amp;A Works (RAG Pipeline)", h1_style))
    story.append(Paragraph("<b>Ingestion &amp; Vector Indexing Phase:</b>", subhead_style))
    story.append(make_pipeline_step("<b>Your Legal PDF / Document</b> (or scanned image auto-converted via OCR)"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("Split into <b>~800-character semantic chunks</b> (preserving page numbers)"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("Each chunk → converted to a <b>384-dimensional number vector (embedding)</b> via HuggingFace <i>all-MiniLM-L6-v2</i>"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("All vectors saved to <b>FAISS</b> (local vector database stored on your disk)"))
    
    story.append(Spacer(1, 4))
    ask_banner = Table([[Paragraph("<b>[ PHASE 2: WHEN YOU ASK A QUESTION ]</b>", ParagraphStyle('AskBanner', alignment=1, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#1E3A8A")))]], colWidths=[536])
    ask_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(ask_banner)
    story.append(Spacer(1, 4))

    story.append(make_pipeline_step("<b>Your question</b> → also converted to a 384-dimensional vector"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("<b>FAISS finds the top 5 most similar chunks</b> by mathematical vector distance (cosine similarity)"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step(
        'Those 5 chunks + your question → sent to the LLM (Groq / Gemini) as a strict prompt:<br/>'
        '<i>"Answer ONLY from these provided excerpts: [chunks]. Question: [your question]"</i>'
    ))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("<b>AI generates the answer</b> → returned immediately with exact clickable <b>page sources</b>"))
    story.append(Spacer(1, 4))
    story.append(make_key_point(
        "The LLM <b>never reads the entire PDF blindly</b>. It only receives the 5 most relevant chunks retrieved by FAISS. This prevents hallucinations and guarantees pinpoint page citations."
    ))

    story.append(PageBreak())

    # ================= PAGE 2 =================
    story.append(Spacer(1, 4))

    # 2. HOW SUMMARISATION WORKS
    story.append(Paragraph("2. How Summarisation Works", h1_style))
    story.append(make_pipeline_step("<b>Your PDF</b>"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("All pages extracted &amp; joined into one continuous text (capped at 15,000 characters for optimal context)"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step(
        'Sent to the LLM with a strict JSON-enforcement prompt:<br/>'
        '<i>"Read this legal agreement. Return a structured JSON containing: parties, effective dates, core obligations, financial terms, risk flags, governing law, and termination conditions."</i>'
    ))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("<b>LLM returns structured JSON data</b> (validated against Pydantic schema)"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("<b>Frontend dynamically renders</b> each field into dedicated UI cards: Executive Overview, Commercial Terms, and Practical Takeaways"))
    story.append(Spacer(1, 4))
    story.append(make_key_point(
        "Zero unstructured guesswork. Strict JSON formatting ensures consistent commercial extraction every single time, without missing dates, parties, or dollar amounts."
    ))

    story.append(Spacer(1, 12))

    # 3. HOW CLAUSE ANALYSIS WORKS
    story.append(Paragraph("3. How Clause Analysis &amp; Risk Profiling Works", h1_style))
    story.append(make_pipeline_step("<b>Your PDF</b>"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("System scans text to locate standard contract clauses (Indemnification, Termination, Governing Law, Liability Cap, Confidentiality, Dispute Resolution)"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step(
        'Relevant clause excerpts sent to the LLM with an audit rubric:<br/>'
        '<i>"Classify each clause, evaluate balance of power, assign Risk (High / Medium / Low), and give risk rationale."</i>'
    ))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step(
        '<b>AI evaluates legal risk:</b><br/>'
        '• <font color="#DC2626"><b>HIGH RISK:</b></font> Unlimited liability, one-sided indemnification, automatic renewals with short notice.<br/>'
        '• <font color="#D97706"><b>MEDIUM RISK:</b></font> Ambiguous termination triggers or unfamiliar foreign governing jurisdictions.<br/>'
        '• <font color="#16A34A"><b>LOW RISK:</b></font> Standard bilateral confidentiality and mutual dispute resolution.'
    ))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("<b>Returns structured list of clauses</b> with severity color badges, exact quotes, and proposed amendment language"))
    story.append(Spacer(1, 4))
    story.append(make_key_point(
        "Surfaces dangerous legal commitments <i>before</i> you sign, giving you the exact rationale and redline suggestions to negotiate with the counterparty."
    ))

    story.append(PageBreak())

    # ================= PAGE 3 =================
    story.append(Spacer(1, 4))

    # 4. HOW BLIND-SPOT DETECTOR WORKS
    story.append(Paragraph("4. How Contract Blind-Spot Detector Works", h1_style))
    story.append(make_pipeline_step("<b>Your PDF</b>"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step("Full document text extracted and audited against a comprehensive <b>Contract Gap Checklist</b> (liability limits, remedies for breach, unattached exhibits, undefined terms, vague deadlines)"))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step(
        'Sent to the LLM with a specialized omission-detection prompt:<br/>'
        '<i>"Identify what is MISSING, VAGUE, or UNRESOLVED. Check for: 1) Potential Gaps, 2) Ambiguous terms, 3) Missing references, 4) Unresolved contingencies. Do not hallucinate."</i>'
    ))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step(
        '<b>AI classifies findings into 4 distinct gap categories:</b><br/>'
        '• <b>Potential Gap:</b> Missing protective provisions (e.g. no cap on damages, no audit rights).<br/>'
        '• <b>Ambiguity:</b> Subjective phrases like <i>"reasonable efforts"</i>, <i>"timely manner"</i>, or <i>"to satisfaction"</i>.<br/>'
        '• <b>Missing Reference:</b> Refers to unattached schedules (e.g. <i>"as defined in Exhibit B"</i>, but Exhibit B is missing).<br/>'
        '• <b>Needs Human Review:</b> Unilateral obligations or assumptions requiring lawyer clarification.'
    ))
    story.append(Paragraph("↓", arrow_style))
    story.append(make_pipeline_step(
        "<b>Outputs comprehensive audit card for each finding:</b><br/>"
        "Severity Badge (High / Med / Low) + Explanation + Supporting Quote + Page Number + <b>Targeted Question for Human Counsel</b>"
    ))
    story.append(Spacer(1, 4))
    story.append(make_key_point(
        "Unlike standard tools that only read what is written on the page, the <b>Blind-Spot Detector actively searches for what was left out</b>. It equips legal counsel with specific questions to ask the counterparty during negotiation."
    ))

    story.append(Spacer(1, 14))

    # Final summary box
    summary_box_data = [[
        Paragraph(
            "<b>Architecture Summary:</b><br/>"
            "• <b>Q&amp;A:</b> Local FAISS vector search + 5 retrieved chunks + strict LLM prompt + page citations.<br/>"
            "• <b>Summary:</b> Full-text ingestion + structured JSON schema prompt + card-based rendering.<br/>"
            "• <b>Clause Analysis:</b> Pattern extraction + risk rubric (High/Med/Low) + amendment recommendations.<br/>"
            "• <b>Blind-Spot Detector:</b> Omission auditing + 4-gap taxonomy + human counsel questions.",
            flow_box_style
        )
    ]]
    summary_box_table = Table(summary_box_data, colWidths=[536])
    summary_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94A3B8")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_box_table)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF generated successfully:", OUTPUT_PDF)

if __name__ == "__main__":
    build_pdf()
