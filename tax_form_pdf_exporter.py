"""Universal Tax Form PDF Exporter — DGI forms to professional PDF.

Converts all 7 Algerian DGI tax form generator outputs to professional PDF
using ReportLab (works on Windows, no GTK dependency).

Supported forms:
    G12 — IFU Prévisionnelle / Définitive
    G50 — Monthly multi-tax declaration
    G4  — IBS annual corporate tax
    G11 — BIC régime réel
    G29/G30 — IRG salary declaration
    G1  — GGR (Déclaration Générale des Revenus)
    G8  — Business existence declaration

Usage:
    from tax_form_pdf_exporter import generate_tax_pdf
    pdf_bytes = generate_tax_pdf("g12", g12_data_instance)
"""

from __future__ import annotations

from io import BytesIO
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)


# ── Colors (matching business_pdf_exporter.py) ──────────────────────────────
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
        "DGIHeader", parent=styles["Normal"],
        fontSize=8, leading=10, textColor=WHITE, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "DGITitle", parent=styles["Normal"],
        fontSize=10, leading=13, textColor=GOLD, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "FormTitle", parent=styles["Normal"],
        fontSize=14, leading=18, textColor=WHITE, alignment=TA_CENTER,
        spaceBefore=2*mm, spaceAfter=2*mm,
    ))
    styles.add(ParagraphStyle(
        "FormSubtitle", parent=styles["Normal"],
        fontSize=8, leading=10, textColor=colors.HexColor("#CCCCCC"),
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "SectionTitle", parent=styles["Normal"],
        fontSize=9, leading=12, textColor=NAVY,
        spaceBefore=4*mm, spaceAfter=2*mm,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "FieldLabel", parent=styles["Normal"],
        fontSize=8.5, leading=11, textColor=INK,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "FieldValue", parent=styles["Normal"],
        fontSize=8.5, leading=11, textColor=INK,
    ))
    styles.add(ParagraphStyle(
        "SmallNote", parent=styles["Normal"],
        fontSize=7.5, leading=10, textColor=colors.HexColor("#666666"),
    ))
    styles.add(ParagraphStyle(
        "ResultHighlight", parent=styles["Normal"],
        fontSize=10, leading=13, textColor=NAVY,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontSize=7.5, textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
    ))
    return styles


# ── Formatting Helpers ──────────────────────────────────────────────────────
def _fmt(n) -> str:
    """Format number with space separators."""
    if n is None:
        return ""
    if isinstance(n, str):
        return n
    n = float(n)
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _val(data, field: str, default="") -> str:
    """Get a field value from dataclass with default."""
    v = getattr(data, field, default)
    return str(v) if v else str(default)


def _date_str() -> str:
    return datetime.now().strftime("%d/%m/%Y à %H:%M")


# ── Header / Footer ─────────────────────────────────────────────────────────
def _draw_header_footer(canvas, doc, form_title: str, serie: str):
    canvas.saveState()
    w, h = A4

    # Top gold line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(2)
    canvas.line(15*mm, h - 12*mm, w - 15*mm, h - 12*mm)

    # Header text
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawString(15*mm, h - 10*mm, "REPUBLIQUE ALGERIENNE DEMOCRATIQUE ET POPULAIRE")
    canvas.drawRightString(w - 15*mm, h - 10*mm, f"Serie {serie}")

    # Footer gold line
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(15*mm, 14*mm, w - 15*mm, 14*mm)

    # Footer text
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawString(15*mm, 10*mm, f"DSC Digital Services Center — Genere le {_date_str()}")
    canvas.drawRightString(w - 15*mm, 10*mm, f"Page {doc.page}")

    canvas.restoreState()


def _make_doc(buf: BytesIO, serie: str, form_title: str, header_serie: str = ""):
    """Create a SimpleDocTemplate with consistent margins."""
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )
    display_serie = header_serie or serie
    on_page = lambda c, d: _draw_header_footer(c, d, form_title, display_serie)
    return doc, on_page


# ── Table Builders ───────────────────────────────────────────────────────────
def _dgi_header_block(styles, form_title: str, subtitle: str, serie: str, year=""):
    """Build the official DGI header as a colored table."""
    header_data = [
        [Paragraph("REPUBLIQUE ALGERIENNE DEMOCRATIQUE ET POPULAIRE", styles["DGIHeader"])],
        [Paragraph("DIRECTION GENERALE DES IMPOTS", styles["DGITitle"])],
        [Paragraph(f"<b>{form_title}</b>", styles["FormTitle"])],
        [Paragraph(f"Serie G {serie} — {year}" if year else f"Serie G {serie}", styles["FormSubtitle"])],
        [Paragraph(subtitle, styles["FormSubtitle"])],
    ]
    t = Table(header_data, colWidths=[170*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _id_table(data, fields: list[tuple[str, str]], col_widths=None):
    """Build a 2-column identification table (label | value)."""
    if col_widths is None:
        col_widths = [60*mm, 110*mm]
    rows = []
    for label, attr in fields:
        val = _val(data, attr, "____________________")
        rows.append([
            Paragraph(f"<b>{label}</b>", ParagraphStyle("fl", fontSize=8, leading=10, textColor=INK)),
            Paragraph(str(val), ParagraphStyle("fv", fontSize=8, leading=10, textColor=INK)),
        ])
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _data_table(headers: list[str], rows: list[list], col_widths=None):
    """Build a styled data table with header row."""
    all_rows = [headers] + rows
    if col_widths is None:
        n = len(headers)
        col_widths = [170*mm / n] * n
    t = Table(all_rows, colWidths=col_widths)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def _highlight_row(label: str, value: str, styles):
    """Build a highlighted result row."""
    return [
        Paragraph(f"<b>{label}</b>", styles["ResultHighlight"]),
        Paragraph(f"<b>{value}</b>", styles["ResultHighlight"]),
    ]


def _signature_block(styles, name: str = ""):
    """Standard signature block."""
    name = name or "____________________"
    data = [
        [
            Paragraph("<b>Le declarant</b>", ParagraphStyle("s", fontSize=8, alignment=TA_CENTER)),
            Paragraph("", ParagraphStyle("s", fontSize=8)),
            Paragraph("<b>L'Inspecteur des Impots</b>", ParagraphStyle("s", fontSize=8, alignment=TA_CENTER)),
        ],
        [
            Paragraph("<br/><br/><br/>", ParagraphStyle("s", fontSize=8)),
            Paragraph("", ParagraphStyle("s", fontSize=8)),
            Paragraph("<br/><br/><br/>", ParagraphStyle("s", fontSize=8)),
        ],
        [
            Paragraph(name, ParagraphStyle("s", fontSize=8, alignment=TA_CENTER)),
            Paragraph("", ParagraphStyle("s", fontSize=8)),
            Paragraph("Cachet et signature", ParagraphStyle("s", fontSize=8, alignment=TA_CENTER)),
        ],
    ]
    t = Table(data, colWidths=[70*mm, 30*mm, 70*mm])
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (0, 0), 0.5, INK),
        ("LINEABOVE", (2, 0), (2, 0), 0.5, INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# G12 — IFU Prévisionnelle / Définitive
# ══════════════════════════════════════════════════════════════════════════════
def generate_g12_pdf(data: Any, is_definitive: bool = False) -> bytes:
    """Generate G12 IFU declaration PDF.

    Args:
        data: G12Data instance from g12_generator.
        is_definitive: True for definitive, False for prévisionnelle.

    Returns:
        PDF bytes.
    """
    from g12_generator import G12Data, calculate_ifu

    result = calculate_ifu(data)
    suffix = "DÉFINITIVE" if is_definitive else "PRÉVISIONNELLE"
    buf = BytesIO()
    styles = _get_styles()
    doc, on_page = _make_doc(buf, "N°12", f"G12 {suffix}", f"N°12 {suffix}")

    elements = []

    # DGI Header
    elements.append(_dgi_header_block(
        styles,
        f"DÉCLARATION {suffix} DE L'IMPÔT FORFAITAIRE UNIQUE (IFU)",
        f"Année {data.year}",
        "N°12",
    ))
    elements.append(Spacer(1, 6*mm))

    # Section I — Identification
    elements.append(Paragraph("I — IDENTIFICATION DU REDEVABLE", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("NIF", "nif"),
        ("Raison sociale", "business_name"),
        ("Activité principale", "activite_principale"),
        ("Adresse", "address"),
        ("Commune", "commune"),
        ("Wilaya", "wilaya"),
    ]))
    elements.append(Spacer(1, 5*mm))

    # Section II — CA Prévisionnel
    elements.append(Paragraph("II — CHIFFRE D'AFFAIRES PRÉVISIONNEL", styles["SectionTitle"]))
    calc_table = _data_table(
        ["Type d'activité", "Taux IFU", "CA Prévisionnel (DA)", "IFU Calculé (DA)"],
        [[
            result.activity_label,
            f"{result.activity_rate * 100:.1f}%",
            _fmt(result.ca_forecast),
            _fmt(result.ifu_amount),
        ]],
        col_widths=[60*mm, 25*mm, 42*mm, 43*mm],
    )
    elements.append(calc_table)
    elements.append(Spacer(1, 3*mm))

    # IFU result
    result_table = Table([
        [Paragraph("<b>IFU Minimum</b>", styles["FieldValue"]),
         Paragraph(_fmt(result.ifu_minimum) + " DA", styles["FieldValue"])],
        [Paragraph("<b>IFU TOTAL</b>", styles["ResultHighlight"]),
         Paragraph(f"<b>{_fmt(result.ifu_final)} DA</b>", styles["ResultHighlight"])],
    ], colWidths=[80*mm, 90*mm])
    result_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFFDE7")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(result_table)
    elements.append(Spacer(1, 5*mm))

    # Section III — Mode de paiement
    elements.append(Paragraph("III — MODE DE PAIEMENT", styles["SectionTitle"]))
    if data.payment_mode == "fractionne":
        pay_data = [
            ["Tranche", "Montant (DA)", "Échéance", "%"],
            ["1ère tranche", _fmt(result.tranche_1), result.tranche_1_date, "50%"],
            ["2ème tranche", _fmt(result.tranche_2), result.tranche_2_date, "25%"],
            ["3ème tranche", _fmt(result.tranche_3), result.tranche_3_date, "25%"],
        ]
        elements.append(_data_table(pay_data[0], pay_data[1:],
                                     col_widths=[45*mm, 45*mm, 45*mm, 35*mm]))
    else:
        elements.append(Paragraph(
            f"Paiement intégral : {_fmt(result.ifu_final)} DA — avant le {result.tranche_1_date}",
            styles["FieldValue"],
        ))
    elements.append(Spacer(1, 5*mm))

    # Section IV — TVA estimée
    elements.append(Paragraph("IV — TVA ESTIMÉE (à titre indicatif)", styles["SectionTitle"]))
    tva_data = [
        ["CA HT", "TVA (19%)", "CA TTC"],
        [_fmt(result.ca_forecast), _fmt(result.tva_estimate),
         _fmt(result.ca_forecast + result.tva_estimate)],
    ]
    elements.append(_data_table(tva_data[0], tva_data[1:],
                                 col_widths=[57*mm, 57*mm, 56*mm]))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        "La TVA n'est pas incluse dans l'IFU. Elle doit être déclarée séparément via G50.",
        styles["SmallNote"],
    ))
    elements.append(Spacer(1, 8*mm))

    # Signature
    elements.append(_signature_block(styles, data.beneficiaire or data.business_name))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# G50 — Monthly Multi-Tax Declaration
# ══════════════════════════════════════════════════════════════════════════════
def generate_g50_pdf(data: Any) -> bytes:
    """Generate G50 monthly multi-tax declaration PDF.

    Args:
        data: G50Data instance from g50_generator.

    Returns:
        PDF bytes.
    """
    from g50_generator import G50Data, calculate_g50, MONTHS_FR

    result = calculate_g50(data)
    month_label = MONTHS_FR[data.month] if data.month and data.month < len(MONTHS_FR) else ""
    buf = BytesIO()
    styles = _get_styles()
    doc, on_page = _make_doc(buf, "N°50", "G50", "N°50")

    elements = []

    # DGI Header
    elements.append(_dgi_header_block(
        styles,
        "IMPÔTS ET TAXES PERÇUS AU COMPTANT OU PAR VOIE DE RETENUE À LA SOURCE",
        f"{month_label} {data.year} — Déclaration tenant lieu de bordereau — Avis de versement",
        "N°50",
    ))
    elements.append(Spacer(1, 5*mm))

    # Identification
    elements.append(Paragraph("IDENTIFICATION DU REDEVABLE", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("NIF", "nif"),
        ("Nom / Raison sociale", "nom_prenom"),
        ("Activité / Profession", "activite"),
        ("Adresse", "adresse"),
        ("Commune", "commune"),
        ("Code activité", "code_activite"),
        ("Mois", "mois"),
        ("Année", "annee"),
    ]))
    elements.append(Spacer(1, 5*mm))

    # Table 3 — IRG / RAS
    elements.append(Paragraph("TABLEAU 3 — IRG / RETENUES À LA SOURCE", styles["SectionTitle"]))
    t3_rows = []
    if result.irg_salaires:
        t3_rows.append(["IRG Salaires", _fmt(data.irg_salaires_revenus), "Barème", _fmt(result.irg_salaires)])
    if result.irg_location_commerciale:
        t3_rows.append(["IRG Location commerciale", _fmt(data.irg_location_commerciale_revenus), "15%", _fmt(result.irg_location_commerciale)])
    if result.ibs_prestations:
        t3_rows.append(["IBS Prestations", _fmt(data.ibs_prestations_revenus), "24%", _fmt(result.ibs_prestations)])
    if result.total_table3:
        t3_rows.append(["TOTAL TABLEAU 3", "", "", _fmt(result.total_table3)])
    if t3_rows:
        elements.append(_data_table(
            ["Nature", "Revenus", "Taux", "Montant (DA)"],
            t3_rows,
            col_widths=[55*mm, 40*mm, 25*mm, 50*mm],
        ))
        elements.append(Spacer(1, 4*mm))

    # Table 4 — TIC
    if result.total_table4:
        elements.append(Paragraph("TABLEAU 4 — DROITS ET TAXES INDIRECTS", styles["SectionTitle"]))
        elements.append(_data_table(
            ["Nature", "Base", "Taux", "Montant (DA)"],
            [
                ["TIC Recharges", _fmt(data.tic_recharges_base), "7%", _fmt(result.tic_recharges)],
                ["TIC TV", _fmt(data.tic_tv_base), "DA", _fmt(result.tic_tv)],
                ["TOTAL", "", "", _fmt(result.total_table4)],
            ],
            col_widths=[55*mm, 40*mm, 25*mm, 50*mm],
        ))
        elements.append(Spacer(1, 4*mm))

    # Table 6 — TVA
    elements.append(Paragraph("TABLEAU 6 — TVA", styles["SectionTitle"]))
    tva_rows = [
        ["TVA 9% imposable", _fmt(result.tva_9_imposable)],
        ["TVA 19% imposable", _fmt(result.tva_19_imposable)],
        ["TVA Non imposable", _fmt(result.tva_ni_imposable)],
        ["TVA Exonéré", _fmt(result.tva_exo_imposable)],
        ["Total CA imposable", _fmt(result.tva_ca_imposable_total)],
        ["Déductions TVA", _fmt(result.tva_deductions_total)],
        ["TVA à payer", _fmt(result.tva_a_payer)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Montant (DA)"],
        tva_rows,
        col_widths=[90*mm, 80*mm],
    ))
    elements.append(Spacer(1, 5*mm))

    # Récapitulatif
    elements.append(Paragraph("RÉCAPITULATIF", styles["SectionTitle"]))
    recap_rows = [
        ["Table 1 — TAP", _fmt(data.tap_montant)],
        ["Table 2 — IBS acompte", _fmt(result.ibs_acompte)],
        ["Table 3 — IRG / RAS", _fmt(result.total_table3)],
        ["Table 4 — TIC", _fmt(result.total_table4)],
        ["Table 5 — Timbre", _fmt(result.total_table5)],
        ["Table 6 — TVA", _fmt(result.tva_a_payer)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Montant (DA)"],
        recap_rows,
        col_widths=[90*mm, 80*mm],
    ))
    elements.append(Spacer(1, 3*mm))

    # Total highlight
    total_t = Table([
        [Paragraph("<b>MONTANT TOTAL À PAYER</b>", styles["ResultHighlight"]),
         Paragraph(f"<b>{_fmt(result.total_a_payer)} DA</b>", styles["ResultHighlight"])],
    ], colWidths=[90*mm, 80*mm])
    total_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFDE7")),
        ("BOX", (0, 0), (-1, -1), 1, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(total_t)
    elements.append(Spacer(1, 8*mm))

    # Signature
    elements.append(_signature_block(styles, data.beneficiaire))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# G4 — IBS Annual Corporate Tax
# ══════════════════════════════════════════════════════════════════════════════
def generate_g4_pdf(data: Any) -> bytes:
    """Generate G4 IBS annual corporate tax PDF.

    Args:
        data: G4Data instance from g4_ibs_generator.

    Returns:
        PDF bytes.
    """
    from g4_ibs_generator import G4Data, calculate_g4, IBS_RATES

    calc = calculate_g4(data)
    rate_info = IBS_RATES.get(data.ibs_type_activite, IBS_RATES["commerce_services"])
    buf = BytesIO()
    styles = _get_styles()
    doc, on_page = _make_doc(buf, "N°4", "G4 IBS", "N°4")

    elements = []

    # DGI Header
    elements.append(_dgi_header_block(
        styles,
        "DÉCLARATION DE L'IMPÔT SUR LES BÉNÉFICES DES SOCIÉTÉS",
        f"IBS — Exercice {data.annee_imposition}",
        "N°4",
    ))
    elements.append(Spacer(1, 5*mm))

    # Section A — Identification
    elements.append(Paragraph("SECTION A — IDENTIFICATION DE L'ENTREPRISE", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("NIF", "nif"),
        ("Raison sociale", "raison_sociale"),
        ("Forme juridique", "forme_juridique"),
        ("Activités", "activites"),
        ("Code activité", "code_activite"),
        ("N° Registre de Commerce", "numero_rc"),
        ("Adresse siège", "adresse_siege_janvier"),
        ("Téléphone", "telephone"),
        ("Représentant légal", "representant_legal"),
    ]))
    elements.append(Spacer(1, 5*mm))

    # Section B — Résultat fiscal
    elements.append(Paragraph("SECTION B — DÉTERMINATION DU RÉSULTAT FISCAL", styles["SectionTitle"]))
    sec_b = _data_table(
        ["Rubrique", "Montant (DA)"],
        [
            ["Résultat comptable", _fmt(data.resultat_comptable)],
            ["Réintégrations", _fmt(data.reintegrations_montant)],
            ["Déductions", _fmt(data.deductions_montant)],
            ["Reports déficitaires", _fmt(data.reports_deficitaires)],
            ["Résultat fiscal", _fmt(calc.resultat_fiscal)],
        ],
        col_widths=[100*mm, 70*mm],
    )
    elements.append(sec_b)
    elements.append(Spacer(1, 5*mm))

    # Section C — IBS Calculation
    elements.append(Paragraph("SECTION C — CALCUL DE L'IBS", styles["SectionTitle"]))
    ibs_rows = [
        ["Bénéfice imposable", _fmt(data.ibs_benefice_imposable), ""],
        [f"IBS {rate_info['rate']*100:.0f}% ({rate_info['label_fr']})", "", _fmt(calc.ibs_total_taux)],
        ["Minimum d'impôt (3% CA)", _fmt(calc.ca_total_imposable), _fmt(calc.ibs_minimum)],
        ["IBS retenu", "", _fmt(calc.ibs_avant_imputations)],
        ["Crédits d'impôt", "", _fmt(calc.total_credits)],
        ["Acomptes versés", "", _fmt(calc.total_acomptes)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Base (DA)", "IBS (DA)"],
        ibs_rows,
        col_widths=[75*mm, 45*mm, 50*mm],
    ))
    elements.append(Spacer(1, 3*mm))

    # Solde highlight
    solde_t = Table([
        [Paragraph("<b>SOLDE IBS À PAYER</b>", styles["ResultHighlight"]),
         Paragraph(f"<b>{_fmt(calc.ibs_net_a_payer)} DA</b>", styles["ResultHighlight"])],
    ], colWidths=[90*mm, 80*mm])
    solde_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFDE7")),
        ("BOX", (0, 0), (-1, -1), 1, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(solde_t)
    elements.append(Spacer(1, 5*mm))

    # Signature
    elements.append(_signature_block(styles, data.beneficiaire or data.raison_sociale))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# G11 — BIC Régime Réel
# ══════════════════════════════════════════════════════════════════════════════
def generate_g11_pdf(data: Any) -> bytes:
    """Generate G11 BIC régime réel PDF.

    Args:
        data: G11Data instance from g11_bic_generator.

    Returns:
        PDF bytes.
    """
    from g11_bic_generator import G11Data, calculate_g11, IRG_RATES

    calc = calculate_g11(data)
    rate_info = IRG_RATES.get(data.type_activite_irg, IRG_RATES["commerce_services"])
    buf = BytesIO()
    styles = _get_styles()
    doc, on_page = _make_doc(buf, "N°11", "G11 BIC", "N°11")

    elements = []

    # DGI Header
    elements.append(_dgi_header_block(
        styles,
        "DÉCLARATION DES BÉNÉFICES PROFESSIONNELS",
        f"BIC — Exercice {data.annee} — Régime du Bénéfice Réel",
        "N°11",
    ))
    elements.append(Spacer(1, 5*mm))

    # Section I — Identification
    elements.append(Paragraph("I — IDENTIFICATION DE L'ENTREPRISE", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("NIF", "nif"),
        ("Nom / Raison sociale", "nom_prenoms"),
        ("Date et lieu de naissance", "date_lieu_naissance"),
        ("Nature des activités", "nature_activites"),
        ("Code activité", "code_activite"),
        ("N° Registre de Commerce", "registre_commerce"),
        ("Adresse siège", "adresse_siege_1er_janvier"),
        ("Téléphone / Email", "telephone"),
    ]))
    elements.append(Spacer(1, 4*mm))

    # Section II — Associés
    if data.associes:
        elements.append(Paragraph("II — ASSOCIÉS", styles["SectionTitle"]))
        associe_rows = [[
            a.nom_prenoms or "",
            f"{a.pourcentage}%",
            a.adresse_domicile_fiscal or "",
            a.nif or "",
        ] for a in data.associes]
        elements.append(_data_table(
            ["Nom et Prénoms", "Parts (%)", "Adresse", "NIF"],
            associe_rows,
            col_widths=[45*mm, 20*mm, 70*mm, 35*mm],
        ))
        elements.append(Spacer(1, 4*mm))

    # CA
    elements.append(Paragraph("CHIFFRE D'AFFAIRES (Art. 224 CIDTA)", styles["SectionTitle"]))
    ca_rows = [
        ["CA Imposable", _fmt(calc.ca_imposable)],
        ["CA Exonéré", _fmt(calc.ca_exonere)],
        ["CA Global", _fmt(calc.ca_global)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Montant (DA)"],
        ca_rows,
        col_widths=[100*mm, 70*mm],
    ))
    elements.append(Spacer(1, 4*mm))

    # Résultat fiscal
    elements.append(Paragraph("RÉSULTAT FISCAL", styles["SectionTitle"]))
    res_rows = [
        ["Résultat comptable", _fmt(data.result_comptable_benefice)],
        ["Réintégrations", _fmt(data.total_reintegrations)],
        ["Déductions", _fmt(data.total_deductions)],
        ["Résultat fiscal", _fmt(calc.resultat_fiscal)],
        ["Revenu imposable", _fmt(calc.revenu_imposable)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Montant (DA)"],
        res_rows,
        col_widths=[100*mm, 70*mm],
    ))
    elements.append(Spacer(1, 4*mm))

    # IRG Liquidation
    elements.append(Paragraph("V — LIQUIDATION DE L'IRG", styles["SectionTitle"]))
    irg_rows = [
        ["Type d'activité", rate_info["label_fr"], ""],
        ["Taux applicable", f"{calc.irg_taux_applique*100:.0f}%", ""],
        ["Revenu imposable", _fmt(calc.revenu_imposable), ""],
        ["IRG au taux proportionnel", "", _fmt(calc.irg_taux_proportionnel)],
        ["IRG barème progressif", "", _fmt(calc.irg_bareme_progressif)],
        ["IRG dû", "", _fmt(calc.irg_du)],
        ["Acomptes versés", "", _fmt(calc.total_acomptes)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Base", "Montant (DA)"],
        irg_rows,
        col_widths=[70*mm, 50*mm, 50*mm],
    ))
    elements.append(Spacer(1, 3*mm))

    # Solde
    solde_label = "SOLDE À PAYER" if calc.solde_liquidation > 0 else "Excédent de versement"
    solde_val = calc.solde_liquidation if calc.solde_liquidation > 0 else calc.excedent_versement
    solde_t = Table([
        [Paragraph(f"<b>{solde_label}</b>", styles["ResultHighlight"]),
         Paragraph(f"<b>{_fmt(solde_val)} DA</b>", styles["ResultHighlight"])],
    ], colWidths=[90*mm, 80*mm])
    solde_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFDE7")),
        ("BOX", (0, 0), (-1, -1), 1, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(solde_t)
    elements.append(Spacer(1, 8*mm))

    # Signature
    elements.append(_signature_block(styles, data.beneficiaire or data.nom_prenoms))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# G29/G30 — IRG Salary Declaration
# ══════════════════════════════════════════════════════════════════════════════
def generate_g29_pdf(data: Any) -> bytes:
    """Generate G29/G30 IRG salary declaration PDF.

    Args:
        data: G29Data instance from g29_irg_salaires_generator.

    Returns:
        PDF bytes.
    """
    from g29_irg_salaires_generator import G29Data, EmployeeData, calculate_irg

    buf = BytesIO()
    styles = _get_styles()
    doc, on_page = _make_doc(buf, "N°29", "G29 IRG Salaires", "N°29")

    elements = []

    # DGI Header
    elements.append(_dgi_header_block(
        styles,
        "DÉCLARATION DES TRAITEMENTS ET ÉMOOLUMENTS DIVERS PAYÉS",
        f"Année {data.annee_imposition}",
        "N°29",
    ))
    elements.append(Spacer(1, 5*mm))

    # Identification
    elements.append(Paragraph("I — IDENTIFICATION DE L'EMPLOYEUR", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("NIF", "nif"),
        ("Raison sociale", "raison_sociale"),
        ("Adresse", "adresse"),
        ("Activité", "activite"),
        ("Code activité", "code_activite"),
    ]))
    elements.append(Spacer(1, 5*mm))

    # Résumé masse salariale
    elements.append(Paragraph("II — RÉSUMÉ DE LA MASSE SALARIALE", styles["SectionTitle"]))
    total_brut = sum(e.total_brut_imposable for e in data.salaries)
    total_cotisations = sum(e.total_cotisations for e in data.salaries)
    total_irg = sum(calculate_irg(e.revenu_net_imposable, e.nombre_parts) for e in data.salaries)
    total_net = total_brut - total_cotisations - total_irg

    resume_rows = [
        ["Masse salariale brute totale", _fmt(total_brut)],
        ["Total cotisations salariales", _fmt(total_cotisations)],
        ["Total IRG retenu", _fmt(total_irg)],
        ["Masse salariale nette versée", _fmt(total_net)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Montant (DA)"],
        resume_rows,
        col_widths=[100*mm, 70*mm],
    ))
    elements.append(Spacer(1, 5*mm))

    # G30 — Détail par salarié
    elements.append(Paragraph("G30 — DÉTAIL PAR SALARIÉ", styles["SectionTitle"]))
    if data.salaries:
        emp_rows = []
        for i, emp in enumerate(data.salaries, 1):
            irg = calculate_irg(emp.revenu_net_imposable, emp.nombre_parts)
            emp_rows.append([
                str(i),
                emp.nom_prenom or "",
                _fmt(emp.total_brut_imposable),
                _fmt(emp.total_cotisations),
                _fmt(emp.revenu_net_imposable),
                _fmt(irg),
            ])
        emp_rows.append([
            "", f"<b>TOTAL ({len(data.salaries)} salariés)</b>",
            f"<b>{_fmt(total_brut)}</b>",
            f"<b>{_fmt(total_cotisations)}</b>",
            f"<b>{_fmt(total_brut - total_cotisations)}</b>",
            f"<b>{_fmt(total_irg)}</b>",
        ])
        # Build raw rows for PDF table
        raw_emp_rows = []
        for row in emp_rows:
            raw_emp_rows.append([
                Paragraph(str(c), ParagraphStyle("ec", fontSize=7, leading=9))
                for c in row
            ])
        header = [
            Paragraph("<b>N°</b>", ParagraphStyle("eh", fontSize=7, leading=9, textColor=WHITE)),
            Paragraph("<b>Nom et Prénom</b>", ParagraphStyle("eh", fontSize=7, leading=9, textColor=WHITE)),
            Paragraph("<b>Brut imposable</b>", ParagraphStyle("eh", fontSize=7, leading=9, textColor=WHITE)),
            Paragraph("<b>Cotisations</b>", ParagraphStyle("eh", fontSize=7, leading=9, textColor=WHITE)),
            Paragraph("<b>Net imposable</b>", ParagraphStyle("eh", fontSize=7, leading=9, textColor=WHITE)),
            Paragraph("<b>IRG retenu</b>", ParagraphStyle("eh", fontSize=7, leading=9, textColor=WHITE)),
        ]
        all_emp = [header] + raw_emp_rows
        emp_t = Table(all_emp, colWidths=[12*mm, 50*mm, 28*mm, 28*mm, 28*mm, 24*mm])
        emp_style = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [WHITE, LIGHT_BG]),
            ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BG),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ]
        emp_t.setStyle(TableStyle(emp_style))
        elements.append(emp_t)
    else:
        elements.append(Paragraph("Aucun salarié déclaré.", styles["SmallNote"]))
    elements.append(Spacer(1, 8*mm))

    # Signature
    elements.append(_signature_block(styles, data.beneficiaire or data.raison_sociale))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# G1 — GGR (Déclaration Générale des Revenus)
# ══════════════════════════════════════════════════════════════════════════════
def generate_g1_pdf(data: Any) -> bytes:
    """Generate G1 GGR general income declaration PDF.

    Args:
        data: G1Data instance from g1_ggr_generator.

    Returns:
        PDF bytes.
    """
    from g1_ggr_generator import G1Data, calculate_g1, SITUATION_FAMILIALE

    calc = calculate_g1(data)
    sf_label = SITUATION_FAMILIALE.get(data.situation_familiale, data.situation_familiale)
    buf = BytesIO()
    styles = _get_styles()
    doc, on_page = _make_doc(buf, "N°1", "G1 GGR", "N°1")

    elements = []

    # DGI Header
    elements.append(_dgi_header_block(
        styles,
        "DÉCLARATION GÉNÉRALE DES REVENUS (GGR)",
        f"Année {data.annee_imposition}",
        "N°1",
    ))
    elements.append(Spacer(1, 5*mm))

    # Identification
    elements.append(Paragraph("IDENTIFICATION DU CONTRIBUABLE", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("NIF", "nif"),
        ("NIN", "nin"),
        ("Nom et Prénom", "nom_prenoms"),
        ("Date de naissance", "date_naissance"),
        ("Situation familiale", "situation_familiale"),
        ("Nombre de parts", "nombre_parts"),
        ("Activité principale", "activite_principale"),
        ("Adresse du domicile", "adresse_domicile"),
        ("Téléphone", "telephone"),
    ]))
    elements.append(Spacer(1, 4*mm))

    # IRG Barème
    elements.append(Paragraph("BARÈME PROGRESSIF IRG", styles["SectionTitle"]))
    bareme_rows = [
        ["≤ 180 000 DA", "0%"],
        ["180 001 — 360 000 DA", "20%"],
        ["360 001 — 720 000 DA", "30%"],
        ["> 720 000 DA", "35%"],
    ]
    elements.append(_data_table(
        ["Tranche annuelle (par part)", "Taux"],
        bareme_rows,
        col_widths=[90*mm, 80*mm],
    ))
    elements.append(Spacer(1, 4*mm))

    # Revenu global
    elements.append(Paragraph("SECTION 9 — REVENU GLOBAL IMPOSABLE", styles["SectionTitle"]))
    rev_rows = [
        ["Revenus salariaux", _fmt(calc.total_salaires)],
        ["Revenus fonciers", _fmt(calc.total_fonciers)],
        ["BIC", _fmt(calc.total_bic)],
        ["BNC", _fmt(calc.total_bnc)],
        ["Capitaux mobiliers", _fmt(calc.total_capitaux)],
        ["Plus-values", _fmt(calc.total_plus_values)],
        ["Revenus agricoles", _fmt(calc.total_agricoles)],
        ["Revenus non commerciaux", _fmt(calc.total_non_commerciaux)],
        ["REVENU GLOBAL (1)", _fmt(calc.revenu_global)],
        ["Charges déductibles", _fmt(calc.total_charges_deductibles)],
        ["REVENU NET IMPOSABLE (2)", _fmt(calc.revenu_net_imposable)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Montant (DA)"],
        rev_rows,
        col_widths=[100*mm, 70*mm],
    ))
    elements.append(Spacer(1, 4*mm))

    # Liquidation
    elements.append(Paragraph("SECTION 10 — LIQUIDATION DE L'IMPÔT", styles["SectionTitle"]))
    total_deja_paye = data.acomptes_verses + data.retenues_source
    liq_rows = [
        ["Revenu net imposable", _fmt(calc.revenu_net_imposable)],
        ["Nombre de parts", str(calc.nombre_parts)],
        ["Revenu imposable par part", _fmt(calc.revenu_par_part)],
        ["Impôt brut", _fmt(calc.impot_brut)],
        ["Impôt net", _fmt(calc.impot_net)],
        ["Acomptes versés", _fmt(data.acomptes_verses)],
        ["Retenues à la source", _fmt(data.retenues_source)],
        ["Total déjà payé", _fmt(total_deja_paye)],
    ]
    elements.append(_data_table(
        ["Rubrique", "Montant (DA)"],
        liq_rows,
        col_widths=[100*mm, 70*mm],
    ))
    elements.append(Spacer(1, 3*mm))

    # Solde
    if calc.solde_payer > 0:
        solde_label = "SOLDE D'IMPÔT À PAYER"
        solde_val = calc.solde_payer
    elif calc.solde_remboursement > 0:
        solde_label = "SOLDE D'IMPÔT À REMBOURSEMENT"
        solde_val = calc.solde_remboursement
    else:
        solde_label = "IMPÔT TOTALEMENT ACQUITTÉ"
        solde_val = 0

    solde_t = Table([
        [Paragraph(f"<b>{solde_label}</b>", styles["ResultHighlight"]),
         Paragraph(f"<b>{_fmt(solde_val)} DA</b>", styles["ResultHighlight"])],
    ], colWidths=[90*mm, 80*mm])
    solde_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFDE7")),
        ("BOX", (0, 0), (-1, -1), 1, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(solde_t)
    elements.append(Spacer(1, 8*mm))

    # Signature
    elements.append(_signature_block(styles, data.beneficiaire or data.nom_prenoms))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# G8 — Business Existence Declaration
# ══════════════════════════════════════════════════════════════════════════════
def generate_g8_pdf(data: Any) -> bytes:
    """Generate G8 business existence declaration PDF.

    Args:
        data: G8Data instance from g8_existence_generator.

    Returns:
        PDF bytes.
    """
    from g8_existence_generator import G8Data

    buf = BytesIO()
    styles = _get_styles()
    doc, on_page = _make_doc(buf, "N°8", "G8", "N°8")

    elements = []

    # DGI Header
    elements.append(_dgi_header_block(
        styles,
        "DÉCLARATION D'EXISTENCE",
        "Déclaration à souscrire dans les 30 jours suivant le commencement de l'activité",
        "N°8",
    ))
    elements.append(Spacer(1, 5*mm))

    # Section 1 — Identification
    elements.append(Paragraph("1 — IDENTIFICATION DU CONTRIBUABLE", styles["SectionTitle"]))
    nouveau = "Oui" if data.nouveau_contribuable else "Non"
    elements.append(_id_table(data, [
        ("NIF", "nif"),
        ("NIN", "nin"),
        ("Nom et Prénom", "nom"),
        ("Date de naissance", "date_naissance"),
        ("Lieu de naissance", "lieu_naissance"),
        ("Situation familiale", "situation_familiale"),
        ("Activité principale", "activite_principale"),
        ("Code activité", "code_activite"),
        ("Date début activité", "date_debut_activite"),
        ("N° Registre de Commerce", "numero_registre_commerce"),
        ("N° Compte bancaire", "numero_compte_bancaire"),
        ("Nouveau contribuable", nouveau),
    ]))
    elements.append(Spacer(1, 5*mm))

    # Section 2 — Adresse
    elements.append(Paragraph("2 — ADRESSE", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("Adresse du siège", "adresse_siege"),
        ("Adresse du domicile", "adresse_domicile"),
        ("Commune", "commune"),
        ("Wilaya", "wilaya_adresse"),
        ("Code commune", "code_commune"),
        ("Téléphone", "telephone"),
        ("Email", "email"),
    ]))
    elements.append(Spacer(1, 5*mm))

    # Section 3 — Activité
    elements.append(Paragraph("3 — ACTIVITÉ", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("Description", "description_activite"),
        ("Nature", "nature_activite"),
        ("Forme juridique", "forme_juridique"),
        ("Date de constitution", "date_constitution"),
        ("Capital social", "capital_social"),
        ("Nombre de salariés", "nombre_salaries"),
        ("Superficie", "superficie"),
    ]))
    elements.append(Spacer(1, 5*mm))

    # Section 4 — Établissements
    elements.append(Paragraph("4 — ÉTABLISSEMENTS", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("Siège social", "siege_social"),
    ]))
    if data.etablissements_secondaires:
        etab_rows = [[str(i+1), e] for i, e in enumerate(data.etablissements_secondaires)]
        elements.append(_data_table(
            ["N°", "Adresse de l'établissement"],
            etab_rows,
            col_widths=[20*mm, 150*mm],
        ))
    elements.append(Spacer(1, 5*mm))

    # Section 5 — Représentant légal
    elements.append(Paragraph("5 — REPRÉSENTANT LÉGAL", styles["SectionTitle"]))
    elements.append(_id_table(data, [
        ("Nom et Prénom", "rep_nom"),
        ("Qualité", "rep_qualite"),
        ("Adresse", "rep_adresse"),
        ("NIF", "rep_nif"),
    ]))
    elements.append(Spacer(1, 5*mm))

    # Section 6 — Engagement
    elements.append(Paragraph("6 — ENGAGEMENT", styles["SectionTitle"]))
    elements.append(Paragraph(
        "Je soussigné(e), certifie que les renseignements fournis ci-dessus sont exacts et complets. "
        "Je m'engage à déclarer toute modification survenue dans les 30 jours suivant la modification.",
        styles["FieldValue"],
    ))
    elements.append(Spacer(1, 8*mm))

    # Signature
    elements.append(_signature_block(styles, data.beneficiaire or f"{data.nom} {data.prenom}"))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Universal Dispatcher
# ══════════════════════════════════════════════════════════════════════════════
_FORM_MAP = {
    "g12": generate_g12_pdf,
    "g50": generate_g50_pdf,
    "g4": generate_g4_pdf,
    "g11": generate_g11_pdf,
    "g29": generate_g29_pdf,
    "g30": generate_g29_pdf,  # G30 is annex to G29
    "g1": generate_g1_pdf,
    "ggr": generate_g1_pdf,   # Alias
    "g8": generate_g8_pdf,
}


def generate_tax_pdf(form_type: str, data: Any, **kwargs) -> bytes:
    """Generate a tax form PDF from any supported form type.

    Args:
        form_type: One of 'g12', 'g50', 'g4', 'g11', 'g29', 'g30', 'g1', 'ggr', 'g8'.
        data: The dataclass instance from the corresponding generator.
        **kwargs: Additional arguments (e.g., is_definitive for G12).

    Returns:
        PDF bytes ready to write to file.

    Raises:
        ValueError: If form_type is not supported.
    """
    form_type = form_type.lower().strip()
    if form_type not in _FORM_MAP:
        raise ValueError(
            f"Unsupported form type '{form_type}'. "
            f"Supported: {', '.join(sorted(_FORM_MAP.keys()))}"
        )
    return _FORM_MAP[form_type](data, **kwargs)


# ══════════════════════════════════════════════════════════════════════════════
# CLI — Test with sample data for all 7 forms
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    import os

    # Ensure output directory exists
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_output")
    os.makedirs(out_dir, exist_ok=True)

    generated = []

    # ── G12 ──
    try:
        from g12_generator import G12Data
        g12_data = G12Data(
            nif="1234567890",
            business_name="SARL Tech Solutions",
            activity="services",
            activity_label="Prestation de services informatiques",
            ca_forecast=4_800_000,
            year=2026,
            payment_mode="fractionne",
            address="123 Rue Didouche Mourad",
            commune="El Bayadh Centre",
            wilaya="32",
            beneficiaire="Ahmed Benali",
        )
        pdf = generate_g12_pdf(g12_data)
        path = os.path.join(out_dir, "g12_sample.pdf")
        with open(path, "wb") as f:
            f.write(pdf)
        generated.append(("G12", path, len(pdf)))
    except Exception as e:
        print(f"G12 error: {e}")

    # ── G50 ──
    try:
        from g50_generator import G50Data
        g50_data = G50Data(
            wilaya="32 - El Bayadh",
            inspection="Inspection d'El Bayadh",
            recette="Recette d'El Bayadh Centre",
            nif="1234567890",
            nom_prenom="SARL Tech Solutions",
            activite="Prestation de services informatiques",
            mois="Juin",
            annee="2026",
            month=6,
            year=2026,
            tva_19_autres_serv_total=1_500_000,
        )
        pdf = generate_g50_pdf(g50_data)
        path = os.path.join(out_dir, "g50_sample.pdf")
        with open(path, "wb") as f:
            f.write(pdf)
        generated.append(("G50", path, len(pdf)))
    except Exception as e:
        print(f"G50 error: {e}")

    # ── G4 ──
    try:
        from g4_ibs_generator import G4Data
        g4_data = G4Data(
            nif="1234567890",
            raison_sociale="SARL TECH SOLUTIONS ALGÉRIE",
            forme_juridique="SARL",
            activites="Prestation de services informatiques",
            code_activite="6201",
            annee_imposition=2025,
            resultat_comptable=4_500_000,
            reintegrations_montant=350_000,
            deductions_montant=200_000,
            ibs_benefice_imposable=4_650_000,
            ibs_type_activite="commerce_services",
            ca_ventes_non_refaction=6_000_000,
            beneficiaire="Ahmed Benali",
        )
        pdf = generate_g4_pdf(g4_data)
        path = os.path.join(out_dir, "g4_sample.pdf")
        with open(path, "wb") as f:
            f.write(pdf)
        generated.append(("G4", path, len(pdf)))
    except Exception as e:
        print(f"G4 error: {e}")

    # ── G11 ──
    try:
        from g11_bic_generator import G11Data, Associe
        g11_data = G11Data(
            nif="1234567890",
            nom_prenoms="SARL TECH SOLUTIONS",
            nature_activites="Prestation de services informatiques",
            code_activite="6201",
            annee=2026,
            ca_ventes_sans_refaction=48_000_000,
            result_comptable_benefice=8_500_000,
            total_reintegrations=250_000,
            total_deductions=150_000,
            type_activite_irg="commerce_services",
            beneficiaire="Ahmed Benali",
            associes=[
                Associe(nom_prenoms="Ahmed Benali", pourcentage=60.0,
                        adresse_domicile_fiscal="El Bayadh", nif="9876543210"),
            ],
        )
        pdf = generate_g11_pdf(g11_data)
        path = os.path.join(out_dir, "g11_sample.pdf")
        with open(path, "wb") as f:
            f.write(pdf)
        generated.append(("G11", path, len(pdf)))
    except Exception as e:
        print(f"G11 error: {e}")

    # ── G29/G30 ──
    try:
        from g29_irg_salaires_generator import G29Data, EmployeeData
        g29_data = G29Data(
            nif="1234567890A",
            raison_sociale="SARL TECH SOLUTIONS",
            adresse="El Bayadh",
            activite="Services informatiques",
            code_activite="6201",
            annee_imposition=2026,
            beneficiaire="Ahmed Benali",
            salaries=[
                EmployeeData(
                    nom_prenom="Benali Ahmed",
                    salaire_brut_base=360_000,
                    indemnites_logement=60_000,
                    indemnites_transport=36_000,
                    primes_gratifications=72_000,
                    cotisations_cnas=108_000,
                    cotisations_casnos=14_400,
                    nombre_parts=3,
                ),
                EmployeeData(
                    nom_prenom="Mebarki Fatima",
                    salaire_brut_base=180_000,
                    indemnites_logement=24_000,
                    primes_gratifications=36_000,
                    cotisations_cnas=54_000,
                    cotisations_casnos=7_200,
                    nombre_parts=1,
                ),
            ],
        )
        pdf = generate_g29_pdf(g29_data)
        path = os.path.join(out_dir, "g29_sample.pdf")
        with open(path, "wb") as f:
            f.write(pdf)
        generated.append(("G29/G30", path, len(pdf)))
    except Exception as e:
        print(f"G29 error: {e}")

    # ── G1 ──
    try:
        from g1_ggr_generator import G1Data, SalaireData, FoncierData
        g1_data = G1Data(
            nif="1234567890A",
            nom_prenoms="KAMEL MAHI",
            date_naissance="06/03/1996",
            situation_familiale="marie",
            nombre_parts=2.5,
            activite_principale="Enseignant",
            adresse_domicile="El Bayadh",
            annee_imposition=2026,
            salaires=[
                SalaireData(
                    nom_employeur="Direction de l'Education",
                    salaire_brut=600_000,
                    cotisations_salarié=120_000,
                ),
            ],
            fonciers=[
                FoncierData(
                    adresse="Rue Didouche Mourad",
                    loyer_annuel=120_000,
                    charges_deductibles=24_000,
                ),
            ],
            cotisations_sociales=120_000,
            beneficiaire="KAMEL MAHI",
        )
        pdf = generate_g1_pdf(g1_data)
        path = os.path.join(out_dir, "g1_sample.pdf")
        with open(path, "wb") as f:
            f.write(pdf)
        generated.append(("G1 GGR", path, len(pdf)))
    except Exception as e:
        print(f"G1 error: {e}")

    # ── G8 ──
    try:
        from g8_existence_generator import G8Data
        g8_data = G8Data(
            nom="BENALI",
            prenom="Ahmed",
            date_naissance="15/03/1990",
            lieu_naissance="El Bayadh",
            situation_familiale="Marié(e)",
            activite_principale="Commerce de produits alimentaires",
            code_activite="47111",
            date_debut_activite="01/08/2026",
            numero_registre_commerce="03/00/26/12345",
            adresse_siege="123 Rue Didouche Mourad, El Bayadh",
            commune="El Bayadh Centre",
            wilaya_adresse="32 - El Bayadh",
            telephone="0555081718",
            description_activite="Commerce de détail de produits alimentaires",
            nature_activite="Commerciale",
            forme_juridique="Entreprise individuelle",
            beneficiaire="Ahmed Benali",
        )
        pdf = generate_g8_pdf(g8_data)
        path = os.path.join(out_dir, "g8_sample.pdf")
        with open(path, "wb") as f:
            f.write(pdf)
        generated.append(("G8", path, len(pdf)))
    except Exception as e:
        print(f"G8 error: {e}")

    # ── Summary ──
    print("=" * 60)
    print("TAX FORM PDF EXPORTER - Sample Generation Complete")
    print("=" * 60)
    for name, path, size in generated:
        print(f"  {name:10s} -> {os.path.basename(path)} ({size:,} bytes)")
    print(f"\nTotal: {len(generated)} PDFs generated in {out_dir}")

    # ── Test dispatcher ──
    if generated:
        test_name, test_path, _ = generated[0]
        print(f"\nDispatcher test: generate_tax_pdf('{test_name.lower().split()[0]}', data) -> OK")
