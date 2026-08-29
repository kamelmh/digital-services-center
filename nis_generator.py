"""NIS Generator — Formulaire de Demande de Numéro d'Identification Statistique (ONS).

Generates the NIS request form filed with the ONS (Office National des
Statistiques). The NIS is required for: bank accounts, CNAS/CASNOS
affiliation, public tenders, and import/export operations.

Who must file:
- ALL businesses after Registre de Commerce registration
- Often auto-generated with RC via SIDJILCOM, but paper request still
  needed at the local ONS delegation in many wilayas

Usage:
    from nis_generator import NisData, calculate_nis, generate_nis

Reference: knowledge_base/forms/catalog.md (NIS)
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


from policy_constants import WILAYAS

# ── Constants ─────────────────────────────────────────────────────────────────

FORMES_JURIDIQUES = [
    "Personne physique", "SARL", "EURL", "SPA", "SNC",
    "Auto-entrepreneur", "EI (Entreprise Individuelle)", "Association",
]

SECTIONS_NIS = [
    "Section 1 — Agriculture, sylviculture et pêche",
    "Section 2 — Industries extractives et manufacturières, énergie",
    "Section 3 — Bâtiment, travaux publics et hydraulique (BTPH)",
    "Section 4 — Commerce, réparations, restauration",
    "Section 5 — Transport, stockage et communications",
    "Section 6 — Services financiers, immobiliers et aux entreprises",
    "Section 7 — Services non marchands (éducation, santé, administration)",
]

@dataclass
class NisData:
    """Data for the ONS NIS request form."""
    # ONS hierarchy
    delegation_ons: str = ""       # Local ONS delegation
    wilaya: str = ""

    # Applicant identity
    nom_raison_sociale: str = ""
    forme_juridique: str = "Personne physique"
    nif: str = ""
    rc: str = ""                   # RC number (or ANAE card ref for auto-entrepreneurs)
    date_rc: str = ""              # JJ/MM/AAAA

    # Activity classification
    activite_principale: str = ""
    section_nis: str = SECTIONS_NIS[3]   # Default: commerce
    code_activite_detail: str = ""       # Free-text detail

    # Address & contact
    adresse: str = ""
    commune: str = ""
    phone: str = ""
    email: str = ""

    # Employment
    effectif_salarie: int = 0

    # Legal representative
    representant_nom: str = ""
    representant_nin: str = ""

    # Metadata
    fait_a: str = ""
    date_declaration: str = ""


# ── Calculation ───────────────────────────────────────────────────────────────

def calculate_nis(data: NisData) -> dict:
    """Compute derived fields: completeness score, category flags.

    Returns dict with: is_auto_entrepreneur, completeness_pct,
    missing_fields list.
    """
    is_ae = data.forme_juridique == "Auto-entrepreneur"

    required = {
        "nom_raison_sociale": bool(data.nom_raison_sociale.strip()),
        "nif": bool(data.nif.strip()),
        "rc": bool(data.rc.strip()),
        "activite_principale": bool(data.activite_principale.strip()),
        "adresse": bool(data.adresse.strip()),
        "representant_nom": bool(data.representant_nom.strip()),
        "commune": bool(data.commune.strip()),
    }
    missing = [k for k, ok in required.items() if not ok]
    completeness = round(100 * (len(required) - len(missing)) / len(required))

    return {
        "is_auto_entrepreneur": is_ae,
        "completeness_pct": completeness,
        "missing_fields": missing,
        "effectif_tranche": (
            "0 salarié" if data.effectif_salarie == 0
            else "1-9" if data.effectif_salarie < 10
            else "10-49" if data.effectif_salarie < 50
            else "50-99" if data.effectif_salarie < 100
            else "100+"
        ),
    }


# ── Formatting helpers ────────────────────────────────────────────────────────

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
  .ons { font-size: 10pt; font-weight: bold; margin: 3px 0; }
  .header h1 { font-size: 14pt; margin: 5px 0; }
  .subtitle { font-size: 9pt; }
  .note-line { font-size: 8.5pt; margin-top: 5px; font-style: italic; }
  .section { margin: 10px 0; page-break-inside: avoid; }
  .section-title { font-size: 10pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 3px; margin-bottom: 5px; }
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 3px 5px; font-size: 9pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 35%; }
  .field-value { border-bottom: 1px dotted #999; width: 40%; }
  .checkbox-line { font-size: 9pt; margin: 3px 0; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 55%; }
  .summary-table .amount { text-align: right; width: 45%; }
  .warn { background: #fff3cd; font-weight: bold; }
  .ok { background: #d4edda; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


# ── HTML section builders ─────────────────────────────────────────────────────

def _header_html(data: NisData) -> str:
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="ons">OFFICE NATIONAL DES STATISTIQUES (ONS)</div>
  <h1>FORMULAIRE DE DEMANDE D'ATTRIBUTION D'UN NIS</h1>
  <div class="subtitle">Numéro d'Identification Statistique — استمارة طلب رقم التعريف الإحصائي</div>
  <div class="note-line">Obligatoire pour : compte bancaire, CNAS/CASNOS, marchés publics, import-export.</div>
</div>"""


def _identity_html(data: NisData, calc: dict) -> str:
    formes = "".join(
        f'<span style="margin-right:12px;">{_checkbox(data.forme_juridique, f)} {f}</span>'
        for f in FORMES_JURIDIQUES
    )
    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DU DEMANDEUR</div>
  <table class="fields-table">
    <tr><td class="field-label">Nom / Raison sociale :</td><td class="field-value">{_esc(data.nom_raison_sociale) or _blank()}</td></tr>
    <tr><td class="field-label">NIF :</td><td class="field-value">{_esc(data.nif) or _blank()}</td></tr>
    <tr><td class="field-label">{'Réf. carte ANAE' if calc['is_auto_entrepreneur'] else 'N° Registre de Commerce'} :</td><td class="field-value">{_esc(data.rc) or _blank()} {_esc('— déposé le ' + data.date_rc) if data.date_rc else ''}</td></tr>
  </table>
  <p style="font-weight:bold;font-size:9pt;margin-bottom:2px;">Forme juridique :</p>
  <div>{formes}</div>
</div>"""


def _activity_html(data: NisData) -> str:
    sections = "".join(
        f'<div class="checkbox-line">{_checkbox(data.section_nis, s)} {s}</div>'
        for s in SECTIONS_NIS
    )
    return f"""<div class="section">
  <div class="section-title">II — ACTIVITÉ (classification statistique)</div>
  <table class="fields-table">
    <tr><td class="field-label">Activité principale :</td><td class="field-value">{_esc(data.activite_principale) or _blank()}</td></tr>
    <tr><td class="field-label">Détail du code d'activité :</td><td class="field-value">{_esc(data.code_activite_detail) or _blank(25)}</td></tr>
  </table>
  <p style="font-weight:bold;font-size:9pt;margin-bottom:2px;">Section statistique :</p>
  {sections}
</div>"""


def _address_html(data: NisData, calc: dict) -> str:
    return f"""<div class="section">
  <div class="section-title">III — ADRESSE ET CONTACT</div>
  <table class="fields-table">
    <tr><td class="field-label">Adresse de l'établissement :</td><td class="field-value">{_esc(data.adresse) or _blank()}</td></tr>
    <tr><td class="field-label">Commune :</td><td class="field-value">{_esc(data.commune) or _blank(20)}</td></tr>
    <tr><td class="field-label">Wilaya :</td><td class="field-value">{_esc(data.wilaya) or _blank(20)}</td></tr>
    <tr><td class="field-label">Délégation ONS :</td><td class="field-value">{_esc(data.delegation_ons) or _blank(20)}</td></tr>
    <tr><td class="field-label">Téléphone :</td><td class="field-value">{_esc(data.phone) or _blank(20)}</td></tr>
    <tr><td class="field-label">Email :</td><td class="field-value">{_esc(data.email) or _blank(20)}</td></tr>
    <tr><td class="field-label">Effectif salarié :</td><td class="field-value">{data.effectif_salarie} ({calc['effectif_tranche']})</td></tr>
    <tr><td class="field-label">Représentant légal :</td><td class="field-value">{_esc(data.representant_nom) or _blank()} {_esc('— NIN ' + data.representant_nin) if data.representant_nin else ''}</td></tr>
  </table>
</div>"""


def _documents_html(calc: dict) -> str:
    docs = [
        "Copie du Registre de Commerce (ou carte auto-entrepreneur ANAE)",
        "Carte d'immatriculation fiscale (NIF)",
        "Pièce d'identité du représentant légal",
        "Justificatif d'adresse de l'établissement",
    ]
    items = "".join(f'<div class="checkbox-line">☐ {d}</div>' for d in docs)
    warn = (
        '<div class="summary-table"><tr class="warn"><td class="label">Dossier incomplet — champs manquants :</td>'
        f'<td class="amount">{", ".join(calc["missing_fields"])}</td></tr></div>'
        if calc["missing_fields"] else
        '<div class="summary-table"><tr class="ok"><td class="label">Complétude du dossier</td>'
        f'<td class="amount">{calc["completeness_pct"]}% ✓</td></tr></div>'
    )
    return f"""<div class="section">
  <div class="section-title">IV — PIÈCES À JOINDRE</div>
  {items}
  {warn}
</div>"""


def _signature_html(data: NisData) -> str:
    return f"""<div class="section">
  <div class="attestation">
    Je soussigné(e) demande l'attribution d'un Numéro d'Identification Statistique
    et certifie l'exactitude des renseignements fournis.
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {_esc(data.fait_a) or '....................'} <strong>le</strong> {_esc(data.date_declaration) or '....../....../......'}
  </div>
  <div class="signature-block">
    <div class="sig-box">Signature du demandeur<br><br><br>Cachet</div>
    <div class="sig-box">Agent ONS<br><br><br>N° attribué : ..................</div>
  </div>
</div>"""


# ── Main generator ────────────────────────────────────────────────────────────

def generate_nis(data: NisData) -> str:
    """Generate complete NIS request form as HTML."""
    calc = calculate_nis(data)

    body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>NIS — Demande {data.nom_raison_sociale or ''}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_identity_html(data, calc)}
{_activity_html(data)}
{_address_html(data, calc)}
{_documents_html(calc)}
{_signature_html(data)}

</body>
</html>"""

    hook_generation(
        "nis_ons",
        {"nom_raison_sociale": data.nom_raison_sociale, "wilaya": data.wilaya},
        body,
    )
    return body


generate_nis_html = generate_nis


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = NisData(
        delegation_ons="Délégation ONS El Bayadh",
        wilaya="32-El Bayadh",
        nom_raison_sociale="Entreprise Mahi Travaux",
        forme_juridique="Personne physique",
        nif="123456789012345",
        rc="32/00-7654321B18",
        date_rc="15/06/2018",
        activite_principale="Travaux de plomberie générale",
        section_nis=SECTIONS_NIS[2],  # BTPH
        code_activite_detail="Installation sanitaires bâtiment",
        adresse="Centre-ville",
        commune="El Bayadh",
        phone="+213 661 23 45 67",
        email="contact@mahitravaux.dz",
        effectif_salarie=4,
        representant_nom="Mahi Kamel Abdelghani",
        representant_nin="199603061234567890",
        fait_a="El Bayadh",
        date_declaration="20/06/2018",
    )

    calc = calculate_nis(sample)
    print("=== NIS — Demande ONS ===")
    print(f"Demandeur : {sample.nom_raison_sociale}")
    print(f"Tranche effectif : {calc['effectif_tranche']}")
    print(f"Complétude : {calc['completeness_pct']}%")
    if calc["missing_fields"]:
        print(f"Manquant : {', '.join(calc['missing_fields'])}")

    if "--html" in sys.argv:
        html = generate_nis(sample)
        out = "nis_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out} ({len(html):,} chars)")
