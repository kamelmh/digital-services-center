"""Business Document PDF Exporter — Professional PDFs with Arabic support.

Uses ReportLab with Tahoma (Arabic-capable) fonts + arabic-reshaper + python-bidi.
Supports markdown content parsing: headers, tables, bullets, bold text.
RTL-aware for Arabic content.

Services: feasibility studies, business plans, market research, financial projections,
marketing plans, invoices, quotes.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
import re
import arabic_reshaper
from bidi.algorithm import get_display


# ── Font Registration ────────────────────────────────────────────────────────
def _register_fonts():
    """Register fonts for Arabic + Latin. Returns (FONT, FONT_BOLD).

    Priority: Tahoma (best Arabic coverage) → Dubai → Majalla → Helvetica.
    Tahoma handles Arabic presentation forms from bidi.get_display() correctly.
    """
    try:
        # Primary: Tahoma (excellent Arabic glyph coverage)
        pdfmetrics.registerFont(TTFont('Arabic', 'C:/Windows/Fonts/tahoma.ttf'))
        pdfmetrics.registerFont(TTFont('ArabicBold', 'C:/Windows/Fonts/tahomabd.ttf'))
        pdfmetrics.registerFont(TTFont('Latin', 'C:/Windows/Fonts/cambria.ttc'))
        pdfmetrics.registerFont(TTFont('LatinBold', 'C:/Windows/Fonts/cambriab.ttf'))
        return 'Arabic', 'ArabicBold'
    except Exception:
        try:
            # Fallback: Dubai (professional but limited presentation forms)
            pdfmetrics.registerFont(TTFont('Arabic', 'C:/Windows/Fonts/DUBAI-REGULAR.TTF'))
            pdfmetrics.registerFont(TTFont('ArabicBold', 'C:/Windows/Fonts/DUBAI-MEDIUM.TTF'))
            pdfmetrics.registerFont(TTFont('Latin', 'C:/Windows/Fonts/cambria.ttc'))
            pdfmetrics.registerFont(TTFont('LatinBold', 'C:/Windows/Fonts/cambriab.ttf'))
            return 'Arabic', 'ArabicBold'
        except Exception:
            try:
                # Last fallback: Arial
                pdfmetrics.registerFont(TTFont('Arabic', 'C:/Windows/Fonts/arial.ttf'))
                pdfmetrics.registerFont(TTFont('ArabicBold', 'C:/Windows/Fonts/arialbd.ttf'))
                return 'Arabic', 'ArabicBold'
            except Exception:
                return 'Helvetica', 'Helvetica-Bold'

FONT, FONT_BOLD = _register_fonts()


# ── Colors ──────────────────────────────────────────────────────────────────
NAVY = colors.HexColor("#0A1628")
GOLD = colors.HexColor("#D4AF37")
LIGHT_BG = colors.HexColor("#F5F5F0")
INK = colors.HexColor("#1A1A1A")
LIGHT_GRAY = colors.HexColor("#E8E8E8")
WHITE = colors.white


# ── Styles ──────────────────────────────────────────────────────────────────
def _get_styles():
    styles = getSampleStyleSheet()

    # Cover page styles (centered)
    styles.add(ParagraphStyle(
        "CoverTitle", parent=styles["Title"],
        fontName=FONT_BOLD, fontSize=26, leading=32, textColor=NAVY,
        spaceAfter=6*mm, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "CoverSubtitle", parent=styles["Normal"],
        fontName=FONT, fontSize=13, leading=17, textColor=GOLD,
        spaceAfter=8*mm, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "CoverInfo", parent=styles["Normal"],
        fontName=FONT, fontSize=10.5, leading=15, textColor=INK,
        spaceAfter=3*mm, alignment=TA_CENTER,
    ))

    # Headings
    styles.add(ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontName=FONT_BOLD, fontSize=16, leading=20, textColor=NAVY,
        spaceBefore=8*mm, spaceAfter=4*mm,
    ))
    styles.add(ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontName=FONT_BOLD, fontSize=13, leading=17, textColor=NAVY,
        spaceBefore=5*mm, spaceAfter=3*mm,
    ))
    styles.add(ParagraphStyle(
        "H3", parent=styles["Heading3"],
        fontName=FONT_BOLD, fontSize=11, leading=14, textColor=INK,
        spaceBefore=4*mm, spaceAfter=2*mm,
    ))

    # Body text — Arabic (RTL)
    styles.add(ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName=FONT, fontSize=10, leading=14.5, textColor=INK,
        spaceAfter=2.5*mm, alignment=TA_RIGHT, wordWrap='CJK',
    ))
    # Body text — Latin (LTR)
    styles.add(ParagraphStyle(
        "BodyLTR", parent=styles["Normal"],
        fontName=FONT, fontSize=10, leading=14.5, textColor=INK,
        spaceAfter=2.5*mm, alignment=TA_LEFT,
    ))
    # Bold body
    styles.add(ParagraphStyle(
        "BodyBold", parent=styles["Normal"],
        fontName=FONT_BOLD, fontSize=10, leading=14.5, textColor=INK,
        spaceAfter=2.5*mm, alignment=TA_RIGHT,
    ))
    # Right-aligned body
    styles.add(ParagraphStyle(
        "BodyRight", parent=styles["Normal"],
        fontName=FONT, fontSize=10, leading=14.5, textColor=INK,
        spaceAfter=2.5*mm, alignment=TA_RIGHT,
    ))

    # Bullet points
    styles.add(ParagraphStyle(
        "BulletItem", parent=styles["Normal"],
        fontName=FONT, fontSize=10, leading=14, textColor=INK,
        leftIndent=15, rightIndent=5, spaceAfter=2*mm,
        bulletIndent=5, alignment=TA_RIGHT,
    ))

    # Table styles
    styles.add(ParagraphStyle(
        "TableHeader", parent=styles["Normal"],
        fontName=FONT_BOLD, fontSize=9, textColor=WHITE, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "TableCell", parent=styles["Normal"],
        fontName=FONT, fontSize=8.5, textColor=INK, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "TableCellRight", parent=styles["Normal"],
        fontName=FONT, fontSize=8.5, textColor=INK, alignment=TA_RIGHT,
    ))

    # Footer
    styles.add(ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName=FONT, fontSize=7.5, textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
    ))

    return styles


# ── Header/Footer ───────────────────────────────────────────────────────────
def _header_footer(canvas, doc, business_name="DSC Digital Services Center"):
    canvas.saveState()
    w, h = A4

    # Header line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(2)
    canvas.line(20*mm, h - 18*mm, w - 20*mm, h - 18*mm)

    # Header text — left side (Latin)
    canvas.setFont("Latin", 7.5)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawString(20*mm, h - 16*mm, "DSC Digital Services Center")

    # Header text — right side (may be Arabic)
    if _has_arabic(business_name):
        canvas.setFont(FONT, 7.5)
        reshaped_name = _reshape_arabic(business_name)
        canvas.drawRightString(w - 20*mm, h - 16*mm, reshaped_name)
    else:
        canvas.setFont("Latin", 7.5)
        canvas.drawRightString(w - 20*mm, h - 16*mm, business_name)

    # Footer line
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, 18*mm, w - 20*mm, 18*mm)

    # Footer text
    canvas.setFont("Latin", 7.5)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawString(20*mm, 13*mm, "www.dsc-dz.com | contact@dsc-dz.com")
    canvas.drawRightString(w - 20*mm, 13*mm, f"Page {doc.page}")

    canvas.restoreState()


# ── Markdown Parser ─────────────────────────────────────────────────────────
def _has_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', text))


def _reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper connected rendering.

    Uses arabic-reshaper to join letters, then get_display() for
    correct visual ordering (right-to-left character sequence).
    """
    if not _has_arabic(text):
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def _escape_xml(text: str) -> str:
    """Escape XML special characters for ReportLab paragraphs."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def _reshape_mixed_segment(text: str) -> str:
    """Reshape a text segment that may contain Arabic + numbers/Latin.

    Split into runs of Arabic vs non-Arabic, reshape + reorder Arabic runs,
    then rejoin. This preserves Latin/number order while correctly
    displaying connected Arabic letters in visual (RTL) order.
    """
    if not _has_arabic(text):
        return text

    arabic_re = r'([\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+)'
    runs = re.split(arabic_re, text)
    result = []
    for run in runs:
        if re.match(r'^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+$', run):
            reshaped = arabic_reshaper.reshape(run)
            result.append(get_display(reshaped))
        else:
            result.append(run)

    return ''.join(result)


def _reshape_text(text: str) -> str:
    """Reshape Arabic in text while preserving XML tags.

    Handles text like '<b>اسم المشروع</b>' by reshaping
    only the text content inside tags.
    """
    if not _has_arabic(text):
        return text

    # Split by XML tags, reshape only text parts
    parts = re.split(r'(<[^>]+>)', text)
    result = []
    for part in parts:
        if part.startswith('<'):
            result.append(part)  # XML tag, keep as-is
        else:
            # For mixed content, reshape each segment separately
            result.append(_reshape_mixed_segment(part))
    return ''.join(result)


def _format_inline(text: str) -> str:
    """Convert markdown inline formatting to ReportLab XML with Arabic reshaping."""
    # Escape first
    text = _escape_xml(text)
    # Bold: **text** → <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic: *text* → <i>text</i> (but not **)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    # Code: `text` → <font face="Courier" size="9">text</font>
    text = re.sub(r'`(.+?)`', r'<font face="Courier" size="9">\1</font>', text)
    # Reshape Arabic text while preserving tags
    text = _reshape_text(text)
    return text


def _parse_md_table(lines: list) -> list:
    """Parse markdown table lines into headers and rows."""
    if len(lines) < 2:
        return [], []

    # First line: headers
    header_line = lines[0].strip()
    headers = [h.strip() for h in header_line.split("|") if h.strip()]

    # Skip separator line (lines[1])
    rows = []
    for line in lines[2:]:
        line = line.strip()
        if not line or line.startswith("|---") or line.startswith("| ---"):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if cells:
            rows.append(cells)

    return headers, rows


def _make_table(headers: list, rows: list, col_widths: list = None) -> Table:
    """Create a styled table from headers and rows."""
    # Use our custom styles with Arabic font, NOT built-in ReportLab styles
    header_style = ParagraphStyle(
        "TblHeader", fontName=FONT_BOLD, fontSize=10, textColor=WHITE,
        alignment=TA_CENTER, leading=14,
    )
    cell_style = ParagraphStyle(
        "TblCell", fontName=FONT, fontSize=9.5, textColor=INK,
        alignment=TA_CENTER, leading=13, wordWrap='CJK',
    )

    data = [[Paragraph(_format_inline(h), header_style) for h in headers]]
    for row in rows:
        data.append([Paragraph(_format_inline(c), cell_style) for c in row])

    if col_widths is None:
        available = 170*mm
        col_widths = [available / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("FONTNAME", (0, 1), (-1, -1), FONT),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def md_to_flowables(md_text: str, styles) -> list:
    """Convert markdown text to ReportLab flowables.

    Handles: # headings, | tables |, - bullets, **bold**, empty lines, plain text.
    """
    flowables = []
    lines = md_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        # Empty line → spacer
        if not stripped:
            flowables.append(Spacer(1, 2*mm))
            i += 1
            continue

        # Table detection: line starts with |
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            headers, rows = _parse_md_table(table_lines)
            if headers and rows:
                # Calculate column widths
                n = len(headers)
                available = 170*mm
                col_w = [available / n] * n
                flowables.append(Spacer(1, 2*mm))
                flowables.append(_make_table(headers, rows, col_w))
                flowables.append(Spacer(1, 3*mm))
            continue

        # Headings
        if stripped.startswith("### "):
            text = _format_inline(stripped[4:])
            flowables.append(Paragraph(text, styles["H3"]))
            i += 1
            continue
        if stripped.startswith("## "):
            text = _format_inline(stripped[3:])
            flowables.append(Paragraph(text, styles["H2"]))
            i += 1
            continue
        if stripped.startswith("# "):
            text = _format_inline(stripped[2:])
            flowables.append(Paragraph(text, styles["H1"]))
            i += 1
            continue

        # Bullet points
        if stripped.startswith("- ") or stripped.startswith("* "):
            text = _format_inline(stripped[2:])
            flowables.append(Paragraph(f"• {text}", styles["BulletItem"]))
            i += 1
            continue

        # Numbered list items (1. 2. etc.)
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            num, text = m.group(1), m.group(2)
            text = _format_inline(text)
            flowables.append(Paragraph(f"{num}. {text}", styles["BulletItem"]))
            i += 1
            continue

        # Bold-only line
        if stripped.startswith("**") and stripped.endswith("**"):
            text = _format_inline(stripped)
            flowables.append(Paragraph(text, styles["BodyBold"]))
            i += 1
            continue

        # Regular text
        text = _format_inline(stripped)
        flowables.append(Paragraph(text, styles["Body"]))
        i += 1

    return flowables


# ── Main Class ──────────────────────────────────────────────────────────────
class BusinessDocumentPDF:
    """Generate professional PDFs for DSC business documents."""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = str(Path(__file__).parent / "generated_output")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.styles = _get_styles()

    def _build_pdf(self, filename: str, elements: list,
                   business_name: str = "DSC Digital Services Center") -> str:
        filepath = self.output_dir / filename
        doc = SimpleDocTemplate(
            str(filepath), pagesize=A4,
            rightMargin=20*mm, leftMargin=20*mm,
            topMargin=25*mm, bottomMargin=25*mm,
        )
        doc.build(
            elements,
            onFirstPage=lambda c, d: _header_footer(c, d, business_name),
            onLaterPages=lambda c, d: _header_footer(c, d, business_name),
        )
        return str(filepath)

    def _cover_page(self, title: str, subtitle: str, info_lines: list) -> list:
        elements = [
            Spacer(1, 40*mm),
            Paragraph(_reshape_text(_escape_xml(title)), self.styles["CoverTitle"]),
            Paragraph(_reshape_text(_escape_xml(subtitle)), self.styles["CoverSubtitle"]),
            Spacer(1, 10*mm),
        ]
        for line in info_lines:
            elements.append(Paragraph(_reshape_text(_escape_xml(line)), self.styles["CoverInfo"]))
        elements.append(Spacer(1, 20*mm))
        elements.append(HRFlowable(width="60%", color=GOLD, thickness=2))
        elements.append(PageBreak())
        return elements

    def _section(self, title: str, level: str = "h1") -> Paragraph:
        style_key = {"h1": "H1", "h2": "H2", "h3": "H3"}.get(level, "H1")
        return Paragraph(_format_inline(title), self.styles[style_key])

    def _body(self, text: str) -> Paragraph:
        return Paragraph(_format_inline(text), self.styles["Body"])

    def _bullet(self, text: str) -> Paragraph:
        return Paragraph(f"• {_format_inline(text)}", self.styles["BulletItem"])

    # ── Feasibility Study PDF ───────────────────────────────────────────────
    def feasibility(self, data: dict) -> str:
        """Generate feasibility study PDF from generator output.

        data = {
            "project_name": "...",
            "business_type": "...",
            "wilaya": "...",
            "investment_amount": 350000,
            "sections": [{"title": "...", "content": "markdown string"}],
            "real_financials": {...}  # optional
        }
        """
        project = data.get("project_name", "Project")
        biz_type = data.get("business_type", "Business")
        wilaya = data.get("wilaya", "Algeria")
        investment = data.get("investment_amount", 0)
        rf = data.get("real_financials")

        elements = self._cover_page(
            f"Étude de Faisabilité\n{project}",
            f"{biz_type} — {wilaya}",
            [
                f"Montant d'investissement: {investment:,.0f} DZD",
                f"Date: {datetime.now().strftime('%d/%m/%Y')}",
                "Établi par: DSC Digital Services Center",
            ]
        )

        # Real financials summary table (if available)
        if rf:
            elements.append(self._section("Résumé Financier", "h1"))
            summary_rows = [
                ["VAN", f"{rf.get('van', 0):,.0f} DZD"],
                ["TRI", f"{rf.get('tri', 0)*100:.1f}%"],
                ["Délai de récupération", f"{rf.get('payback', 0):.1f} ans"],
                ["Seuil de rentabilité", f"{rf.get('breakeven', 0):,.0f} DZD/an"],
                ["Marge nette Année 1", f"{rf.get('net_margin_year1', 0):,.0f} DZD"],
            ]
            summary_table = _make_table(
                ["Indicateur", "Valeur"],
                summary_rows,
                [85*mm, 85*mm]
            )
            elements.append(summary_table)
            elements.append(Spacer(1, 5*mm))

        # Sections with markdown parsing
        sections = data.get("sections", [])
        for section in sections:
            title = section.get("title", "Section")
            content = section.get("content", "")

            elements.append(self._section(title, "h1"))

            if isinstance(content, str) and content.strip():
                flowables = md_to_flowables(content, self.styles)
                elements.extend(flowables)
            elif isinstance(content, list):
                for item in content:
                    elements.append(self._bullet(str(item)))

            elements.append(Spacer(1, 3*mm))

        return self._build_pdf(
            f"feasibility_{project.replace(' ', '_')}.pdf",
            elements, project
        )

    # ── Business Plan PDF ───────────────────────────────────────────────────
    def business_plan(self, data: dict) -> str:
        project = data.get("project_name", "Project")
        biz_type = data.get("business_type", "Business")

        elements = self._cover_page(
            f"Business Plan\n{project}",
            biz_type,
            [
                f"Date: {datetime.now().strftime('%d/%m/%Y')}",
                "Établi par: DSC Digital Services Center",
            ]
        )

        sections = data.get("sections", [])
        for section in sections:
            elements.append(self._section(section.get("title", "Section"), "h1"))
            content = section.get("content", "")
            if isinstance(content, str) and content.strip():
                flowables = md_to_flowables(content, self.styles)
                elements.extend(flowables)
            elif isinstance(content, list):
                for item in content:
                    elements.append(self._bullet(str(item)))

        return self._build_pdf(
            f"business_plan_{project.replace(' ', '_')}.pdf",
            elements, project
        )

    # ── Market Research PDF ─────────────────────────────────────────────────
    def market_research(self, data: dict) -> str:
        sector = data.get("sector", "Sector")
        wilaya = data.get("wilaya", "Algeria")

        elements = self._cover_page(
            f"Étude de Marché\n{sector}",
            wilaya,
            [
                f"Date: {datetime.now().strftime('%d/%m/%Y')}",
                "Établi par: DSC Digital Services Center",
            ]
        )

        sections = data.get("sections", [])
        for section in sections:
            elements.append(self._section(section.get("title", "Section"), "h1"))
            content = section.get("content", "")
            if isinstance(content, str) and content.strip():
                flowables = md_to_flowables(content, self.styles)
                elements.extend(flowables)

        return self._build_pdf(
            f"market_research_{sector.replace(' ', '_')}.pdf",
            elements, sector
        )

    # ── Financial Projections PDF ───────────────────────────────────────────
    def financial_projections(self, data: dict) -> str:
        project = data.get("project_name", "Project")

        elements = self._cover_page(
            f"Prévisions Financières\n{project}",
            "5 ans prévisionnels",
            [
                f"Date: {datetime.now().strftime('%d/%m/%Y')}",
                "Établi par: DSC Digital Services Center",
            ]
        )

        sections = data.get("sections", [])
        for section in sections:
            elements.append(self._section(section.get("title", "Section"), "h1"))
            content = section.get("content", "")
            if isinstance(content, str) and content.strip():
                flowables = md_to_flowables(content, self.styles)
                elements.extend(flowables)

        return self._build_pdf(
            f"financial_projections_{project.replace(' ', '_')}.pdf",
            elements, project
        )

    # ── Marketing Plan PDF ──────────────────────────────────────────────────
    def marketing_plan(self, data: dict) -> str:
        project = data.get("project_name", "Project")

        elements = self._cover_page(
            f"Plan Marketing\n{project}",
            "Stratégie digitale & traditionnelle",
            [
                f"Date: {datetime.now().strftime('%d/%m/%Y')}",
                "Établi par: DSC Digital Services Center",
            ]
        )

        sections = data.get("sections", [])
        for section in sections:
            elements.append(self._section(section.get("title", "Section"), "h1"))
            content = section.get("content", "")
            if isinstance(content, str) and content.strip():
                flowables = md_to_flowables(content, self.styles)
                elements.extend(flowables)

        return self._build_pdf(
            f"marketing_plan_{project.replace(' ', '_')}.pdf",
            elements, project
        )

    # ── Invoice PDF ─────────────────────────────────────────────────────────
    def invoice(self, data: dict) -> str:
        doc_number = data.get("number", "INV-0001")
        client = data.get("client_name", "Client")
        items = data.get("items", [])
        total_ht = data.get("total_ht", 0)
        tva = data.get("tva", 0)
        total_ttc = data.get("total_ttc", 0)

        elements = [
            Spacer(1, 10*mm),
            Paragraph("FACTURE / INVOICE", self.styles["CoverTitle"]),
            Paragraph(f"N° {doc_number}", self.styles["CoverSubtitle"]),
            Spacer(1, 5*mm),
            Paragraph(f"<b>Client:</b> {client}", self.styles["Body"]),
            Paragraph(f"<b>Date:</b> {data.get('date', datetime.now().strftime('%d/%m/%Y'))}", self.styles["Body"]),
            Paragraph(f"<b>Échéance:</b> {data.get('due_date', '30 jours')}", self.styles["Body"]),
            Spacer(1, 5*mm),
        ]

        if items:
            headers = ["Description", "Qté", "PU (DZD)", "Total (DZD)"]
            rows = []
            for item in items:
                rows.append([
                    item.get("description", ""),
                    str(item.get("quantity", 1)),
                    f"{item.get('unit_price', 0):,.0f}",
                    f"{item.get('total', 0):,.0f}",
                ])
            t = _make_table(headers, rows, [80*mm, 20*mm, 35*mm, 35*mm])
            elements.append(t)
            elements.append(Spacer(1, 5*mm))

        elements.append(Paragraph(f"<b>Total HT:</b> {total_ht:,.0f} DZD", self.styles["BodyRight"]))
        elements.append(Paragraph(f"<b>TVA (19%):</b> {tva:,.0f} DZD", self.styles["BodyRight"]))
        elements.append(Paragraph(f"<b>Total TTC:</b> {total_ttc:,.0f} DZD", self.styles["BodyRight"]))
        elements.append(Spacer(1, 10*mm))
        elements.append(HRFlowable(width="100%", color=GOLD, thickness=1))
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("DSC Digital Services Center — contact@dsc-dz.com — +213 XXX XXX XXX", self.styles["Footer"]))

        return self._build_pdf(f"invoice_{doc_number}.pdf", elements, client)

    # ── Quote (Devis) PDF ───────────────────────────────────────────────────
    def quote(self, data: dict) -> str:
        doc_number = data.get("number", "DEV-0001")
        client = data.get("client_name", "Client")
        items = data.get("items", [])
        total_ht = data.get("total_ht", 0)
        tva = data.get("tva", 0)
        total_ttc = data.get("total_ttc", 0)

        elements = [
            Spacer(1, 10*mm),
            Paragraph("DEVIS / QUOTE", self.styles["CoverTitle"]),
            Paragraph(f"N° {doc_number}", self.styles["CoverSubtitle"]),
            Spacer(1, 5*mm),
            Paragraph(f"<b>Client:</b> {client}", self.styles["Body"]),
            Paragraph(f"<b>Date:</b> {data.get('date', datetime.now().strftime('%d/%m/%Y'))}", self.styles["Body"]),
            Paragraph(f"<b>Validité:</b> {data.get('validity', '30 jours')}", self.styles["Body"]),
            Spacer(1, 5*mm),
        ]

        if items:
            headers = ["Description", "Qté", "PU (DZD)", "Total (DZD)"]
            rows = []
            for item in items:
                rows.append([
                    item.get("description", ""),
                    str(item.get("quantity", 1)),
                    f"{item.get('unit_price', 0):,.0f}",
                    f"{item.get('total', 0):,.0f}",
                ])
            t = _make_table(headers, rows, [80*mm, 20*mm, 35*mm, 35*mm])
            elements.append(t)
            elements.append(Spacer(1, 5*mm))

        elements.append(Paragraph(f"<b>Total HT:</b> {total_ht:,.0f} DZD", self.styles["BodyRight"]))
        elements.append(Paragraph(f"<b>TVA (19%):</b> {tva:,.0f} DZD", self.styles["BodyRight"]))
        elements.append(Paragraph(f"<b>Total TTC:</b> {total_ttc:,.0f} DZD", self.styles["BodyRight"]))

        return self._build_pdf(f"quote_{doc_number}.pdf", elements, client)

    # ── Generic Document PDF ────────────────────────────────────────────────
    def generic(self, title: str, content: str, filename: str = None) -> str:
        if filename is None:
            filename = f"{title.replace(' ', '_').lower()}.pdf"

        elements = self._cover_page(title, "", [
            f"Date: {datetime.now().strftime('%d/%m/%Y')}",
            "Établi par: DSC Digital Services Center",
        ])

        flowables = md_to_flowables(content, self.styles)
        elements.extend(flowables)

        return self._build_pdf(filename, elements)


# ── Self-Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pdf = BusinessDocumentPDF()

    # Test invoice
    invoice_data = {
        "number": "INV-2026-001",
        "client_name": "Ets Abdelli",
        "date": "05/08/2026",
        "due_date": "05/09/2026",
        "items": [
            {"description": "Étude de faisabilité quincaillerie", "quantity": 1, "unit_price": 25000, "total": 25000},
            {"description": "Business plan complet", "quantity": 1, "unit_price": 30000, "total": 30000},
            {"description": "Logo & identité visuelle", "quantity": 1, "unit_price": 12000, "total": 12000},
        ],
        "total_ht": 67000,
        "tva": 12730,
        "total_ttc": 79730,
    }
    path = pdf.invoice(invoice_data)
    print(f"Invoice: {path}")

    # Test quote
    quote_data = {
        "number": "DEV-2026-001",
        "client_name": "Nouvelle Boutique El Bayadh",
        "date": "05/08/2026",
        "validity": "30 jours",
        "items": [
            {"description": "Étude de faisabilité complète (25-35 pages)", "quantity": 1, "unit_price": 45000, "total": 45000},
            {"description": "Prévisions financières 5 ans + VAN/TRI", "quantity": 1, "unit_price": 20000, "total": 20000},
            {"description": "AAPI scoring & optimisation", "quantity": 1, "unit_price": 100000, "total": 100000},
        ],
        "total_ht": 165000,
        "tva": 31350,
        "total_ttc": 196350,
    }
    path = pdf.quote(quote_data)
    print(f"Quote: {path}")

    # Test feasibility with markdown content
    feasibility_data = {
        "project_name": "مركز الخدمات الرقمية",
        "business_type": "مركز خدمات رقمية",
        "wilaya": "البيض",
        "investment_amount": 350000,
        "sections": [
            {
                "title": "1. تحديد هوية صاحب المشروع",
                "content": """**اسم صاحب المشروع:** [الاسم الكامل]
**الجنسية:** جزائرية
**المؤهل:** شهادة جامعية
**الخبرة:** [عدد] سنوات في בתחום

### الأهداف
- تلبية احتياجات السوق المحلي
- خلق فرص عمل للشباب
- المساهمة في التحول الرقمي"""
            },
            {
                "title": "2. وصف المشروع",
                "content": """يهدف هذا المشروع إلى إنشاء مركز خدمات رقمية متكامل يوفر:

| الخدمة | السعر الشهري | عدد الزبائن المتوقع |
|--------|-------------|-------------------|
| تصميم المواقع | 15,000 دج | 10 |
| إدارة وسائل التواصل | 25,000 دج | 5 |
| التسويق الرقمي | 20,000 دج | 8 |
| التدريب | 10,000 دج | 15 |

### الميزة التنافسية
- فريق عمل شبابي ومبدع
- أسعار تنافسية
- خدمة ما بعد البيع"""
            },
            {
                "title": "3. الجدوى المالية",
                "content": """### حساب الاستثمار

| البند | المبلغ (دج) |
|-------|------------|
| تجهيزات مكتبية | 150,000 |
| تجهيزات رقمية | 120,000 |
| إيجارперв | 60,000 |
| رأس المال العامل | 20,000 |
| **المجموع** | **350,000** |

### حساب الأرباح والخسائر
- الإيراد السنوي المتوقع: 1,800,000 دج
- التكاليف السنوية: 1,200,000 دج
- **صافي الربح: 600,000 دج/سنة**"""
            },
        ],
    }
    path = pdf.feasibility(feasibility_data)
    print(f"Feasibility: {path}")

    print("\nAll PDFs generated successfully!")
