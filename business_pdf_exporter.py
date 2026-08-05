"""Business Document PDF Exporter — Generate professional PDFs for all DSC services.

Uses ReportLab (works on Windows, no GTK dependency like WeasyPrint).
Supports: feasibility studies, business plans, market research, financial projections,
marketing plans, tax declarations, invoices, quotes, cover letters.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import os
import json
from datetime import datetime


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

    styles.add(ParagraphStyle(
        "CoverTitle", parent=styles["Title"],
        fontSize=28, leading=34, textColor=NAVY,
        spaceAfter=6*mm, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "CoverSubtitle", parent=styles["Normal"],
        fontSize=14, leading=18, textColor=GOLD,
        spaceAfter=10*mm, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "CoverInfo", parent=styles["Normal"],
        fontSize=11, leading=16, textColor=INK,
        spaceAfter=3*mm, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=18, leading=22, textColor=NAVY,
        spaceBefore=10*mm, spaceAfter=5*mm,
        borderPadding=(0, 0, 2*mm, 0),
    ))
    styles.add(ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=14, leading=18, textColor=NAVY,
        spaceBefore=6*mm, spaceAfter=3*mm,
    ))
    styles.add(ParagraphStyle(
        "H3", parent=styles["Heading3"],
        fontSize=12, leading=15, textColor=INK,
        spaceBefore=4*mm, spaceAfter=2*mm,
    ))
    styles.add(ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10.5, leading=15, textColor=INK,
        spaceAfter=3*mm, alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        "BodyRight", parent=styles["Normal"],
        fontSize=10.5, leading=15, textColor=INK,
        spaceAfter=3*mm, alignment=TA_RIGHT,
    ))
    styles.add(ParagraphStyle(
        "BulletItem", parent=styles["Normal"],
        fontSize=10.5, leading=15, textColor=INK,
        leftIndent=15, spaceAfter=2*mm, bulletIndent=5,
    ))
    styles.add(ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "TableHeader", parent=styles["Normal"],
        fontSize=10, textColor=WHITE, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "TableCell", parent=styles["Normal"],
        fontSize=9.5, textColor=INK, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "TableCellLeft", parent=styles["Normal"],
        fontSize=9.5, textColor=INK, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        "PriceTag", parent=styles["Normal"],
        fontSize=11, textColor=GOLD, alignment=TA_CENTER,
    ))
    return styles


def _header_footer(canvas, doc, business_name="DSC Digital Services Center"):
    """Draw header and footer on every page."""
    canvas.saveState()
    w, h = A4

    # Header line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(2)
    canvas.line(20*mm, h - 18*mm, w - 20*mm, h - 18*mm)

    # Header text
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawString(20*mm, h - 16*mm, f"DSC Digital Services Center")
    canvas.drawRightString(w - 20*mm, h - 16*mm, business_name)

    # Footer
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, 18*mm, w - 20*mm, 18*mm)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawString(20*mm, 13*mm, f"www.dsc-dz.com | contact@dsc-dz.com")
    canvas.drawRightString(w - 20*mm, 13*mm, f"Page {doc.page}")

    canvas.restoreState()


def _make_table(headers, rows, col_widths=None):
    """Create a styled table."""
    data = [headers] + rows
    if col_widths is None:
        col_widths = [170*mm / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


class BusinessDocumentPDF:
    """Generate professional PDFs for DSC business documents."""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = str(Path(__file__).parent / "generated_output")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.styles = _get_styles()

    def _build_pdf(self, filename: str, elements: list, business_name: str = "DSC Digital Services Center"):
        """Build a PDF from elements."""
        filepath = self.output_dir / filename
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=25*mm,
            bottomMargin=25*mm,
        )
        doc.build(elements, onFirstPage=lambda c, d: _header_footer(c, d, business_name), onLaterPages=lambda c, d: _header_footer(c, d, business_name))
        return str(filepath)

    def _cover_page(self, title, subtitle, info_lines):
        """Generate a cover page."""
        elements = [
            Spacer(1, 40*mm),
            Paragraph(title, self.styles["CoverTitle"]),
            Paragraph(subtitle, self.styles["CoverSubtitle"]),
            Spacer(1, 10*mm),
        ]
        for line in info_lines:
            elements.append(Paragraph(line, self.styles["CoverInfo"]))
        elements.append(Spacer(1, 20*mm))
        elements.append(HRFlowable(width="60%", color=GOLD, thickness=2))
        elements.append(PageBreak())
        return elements

    def _section(self, title, level="h1"):
        """Generate a section heading."""
        style = self.styles[f"H{1 if level == 'h1' else 2 if level == 'h2' else 3}"]
        return Paragraph(title, style)

    def _body(self, text):
        """Generate body text."""
        return Paragraph(text, self.styles["Body"])

    def _bullet(self, text):
        """Generate a bullet point."""
        return Paragraph(f"• {text}", self.styles["BulletItem"])

    # ── Feasibility Study PDF ───────────────────────────────────────────────
    def feasibility(self, data: dict) -> str:
        """Generate feasibility study PDF from generator output."""
        project = data.get("project_name", "Project")
        biz_type = data.get("business_type", "Business")
        wilaya = data.get("wilaya", "Algeria")
        investment = data.get("investment_amount", 0)

        elements = self._cover_page(
            f"Étude de Faisabilité\n{project}",
            f"{biz_type} — {wilaya}",
            [
                f"Montant d'investissement: {investment:,.0f} DZD",
                f"Date: {datetime.now().strftime('%d/%m/%Y')}",
                "Établi par: DSC Digital Services Center",
            ]
        )

        sections = data.get("sections", [])
        for section in sections:
            elements.append(self._section(section.get("title", "Section")))
            content = section.get("content", "")
            if isinstance(content, str):
                for para in content.split("\n"):
                    para = para.strip()
                    if para:
                        elements.append(self._body(para))
            elif isinstance(content, list):
                for item in content:
                    elements.append(self._bullet(str(item)))

        return self._build_pdf(
            f"feasibility_{project.replace(' ', '_')}.pdf",
            elements, project
        )

    # ── Business Plan PDF ───────────────────────────────────────────────────
    def business_plan(self, data: dict) -> str:
        """Generate business plan PDF."""
        project = data.get("project_name", "Project")
        biz_type = data.get("business_type", "Business")

        elements = self._cover_page(
            f"Business Plan\n{project}",
            f"{biz_type}",
            [
                f"Date: {datetime.now().strftime('%d/%m/%Y')}",
                "Établi par: DSC Digital Services Center",
            ]
        )

        sections = data.get("sections", [])
        for section in sections:
            elements.append(self._section(section.get("title", "Section")))
            content = section.get("content", "")
            if isinstance(content, str):
                for para in content.split("\n"):
                    para = para.strip()
                    if para:
                        elements.append(self._body(para))

        return self._build_pdf(
            f"business_plan_{project.replace(' ', '_')}.pdf",
            elements, project
        )

    # ── Market Research PDF ─────────────────────────────────────────────────
    def market_research(self, data: dict) -> str:
        """Generate market research PDF."""
        sector = data.get("sector", "Sector")
        wilaya = data.get("wilaya", "Algeria")

        elements = self._cover_page(
            f"Étude de Marché\n{sector}",
            f"{wilaya}",
            [
                f"Date: {datetime.now().strftime('%d/%m/%Y')}",
                "Établi par: DSC Digital Services Center",
            ]
        )

        sections = data.get("sections", [])
        for section in sections:
            elements.append(self._section(section.get("title", "Section")))
            content = section.get("content", "")
            if isinstance(content, str):
                for para in content.split("\n"):
                    para = para.strip()
                    if para:
                        elements.append(self._body(para))

        return self._build_pdf(
            f"market_research_{sector.replace(' ', '_')}.pdf",
            elements, sector
        )

    # ── Financial Projections PDF ───────────────────────────────────────────
    def financial_projections(self, data: dict) -> str:
        """Generate financial projections PDF."""
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
            elements.append(self._section(section.get("title", "Section")))
            content = section.get("content", "")
            if isinstance(content, str):
                for para in content.split("\n"):
                    para = para.strip()
                    if para:
                        elements.append(self._body(para))

        return self._build_pdf(
            f"financial_projections_{project.replace(' ', '_')}.pdf",
            elements, project
        )

    # ── Marketing Plan PDF ──────────────────────────────────────────────────
    def marketing_plan(self, data: dict) -> str:
        """Generate marketing plan PDF."""
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
            elements.append(self._section(section.get("title", "Section")))
            content = section.get("content", "")
            if isinstance(content, str):
                for para in content.split("\n"):
                    para = para.strip()
                    if para:
                        elements.append(self._body(para))

        return self._build_pdf(
            f"marketing_plan_{project.replace(' ', '_')}.pdf",
            elements, project
        )

    # ── Invoice PDF ─────────────────────────────────────────────────────────
    def invoice(self, data: dict) -> str:
        """Generate invoice PDF."""
        doc_number = data.get("number", "INV-0001")
        client = data.get("client_name", "Client")
        items = data.get("items", [])
        total_ht = data.get("total_ht", 0)
        tva = data.get("tva", 0)
        total_ttc = data.get("total_ttc", 0)

        elements = [
            Spacer(1, 10*mm),
            Paragraph(f"FACTURE / INVOICE", self.styles["CoverTitle"]),
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

        return self._build_pdf(
            f"invoice_{doc_number}.pdf",
            elements, client
        )

    # ── Quote (Devis) PDF ───────────────────────────────────────────────────
    def quote(self, data: dict) -> str:
        """Generate quote PDF."""
        doc_number = data.get("number", "DEV-0001")
        client = data.get("client_name", "Client")
        items = data.get("items", [])
        total_ht = data.get("total_ht", 0)
        tva = data.get("tva", 0)
        total_ttc = data.get("total_ttc", 0)

        elements = [
            Spacer(1, 10*mm),
            Paragraph(f"DEVIS / QUOTE", self.styles["CoverTitle"]),
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

        return self._build_pdf(
            f"quote_{doc_number}.pdf",
            elements, client
        )

    # ── Generic Document PDF ────────────────────────────────────────────────
    def generic(self, title: str, content: str, filename: str = None) -> str:
        """Generate a generic PDF from markdown-like content."""
        if filename is None:
            filename = f"{title.replace(' ', '_').lower()}.pdf"

        elements = self._cover_page(title, "", [
            f"Date: {datetime.now().strftime('%d/%m/%Y')}",
            "Établi par: DSC Digital Services Center",
        ])

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("### "):
                elements.append(self._section(line[4:], "h3"))
            elif line.startswith("## "):
                elements.append(self._section(line[3:], "h2"))
            elif line.startswith("# "):
                elements.append(self._section(line[2:], "h1"))
            elif line.startswith("- ") or line.startswith("* "):
                elements.append(self._bullet(line[2:]))
            elif line.startswith("**") and line.endswith("**"):
                elements.append(Paragraph(f"<b>{line[2:-2]}</b>", self.styles["Body"]))
            else:
                elements.append(self._body(line))

        return self._build_pdf(filename, elements)


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

    print("PDF export working!")
