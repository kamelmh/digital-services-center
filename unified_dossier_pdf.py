"""Unified Dossier PDF — Compile all generator outputs into one professional PDF.

Uses ReportLab with:
- Cover page (client info, DSC branding)
- Table of contents
- Feasibility study sections
- Financial projections with proper tables
- AAPI scoring summary
- Quality report
- DSC branding (navy/gold header/footer)
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart


# ── Colors ──────────────────────────────────────────────────────────────────
NAVY = colors.HexColor("#0A1628")
GOLD = colors.HexColor("#D4AF37")
LIGHT_BG = colors.HexColor("#F5F5F0")
INK = colors.HexColor("#1A1A1A")
LIGHT_GRAY = colors.HexColor("#E8E8E8")
WHITE = colors.white
GREEN = colors.HexColor("#28a745")
RED = colors.HexColor("#dc3545")
ORANGE = colors.HexColor("#ffc107")


def _header_footer(canvas, doc, client_name="Client"):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(2)
    canvas.line(20*mm, h - 18*mm, w - 20*mm, h - 18*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawString(20*mm, h - 16*mm, "DSC Digital Services Center")
    canvas.drawRightString(w - 20*mm, h - 16*mm, client_name)
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, 18*mm, w - 20*mm, 18*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawString(20*mm, 13*mm, "contact@dsc-dz.com")
    canvas.drawRightString(w - 20*mm, 13*mm, f"Page {doc.page}")
    canvas.restoreState()


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("CoverTitle", parent=s["Title"], fontSize=26, leading=32, textColor=NAVY, spaceAfter=6*mm, alignment=TA_CENTER))
    s.add(ParagraphStyle("CoverSub", parent=s["Normal"], fontSize=14, leading=18, textColor=GOLD, spaceAfter=8*mm, alignment=TA_CENTER))
    s.add(ParagraphStyle("CoverInfo", parent=s["Normal"], fontSize=11, leading=16, textColor=INK, spaceAfter=3*mm, alignment=TA_CENTER))
    s.add(ParagraphStyle("H1", parent=s["Heading1"], fontSize=18, leading=22, textColor=NAVY, spaceBefore=10*mm, spaceAfter=5*mm))
    s.add(ParagraphStyle("H2", parent=s["Heading2"], fontSize=14, leading=18, textColor=NAVY, spaceBefore=6*mm, spaceAfter=3*mm))
    s.add(ParagraphStyle("H3", parent=s["Heading3"], fontSize=12, leading=15, textColor=INK, spaceBefore=4*mm, spaceAfter=2*mm))
    s.add(ParagraphStyle("Body", parent=s["Normal"], fontSize=10.5, leading=15, textColor=INK, spaceAfter=3*mm, alignment=TA_JUSTIFY))
    s.add(ParagraphStyle("BodyRight", parent=s["Normal"], fontSize=10.5, leading=15, textColor=INK, spaceAfter=3*mm, alignment=TA_RIGHT))
    s.add(ParagraphStyle("BulletItem", parent=s["Normal"], fontSize=10.5, leading=15, textColor=INK, leftIndent=15, spaceAfter=2*mm))
    s.add(ParagraphStyle("Small", parent=s["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#666666"), spaceAfter=2*mm))
    return s


def _make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    if col_widths is None:
        col_widths = [170*mm / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


class UnifiedDossierPDF:
    """Compile all dossier sections into one professional PDF."""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = str(Path(__file__).parent / "generated_output")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.S = _styles()

    def compile(
        self,
        client_name: str,
        business_type: str,
        wilaya: str,
        investment: int,
        feasibility: dict,
        financials: dict,
        aapi: dict,
        quality: dict,
        profitability: dict = None,
    ) -> str:
        """Build the unified PDF and return filepath."""
        filename = f"dossier_{client_name.replace(' ', '_')}_{datetime.now():%Y%m%d}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath), pagesize=A4,
            rightMargin=20*mm, leftMargin=20*mm,
            topMargin=25*mm, bottomMargin=25*mm,
        )

        elements = []
        elements += self._cover(client_name, business_type, wilaya, investment)
        elements += self._toc()
        elements += self._feasibility_section(feasibility)
        elements += self._financials_section(financials, profitability)
        elements += self._aapi_section(aapi)
        elements += self._quality_section(quality)
        elements += self._closing()

        doc.build(
            elements,
            onFirstPage=lambda c, d: _header_footer(c, d, client_name),
            onLaterPages=lambda c, d: _header_footer(c, d, client_name),
        )
        return str(filepath)

    # ── Cover Page ──────────────────────────────────────────────────────────
    def _cover(self, client, biz_type, wilaya, investment):
        now = datetime.now()
        return [
            Spacer(1, 35*mm),
            Paragraph("ÉTUDE DE FAISABILITÉ", self.S["CoverTitle"]),
            Paragraph("TECHNICO-ÉCONOMIQUE", self.S["CoverTitle"]),
            Spacer(1, 8*mm),
            Paragraph(f"{biz_type}", self.S["CoverSub"]),
            Spacer(1, 8*mm),
            HRFlowable(width="40%", color=GOLD, thickness=2),
            Spacer(1, 8*mm),
            Paragraph(f"<b>Client:</b> {client}", self.S["CoverInfo"]),
            Paragraph(f"<b>Localisation:</b> {wilaya}", self.S["CoverInfo"]),
            Paragraph(f"<b>Investissement:</b> {investment:,.0f} DZD", self.S["CoverInfo"]),
            Paragraph(f"<b>Date:</b> {now:%d/%m/%Y}", self.S["CoverInfo"]),
            Spacer(1, 15*mm),
            Paragraph("Établi par", self.S["CoverInfo"]),
            Paragraph("<b>DSC Digital Services Center</b>", self.S["CoverInfo"]),
            Paragraph("contact@dsc-dz.com", self.S["CoverInfo"]),
            PageBreak(),
        ]

    # ── Table of Contents ───────────────────────────────────────────────────
    def _toc(self):
        elements = [
            Paragraph("TABLE DES MATIÈRES", self.S["H1"]),
            HRFlowable(width="100%", color=GOLD, thickness=1),
            Spacer(1, 5*mm),
        ]
        toc_items = [
            ("1.", "Présentation du Projet"),
            ("2.", "Étude de Marché"),
            ("3.", "Étude Technique"),
            ("4.", "Étude Financière"),
            ("5.", "Prévisions Financières (5 ans)"),
            ("6.", "Analyse VAN / TRI"),
            ("7.", "Scoring AAPI"),
            ("8.", "Rapport de Qualité"),
        ]
        for num, title in toc_items:
            elements.append(Paragraph(f"<b>{num}</b> {title}", self.S["Body"]))
        elements.append(PageBreak())
        return elements

    # ── Feasibility Section ─────────────────────────────────────────────────
    def _feasibility_section(self, feasibility):
        elements = [
            Paragraph("1. PRÉSENTATION DU PROJET", self.S["H1"]),
            HRFlowable(width="100%", color=GOLD, thickness=1),
        ]

        if "error" in feasibility:
            elements.append(Paragraph(f"<i>Erreur: {feasibility['error']}</i>", self.S["Small"]))
            return elements

        sections = feasibility.get("sections", {})
        if not sections:
            content = feasibility.get("content", "")
            if content:
                elements += self._parse_markdown(content)
            else:
                elements.append(Paragraph("<i>Aucune donnée disponible</i>", self.S["Small"]))
            return elements

        section_num = 2
        for name, body in sections.items():
            elements.append(Paragraph(f"{section_num}. {name}", self.S["H2"]))
            if isinstance(body, str):
                elements += self._parse_markdown(body)
            section_num += 1

        return elements

    # ── Financials Section ──────────────────────────────────────────────────
    def _financials_section(self, financials, profitability):
        elements = [
            Paragraph("5. PRÉVISIONS FINANCIÈRES", self.S["H1"]),
            HRFlowable(width="100%", color=GOLD, thickness=1),
        ]

        # Profitability summary table from business defaults
        if profitability:
            elements.append(Paragraph("5.1 Résumé de Profitabilité (Estimation)", self.S["H2"]))
            rows = [
                ["Chiffre d'affaires annuel", f"{profitability.get('annual_revenue', 0):,.0f} DZD"],
                ["Coût d'achat (COGS)", f"{profitability.get('annual_cogs', 0):,.0f} DZD"],
                ["Charges opérationnelles", f"{profitability.get('annual_operating', 0):,.0f} DZD"],
                ["Marge brute", f"{profitability.get('gross_margin', 0):.1%}"],
                ["Résultat net (avant impôt)", f"{profitability.get('net_profit_before_tax', 0):,.0f} DZD"],
                ["Résultat net (après impôt 19%)", f"{profitability.get('net_profit_after_tax', 0):,.0f} DZD"],
                ["Marge nette", f"{profitability.get('net_margin', 0):.1%}"],
                ["Délai de récupération", f"{profitability.get('payback_years', 0):.1f} ans"],
                ["ROI annuel", f"{profitability.get('roi_annual', 0):.1%}"],
            ]
            t = _make_table(["Indicateur", "Valeur"], rows, [100*mm, 70*mm])
            elements.append(t)
            elements.append(Spacer(1, 5*mm))

        # LLM-generated financial content
        if "error" not in financials:
            content = financials.get("content", "")
            if content:
                elements.append(Paragraph("5.2 Détails des Prévisions", self.S["H2"]))
                elements += self._parse_markdown(content)
        else:
            elements.append(Paragraph(f"<i>Erreur: {financials.get('error', 'N/A')}</i>", self.S["Small"]))

        return elements

    # ── AAPI Section ────────────────────────────────────────────────────────
    def _aapi_section(self, aapi):
        elements = [
            Paragraph("7. SCORING AAPI", self.S["H1"]),
            HRFlowable(width="100%", color=GOLD, thickness=1),
        ]

        if "error" in aapi:
            elements.append(Paragraph(f"<i>Erreur: {aapi['error']}</i>", self.S["Small"]))
            return elements

        total = aapi.get("total", 0)
        pct = aapi.get("percentage", 0)
        rating = aapi.get("rating", "N/A")

        # Score summary
        color = GREEN if pct >= 60 else ORANGE if pct >= 40 else RED
        elements.append(Paragraph(
            f'<font color="{color.hexval()}">{total}/1500</font> — {rating} ({pct:.0f}%)',
            self.S["H2"]
        ))

        # Details table
        details = aapi.get("details", {})
        if details:
            criteria_map = {
                "activity_type": ("Nature activité", 420),
                "investment_amount": ("Investissement", 360),
                "employment": ("Emploi", 300),
                "equity_contribution": ("Fonds propres", 200),
                "local_content": ("Contenu local", 60),
                "employment_permanence": ("Pérennité emploi", 60),
                "investment_extension": ("Extension", 70),
                "export_diversification": ("Exportations", 30),
            }
            rows = []
            for key, (label, max_pts) in criteria_map.items():
                val = details.get(key, 0)
                p = (val / max_pts * 100) if max_pts else 0
                bar = "█" * int(p / 10) + "░" * (10 - int(p / 10))
                rows.append([label, f"{val}/{max_pts}", f"{bar}", f"{p:.0f}%"])

            t = _make_table(["Critère", "Score", "Barre", "%"], rows, [50*mm, 30*mm, 50*mm, 25*mm])
            elements.append(t)
            elements.append(Spacer(1, 5*mm))

        # Suggestions
        suggestions = aapi.get("suggestions", [])
        if suggestions:
            elements.append(Paragraph("Recommandations", self.S["H3"]))
            for s in suggestions:
                elements.append(Paragraph(
                    f"• <b>{s.get('criterion', '')}</b>: +{s.get('gap', 0)} pts — {s.get('advice', '')}",
                    self.S["BulletItem"]
                ))

        return elements

    # ── Quality Section ─────────────────────────────────────────────────────
    def _quality_section(self, quality):
        elements = [
            Paragraph("8. RAPPORT DE QUALITÉ", self.S["H1"]),
            HRFlowable(width="100%", color=GOLD, thickness=1),
        ]

        if not quality:
            elements.append(Paragraph("<i>Contrôles de qualité désactivés</i>", self.S["Small"]))
            return elements

        for gen_name, report in quality.items():
            elements.append(Paragraph(f"{gen_name}", self.S["H3"]))
            grade_color = GREEN if report.grade in ("A", "B") else ORANGE if report.grade == "C" else RED
            elements.append(Paragraph(
                f'Score: <font color="{grade_color.hexval()}">{report.overall_score:.0%} ({report.grade})</font> — {"PASS" if report.passed else "FAIL"}',
                self.S["Body"]
            ))
            for check in report.checks:
                status = "✓" if check.passed else "✗"
                elements.append(Paragraph(
                    f"  {status} {check.name}: {check.detail}",
                    self.S["Small"]
                ))

        return elements

    # ── Closing ─────────────────────────────────────────────────────────────
    def _closing(self):
        return [
            Spacer(1, 10*mm),
            HRFlowable(width="100%", color=GOLD, thickness=1),
            Spacer(1, 5*mm),
            Paragraph("Ce document a été établi par DSC Digital Services Center.", self.S["Body"]),
            Paragraph("Les données financières sont des estimations et doivent être vérifiées avant toute décision d'investissement.", self.S["Small"]),
            Paragraph("contact@dsc-dz.com | www.dsc-dz.com", self.S["Small"]),
        ]

    # ── Markdown Parser ─────────────────────────────────────────────────────
    def _parse_markdown(self, text: str) -> list:
        """Parse markdown-ish text into ReportLab elements."""
        elements = []
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Headings
            if line.startswith("### "):
                elements.append(Paragraph(line[4:], self.S["H3"]))
            elif line.startswith("## "):
                elements.append(Paragraph(line[3:], self.S["H2"]))
            elif line.startswith("# "):
                elements.append(Paragraph(line[2:], self.S["H1"]))
            # Bold lines
            elif line.startswith("**") and line.endswith("**"):
                elements.append(Paragraph(f"<b>{line[2:-2]}</b>", self.S["Body"]))
            # Table detection (| col | col |)
            elif line.startswith("|") and line.endswith("|"):
                # Collect consecutive table lines
                table_lines = [line]
                # This is a simple table parser — just render as formatted text
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if cells and not all(c.startswith("-") for c in cells):
                    row_text = " | ".join(cells)
                    elements.append(Paragraph(f"<font face='Courier' size='8'>{row_text}</font>", self.S["Small"]))
            # Horizontal rule
            elif line.startswith("---"):
                elements.append(HRFlowable(width="100%", color=LIGHT_GRAY, thickness=0.5))
            # Bullet
            elif line.startswith("- ") or line.startswith("* "):
                elements.append(Paragraph(f"• {line[2:]}", self.S["BulletItem"]))
            # Regular text
            else:
                # Escape HTML entities that ReportLab might choke on
                safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                elements.append(Paragraph(safe, self.S["Body"]))

        return elements
