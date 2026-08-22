"""ANAE Auto-Entrepreneur Generator — Déclaration d'Activité.

Generates the ANAE (Agence Nationale d'Appui et de Développement de
l'Entrepreneuriat) auto-entrepreneur activity declaration form.

Who must file:
- Micro-business owners and freelancers registering under the
  auto-entrepreneur regime (Law 22-23 of December 2022)
- Filed online via anae.dz or paper at ANAE local offices

Auto-entrepreneur regime highlights (2026):
- IFU: 5% of turnover (services) / 12% (other activities), minimum flat tax applies
- CASNOS: optional affiliation for social security
- Turnover ceiling: 5M DZD/year (services) / 8M DZD/year (production/sale)

Usage:
    from anae_generator import AnaeData, calculate_anae, generate_anae

Reference: knowledge_base/forms/catalog.md (ANAE — Auto-Entrepreneur)
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass
from datetime import datetime


def _esc(value: object, default: str = "") -> str:
    if value is None:
        return default
    return _html_mod.escape(str(value))


# ── Constants ─────────────────────────────────────────────────────────────────

ACTIVITE_TYPES = [
    "Services",                       # IFU 5%
    "Production / Vente",             # IFU 12%
    "Artisanat",
    "Prestations intellectuelles",
]

IFU_RATES = {
    "Services": 0.12,
    "Prestations intellectuelles": 0.12,
    "Production / Vente": 0.05,
    "Artisanat": 0.05,
}

PLAFONDS = {
    "Services": 5_000_000,
    "Prestations intellectuelles": 5_000_000,
    "Production / Vente": 8_000_000,
    "Artisanat": 8_000_000,
}

SECTEURS = [
    "Numérique (développement, design, marketing digital)",
    "Services à la personne",
    "Commerce et distribution",
    "Artisanat traditionnel",
    "Transport et logistique",
    "Tourisme et loisirs",
    "Enseignement et formation",
    "Autre",
]


@dataclass
class AnaeData:
    """Data for ANAE auto-entrepreneur activity declaration."""
    # ANAE hierarchy
    antenne_anae: str = ""         # Local ANAE branch
    wilaya: str = ""

    # Applicant identity
    nom_prenom: str = ""
    nin: str = ""                  # 18 digits
    date_naissance: str = ""
    lieu_naissance: str = ""
    adresse: str = ""
    commune: str = ""
    phone: str = ""
    email: str = ""

    # Activity
    type_activite: str = "Services"     # One of ACTIVITE_TYPES
    secteur: str = ""                    # Description from SECTEURS
    description_activite: str = ""
    adresse_exercice: str = ""           # Where the activity is performed

    # Financial estimate
    ca_annuel_prevu: float = 0.0    # Expected annual turnover (DZD)
    casnos_affiliation: bool = True # Request CASNOS affiliation

    # Metadata
    fait_a: str = ""
    date_declaration: str = ""


# ── Calculation ───────────────────────────────────────────────────────────────

def calculate_anae(data: AnaeData) -> dict:
    """Compute IFU rate, estimated tax, plafond check, CASNOS estimate.

    Returns dict with: ifu_rate, ifu_annual, plafond, plafond_ok,
    casnos_monthly, casnos_annual, effective_load.
    """
    ifu_rate = IFU_RATES.get(data.type_activite, 0.05)
    plafond = PLAFONDS.get(data.type_activite, 5_000_000)

    ca = max(0.0, data.ca_annuel_prevu)
    ifu_annual = round(ca * ifu_rate, 2)
    plafond_ok = ca <= plafond

    # CASNOS: flat annual contribution ~43,200 DZD/year (2026 convention in ALGERIA_DATA)
    casnos_annual = 43_200.0 if data.casnos_affiliation else 0.0

    total_charge = ifu_annual + casnos_annual
    effective_load = round(total_charge / ca * 100, 2) if ca > 0 else 0.0

    return {
        "ifu_rate": ifu_rate,
        "ifu_annual": ifu_annual,
        "plafond": plafond,
        "plafond_ok": plafond_ok,
        "casnos_annual": casnos_annual,
        "total_charges": round(total_charge, 2),
        "effective_load": effective_load,
    }


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt(n: float) -> str:
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _checkbox(selected: str, value: str) -> str:
    return "☑" if selected == value else "☐"


def _blank(n: int = 30) -> str:
    return "." * n


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css() -> str:
    return """<style>
  @page { size: A4; margin: 12mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 10pt; color: #1a1a1a; margin: 0; padding: 15px;
    line-height: 1.4; direction: ltr;
  }
  .header { text-align: center; border: 2px solid #000; padding: 8px; margin-bottom: 10px; }
  .republique { font-size: 9pt; letter-spacing: 1px; }
  .anae { font-size: 10pt; font-weight: bold; margin: 3px 0; }
  .header h1 { font-size: 14pt; margin: 5px 0; }
  .subtitle { font-size: 9pt; }
  .deadline { font-size: 9pt; font-weight: bold; margin-top: 5px; padding: 4px; border: 1px solid #000; background: #f8f8f8; }
  .section { margin: 10px 0; page-break-inside: avoid; }
  .section-title { font-size: 10pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 3px; margin-bottom: 5px; }
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 3px 5px; font-size: 9pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 35%; }
  .field-value { border-bottom: 1px dotted #999; width: 40%; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 55%; }
  .summary-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .summary-table .total-row { background: #e8e8e8; font-weight: bold; font-size: 10pt; }
  .summary-table .warn { background: #fff3cd; font-weight: bold; }
  .checkbox-line { font-size: 9pt; margin: 3px 0; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }
  .legal-page p { font-size: 8.5pt; text-align: justify; margin: 5px 0; line-height: 1.5; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


# ── HTML section builders ─────────────────────────────────────────────────────

def _header_html(data: AnaeData) -> str:
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="anae">AGENCE NATIONALE D'APPUI ET DE DÉVELOPPEMENT DE L'ENTREPRENEURIAT (ANAE)</div>
  <h1>DÉCLARATION D'ACTIVITÉ — AUTO-ENTREPRENEUR</h1>
  <div class="subtitle">Régime de l'auto-entrepreneur (Loi n°22-23 du 18 décembre 2022)</div>
  <div class="deadline">À déposer avant le début d'activité — en ligne sur anae.dz ou auprès de l'antenne locale</div>
</div>"""


def _identity_html(data: AnaeData) -> str:
    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DU DÉCLARANT</div>
  <table class="fields-table">
    <tr><td class="field-label">Nom et Prénom :</td><td class="field-value">{_esc(data.nom_prenom) or _blank()}</td></tr>
    <tr><td class="field-label">NIN (18 chiffres) :</td><td class="field-value">{_esc(data.nin) or _blank()}</td></tr>
    <tr><td class="field-label">Date de naissance :</td><td class="field-value">{_esc(data.date_naissance) or '....../....../......'}</td></tr>
    <tr><td class="field-label">Lieu de naissance :</td><td class="field-value">{_esc(data.lieu_naissance) or _blank(20)}</td></tr>
    <tr><td class="field-label">Adresse personnelle :</td><td class="field-value">{_esc(data.adresse) or _blank()}</td></tr>
    <tr><td class="field-label">Commune :</td><td class="field-value">{_esc(data.commune) or _blank(20)}</td></tr>
    <tr><td class="field-label">Wilaya :</td><td class="field-value">{_esc(data.wilaya) or _blank(20)}</td></tr>
    <tr><td class="field-label">Téléphone :</td><td class="field-value">{_esc(data.phone) or _blank(20)}</td></tr>
    <tr><td class="field-label">Email :</td><td class="field-value">{_esc(data.email) or _blank(20)}</td></tr>
  </table>
</div>"""


def _activity_html(data: AnaeData) -> str:
    type_lines = "".join(
        f'<div class="checkbox-line">{_checkbox(data.type_activite, t)} {t}</div>'
        for t in ACTIVITE_TYPES
    )
    return f"""<div class="section">
  <div class="section-title">II — NATURE DE L'ACTIVITÉ</div>
  <p style="font-weight:bold;font-size:9pt;">Type d'activité :</p>
  {type_lines}
  <table class="fields-table">
    <tr><td class="field-label">Secteur :</td><td class="field-value">{_esc(data.secteur) or _blank()}</td></tr>
    <tr><td class="field-label">Description détaillée :</td><td class="field-value">{_esc(data.description_activite) or _blank(40)}</td></tr>
    <tr><td class="field-label">Adresse d'exercice :</td><td class="field-value">{_esc(data.adresse_exercice) or 'Domicile'}</td></tr>
    <tr><td class="field-label">Antenne ANAE :</td><td class="field-value">{_esc(data.antenne_anae) or _blank(20)}</td></tr>
  </table>
</div>"""


def _financial_html(data: AnaeData, calc: dict) -> str:
    warn = (
        f'<div class="note" style="color:#b00;">⚠ Le CA prévu ({_fmt(data.ca_annuel_prevu)} DA) dépasse '
        f'le plafond autorisé ({_fmt(calc["plafond"])} DA) pour ce type d\'activité.</div>'
        if not calc["plafond_ok"] else ""
    )
    return f"""<div class="section">
  <div class="section-title">III — ESTIMATION FINANCIÈRE ET RÉGIME FISCAL</div>
  <table class="summary-table">
    <tr><td class="label">Chiffre d'affaires annuel prévu</td><td class="amount">{_fmt(data.ca_annuel_prevu)} DA</td></tr>
    <tr><td class="label">Plafond du régime ({_esc(data.type_activite)})</td><td class="amount">{_fmt(calc['plafond'])} DA</td></tr>
    <tr><td class="label">Taux IFU applicable</td><td class="amount">{calc['ifu_rate']*100:.0f}%</td></tr>
    <tr><td class="label">IFU annuel estimé</td><td class="amount">{_fmt(calc['ifu_annual'])} DA</td></tr>
    <tr><td class="label">Cotisation CASNOS annuelle {'(demandée)' if data.casnos_affiliation else '(non demandée)'}</td><td class="amount">{_fmt(calc['casnos_annual'])} DA</td></tr>
    <tr class="total-row"><td class="label">Total charges annuelles estimées</td><td class="amount">{_fmt(calc['total_charges'])} DA</td></tr>
    <tr><td class="label">Charge effective (sur CA prévu)</td><td class="amount">{calc['effective_load']:.2f}%</td></tr>
  </table>
  {warn}
</div>"""


def _documents_html() -> str:
    docs = [
        "Pièce d'identité nationale (copie lisible)",
        "Certificat de résidence (moins de 3 mois)",
        "Justificatif de domicile (contrat de bail, acte de propriété)",
        "Deux photos d'identité récentes",
        "Attestation de non-affiliation CNAS/CASNOS (si applicable)",
    ]
    items = "".join(f'<div class="checkbox-line">☐ {d}</div>' for d in docs)
    return f"""<div class="section">
  <div class="section-title">IV — PIÈCES À JOINDRE</div>
  {items}
  <div class="note">Cochez les pièces jointes au dossier.</div>
</div>"""


def _signature_html(data: AnaeData) -> str:
    return f"""<div class="section">
  <div class="attestation">
    Je soussigné(e) déclare créer une activité en qualité d'auto-entrepreneur,
    m'engage à respecter les conditions du régime (plafonds de chiffre d'affaires,
    cotisations) et certifie l'exactitude des renseignements fournis.
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {_esc(data.fait_a) or '....................'} <strong>le</strong> {_esc(data.date_declaration) or '....../....../......'}
  </div>
  <div class="signature-block">
    <div class="sig-box">Signature du déclarant<br><br><br>(précédée de la mention manuscrite « Lu et approuvé »)</div>
    <div class="sig-box">Agent ANAE<br><br><br>Cachet et signature</div>
  </div>
</div>"""


def _legal_html() -> str:
    return """<div class="section legal-page">
  <div class="page-header">RÉFÉRENCES LÉGALES — AUTO-ENTREPRENEUR</div>
  <p>Base légale : Loi n°22-23 du 18 décembre 2022 portant création du statut
  d'auto-entrepreneur, et ses textes d'application.</p>
  <p>L'auto-entrepreneur exerce une activité individuelle à titre principal ou
  complémentaire, sous plafonds de chiffre d'affaires : 5 000 000 DA/an
  (prestations de services) ou 8 000 000 DA/an (activités de production et vente).</p>
  <p>Régime fiscal : IFU au taux libératoire de 5% (services) ou 12%
  (production/vente) du chiffre d'affaires annuel déclaré, avec minimum de
  perception. La déclaration définitive du CA se fait au plus tard le 20 janvier
  de l'année suivante (formulaire G12 bis).</p>
  <p>Protection sociale : affiliation facultative à la CASNOS pour couverture
  maladie et retraite. L'immatriculation est gratuite et se fait en ligne
  (anae.dz) ou auprès des antennes locales de l'ANAE.</p>
</div>"""


# ── Main generator ────────────────────────────────────────────────────────────

def generate_anae(data: AnaeData) -> str:
    """Generate complete ANAE auto-entrepreneur declaration as HTML.

    Args:
        data: AnaeData with applicant info, activity, financial estimates

    Returns:
        Complete HTML string ready to save or render
    """
    calc = calculate_anae(data)

    body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>ANAE Auto-Entrepreneur — Déclaration {data.nom_prenom or ''}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_identity_html(data)}
{_activity_html(data)}
{_financial_html(data, calc)}
{_documents_html()}
{_signature_html(data)}
{_legal_html()}

</body>
</html>"""

    hook_generation(
        "anae_auto_entrepreneur",
        {"type_activite": data.type_activite, "wilaya": data.wilaya},
        body,
    )
    return body


generate_anae_html = generate_anae


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = AnaeData(
        antenne_anae="Antenne ANAE El Bayadh",
        wilaya="32-El Bayadh",
        nom_prenom="Mahi Kamel Abdelghani",
        nin="199603061234567890",
        date_naissance="06/03/1996",
        lieu_naissance="El Bayadh",
        adresse="Centre-ville",
        commune="El Bayadh",
        phone="+213 661 23 45 67",
        email="kamelmahi71@gmail.com",
        type_activite="Services",
        secteur="Numérique (développement, design, marketing digital)",
        description_activite="Développement web et mobile, conseil en transformation numérique",
        adresse_exercice="Domicile",
        ca_annuel_prevu=1_800_000,
        casnos_affiliation=True,
        fait_a="El Bayadh",
        date_declaration="15/01/2026",
    )

    calc = calculate_anae(sample)
    print("=== ANAE — Déclaration Auto-Entrepreneur ===")
    print(f"Déclarant : {sample.nom_prenom}")
    print(f"Type activité : {sample.type_activite}")
    print(f"CA prévu : {_fmt(sample.ca_annuel_prevu)} DA")
    print(f"Taux IFU : {calc['ifu_rate']*100:.0f}%")
    print(f"IFU annuel : {_fmt(calc['ifu_annual'])} DA")
    print(f"CASNOS : {_fmt(calc['casnos_annual'])} DA")
    print(f"Total charges : {_fmt(calc['total_charges'])} DA ({calc['effective_load']:.2f}% du CA)")
    print(f"Plafond OK : {calc['plafond_ok']}")

    if "--html" in sys.argv:
        html = generate_anae(sample)
        out = "anae_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out} ({len(html):,} chars)")
