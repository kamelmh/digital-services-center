"""G13 BNC Official Form Generator — Déclaration du Résultat des Professions Non Commerciales.

Generates the official G N°13 annual income declaration form for liberal professions
(aspiring accountants, lawyers, doctors, consultants, engineers, teachers, freelancers).

Who must file:
- All liberal professionals (avocats, médecins, experts-comptables, consultants,
  ingénieurs, enseignants, traducteurs, etc.)
- Annual declaration of global income (IRG) — Impôt sur le Revenu Global
- Deadline: April 30 each year (for previous year's income)
- Legal basis: Article 31 bis du Code des Impôts Directs et Taxes Assimilées (CIDTA)

Usage:
    from g13_bnc_generator import G13Input, calculate_g13, generate_g13, generate_g13_html

Reference: knowledge_base/forms/g13_deep_dive.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


# ── G13Input ─────────────────────────────────────────────────────────────────
# Structured input for the G13 BNC generator — mirrors the deep-dive form fields.

@dataclass
class G13Input:
    """Input data for G13 BNC generator."""

    nif: str = ""                          # Numéro d'Identification Fiscale (15 chiffres)
    nin: str = ""                          # Numéro d'Identification Nationale (18 chiffres)
    name: str = ""                         # Nom complet (français / arabe)
    profession: str = ""                   # Ex: "Consultant", "Médecin", "Avocat"
    address: str = ""                      # Adresse complète
    wilaya: str = "32"                     # Code wilaya (32 = El Bayadh par défaut)
    year: int = datetime.now().year       # Année d'imposition

    # Financial
    annual_revenue: float = 0.0            # Chiffre d'affaires / recettes annuelles (DA)
    cascnos_contribution: float | None = None  # Cotisation CASNOS (15% du CA); if None, computed
    advance_payments: float = 0.0          # Acomptes déjà versés (acomptes provisionnels) (DA)

    # Deductible expenses (charges déductibles per Article 31 bis CIDTA)
    rent_expenses: float = 0.0             # Loyer professionnel (déductible) (DA)
    equipment_expenses: float = 0.0        # Petit matériel / équipement (déductible) (DA)
    insurance_expenses: float = 0.0        # Assurance responsabilité professionnelle (déductible) (DA)
    other_expenses: float = 0.0            # Autres frais professionnels (déductibles) (DA)
    depreciation: float = 0.0              # Amortissements (10-25%/an, déductible) (DA)

    # Metadata
    fait_a: str = ""                       # Ville où la déclaration est faite
    date_declaration: str = ""             # Date de la déclaration (DD/MM/AAAA)


# ── IRG 2026 Bareme (6 tranches) ──────────────────────────────────────────────
# Applied to annual net result. Limits are annual DZD.
# Source: DGI 2026 rates (same as G1/G29)
IRG_BAREME = [
    (240_000, 0.00),    # 0 – 240 000 DA → 0%
    (480_000, 0.23),    # 240 001 – 480 000 DA → 23%
    (960_000, 0.27),    # 480 001 – 960 000 DA → 27%
    (1_920_000, 0.30),  # 960 001 – 1 920 000 DA → 30%
    (3_840_000, 0.33),  # 1 920 001 – 3 840 000 DA → 33%
    (float("inf"), 0.35), # 3 840 001+ → 35%
]


def _fmt_dzd(n: float) -> str:
    """Format number with spaces as thousand separators, for DZD display."""
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _compute_net_result(annual_revenue: float,
                        rent_expenses: float,
                        equipment_expenses: float,
                        insurance_expenses: float,
                        other_expenses: float,
                        depreciation: float,
                        cascnos_contribution: float | None = None) -> float:
    """Net result = revenue - all deductible expenses - CASNOS (if provided).

    Deductible expenses (charges déductibles) per Article 31 bis CIDTA:
    - Professional costs (rent, equipment, supplies) — actual
    - Social contributions (CASNOS 15% of turnover) — computed if not provided
    - Professional liability insurance — actual
    - Depreciation — 10-25%/year on equipment (user provides % or amount)
    - Other professional expenses — actual
    """
    total_expenses = (
        rent_expenses
        + equipment_expenses
        + insurance_expenses
        + other_expenses
        + depreciation
    )
    # CASNOS: 15% of annual revenue if not explicitly provided
    cascnos = cascnos_contribution if (cascnos_contribution or 0) > 0 else (annual_revenue * 0.15)

    net = annual_revenue - total_expenses - cascnos
    return max(net, 0.0)  # never negative for IRG calculation


def _calculate_irg(net_result_annual: float) -> dict:
    """Apply the 6-tranche IRG bareme to annual net result.

    Matches the G1 GGR pattern: bareme limits are annual (DZD),
    we compute cumulative tax on the full annual net result,
    then the "monthly average" and "multiply by 12" in the
    deep-dive are descriptive steps — the final tax is already annual.
    """
    tax = 0.0
    prev_limit = 0.0
    for limit, rate in IRG_BAREME:
        if net_result_annual <= prev_limit:
            break
        taxable = min(net_result_annual, limit) - prev_limit
        if taxable > 0:
            tax += taxable * rate
        prev_limit = limit

    monthly_avg = net_result_annual / 12.0
    effective_rate = round((tax / net_result_annual * 100) if net_result_annual > 0 else 0, 2)

    return {
        "net_result": net_result_annual,
        "monthly_average": round(monthly_avg, 2),
        "tax_annual": round(tax, 2),
        "effective_rate": effective_rate,
    }


def calculate_g13(annual_revenue: float,
                  rent_expenses: float,
                  equipment_expenses: float,
                  insurance_expenses: float,
                  other_expenses: float,
                  depreciation: float,
                  cascnos_contribution: float | None = None,
                  advance_payments: float = 0.0) -> dict:
    """Calculate G13 IRG and financial fields.

    Args:
        annual_revenue: Chiffre d'affaires / recettes annuelles (DA)
        rent_expenses: Loyer professionnel (déductible) (DA)
        equipment_expenses: Petit matériel / équipement (déductible) (DA)
        insurance_expenses: Assurance responsabilité professionnelle (déductible) (DA)
        other_expenses: Autres frais professionnels (déductibles) (DA)
        depreciation: Amortissements (10-25%/an, déductible) (DA)
        cascnos_contribution: Cotisation CASNOS 15% du CA (DA); if None, computed as 15% of revenue
        advance_payments: Acomptes déjà versés (acomptes provisionnels) (DA)

    Returns:
        dict with: net_result, monthly_average, tax_annual, tax_due, effective_rate
    """
    net_result = _compute_net_result(
        annual_revenue=annual_revenue,
        rent_expenses=rent_expenses,
        equipment_expenses=equipment_expenses,
        insurance_expenses=insurance_expenses,
        other_expenses=other_expenses,
        depreciation=depreciation,
        cascnos_contribution=cascnos_contribution,
    )

    # IRG on the ANNUAL net result (bareme limits are annual DZD)
    irg = _calculate_irg(net_result)
    tax_due = irg["tax_annual"] - advance_payments

    effective_rate = round((irg["tax_annual"] / annual_revenue * 100) if annual_revenue > 0 else 0, 2)

    return {
        "net_result": net_result,
        "monthly_average": irg["monthly_average"],
        "tax_annual": irg["tax_annual"],
        "tax_due": tax_due,
        "effective_rate": effective_rate,
    }


def _css_g13() -> str:
    """CSS for G13 form, matching DGI printable form style."""
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
  .dgi { font-size: 10pt; font-weight: bold; margin: 3px 0; }
  .header h1 { font-size: 14pt; margin: 5px 0; }
  .subtitle { font-size: 9pt; }
  .deadline { font-size: 9pt; font-weight: bold; margin-top: 5px; padding: 4px; border: 1px solid #000; background: #f8f8f8; }
  .section { margin: 10px 0; page-break-inside: avoid; }
  .section-title { font-size: 10pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 3px; margin-bottom: 5px; }
  .section-title-ar { font-size: 9pt; color: #666; margin-bottom: 5px; text-align: right; direction: rtl; }
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 3px 5px; font-size: 9pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 35%; }
  .field-value { border-bottom: 1px dotted #999; width: 40%; }
  .rev-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .rev-table th, .rev-table td { border: 1px solid #000; padding: 4px 6px; font-size: 8.5pt; text-align: center; }
  .rev-table th { background: #f0f0f0; font-weight: bold; }
  .rev-table .num { font-family: 'Courier New', monospace; font-size: 9pt; }
  .rev-table .activity { text-align: left; }
  .rev-table .total-row { background: #f8f8f8; font-weight: bold; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 55%; }
  .summary-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .summary-table .highlight { background: #f0f0f0; font-weight: bold; font-size: 10pt; }
  .summary-table .result { background: #e8e8e8; font-weight: bold; font-size: 11pt; }
  .impot-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .impot-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .impot-table .label { font-weight: bold; width: 55%; }
  .impot-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .impot-table .highlight { background: #f0f0f0; font-weight: bold; }
  .impot-table .result { background: #e8e8e8; font-weight: bold; font-size: 10pt; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }
  .page { page-break-before: always; }
  .page-header { font-size: 10pt; font-weight: bold; text-align: center; margin-bottom: 10px; }
  .legal-page h3 { font-size: 10pt; margin: 10px 0 5px; }
  .legal-page p { font-size: 8.5pt; text-align: justify; margin: 5px 0; line-height: 1.5; }
  @media print { body { padding: 0; } .no-print { display: none; }
</style>"""


def generate_g13_html(input_: G13Input, calc: dict) -> str:
    """Generate complete G13 form as HTML, matching the DGI printable form style.

    Layout follows knowledge_base/forms/g13_deep_dive.md sections:
    - Header (République, DGI, Série G N°13)
    - Identification (NIF, NIN, name, profession, address, wilaya)
    - Declaration type (IRG — professions non commerciales)
    - Key sections: Chiffre d'affaires, Charges déductibles, Résultat net, IRG calculation, Acomptes versés, Solde dû
    - Tax scale reference (bareme)
    - Signature block
    """
    net_result = calc["net_result"]
    monthly_avg = calc["monthly_average"]
    tax_annual = calc["tax_annual"]
    tax_due = tax_annual - input_.advance_payments
    effective_rate = calc["effective_rate"]

    # --- Helper: HTML escape ---
    def _esc(v: object, default: str = "") -> str:
        if v is None:
            return default
        import html as _h
        return _h.escape(str(v))

    # --- Format DZD ---
    def _fmt_dzd(n: float) -> str:
        if n == int(n):
            return f"{int(n):,}".replace(",", " ")
        return f"{n:,.2f}".replace(",", " ")

    # --- IRG bareme HTML ---
    bareme_rows = ""
    for limit, rate in IRG_BAREME:
        label = f"≤ {_fmt_dzd(limit)} DA" if limit != float("inf") else "3 840 001+ DA"
        bareme_rows += f"<tr><td>{label}</td><td>{rate*100:.0f}%</td></tr>"

    # --- Header ---
    html = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G13 — Déclaration IRG Professions Non Commerciales {input_.year}</title>
{_css_g13()}
</head>
<body>

<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h1>Série G N°13</h1>
  <div class="subtitle">DÉCLARATION DU RÉSULTAT DES PROFESSIONS NON COMMERCIALES</div>
  <div class="subtitle">(BNC)</div>
  <div class="deadline">Déclaration à souscrire, au plus tard le 30 Avril de chaque année</div>
</div>"""

    # --- DGI Hierarchy ---
    html += f"""<div class="section">
  <table class="dgi-table">
    <tr><td class="dgi-label">Wilaya :</td><td class="dgi-value">{_esc(input_.wilaya) or '...................................................'}</td></tr>
    <tr><td class="dgi-label">Structure :</td><td class="dgi-value">{_esc(input_.address[:40]) or '...................................................'}</td></tr>
    <tr><td class="dgi-label">Année d'imposition :</td><td class="dgi-value">{input_.year}</td></tr>
  </table>
</div>"""

    # --- Identification ---
    html += f"""<div class="section">
  <div class="section-title">IDENTIFICATION DU DÉCLARANT</div>
  <table class="fields-table">
    <tr><td class="field-label">NIF :</td><td class="field-value">{_esc(input_.nif) or '................................'}</td></tr>
    <tr><td class="field-label">NIN :</td><td class="field-value">{_esc(input_.nin) or '................................'}</td></tr>
    <tr><td class="field-label">Nom et Prénom :</td><td class="field-value">{_esc(input_.name) or '................................'}</td></tr>
    <tr><td class="field-label">Profession :</td><td class="field-value">{_esc(input_.profession) or '................................'}</td></tr>
    <tr><td class="field-label">Adresse :</td><td class="field-value">{_esc(input_.address) or '................................'}</td></tr>
    <tr><td class="field-label">Wilaya :</td><td class="field-value">{_esc(input_.wilaya)}</td></tr>
  </table>
</div>"""

    # --- Declaration Type ---
    html += f"""<div class="section">
  <div class="section-title">TYPE DE DÉCLARATION</div>
  <p>IMPÔT SUR LE REVENU GLOBAL<br>
  Déclaration des bénéfices des professions non commerciales<br>
  (Régime simplifié des professions non commerciales)<br>
  Année de souscription: {input_.year}<br>
  Résultat de l'année: {_fmt_dzd(net_result)} DA</p>
</div>"""

    # --- Section 1: Chiffre d'affaires ---
    html += f"""<div class="section">
  <div class="section-title">SECTION 1 — CHIFFRE D'AFFAIRES ANNUEL</div>
  <table class="rev-table">
    <thead><tr><th>Description</th><th>Montant DA</th></thead>
    <tbody>
      <tr><td>Chiffre d'affaires / recettes annuelles</td><td class="num">{_fmt_dzd(input_.annual_revenue)}</td></tr>
      <tr><td>Cotisation CASNOS (15%)</td><td class="num">{_fmt_dzd(input_.cascnos_contribution if input_.cascnos_contribution > 0 else input_.annual_revenue * 0.15)}</td></tr>
      <tr class="total-row"><td><strong>Total charges déductibles</strong></td><td class="num"><strong>{_fmt_dzd(calc.get('total_deductible_expenses', 0))}</strong></td></tr>
    </tbody>
  </table>
</div>"""

    # --- Section 2: Charges déductibles ---
    html += f"""<div class="section">
  <div class="section-title">SECTION 2 — CHARGES DÉDUCTIBLES</div>
  <table class="fields-table">
    <tr><td class="field-label">Loyer professionnel</td><td class="field-value">{_fmt_dzd(input_.rent_expenses)}</td></tr>
    <tr><td class="field-label">Petit matériel / Équipement</td><td class="field-value">{_fmt_dzd(input_.equipment_expenses)}</td></tr>
    <tr><td class="field-label">Assurance responsabilité professionnelle</td><td class="field-value">{_fmt_dzd(input_.insurance_expenses)}</td></tr>
    <tr><td class="field-label">Autres frais professionnels</td><td class="field-value">{_fmt_dzd(input_.other_expenses)}</td></tr>
    <tr><td class="field-label">Amortissements (10-25%/an)</td><td class="field-value">{_fmt_dzd(input_.depreciation)}</td></tr>
    <tr class="highlight"><td class="label">Total charges déductibles :</td><td class="amount">{_fmt_dzd(calc.get('total_deductible_expenses', 0))}</td></tr>
  </table>
</div>"""

    # --- Section 3: Résultat net ---
    html += f"""<div class="section">
  <div class="section-title">SECTION 3 — RÉSULTAT NET</div>
  <table class="fields-table">
    <tr><td class="field-label">Chiffre d'affaires</td><td class="amount">{_fmt_dzd(input_.annual_revenue)}</td></tr>
    <tr><td class="field-label">Charges déductibles totales</td><td class="amount">{_fmt_dzd(calc.get('total_deductible_expenses', 0))}</td></tr>
    <tr class="result"><td class="label">Résultat net (recettes - charges) :</td><td class="amount">{_fmt_dzd(net_result)}</td></tr>
  </table>
</div>"""

    # --- Section 4: Calcul de l'IRG ---
    html += f"""<div class="section">
  <div class="section-title">SECTION 4 — CALCUL DE L'IRG (BARÈME PROGRESSIF)</div>
  <table class="rev-table">
    <thead><tr><th>Tranche mensuelle</th><th>Taux</th></thead>
    <tbody>{bareme_rows}</tbody>
  </table>
  <p>Moyenne mensuelle : {_fmt_dzd(monthly_avg)} DA</p>
  <p>Impôt annuel brut : {_fmt_dzd(tax_annual)} DA</p>
  <p>Acomptes déjà versés : {_fmt_dzd(input_.advance_payments)}</p>
  <p><strong>Solde dû (impôt − acomptes) : {_fmt_dzd(tax_due)}</strong></p>
</div>"""

    # --- Section 5: Acomptes versés ---
    html += f"""<div class="section">
  <div class="section-title">SECTION 5 — ACOMPTES VERSÉS</div>
  <table class="fields-table">
    <tr><td class="field-label">Acomptes déjà payés (20{input_.year-1}</td><td class="field-value">{_fmt_dzd(input_.advance_payments)}</td></tr>
  </table>
</div>"""

    # --- Signature ---
    html += f"""<div class="section">
  <div class="attestation">
    J'atteste de l'exactitude des renseignements portés sur la présente déclaration.
    Je suis informé(e) que tout fait passible des sanctions prévues par les textes en vigueur
    pourra être relevé contre moi.
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {_esc(input_.fait_a) or '....................'} <strong>le</strong> {_esc(input_.date_declaration) or '....../....../......'}
  </div>
  <div class="signature-block">
    <div class="sig-box">Signature du déclarant<br><br><br>Cachet</div>
    <div class="sig-box">Cadre réservé à l'administration<br><br><br>Cachet et signature</div>
  </div>
</div>"""

    # --- Legal references ---
    html += f"""<div class="page legal-page">
  <div class="page-header">RÉFÉRENCES LÉGALES — G13 BNC</div>
  <p>Base légale: Article 31 bis du Code des Impôts Directs et Taxes Assimilées (CIDTA).</p>
  <p>Toute personne physique percevant des revenus des professions non commerciales en Algérie
  est tenue de souscrire une déclaration annuelle au plus tard le 30 avril de chaque année.</p>
  <p>Le défaut de déclaration ou la déclaration inexacte est passible de majorations et amendes
  conformément au Code des Procédures Fiscales et au CIDTA.</p>
</div>"""

    html += "</body></html>"
    return html


if __name__ == "__main__":
    # CLI demo
    import sys

    # Sample: consultant with 2M DA revenue
    result = calculate_g13(
        annual_revenue=2_000_000,
        rent_expenses=240_000,
        equipment_expenses=50_000,
        insurance_expenses=30_000,
        other_expenses=20_000,
        depreciation=15_000,
        cascnos_contribution=300_000,
        advance_payments=100_000,
    )

    print("=== G13 BNC — IRG Calculation ===")
    print(f"Résultat net: {result['net_result']:,.0f} DA")
    print(f"Moyenne mensuelle: {result['monthly_average']:,.0f} DA")
    print(f"Impôt annuel brut: {result['tax_annual']:,.0f} DA")
    print(f"Acomptes versés: {100_000:,.0f} DA")
    print(f"Solde dû: {result['tax_due']:,.0f} DA")
    print(f"Taux effectif: {result['effective_rate']:.2f}%")

    if "--html" in sys.argv:
        # Minimal HTML generation for demo (would need full G13Input + generate_g13_html)
        print("\n(Use Python API for full HTML generation)")