"""SECU 01 Generator — Déclaration et Demande d'Affiliation CNAS.

Generates the CNAS employer affiliation form (SECU 01 — Déclaration et
Demande d'Affiliation) required BEFORE paying the first salary to the
first employee.

Who must file: New employers hiring their first employee.
Deadline: Before first salary payment.

Usage:
    from secu01_generator import Secu01Data, calculate_secu01, generate_secu01

Reference: knowledge_base/agencies/cnas.md
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


def _esc(value: object, default: str = "") -> str:
    if value is None:
        return default
    return _html_mod.escape(str(value))


from policy_constants import WILAYAS

# ── Constants ─────────────────────────────────────────────────────────────────

FORMES_JURIDIQUES = ["SARL", "EURL", "SPA", "SNC", "Personne physique", "EI"]

@dataclass
class Secu01Data:
    """Data for CNAS SECU 01 employer affiliation form."""
    # Agency
    agence_cnas: str = ""          # Local CNAS agency
    wilaya: str = ""

    # Employer identification
    nif: str = ""
    nis: str = ""
    rc: str = ""                   # Numéro du Registre de Commerce
    raison_sociale: str = ""
    forme_juridique: str = "SARL"
    activite: str = ""
    adresse: str = ""
    commune: str = ""
    phone: str = ""
    email: str = ""

    # Employment details
    date_debut_activite: str = ""  # JJ/MM/AAAA
    date_premier_emploi: str = ""  # Date of first hire (JJ/MM/AAAA)
    effectif_prevu: int = 1        # Expected headcount
    salaire_mensuel_estime: float = 0.0  # Estimated monthly gross salary of first hire (DA)

    # Legal representative
    representant_nom: str = ""
    representant_qualite: str = "Gérant"

    # Metadata
    fait_a: str = ""
    date_declaration: str = ""


# ── Calculation ───────────────────────────────────────────────────────────────

def calculate_secu01(data: Secu01Data) -> dict:
    """Compute estimated monthly/annual CNAS contributions for the first hire.

    Uses DSC convention: employer 25.5%, employee 9%.
    """
    monthly_gross = max(0.0, data.salaire_mensuel_estime)
    monthly_employer = round(monthly_gross * 25.5 / 100, 2)
    monthly_employee = round(monthly_gross * 9.0 / 100, 2)

    return {
        "salaire_mensuel": monthly_gross,
        "cotisation_mensuelle_employeur": monthly_employer,
        "cotisation_mensuelle_salariale": monthly_employee,
        "cotisation_mensuelle_totale": round(monthly_employer + monthly_employee, 2),
        "cout_total_employeur_mensuel": round(monthly_gross + monthly_employer, 2),
        "effectif_prevu": data.effectif_prevu,
    }


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt(n: float) -> str:
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


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
  .cnas { font-size: 10pt; font-weight: bold; margin: 3px 0; color: #006400; }
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
  .checkbox-line { font-size: 9pt; margin: 3px 0; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }
  .legal-page p { font-size: 8.5pt; text-align: justify; margin: 5px 0; line-height: 1.5; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


# ── HTML section builders ─────────────────────────────────────────────────────

def _header_html(data: Secu01Data) -> str:
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="cnas">CAISSE NATIONALE DES ASSURANCES SOCIALES (CNAS)</div>
  <h1>SECU 01 — DÉCLARATION ET DEMANDE D'AFFILIATION</h1>
  <div class="subtitle">Immatriculation de l'employeur au régime de la sécurité sociale</div>
  <div class="deadline">À déposer AVANT le versement du premier salaire</div>
</div>"""


def _employer_html(data: Secu01Data) -> str:
    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DE L'EMPLOYEUR</div>
  <table class="fields-table">
    <tr><td class="field-label">Raison sociale / Nom :</td><td class="field-value">{_esc(data.raison_sociale) or _blank()}</td></tr>
    <tr><td class="field-label">Forme juridique :</td><td class="field-value">{_esc(data.forme_juridique)}</td></tr>
    <tr><td class="field-label">NIF :</td><td class="field-value">{_esc(data.nif) or _blank()}</td></tr>
    <tr><td class="field-label">NIS :</td><td class="field-value">{_esc(data.nis) or _blank()}</td></tr>
    <tr><td class="field-label">N° Registre de Commerce :</td><td class="field-value">{_esc(data.rc) or _blank()}</td></tr>
    <tr><td class="field-label">Activité :</td><td class="field-value">{_esc(data.activite) or _blank()}</td></tr>
    <tr><td class="field-label">Adresse du siège :</td><td class="field-value">{_esc(data.adresse) or _blank()}</td></tr>
    <tr><td class="field-label">Commune :</td><td class="field-value">{_esc(data.commune) or _blank(20)}</td></tr>
    <tr><td class="field-label">Wilaya :</td><td class="field-value">{_esc(data.wilaya) or _blank(20)}</td></tr>
    <tr><td class="field-label">Téléphone :</td><td class="field-value">{_esc(data.phone) or _blank(20)}</td></tr>
    <tr><td class="field-label">Email :</td><td class="field-value">{_esc(data.email) or _blank(20)}</td></tr>
    <tr><td class="field-label">Représentant légal :</td><td class="field-value">{_esc(data.representant_nom) or _blank()} ({_esc(data.representant_qualite)})</td></tr>
  </table>
</div>"""


def _employment_html(data: Secu01Data) -> str:
    return f"""<div class="section">
  <div class="section-title">II — RENSEIGNEMENTS SUR L'EMPLOI</div>
  <table class="fields-table">
    <tr><td class="field-label">Date de début d'activité :</td><td class="field-value">{_esc(data.date_debut_activite) or '....../....../......'}</td></tr>
    <tr><td class="field-label">Date d'embauche du 1er salarié :</td><td class="field-value">{_esc(data.date_premier_emploi) or '....../....../......'}</td></tr>
    <tr><td class="field-label">Effectif prévu :</td><td class="field-value">{data.effectif_prevu}</td></tr>
    <tr><td class="field-label">Salaire mensuel brut estimé (1er salarié) :</td><td class="field-value">{_fmt(data.salaire_mensuel_estime)} DA</td></tr>
  </table>
</div>"""


def _contributions_html(calc: dict) -> str:
    return f"""<div class="section">
  <div class="section-title">III — ESTIMATION DES COTISATIONS MENSUELLES</div>
  <table class="summary-table">
    <tr><td class="label">Salaire mensuel brut estimé</td><td class="amount">{_fmt(calc['salaire_mensuel'])} DA</td></tr>
    <tr><td class="label">Part salariale (9%)</td><td class="amount">{_fmt(calc['cotisation_mensuelle_salariale'])} DA</td></tr>
    <tr><td class="label">Part patronale (25,5%)</td><td class="amount">{_fmt(calc['cotisation_mensuelle_employeur'])} DA</td></tr>
    <tr><td class="label">Total cotisations CNAS</td><td class="amount">{_fmt(calc['cotisation_mensuelle_totale'])} DA</td></tr>
    <tr class="total-row"><td class="label">Coût total employeur (salaire + cotisations)</td><td class="amount">{_fmt(calc['cout_total_employeur_mensuel'])} DA</td></tr>
  </table>
  <div class="note">Estimation indicative basée sur les taux CNAS 2026. Les cotisations sont dues chaque mois.</div>
</div>"""


def _documents_html() -> str:
    docs = [
        "Copie du Registre de Commerce (personnes morales et physiques)",
        "N° d'identification fiscale (NIF) — carte d'immatriculation",
        "N° d'identification statistique (NIS)",
        "Statuts notariés (personnes morales)",
        "Copie de la pièce d'identité du représentant légal",
        "Contrat de travail du premier salarié",
        "Déclaration de nomination du représentant légal",
    ]
    items = "".join(f'<div class="checkbox-line">☐ {d}</div>' for d in docs)
    return f"""<div class="section">
  <div class="section-title">IV — PIÈCES À JOINDRE</div>
  {items}
  <div class="note">Cochez les pièces jointes au dossier.</div>
</div>"""


def _signature_html(data: Secu01Data) -> str:
    return f"""<div class="section">
  <div class="attestation">
    Je soussigné(e), représentant légal de l'employeur susmentionné, demande
    l'affiliation au régime de la sécurité sociale et certifie l'exactitude
    des renseignements fournis.
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {_esc(data.fait_a) or '....................'} <strong>le</strong> {_esc(data.date_declaration) or '....../....../......'}
  </div>
  <div class="signature-block">
    <div class="sig-box">Signature de l'employeur<br><br><br>Cachet</div>
    <div class="sig-box">Agent CNAS<br><br><br>Cachet et signature</div>
  </div>
</div>"""


def _legal_html() -> str:
    return """<div class="section legal-page">
  <div class="page-header">RÉFÉRENCES LÉGALES — AFFILIATION CNAS</div>
  <p>Base légale : Loi n°83-14 du 2 juillet 1983 relative aux obligations des
  assurés sociaux, modifiée et complétée.</p>
  <p>Tout employeur est tenu de s'affilier à la CNAS et de déclarer ses salariés
  avant le versement du premier salaire. L'affiliation ouvre droit à la gestion
  des cotisations sociales et aux prestations pour les salariés.</p>
  <p>Le défaut d'affiliation ou de déclaration de salarié expose l'employeur à
  des majorations de retard et sanctions prévues par la législation de la
  sécurité sociale.</p>
  <p>Cotisations : part patronale ≈ 25,5% du salaire brut — part salariale ≈ 9%.
  Déclaration et paiement mensuels via la télédeclaration
  (teledeclaration.cnas.dz) ou auprès de l'agence locale.</p>
</div>"""


# ── Main generator ────────────────────────────────────────────────────────────

def generate_secu01(data: Secu01Data) -> str:
    """Generate complete CNAS SECU 01 affiliation form as HTML.

    Args:
        data: Secu01Data with employer info and employment details

    Returns:
        Complete HTML string ready to save or render
    """
    calc = calculate_secu01(data)

    body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>SECU 01 — Affiliation CNAS {data.raison_sociale or 'Employeur'}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_employer_html(data)}
{_employment_html(data)}
{_contributions_html(calc)}
{_documents_html()}
{_signature_html(data)}
{_legal_html()}

</body>
</html>"""

    hook_generation(
        "secu01_cnas",
        {"raison_sociale": data.raison_sociale, "effectif": data.effectif_prevu},
        body,
    )
    return body


generate_secu01_html = generate_secu01


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = Secu01Data(
        agence_cnas="Agence CNAS El Bayadh",
        wilaya="32-El Bayadh",
        nif="1234567890A",
        nis="0998161234567",
        rc="16/00-1234567B21",
        raison_sociale="SARL TECH SOLUTIONS",
        forme_juridique="SARL",
        activite="Prestation de services informatiques",
        adresse="123 Rue Didouche Mourad",
        commune="El Bayadh",
        phone="+213 661 23 45 67",
        email="contact@techsolutions.dz",
        date_debut_activite="01/01/2026",
        date_premier_emploi="01/03/2026",
        effectif_prevu=3,
        salaire_mensuel_estime=60_000,
        representant_nom="Benali Ahmed",
        representant_qualite="Gérant",
        fait_a="El Bayadh",
        date_declaration="15/02/2026",
    )

    calc = calculate_secu01(sample)
    print("=== SECU 01 — Affiliation CNAS ===")
    print(f"Employeur : {sample.raison_sociale}")
    print(f"Salaire estimé : {_fmt(calc['salaire_mensuel'])} DA/mois")
    print(f"Part salariale (9%) : {_fmt(calc['cotisation_mensuelle_salariale'])} DA")
    print(f"Part patronale (25,5%) : {_fmt(calc['cotisation_mensuelle_employeur'])} DA")
    print(f"Coût total employeur : {_fmt(calc['cout_total_employeur_mensuel'])} DA/mois")

    if "--html" in sys.argv:
        html = generate_secu01(sample)
        out = "secu01_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out} ({len(html):,} chars)")
