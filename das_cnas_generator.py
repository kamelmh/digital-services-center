"""DAS CNAS Generator — Déclaration Annuelle des Salaires (Social Security).

Generates the CNAS annual salary declaration (DAS — Déclaration Annuelle
des Salaires) that ALL employers must file by January 31 each year.

Note: Separate from DGI's G29 — both must be filed.

CNAS contribution rates 2026:
- Employer: ~25% of gross salary (15% health + 1% maternity + 1.25% work injury
  + 5.25% family allowances + 6.75% retirement + 0.5% unemployment... etc.)
- Employee: ~9% of gross salary
- Total: 34.5% (including 0.5% social works fund)

Usage:
    from das_cnas_generator import DASData, DASEmployee, calculate_das, generate_das

Reference: knowledge_base/agencies/cnas.md
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


def _esc(value: object, default: str = "") -> str:
    if value is None:
        return default
    return _html_mod.escape(str(value))


# ── Constants ─────────────────────────────────────────────────────────────────

# CNAS contribution breakdown (2026) — % of gross salary
CNAS_RATES = {
    "health_employer": 15.0,
    "health_employee": 5.0,
    "maternity_employer": 1.0,
    "work_injury_employer": 1.25,
    "family_allowances_employer": 5.25,
    "retirement_employer": 6.75,
    "retirement_employee": 3.75,
    "unemployment_employer": 0.5,
    "unemployment_employee": 0.5,
    "social_works_employer": 0.5,
}

EMPLOYER_RATE = round(
    CNAS_RATES["health_employer"]
    + CNAS_RATES["maternity_employer"]
    + CNAS_RATES["work_injury_employer"]
    + CNAS_RATES["family_allowances_employer"]
    + CNAS_RATES["retirement_employer"]
    + CNAS_RATES["unemployment_employer"]
    + CNAS_RATES["social_works_employer"], 2
)  # ~25.5% (per ALGERIA_DATA convention: 25.5%)

EMPLOYEE_RATE = round(
    CNAS_RATES["health_employee"]
    + CNAS_RATES["retirement_employee"]
    + CNAS_RATES["unemployment_employee"], 2
)  # 9.25% → rounded convention: 9%

# Convention used across DSC generators (feasibility, G29): employer 25.5%, employee 9%
EMPLOYER_RATE_CONVENTION = 25.5
EMPLOYEE_RATE_CONVENTION = 9.0


@dataclass
class DASEmployee:
    """Single employee entry for the DAS."""
    nom_prenom: str = ""
    nss: str = ""                  # Numéro de Sécurité Sociale
    nif_salarie: str = ""
    date_naissance: str = ""
    date_embauche: str = ""
    categorie: str = "Non-cadre"   # Cadre / Non-cadre / Apprenti / Stagiaire
    salaire_brut_annuel: float = 0.0

    @property
    def cotisation_employeur(self) -> float:
        return round(self.salaire_brut_annuel * EMPLOYER_RATE_CONVENTION / 100, 2)

    @property
    def cotisation_salariale(self) -> float:
        return round(self.salaire_brut_annuel * EMPLOYEE_RATE_CONVENTION / 100, 2)

    @property
    def total_cotisations(self) -> float:
        return self.cotisation_employeur + self.cotisation_salariale


@dataclass
class DASData:
    """Complete data for CNAS DAS declaration."""
    # Agency hierarchy
    agence_cnas: str = ""          # Local CNAS agency
    wilaya: str = ""
    annee: int = datetime.now().year

    # Employer identification
    nif: str = ""
    nis: str = ""                  # Numéro d'Identification Statistique
    raison_sociale: str = ""
    adresse: str = ""
    activite: str = ""
    code_activite: str = ""

    # Employees
    salaries: List[DASEmployee] = field(default_factory=list)

    # Payment metadata
    numero_quittance: str = ""     # Payment receipt number
    fait_a: str = ""
    date_declaration: str = ""


# ── Calculation ───────────────────────────────────────────────────────────────

def calculate_das(data: DASData) -> dict:
    """Compute DAS totals: masse salariale, cotisations employeur/salarié, totals.

    Returns dict with totals per category and grand totals.
    """
    masse_brute = sum(s.salaire_brut_annuel for s in data.salaries)
    cotis_employeur = sum(s.cotisation_employeur for s in data.salaries)
    cotis_salarial = sum(s.cotisation_salariale for s in data.salaries)

    return {
        "n_salaries": len(data.salaries),
        "masse_salariale_brute": round(masse_brute, 2),
        "cotisations_employeur": round(cotis_employeur, 2),
        "cotisations_salariales": round(cotis_salarial, 2),
        "total_cotisations": round(cotis_employeur + cotis_salarial, 2),
        "masse_nette": round(masse_brute - cotis_salarial, 2),
        "taux_employeur": EMPLOYER_RATE_CONVENTION,
        "taux_salarial": EMPLOYEE_RATE_CONVENTION,
    }


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt(n: float) -> str:
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _fmt_cell(n: float) -> str:
    if n == 0:
        return ""
    return _fmt(n)


def _blank(n: int = 30) -> str:
    return "." * n


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css() -> str:
    return """<style>
  @page { size: A4 landscape; margin: 10mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 9pt; color: #1a1a1a; margin: 0; padding: 10px;
    line-height: 1.3;
  }
  .header { text-align: center; border: 2px solid #000; padding: 6px; margin-bottom: 8px; }
  .republique { font-size: 8pt; letter-spacing: 1px; }
  .cnas { font-size: 9pt; font-weight: bold; margin: 2px 0; color: #006400; }
  .header h1 { font-size: 13pt; margin: 4px 0; }
  .subtitle { font-size: 8pt; }
  .deadline { font-size: 8pt; font-weight: bold; margin-top: 4px; padding: 3px; border: 1px solid #000; background: #f8f8f8; }
  .section { margin: 8px 0; page-break-inside: avoid; }
  .section-title { font-size: 9pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 2px; margin-bottom: 4px; }
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 2px 4px; font-size: 8.5pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 30%; }
  .field-value { border-bottom: 1px dotted #999; width: 35%; }
  .employee-table { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 7.5pt; }
  .employee-table th, .employee-table td { border: 1px solid #000; padding: 3px 4px; text-align: center; }
  .employee-table th { background: #006400; color: #fff; font-weight: bold; font-size: 7pt; }
  .employee-table .text-left { text-align: left; }
  .employee-table .num { font-family: 'Courier New', monospace; }
  .employee-table .total-row { background: #f0f0f0; font-weight: bold; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 8.5pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 50%; }
  .summary-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 25%; }
  .summary-table .arabic { width: 25%; text-align: right; direction: rtl; }
  .summary-table .total-row { background: #e8e8e8; font-weight: bold; font-size: 9.5pt; }
  .note { font-size: 7pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 12px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 8pt; border-top: 1px solid #000; padding-top: 4px; }
  .attestation { font-size: 8pt; font-style: italic; margin: 8px 0; padding: 4px; border: 1px solid #ccc; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


# ── HTML section builders ─────────────────────────────────────────────────────

def _header_html(data: DASData) -> str:
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="cnas">CAISSE NATIONALE DES ASSURANCES SOCIALES DES TRAVAILLEURS SALARIÉS</div>
  <h1>DÉCLARATION ANNUELLE DES SALAIRES (DAS)</h1>
  <div class="subtitle">Année civile {data.annee}</div>
  <div class="deadline">À souscrire au plus tard le 31 Janvier {data.annee + 1}</div>
</div>"""


def _identification_html(data: DASData) -> str:
    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DE L'EMPLOYEUR</div>
  <table class="fields-table">
    <tr><td class="field-label">NIF :</td><td class="field-value">{_esc(data.nif) or _blank()}</td></tr>
    <tr><td class="field-label">NIS :</td><td class="field-value">{_esc(data.nis) or _blank()}</td></tr>
    <tr><td class="field-label">Raison sociale :</td><td class="field-value">{_esc(data.raison_sociale) or _blank()}</td></tr>
    <tr><td class="field-label">Adresse :</td><td class="field-value">{_esc(data.adresse) or _blank()}</td></tr>
    <tr><td class="field-label">Activité :</td><td class="field-value">{_esc(data.activite) or _blank()}</td></tr>
    <tr><td class="field-label">Agence CNAS :</td><td class="field-value">{_esc(data.agence_cnas) or _esc(data.wilaya) or _blank(20)}</td></tr>
    <tr><td class="field-label">Nombre de salariés :</td><td class="field-value">{len(data.salaries)}</td></tr>
  </table>
</div>"""


def _employees_table_html(data: DASData) -> str:
    if not data.salaries:
        return '<div class="section"><p style="font-style:italic;text-align:center;">Aucun salarié déclaré.</p></div>'

    rows = ""
    for i, emp in enumerate(data.salaries, 1):
        rows += f"""      <tr>
        <td>{i}</td>
        <td class="text-left">{_esc(emp.nom_prenom)}</td>
        <td>{_esc(emp.nss)}</td>
        <td>{_esc(emp.date_naissance)}</td>
        <td>{_esc(emp.date_embauche)}</td>
        <td>{_esc(emp.categorie)}</td>
        <td class="num">{_fmt(emp.salaire_brut_annuel)}</td>
        <td class="num">{_fmt(emp.cotisation_salariale)}</td>
        <td class="num">{_fmt(emp.cotisation_employeur)}</td>
        <td class="num"><strong>{_fmt(emp.total_cotisations)}</strong></td>
      </tr>"""

    calc = calculate_das(data)
    total_row = f"""      <tr class="total-row">
        <td colspan="6"><strong>TOTAL ({calc['n_salaries']} salariés)</strong></td>
        <td class="num"><strong>{_fmt(calc['masse_salariale_brute'])}</strong></td>
        <td class="num"><strong>{_fmt(calc['cotisations_salariales'])}</strong></td>
        <td class="num"><strong>{_fmt(calc['cotisations_employeur'])}</strong></td>
        <td class="num"><strong>{_fmt(calc['total_cotisations'])}</strong></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">II — DÉTAIL PAR SALARIÉ</div>
  <table class="employee-table">
    <thead>
      <tr>
        <th>N°</th><th>Nom et Prénom</th><th>N° Sécurité<br>Sociale (NSS)</th>
        <th>Date<br>naissance</th><th>Date<br>embauche</th><th>Catégorie</th>
        <th>Salaire brut<br>annuel (DA)</th>
        <th>Cotisation<br>salariale ({EMPLOYEE_RATE_CONVENTION:.0f}%)</th>
        <th>Cotisation<br>employeur ({EMPLOYER_RATE_CONVENTION}%)</th>
        <th>Total<br>cotisations</th>
      </tr>
    </thead>
    <tbody>
{rows}{total_row}
    </tbody>
  </table>
</div>"""


def _summary_html(data: DASData, calc: dict) -> str:
    return f"""<div class="section">
  <div class="section-title">III — RÉCAPITULATIF DES COTISATIONS</div>
  <table class="summary-table">
    <tbody>
      <tr><td class="label">Masse salariale brute annuelle</td><td class="amount">{_fmt(calc['masse_salariale_brute'])}</td><td class="arabic">إجمالي الأجور الخام</td></tr>
      <tr><td class="label">Cotisations salariales ({EMPLOYEE_RATE_CONVENTION:.0f}%)</td><td class="amount">{_fmt(calc['cotisations_salariales'])}</td><td class="arabic">اشتراكات العمال</td></tr>
      <tr><td class="label">Cotisations patronales ({EMPLOYER_RATE_CONVENTION}%)</td><td class="amount">{_fmt(calc['cotisations_employeur'])}</td><td class="arabic">اشتراكات المستخدم</td></tr>
      <tr><td class="label">Total cotisations CNAS</td><td class="amount">{_fmt(calc['total_cotisations'])}</td><td class="arabic">مجموع الاشتراكات</td></tr>
      <tr class="total-row"><td class="label">Masse salariale nette versée</td><td class="amount">{_fmt(calc['masse_nette'])}</td><td class="arabic">صافي الأجور المدفوعة</td></tr>
    </tbody>
  </table>
  {'<table class="summary-table"><tr><td class="label">N° quittance de paiement :</td><td class="amount">' + _esc(data.numero_quittance) + '</td></tr></table>' if data.numero_quittance else ''}
</div>"""


def _rates_reference_html() -> str:
    rows = "".join(
        f"<tr><td>{k.replace('_', ' ').title()}</td>"
        f"<td>{v}%</td></tr>"
        for k, v in CNAS_RATES.items()
    )
    return f"""<div class="section">
  <div class="section-title">BARÈME DE RÉFÉRENCE — TAUX CNAS {datetime.now().year}</div>
  <table class="summary-table">
    <thead><tr><th style="width:70%">Composante</th><th>Taux (% du brut)</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="note">
    Part patronale ≈ {EMPLOYER_RATE_CONVENTION}% — Part salariale ≈ {EMPLOYEE_RATE_CONVENTION:.0f}% — Total ≈ 34.5%.<br>
    Source : cnas.dz — taux vérifiés 2026.
  </div>
</div>"""


def _signature_html(data: DASData) -> str:
    return f"""<div class="section">
  <div class="attestation">
    J'atteste de l'exactitude des renseignements portés sur la présente déclaration annuelle des salaires.
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {_esc(data.fait_a) or '....................'} <strong>le</strong> {_esc(data.date_declaration) or '....../....../......'}
  </div>
  <div class="signature-block">
    <div class="sig-box">L'Employeur<br><br><br>Cachet et signature</div>
    <div class="sig-box">Agent CNAS<br><br><br>Cachet et signature</div>
  </div>
</div>"""


# ── Main generator ────────────────────────────────────────────────────────────

def generate_das(data: DASData) -> str:
    """Generate complete CNAS DAS declaration as HTML.

    Args:
        data: DASData with employer info and employee list

    Returns:
        Complete HTML string ready to save or render
    """
    calc = calculate_das(data)

    body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>DAS CNAS {data.annee} — {data.raison_sociale or 'Employeur'}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_identification_html(data)}
{_employees_table_html(data)}
{_summary_html(data, calc)}
{_rates_reference_html()}
{_signature_html(data)}

</body>
</html>"""

    hook_generation(
        "das_cnas",
        {"annee": data.annee, "raison_sociale": data.raison_sociale},
        body,
    )
    return body


generate_das_html = generate_das


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = DASData(
        agence_cnas="Agence CNAS El Bayadh",
        wilaya="32-El Bayadh",
        annee=2026,
        nif="1234567890A",
        nis="0998161234567",
        raison_sociale="SARL TECH SOLUTIONS",
        adresse="123 Rue Didouche Mourad, El Bayadh",
        activite="Prestation de services informatiques",
        code_activite="6201",
        fait_a="El Bayadh",
        date_declaration="15/01/2027",
        numero_quittance="Q-2027-004512",
        salaries=[
            DASEmployee(
                nom_prenom="Benali Ahmed",
                nss="9603061234",
                date_naissance="06/03/1996",
                date_embauche="01/01/2026",
                categorie="Cadre",
                salaire_brut_annuel=720_000,
            ),
            DASEmployee(
                nom_prenom="Mebarki Fatima",
                nss="8507212345",
                date_naissance="21/07/1985",
                date_embauche="01/03/2026",
                categorie="Non-cadre",
                salaire_brut_annuel=420_000,
            ),
            DASEmployee(
                nom_prenom="Khelifi Youcef",
                nss="9205153456",
                date_naissance="15/05/1992",
                date_embauche="01/06/2026",
                categorie="Non-cadre",
                salaire_brut_annuel=300_000,
            ),
        ],
    )

    result = calculate_das(sample)
    print("=== DAS CNAS — Déclaration Annuelle des Salaires ===")
    print(f"Employeur : {sample.raison_sociale}")
    print(f"Salariés : {result['n_salaries']}")
    print(f"Masse brute : {_fmt(result['masse_salariale_brute'])} DA")
    print(f"Cotisations salariales ({result['taux_salarial']}%) : {_fmt(result['cotisations_salariales'])} DA")
    print(f"Cotisations patronales ({result['taux_employeur']}%) : {_fmt(result['cotisations_employeur'])} DA")
    print(f"Total cotisations : {_fmt(result['total_cotisations'])} DA")

    if "--html" in sys.argv:
        html = generate_das(sample)
        out = "das_cnas_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out} ({len(html):,} chars)")
