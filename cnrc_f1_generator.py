"""CNRC F1 Official Form Generator — Registre du Commerce (Personne Morale).

Generates the commercial registration form (Formulaire d'immatriculation) for
companies (SARL, EURL, SPA, SNC) filing with the CNRC
(Centre National du Registre de Commerce).

Who must file:
- All companies before starting commercial activity
- Filed on paper or via SIDJILCOM online portal
- Required docs: Statutes (notarized), NIF, manager ID, lease contract,
  casier judiciaire n3
- Cost: 4,000 DA timbre fiscal

Usage:
    from cnrc_f1_generator import F1Data, generate_f1, generate_f1_html

Reference: knowledge_base/forms/catalog.md (F1 — Personne Morale)
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


def _esc(value: object, default: str = "") -> str:
    """HTML-escape a value for safe rendering."""
    if value is None:
        return default
    return _html_mod.escape(str(value))


# ── Constants ─────────────────────────────────────────────────────────────────

FORMES_JURIDIQUES = [
    "SARL", "EURL", "SPA", "SNC", "SARL unipersonnelle",
]

from policy_constants import WILAYAS

TIMBRE_FISCAL_DA = 4_000  # Cost of F1 filing (timbre fiscal)


@dataclass
class AssocieData:
    """Single partner/shareholder entry."""
    nom_prenom: str = ""
    nin: str = ""
    date_naissance: str = ""       # JJ/MM/AAAA
    adresse: str = ""
    parts_sociales: int = 0        # Number of shares held
    pourcentage: float = 0.0       # % ownership
    fonction: str = ""             # Gérant / Associé / Président du CA


@dataclass
class F1Data:
    """Complete data for CNRC F1 (Personne Morale) registration."""
    # CNRC hierarchy
    wilaya: str = ""
    centre_cnrс: str = ""          # CNRC local centre
    date_depot: str = ""           # JJ/MM/AAAA

    # Company identity
    denomination: str = ""         # Company name (dénomination sociale)
    forme_juridique: str = "SARL"
    sigle: str = ""                # Optional acronym
    objet_social: str = ""         # Business activity description
    capital_social: float = 0.0    # DZD
    apports_numeraire: float = 0.0   # Cash contributions
    apports_nature: float = 0.0      # In-kind contributions

    # Registered address
    adresse_siege: str = ""
    commune: str = ""
    wilaya_siege: str = ""

    # Duration
    duree_annees: int = 99          # Standard: 99 years

    # Partners / managers
    associes: List[AssocieData] = field(default_factory=list)
    gerant_nom: str = ""
    gerant_nin: str = ""
    gerant_adresse: str = ""
    gerant_phone: str = ""
    gerant_email: str = ""

    # Metadata
    fait_a: str = ""
    date_declaration: str = ""


# ── Calculations ──────────────────────────────────────────────────────────────

def calculate_f1(data: F1Data) -> dict:
    """Compute derived F1 fields: total shares, ownership %, timbre cost.

    Returns dict with: total_parts, parts_check, timbre_cost, n_associes,
    capital_per_part
    """
    total_parts = sum(a.parts_sociales for a in data.associes)

    # Ownership percentages must sum to ~100% if shares declared
    pct_sum = sum(a.pourcentage for a in data.associes)

    capital_per_part = (
        round(data.capital_social / total_parts, 2) if total_parts > 0 else 0.0
    )

    return {
        "total_parts": total_parts,
        "pct_sum": round(pct_sum, 2),
        "parts_valid": (total_parts > 0 and abs(pct_sum - 100.0) < 0.5) or total_parts == 0,
        "timbre_cost": TIMBRE_FISCAL_DA,
        "n_associes": len(data.associes),
        "capital_per_part": capital_per_part,
        "apports_total": data.apports_numeraire + data.apports_nature,
        "apports_match": abs(
            (data.apports_numeraire + data.apports_nature) - data.capital_social
        ) < 1,
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
    font-size: 9.5pt; color: #1a1a1a; margin: 0; padding: 15px;
    line-height: 1.4; direction: ltr;
  }
  .header { text-align: center; border: 2px solid #000; padding: 8px; margin-bottom: 10px; }
  .republique { font-size: 9pt; letter-spacing: 1px; }
  .cnrc { font-size: 10pt; font-weight: bold; margin: 3px 0; }
  .header h1 { font-size: 14pt; margin: 5px 0; }
  .subtitle { font-size: 9pt; }
  .deadline { font-size: 9pt; font-weight: bold; margin-top: 5px; padding: 4px; border: 1px solid #000; background: #f8f8f8; }
  .section { margin: 10px 0; page-break-inside: avoid; }
  .section-title { font-size: 10pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 3px; margin-bottom: 5px; }
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 3px 5px; font-size: 9pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 35%; }
  .field-value { border-bottom: 1px dotted #999; width: 40%; }
  .associe-table { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 8pt; }
  .associe-table th, .associe-table td { border: 1px solid #000; padding: 3px 4px; text-align: center; }
  .associe-table th { background: #f0f0f0; font-weight: bold; }
  .associe-table .text-left { text-align: left; }
  .associe-table .total-row { background: #f8f8f8; font-weight: bold; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 55%; }
  .summary-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .summary-table .highlight { background: #f0f0f0; font-weight: bold; }
  .checkbox-line { font-size: 9pt; margin: 3px 0; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }
  .legal-page p { font-size: 8.5pt; text-align: justify; margin: 5px 0; line-height: 1.5; }
  .page-header { font-size: 10pt; font-weight: bold; text-align: center; margin-bottom: 10px; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


# ── HTML section builders ─────────────────────────────────────────────────────

def _header_html(data: F1Data) -> str:
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="cnrc">CENTRE NATIONAL DU REGISTRE DE COMMERCE (CNRC)</div>
  <h1>FORMULAIRE F N°1</h1>
  <div class="subtitle">IMMATRICULATION AU REGISTRE DU COMMERCE — PERSONNE MORALE</div>
  <div class="deadline">Timbre fiscal : {_fmt(TIMBRE_FISCAL_DA)} DA — À déposer avant le début d'activité</div>
</div>"""


def _identification_html(data: F1Data, calc: dict) -> str:
    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DE LA SOCIÉTÉ</div>
  <table class="fields-table">
    <tr><td class="field-label">Dénomination sociale :</td><td class="field-value">{_esc(data.denomination) or _blank()}</td></tr>
    <tr><td class="field-label">Sigle :</td><td class="field-value">{_esc(data.sigle) or _blank(20)}</td></tr>
    <tr><td class="field-label">Forme juridique :</td><td class="field-value">{_esc(data.forme_juridique)}</td></tr>
    <tr><td class="field-label">Objet social :</td><td class="field-value">{_esc(data.objet_social) or _blank(40)}</td></tr>
    <tr><td class="field-label">Capital social :</td><td class="field-value">{_fmt(data.capital_social)} DA</td></tr>
    <tr><td class="field-label">— Apports en numéraire :</td><td class="field-value">{_fmt(data.apports_numeraire)} DA</td></tr>
    <tr><td class="field-label">— Apports en nature :</td><td class="field-value">{_fmt(data.apports_nature)} DA</td></tr>
    <tr><td class="field-label">Durée de la société :</td><td class="field-value">{data.duree_annees} ans</td></tr>
    <tr><td class="field-label">Siège social :</td><td class="field-value">{_esc(data.adresse_siege) or _blank()}</td></tr>
    <tr><td class="field-label">Commune :</td><td class="field-value">{_esc(data.commune) or _blank(20)}</td></tr>
    <tr><td class="field-label">Wilaya :</td><td class="field-value">{_esc(data.wilaya_siege) or _esc(data.wilaya) or _blank(20)}</td></tr>
  </table>
  {'<div class="note">⚠ Apports (numéraire + nature) ne correspondent pas au capital social.</div>' if not calc["apports_match"] and calc["apports_total"] > 0 else ''}
</div>"""


def _associes_html(data: F1Data, calc: dict) -> str:
    if not data.associes:
        return f"""<div class="section">
  <div class="section-title">II — ASSOCIÉS ET GÉRANTS</div>
  <p style="font-style:italic;">Aucun associé déclaré.</p>
</div>"""

    rows = ""
    for i, a in enumerate(data.associes, 1):
        rows += f"""      <tr>
        <td>{i}</td>
        <td class="text-left">{_esc(a.nom_prenom)}</td>
        <td>{_esc(a.nin)}</td>
        <td>{_esc(a.date_naissance)}</td>
        <td class="text-left">{_esc(a.adresse)}</td>
        <td>{a.parts_sociales}</td>
        <td>{a.pourcentage}%</td>
        <td>{_esc(a.fonction)}</td>
      </tr>"""

    warning = ""
    if not calc["parts_valid"]:
        warning = '<div class="note">⚠ Les pourcentages ne totalisent pas 100%.</div>'

    return f"""<div class="section">
  <div class="section-title">II — ASSOCIÉS ({calc['n_associes']})</div>
  <table class="associe-table">
    <thead>
      <tr>
        <th>N°</th><th>Nom et Prénom</th><th>NIN</th><th>Date naissance</th>
        <th>Adresse</th><th>Parts</th><th>%</th><th>Fonction</th>
      </tr>
    </thead>
    <tbody>
{rows}
      <tr class="total-row">
        <td colspan="5"><strong>TOTAL</strong></td>
        <td><strong>{calc['total_parts']}</strong></td>
        <td><strong>{calc['pct_sum']}%</strong></td>
        <td></td>
      </tr>
    </tbody>
  </table>
  <table class="fields-table">
    <tr><td class="field-label">Valeur nominale d'une part :</td><td class="field-value">{_fmt(calc['capital_per_part'])} DA</td></tr>
  </table>
  {warning}
</div>"""


def _gerant_html(data: F1Data) -> str:
    return f"""<div class="section">
  <div class="section-title">III — REPRÉSENTANT LÉGAL (GÉRANT)</div>
  <table class="fields-table">
    <tr><td class="field-label">Nom et Prénom :</td><td class="field-value">{_esc(data.gerant_nom) or _blank()}</td></tr>
    <tr><td class="field-label">NIN :</td><td class="field-value">{_esc(data.gerant_nin) or _blank()}</td></tr>
    <tr><td class="field-label">Adresse personnelle :</td><td class="field-value">{_esc(data.gerant_adresse) or _blank()}</td></tr>
    <tr><td class="field-label">Téléphone :</td><td class="field-value">{_esc(data.gerant_phone) or _blank(20)}</td></tr>
    <tr><td class="field-label">Email :</td><td class="field-value">{_esc(data.gerant_email) or _blank(20)}</td></tr>
  </table>
</div>"""


def _documents_html() -> str:
    docs = [
        "Statuts notariés (2 exemplaires)",
        "Attestation de dépôt des fonds bancaire",
        "Certificat négatif (dénomination)",
        "Justificatif du siège social (contrat de bail ou acte de propriété)",
        "Casier judiciaire du gérant (n°3, moins de 3 mois)",
        "Copie de la pièce d'identité du gérant (CNI ou passeport)",
        "Acte de nomination du gérant (si non prévu aux statuts)",
        "Déclaration sur l'honneur de non-condamnation du gérant",
    ]
    items = "".join(f'<div class="checkbox-line">☐ {d}</div>' for d in docs)
    return f"""<div class="section">
  <div class="section-title">IV — PIÈCES CONSTITUTIVES DU DOSSIER</div>
  {items}
  <div class="note">Cochez les pièces jointes au dossier. Toutes sont obligatoires.</div>
</div>"""


def _payment_html(calc: dict) -> str:
    return f"""<div class="section">
  <div class="section-title">V — DROITS DE TIMBRE</div>
  <table class="summary-table">
    <tr><td class="label">Droit fixe d'immatriculation (timbre fiscal) :</td><td class="amount">{_fmt(calc['timbre_cost'])} DA</td></tr>
    <tr class="highlight"><td class="label"><strong>Total à payer :</strong></td><td class="amount"><strong>{_fmt(calc['timbre_cost'])} DA</strong></td></tr>
  </table>
  <div class="note">Paiement par timbre fiscal apposé sur le formulaire ou versement au Trésor public.</div>
</div>"""


def _signature_html(data: F1Data) -> str:
    return f"""<div class="section">
  <div class="attestation">
    Je soussigné(e), représentant légal de la société susmentionnée, certifie
    l'exactitude des renseignements portés sur la présente déclaration et joins
    les pièces justificatives requises.
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {_esc(data.fait_a) or '....................'} <strong>le</strong> {_esc(data.date_declaration) or '....../....../......'}
  </div>
  <div class="signature-block">
    <div class="sig-box">Signature du représentant légal<br><br><br>Cachet</div>
    <div class="sig-box">Cadre réservé au CNRC<br><br><br>Cachet et signature</div>
  </div>
</div>"""


def _legal_html() -> str:
    return """<div class="section legal-page">
  <div class="page-header">RÉFÉRENCES LÉGALES — REGISTRE DU COMMERCE</div>
  <p>Base légale : Loi n°05-06 du 23 février 2005 portant modification de l'ordonnance
  n°75-59 du 26 septembre 1975 relative au registre du commerce.</p>
  <p>Décret exécutif n°07-161 du 27 mai 2007 fixant les modalités d'application de la
  loi relative au registre du commerce.</p>
  <p>Toute personne morale exerçant une activité commerciale doit être immatriculée
  au registre du commerce avant le commencement de son activité, au Centre National
  du Registre de Commerce (CNRC) ou via le portail SIDJILCOM.</p>
  <p>L'exercice d'une activité commerciale sans immatriculation est passible de
  sanctions pénales conformément à la législation en vigueur.</p>
</div>"""


# ── Main generator ────────────────────────────────────────────────────────────

def generate_f1(data: F1Data) -> str:
    """Generate complete CNRC F1 form as HTML.

    Args:
        data: F1Data with company info, partners, capital

    Returns:
        Complete HTML string ready to save or render
    """
    calc = calculate_f1(data)

    body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>CNRC F1 — Immatriculation {data.denomination or 'Société'}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_identification_html(data, calc)}
{_associes_html(data, calc)}
{_gerant_html(data)}
{_documents_html()}
{_payment_html(calc)}
{_signature_html(data)}
{_legal_html()}

</body>
</html>"""

    hook_generation(
        "cnrc_f1",
        {"denomination": data.denomination, "forme_juridique": data.forme_juridique},
        body,
    )
    return body


generate_f1_html = generate_f1


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = F1Data(
        wilaya="16-Alger",
        centre_cnrс="CNRC Alger Centre",
        denomination="SARL TECH SOLUTIONS",
        forme_juridique="SARL",
        sigle="TS",
        objet_social="Développement logiciel et services informatiques",
        capital_social=1_000_000,
        apports_numeraire=800_000,
        apports_nature=200_000,
        adresse_siege="123 Rue Didouche Mourad",
        commune="Alger Centre",
        wilaya_siege="16-Alger",
        duree_annees=99,
        associes=[
            AssocieData(
                nom_prenom="Benali Ahmed",
                nin="196030612345678901",
                date_naissance="06/03/1996",
                adresse="El Biar, Alger",
                parts_sociales=600,
                pourcentage=60.0,
                fonction="Gérant",
            ),
            AssocieData(
                nom_prenom="Mebarki Fatima",
                nin="198507212345678902",
                date_naissance="21/07/1985",
                adresse="Hydra, Alger",
                parts_sociales=400,
                pourcentage=40.0,
                fonction="Associée",
            ),
        ],
        gerant_nom="Benali Ahmed",
        gerant_nin="196030612345678901",
        gerant_adresse="El Biar, Alger",
        gerant_phone="+213 661 23 45 67",
        gerant_email="ahmed@techsolutions.dz",
        fait_a="Alger",
        date_declaration="15/01/2026",
    )

    result = calculate_f1(sample)
    print("=== CNRC F1 — Immatriculation Personne Morale ===")
    print(f"Dénomination : {sample.denomination}")
    print(f"Forme juridique : {sample.forme_juridique}")
    print(f"Capital social : {_fmt(sample.capital_social)} DA")
    print(f"Associés : {result['n_associes']}")
    print(f"Total parts : {result['total_parts']} ({result['pct_sum']}%)")
    print(f"Valeur/part : {_fmt(result['capital_per_part'])} DA")
    print(f"Timbre fiscal : {_fmt(result['timbre_cost'])} DA")

    if "--html" in sys.argv:
        html = generate_f1(sample)
        out = "cnrc_f1_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out} ({len(html):,} chars)")
