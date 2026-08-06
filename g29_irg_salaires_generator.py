"""G29 + G30 Official Form Generator — IRG Salaires annual tax form.

Generates filled G29 (Déclaration des Traitements et Émoluments Divers Payés)
and G30 (IRG — Traitements, Salaires, Pensions et Rentes Viagères) forms as
HTML matching the official DGI printable forms.

Who must file: All employers — must declare all salaries, benefits, and IRG withheld.
Deadline: Before April 30 each year.
Legal reference: Article 132 of CIDTA.

Usage:
    from g29_irg_salaires_generator import G29Data, EmployeeData, generate_g29, generate_g29_html
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ── Constants ─────────────────────────────────────────────────────────────────

# IRG Barème 2026 — monthly thresholds (DA)
# (annual_threshold = monthly * 12)
IRG_BAREME_MONTHLY = [
    (15_000, 0.00),
    (30_000, 0.10),
    (60_000, 0.20),
    (120_000, 0.30),
    (float("inf"), 0.40),
]

SITUATION_FAMILIALE = [
    "Célibataire",
    "Marié(e)",
    "Divorcé(e)",
    "Veuf/Veuve",
]

CATEGORIES_SALARIE = [
    "Cadre",
    "Non-cadre",
    "Apprenti",
    "Stagiaire",
]

WILAYAS = [
    "01-Adrar", "02-Chlef", "03-Laghouat", "04-Oum El Bouaghi", "05-Batna",
    "06-Béjaïa", "07-Biskra", "08-Béchar", "09-Blida", "10-Bouira",
    "11-Tamanrasset", "12-Tébessa", "13-Tlemcen", "14-Tiaret", "15-Tizi Ouzou",
    "16-Alger", "17-Djelfa", "18-Jijel", "19-Sétif", "20-Saïda",
    "21-Skikda", "22-Sidi Bel Abbès", "23-Annaba", "24-Guelma", "25-Constantine",
    "26-Médéa", "27-Mostaganem", "28-M'Sila", "29-Mascara", "30-Ouargla",
    "31-Oran", "32-El Bayadh", "33-Illizi", "34-Bordj Bou Arréridj", "35-Boumerdès",
    "36-El Tarf", "37-Tindouf", "38-Tissemsilt", "39-El Oued", "40-Khenchela",
    "41-Souk Ahras", "42-Tipaza", "43-Mila", "44-Aïn Defla", "45-Naâma",
    "46-Aïn Témouchent", "47-Ghardaïa", "48-Relizane", "49-El M'Ghair", "50-El Meniaa",
    "51-Ouled Djellal", "52-Bordj Badji Mokhtar", "53-Béni Abbès", "54-Timimoun",
    "55-Touggourt", "56-Djanet", "57-In Salah", "58-In Guezzam",
]


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class EmployeeData:
    """Single employee salary data for G30 annex."""
    # Identification
    nom_prenom: str = ""
    nif_salarie: str = ""
    date_naissance: str = ""  # JJ/MM/AAAA
    sexe: str = "M"  # M or F
    situation_familiale: str = "Célibataire"
    nombre_parts: float = 1.0
    categorie: str = "Non-cadre"

    # Période d'emploi
    date_debut: str = ""  # JJ/MM/AAAA
    date_fin: str = ""  # JJ/MM/AAAA

    # Salaires et avantages (annuels en DA)
    salaire_brut_base: float = 0.0
    indemnites_logement: float = 0.0
    indemnites_transport: float = 0.0
    indemnites_representation: float = 0.0
    primes_gratifications: float = 0.0
    avantages_en_nature: float = 0.0
    indemnite_experience_pro: float = 0.0  # IEP
    heures_supplementaires: float = 0.0
    autres_indemnites: float = 0.0

    # Épargne salariale (exonérée à 80%)
    epargne_salariale: float = 0.0

    # Cotisations salariales
    cotisations_cnas: float = 0.0
    cotisations_casnos: float = 0.0
    cotisations_ramed: float = 0.0
    autres_cotisations: float = 0.0

    @property
    def total_brut_imposable(self) -> float:
        """Total brut imposable = sum of all salary components (10-18)."""
        return (
            self.salaire_brut_base
            + self.indemnites_logement
            + self.indemnites_transport
            + self.indemnites_representation
            + self.primes_gratifications
            + self.avantages_en_nature
            + self.indemnite_experience_pro
            + self.heures_supplementaires
            + self.autres_indemnites
        )

    @property
    def total_cotisations(self) -> float:
        """Total cotisations salariales."""
        return (
            self.cotisations_cnas
            + self.cotisations_casnos
            + self.cotisations_ramed
            + self.autres_cotisations
        )

    @property
    def revenu_net_imposable(self) -> float:
        """Revenu net imposable = total brut imposable - cotisations salariales."""
        return max(0, self.total_brut_imposable - self.total_cotisations)

    @property
    def periode_emploi(self) -> str:
        """Formatted employment period."""
        if self.date_debut and self.date_fin:
            return f"du {self.date_debut} au {self.date_fin}"
        return "..."


@dataclass
class G29Data:
    """Complete data for G29 + G30 form generation."""
    # DGI hierarchy
    wilaya: str = ""
    diw: str = ""
    structure: str = ""
    inspection: str = ""
    recette: str = ""
    annee_imposition: int = datetime.now().year

    # Identification de l'employeur
    nif: str = ""
    raison_sociale: str = ""
    adresse: str = ""
    activite: str = ""
    code_activite: str = ""
    nombre_salaries: int = 0

    # Liste des salariés
    salaries: List[EmployeeData] = field(default_factory=list)

    # Metadata
    beneficiaire: str = ""  # Nom du signataire


# ── IRG Calculation ───────────────────────────────────────────────────────────

def calculate_irg(salaire_annuel: float, nombre_parts: float) -> float:
    """Calculate IRG (Impôt sur le Revenu Global) using the progressive barème.

    The barème is applied monthly. We divide the annual net imposable by 12,
    apply the progressive rates, then multiply back by 12.

    Args:
        salaire_annuel: Annual net imposable (revenu net imposable)
        nombre_parts: Number of fiscal parts (quotient familial)

    Returns:
        Annual IRG amount in DA
    """
    if salaire_annuel <= 0 or nombre_parts <= 0:
        return 0.0

    # Monthly net imposable per part
    monthly_per_part = (salaire_annuel / 12) / nombre_parts

    # Apply progressive barème on monthly_per_part
    irg_monthly = 0.0
    previous_threshold = 0
    for monthly_threshold, rate in IRG_BAREME_MONTHLY:
        if monthly_per_part <= previous_threshold:
            break
        bracket_top = min(monthly_per_part, monthly_threshold)
        bracket_base = bracket_top - previous_threshold
        irg_monthly += bracket_base * rate
        previous_threshold = monthly_threshold

    # Annual IRG = monthly IRG * 12 * number of parts
    irg_annual = irg_monthly * 12 * nombre_parts
    return round(irg_annual, 2)


def calculate_employee_irg(emp: EmployeeData) -> float:
    """Calculate IRG for a single employee."""
    return calculate_irg(emp.revenu_net_imposable, emp.nombre_parts)


# ── Formatting Helpers ────────────────────────────────────────────────────────

def _fmt(n: float) -> str:
    """Format number with spaces as thousand separators."""
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _fmt_cell(n: float) -> str:
    """Format for table cell — empty if zero."""
    if n == 0:
        return ""
    return _fmt(n)


def _checkbox(selected: str, value: str) -> str:
    """Return checked/unchecked checkbox symbol."""
    return "☑" if selected == value else "☐"


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css() -> str:
    """Complete CSS matching g12_official.py style."""
    return """<style>
  @page { size: A4 landscape; margin: 10mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 9pt; color: #1a1a1a; margin: 0; padding: 10px;
    line-height: 1.3;
  }

  /* Header */
  .header { text-align: center; border: 2px solid #000; padding: 6px; margin-bottom: 8px; }
  .republique { font-size: 8pt; letter-spacing: 1px; }
  .dgi { font-size: 9pt; font-weight: bold; margin: 2px 0; }
  .header h1 { font-size: 12pt; margin: 4px 0; }
  .header h2 { font-size: 10pt; margin: 3px 0; font-weight: normal; }
  .subtitle { font-size: 8pt; }
  .deadline { font-size: 8pt; font-weight: bold; margin-top: 4px; padding: 3px; border: 1px solid #000; background: #f8f8f8; }

  /* DGI Hierarchy */
  .dgi-table { width: 100%; border: none; }
  .dgi-table td { border: none; padding: 2px 5px; font-size: 8pt; }
  .dgi-label { font-weight: bold; width: 25%; }
  .dgi-value { border-bottom: 1px dotted #999; }

  /* Sections */
  .section { margin: 8px 0; page-break-inside: avoid; }
  .section-title { font-size: 9pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 2px; margin-bottom: 4px; }

  /* Fields table */
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 2px 4px; font-size: 8pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 30%; }
  .field-value { border-bottom: 1px dotted #999; width: 35%; }

  /* Summary table */
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table th, .summary-table td { border: 1px solid #000; padding: 3px 5px; font-size: 8pt; text-align: center; }
  .summary-table th { background: #f0f0f0; font-weight: bold; }
  .summary-table .num { font-family: 'Courier New', monospace; font-size: 8.5pt; }
  .summary-table .label { text-align: left; }

  /* Employee detail table */
  .employee-table { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 7pt; }
  .employee-table th, .employee-table td { border: 1px solid #000; padding: 2px 3px; text-align: center; }
  .employee-table th { background: #0A1628; color: #D4AF37; font-weight: bold; font-size: 6.5pt; }
  .employee-table td { font-size: 7pt; }
  .employee-table .num { font-family: 'Courier New', monospace; }
  .employee-table .text-left { text-align: left; }
  .employee-table .total-row { background: #f0f0f0; font-weight: bold; }
  .employee-table .subtotal-row { background: #f8f8f8; }

  /* G30 Annex header */
  .g30-header { border: 2px solid #000; padding: 6px; margin: 10px 0 8px; text-align: center; }
  .g30-header h2 { font-size: 11pt; margin: 3px 0; }
  .g30-header .subtitle { font-size: 8pt; }

  /* Notes */
  .note { font-size: 7pt; color: #666; font-style: italic; margin-top: 3px; }

  /* Signature */
  .signature-block { display: flex; justify-content: space-between; margin: 12px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 8pt; border-top: 1px solid #000; padding-top: 4px; }
  .attestation { font-size: 8pt; font-style: italic; margin: 8px 0; padding: 4px; border: 1px solid #ccc; }

  /* Page breaks */
  .page-break { page-break-before: always; }

  /* Print */
  @media print {
    body { padding: 0; font-size: 8pt; }
    .no-print { display: none; }
    .employee-table th { background: #0A1628 !important; color: #D4AF37 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>"""


# ── G29 Page 1: Header + Summary ──────────────────────────────────────────────

def _g29_header_html(data: G29Data) -> str:
    """Official G29 header matching DGI form."""
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h1>Série G N°29</h1>
  <h2>DÉCLARATION DES TRAITEMENTS ET ÉMOOLUMENTS DIVERS PAYÉS</h2>
  <div class="subtitle">DE L'ANNÉE {data.annee_imposition}</div>
  <div class="deadline">Déclaration à souscrire, au plus tard le 30 Avril de chaque année</div>
</div>"""


def _dgi_hierarchy_html(data: G29Data) -> str:
    """DGI institutional hierarchy fields."""
    blank = "..................................................."
    return f"""<div class="section">
  <table class="dgi-table">
    <tr>
      <td class="dgi-label">Wilaya :</td>
      <td class="dgi-value">{data.wilaya or blank}</td>
      <td class="dgi-label">DIW :</td>
      <td class="dgi-value">{data.diw or blank}</td>
    </tr>
    <tr>
      <td class="dgi-label">Structure :</td>
      <td class="dgi-value">{data.structure or blank}</td>
      <td class="dgi-label">Inspection :</td>
      <td class="dgi-value">{data.inspection or blank}</td>
    </tr>
    <tr>
      <td class="dgi-label">Recette des Impôts :</td>
      <td class="dgi-value">{data.recette or blank}</td>
      <td class="dgi-label">Année d'imposition :</td>
      <td class="dgi-value">{data.annee_imposition}</td>
    </tr>
  </table>
</div>"""


def _identification_employeur_html(data: G29Data) -> str:
    """Section I — Identification de l'employeur."""
    blank = "................................"
    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DE L'EMPLOYEUR</div>
  <table class="fields-table">
    <tr>
      <td class="field-label">NIF :</td>
      <td class="field-value">{data.nif or blank}</td>
    </tr>
    <tr>
      <td class="field-label">Raison sociale / Nom :</td>
      <td class="field-value">{data.raison_sociale or blank}</td>
    </tr>
    <tr>
      <td class="field-label">Adresse :</td>
      <td class="field-value">{data.adresse or blank}</td>
    </tr>
    <tr>
      <td class="field-label">Activité :</td>
      <td class="field-value">{data.activite or blank}</td>
    </tr>
    <tr>
      <td class="field-label">Code Activité :</td>
      <td class="field-value">{data.code_activite or blank}</td>
    </tr>
    <tr>
      <td class="field-label">Nombre de salariés :</td>
      <td class="field-value">{data.nombre_salaries or len(data.salaries) or blank}</td>
    </tr>
  </table>
</div>"""


def _resume_masse_salariale_html(data: G29Data) -> str:
    """Section II — Résumé de la masse salariale."""
    total_brut = sum(e.total_brut_imposable for e in data.salaries)
    total_avantages = sum(e.avantages_en_nature for e in data.salaries)
    total_indemnites = sum(
        e.indemnites_logement + e.indemnites_transport + e.indemnites_representation
        + e.indemnite_experience_pro + e.heures_supplementaires + e.autres_indemnites
        for e in data.salaries
    )
    total_cotisations = sum(e.total_cotisations for e in data.salaries)
    total_irg = sum(calculate_employee_irg(e) for e in data.salaries)
    masse_nette = total_brut - total_cotisations - total_irg

    return f"""<div class="section">
  <div class="section-title">II — RÉSUMÉ DE LA MASSE SALARIALE</div>
  <table class="summary-table">
    <thead>
      <tr>
        <th style="width:50%" class="label">Désignation</th>
        <th style="width:25%">Montant (DA)</th>
        <th style="width:25%">Arabe</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="label">Masse salariale brute totale</td>
        <td class="num">{_fmt(total_brut)}</td>
        <td>إجمالي الأجر الخام</td>
      </tr>
      <tr>
        <td class="label">Total avantages en nature</td>
        <td class="num">{_fmt(total_avantages)}</td>
        <td>إجمالي المزايا العينية</td>
      </tr>
      <tr>
        <td class="label">Total indemnités</td>
        <td class="num">{_fmt(total_indemnites)}</td>
        <td>إجمالي التعويضات</td>
      </tr>
      <tr>
        <td class="label">Total cotisations salariales</td>
        <td class="num">{_fmt(total_cotisations)}</td>
        <td>إجمالي الاشتراكات الجبائية</td>
      </tr>
      <tr>
        <td class="label">Total IRG retenu</td>
        <td class="num">{_fmt(total_irg)}</td>
        <td>إجمالي ضريبة الدخل المحتجزة</td>
      </tr>
      <tr class="total-row">
        <td class="label"><strong>Masse salariale nette versée</strong></td>
        <td class="num"><strong>{_fmt(masse_nette)}</strong></td>
        <td><strong>صافي الأجر المصروف</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


# ── G30 Annex: Detailed Employee Table ────────────────────────────────────────

def _g30_header_html(data: G29Data) -> str:
    """G30 annex header."""
    return f"""<div class="g30-header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h2>Série G N°30</h2>
  <div class="subtitle">IRG — TRAITEMENTS, SALAIRES, PENSIONS ET RENTES VIAGÈRES</div>
  <div class="subtitle">Annexé à la déclaration G N°29 — Année {data.annee_imposition}</div>
</div>"""


def _employee_detail_table_html(data: G29Data) -> str:
    """G30 detailed employee table — one row per employee."""
    if not data.salaries:
        return '<div class="section"><p style="text-align:center;font-style:italic;">Aucun salarié déclaré.</p></div>'

    rows = ""
    totals = {
        "salaire_brut_base": 0, "indemnites_logement": 0,
        "indemnites_transport": 0, "indemnites_representation": 0,
        "primes_gratifications": 0, "avantages_en_nature": 0,
        "indemnite_experience_pro": 0, "heures_supplementaires": 0,
        "autres_indemnites": 0, "total_brut_imposable": 0,
        "cotisations": 0, "revenu_net_imposable": 0,
        "irg_retenu": 0, "salaire_net_verse": 0,
    }

    for i, emp in enumerate(data.salaries, 1):
        irg = calculate_employee_irg(emp)
        net_verse = emp.revenu_net_imposable - irg

        # Accumulate totals
        totals["salaire_brut_base"] += emp.salaire_brut_base
        totals["indemnites_logement"] += emp.indemnites_logement
        totals["indemnites_transport"] += emp.indemnites_transport
        totals["indemnites_representation"] += emp.indemnites_representation
        totals["primes_gratifications"] += emp.primes_gratifications
        totals["avantages_en_nature"] += emp.avantages_en_nature
        totals["indemnite_experience_pro"] += emp.indemnite_experience_pro
        totals["heures_supplementaires"] += emp.heures_supplementaires
        totals["autres_indemnites"] += emp.autres_indemnites
        totals["total_brut_imposable"] += emp.total_brut_imposable
        totals["cotisations"] += emp.total_cotisations
        totals["revenu_net_imposable"] += emp.revenu_net_imposable
        totals["irg_retenu"] += irg
        totals["salaire_net_verse"] += net_verse

        rows += f"""      <tr>
        <td>{i}</td>
        <td class="text-left">{emp.nom_prenom}</td>
        <td>{emp.nif_salarie}</td>
        <td>{emp.date_naissance}</td>
        <td>{emp.sexe}</td>
        <td>{emp.situation_familiale}</td>
        <td>{emp.nombre_parts}</td>
        <td>{emp.categorie}</td>
        <td class="text-left">{emp.periode_emploi}</td>
        <td class="num">{_fmt_cell(emp.salaire_brut_base)}</td>
        <td class="num">{_fmt_cell(emp.indemnites_logement)}</td>
        <td class="num">{_fmt_cell(emp.indemnites_transport)}</td>
        <td class="num">{_fmt_cell(emp.indemnites_representation)}</td>
        <td class="num">{_fmt_cell(emp.primes_gratifications)}</td>
        <td class="num">{_fmt_cell(emp.avantages_en_nature)}</td>
        <td class="num">{_fmt_cell(emp.indemnite_experience_pro)}</td>
        <td class="num">{_fmt_cell(emp.heures_supplementaires)}</td>
        <td class="num">{_fmt_cell(emp.autres_indemnites)}</td>
        <td class="num"><strong>{_fmt(emp.total_brut_imposable)}</strong></td>
        <td class="num">{_fmt_cell(emp.total_cotisations)}</td>
        <td class="num"><strong>{_fmt(emp.revenu_net_imposable)}</strong></td>
        <td>{emp.nombre_parts}</td>
        <td class="num"><strong>{_fmt(irg)}</strong></td>
        <td class="num"><strong>{_fmt(net_verse)}</strong></td>
      </tr>
"""

    net_verse_total = totals["revenu_net_imposable"] - totals["irg_retenu"]

    total_row = f"""      <tr class="total-row">
        <td colspan="9"><strong>TOTAL ({len(data.salaries)} salariés)</strong></td>
        <td class="num"><strong>{_fmt(totals["salaire_brut_base"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["indemnites_logement"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["indemnites_transport"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["indemnites_representation"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["primes_gratifications"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["avantages_en_nature"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["indemnite_experience_pro"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["heures_supplementaires"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["autres_indemnites"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["total_brut_imposable"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["cotisations"])}</strong></td>
        <td class="num"><strong>{_fmt(totals["revenu_net_imposable"])}</strong></td>
        <td></td>
        <td class="num"><strong>{_fmt(totals["irg_retenu"])}</strong></td>
        <td class="num"><strong>{_fmt(net_verse_total)}</strong></td>
      </tr>"""

    return f"""<div class="section">
  <table class="employee-table">
    <thead>
      <tr>
        <th rowspan="2">N°</th>
        <th rowspan="2">Nom et Prénom</th>
        <th rowspan="2">NIF</th>
        <th rowspan="2">Date de<br>naissance</th>
        <th rowspan="2">Sexe</th>
        <th rowspan="2">Situation<br>familiale</th>
        <th rowspan="2">Nbre<br>parts</th>
        <th rowspan="2">Catégorie</th>
        <th rowspan="2">Période<br>d'emploi</th>
        <th rowspan="2">Salaire<br>brut de<br>base</th>
        <th rowspan="2">Indemn.<br>logement</th>
        <th rowspan="2">Indemn.<br>transport</th>
        <th rowspan="2">Indemn.<br>repré-</th>
        <th rowspan="2">Primes et<br>gratifi-</th>
        <th rowspan="2">Avantages<br>en nature</th>
        <th rowspan="2">IEP</th>
        <th rowspan="2">Heures<br>suppl.</th>
        <th rowspan="2">Autres<br>indemn.</th>
        <th rowspan="2">Total<br>brut<br>imposable</th>
        <th rowspan="2">Cotis.<br>salariales</th>
        <th rowspan="2">Revenu<br>net<br>imposable</th>
        <th rowspan="2">Nbre<br>parts</th>
        <th rowspan="2">IRG<br>retenu</th>
        <th rowspan="2">Salaire<br>net versé</th>
      </tr>
    </thead>
    <tbody>
{rows}{total_row}
    </tbody>
  </table>
  <div class="note">
    IEP = Indemnité d'Expérience Professionnelle (80% exonéré, plafonné à 50 000 DA/an)
    — Épargne salariale : 80% exonérée — Primes de rendement : plafond 2 mois de salaire
  </div>
</div>"""


# ── G30 Summary + Attestation ─────────────────────────────────────────────────

def _g30_summary_html(data: G29Data) -> str:
    """G30 summary section."""
    total_brut = sum(e.total_brut_imposable for e in data.salaries)
    total_revenu_net = sum(e.revenu_net_imposable for e in data.salaries)
    total_irg = sum(calculate_employee_irg(e) for e in data.salaries)
    n_salaries = len(data.salaries)

    return f"""<div class="section">
  <div class="section-title">RÉCAPITULATIF</div>
  <table class="summary-table">
    <thead>
      <tr>
        <th style="width:50%" class="label">Désignation</th>
        <th style="width:25%">Montant (DA)</th>
        <th style="width:25%">Arabe</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="label">Total masse salariale brute</td>
        <td class="num">{_fmt(total_brut)}</td>
        <td>إجمالي الأجر الخام</td>
      </tr>
      <tr>
        <td class="label">Total revenu net imposable</td>
        <td class="num">{_fmt(total_revenu_net)}</td>
        <td>إجمالي الدخل الصافي الخاضع للضريبة</td>
      </tr>
      <tr>
        <td class="label">Total IRG retenu</td>
        <td class="num">{_fmt(total_irg)}</td>
        <td>إجمالي ضريبة الدخل المحتجزة</td>
      </tr>
      <tr class="total-row">
        <td class="label"><strong>Nombre de salariés déclarés</strong></td>
        <td class="num"><strong>{n_salaries}</strong></td>
        <td><strong>عدد الموظفين المصرح بهم</strong></td>
      </tr>
    </tbody>
  </table>

  <div class="attestation">
    J'atteste de l'exactitude des renseignements portés sur la présente déclaration.
  </div>

  <div class="signature-block">
    <div class="sig-box">L'employeur<br><br><br>Cachet et signature</div>
    <div class="sig-box">L'Inspecteur des Impôts<br><br><br>Cachet et signature</div>
  </div>
</div>"""


# ── IRG Barème Reference ─────────────────────────────────────────────────────

def _bareme_reference_html() -> str:
    """IRG barème reference table (informational)."""
    return f"""<div class="section">
  <div class="section-title">BARÈME IRG PROGRESSIF (Année {datetime.now().year})</div>
  <table class="summary-table">
    <thead>
      <tr>
        <th>Tranche mensuelle (DA)</th>
        <th>Taux</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>≤ 15 000</td><td>0%</td></tr>
      <tr><td>15 001 — 30 000</td><td>10%</td></tr>
      <tr><td>30 001 — 60 000</td><td>20%</td></tr>
      <tr><td>60 001 — 120 000</td><td>30%</td></tr>
      <tr><td>> 120 000</td><td>40%</td></tr>
    </tbody>
  </table>
  <div class="note">
    Le calcul est effectué mensuellement puis multiplié par 12. Le quotient familial (nombre de parts)
    est appliqué avant le barème progressif. — Référence légale : Article 132 du CIDTA.
  </div>
</div>"""


# ── Main Generators ───────────────────────────────────────────────────────────

def generate_g29(data: G29Data) -> str:
    """Generate complete G29 + G30 forms as HTML.

    Args:
        data: G29Data with employer info and list of EmployeeData

    Returns:
        Complete HTML string ready to save or render
    """
    return f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G29 — IRG Salaires {data.annee_imposition} — {data.raison_sociale or 'Employeur'}</title>
{_css()}
</head>
<body>

<!-- ═══════════════════════ PAGE 1: G29 ═══════════════════════ -->
{_g29_header_html(data)}
{_dgi_hierarchy_html(data)}
{_identification_employeur_html(data)}
{_resume_masse_salariale_html(data)}

<!-- ═══════════════════════ PAGE 2+: G30 ═══════════════════════ -->
<div class="page-break"></div>

{_g30_header_html(data)}
{_dgi_hierarchy_html(data)}
{_employee_detail_table_html(data)}

<div class="page-break"></div>

{_g30_summary_html(data)}
{_bareme_reference_html()}

</body>
</html>"""


# Alias for consistency with g12_official.py
generate_g29_html = generate_g29


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys

    # ── Sample data ──
    sample = G29Data(
        wilaya="32 - El Bayadh",
        diw="DIW D'EL BAYADH",
        structure="Direction des Finances",
        inspection="Inspection des Impôts d'El Bayadh",
        recette="Recette des Impôts d'El Bayadh Centre",
        annee_imposition=2026,
        nif="1234567890A",
        raison_sociale="SARL TECH SOLUTIONS",
        adresse="123 Rue Didouche Mourad, El Bayadh",
        activite="Prestation de services informatiques",
        code_activite="6201",
        beneficiaire="Ahmed Benali",
        salaries=[
            EmployeeData(
                nom_prenom="Benali Ahmed",
                nif_salarie="19603061234567",
                date_naissance="06/03/1996",
                sexe="M",
                situation_familiale="Marié(e)",
                nombre_parts=3,
                categorie="Cadre",
                date_debut="01/01/2026",
                date_fin="31/12/2026",
                salaire_brut_base=360_000,
                indemnites_logement=60_000,
                indemnites_transport=36_000,
                indemnites_representation=24_000,
                primes_gratifications=72_000,
                avantages_en_nature=12_000,
                indemnite_experience_pro=40_000,
                heures_supplementaires=18_000,
                autres_indemnites=6_000,
                cotisations_cnas=108_000,
                cotisations_casnos=14_400,
                cotisations_ramed=3_600,
                autres_cotisations=0,
            ),
            EmployeeData(
                nom_prenom="Mebarki Fatima",
                nif_salarie="19850721234567",
                date_naissance="21/07/1985",
                sexe="F",
                situation_familiale="Célibataire",
                nombre_parts=1,
                categorie="Non-cadre",
                date_debut="01/01/2026",
                date_fin="31/12/2026",
                salaire_brut_base=180_000,
                indemnites_logement=24_000,
                indemnites_transport=18_000,
                primes_gratifications=36_000,
                cotisations_cnas=54_000,
                cotisations_casnos=7_200,
                cotisations_ramed=1_800,
            ),
            EmployeeData(
                nom_prenom="Khelifi Youcef",
                nif_salarie="19920515123456",
                date_naissance="15/05/1992",
                sexe="M",
                situation_familiale="Marié(e)",
                nombre_parts=2,
                categorie="Non-cadre",
                date_debut="01/06/2026",
                date_fin="31/12/2026",
                salaire_brut_base=126_000,
                indemnites_logement=16_800,
                indemnites_transport=12_600,
                primes_gratifications=25_200,
                cotisations_cnas=37_800,
                cotisations_casnos=5_040,
                cotisations_ramed=1_260,
            ),
        ],
    )

    # ── Print summary ──
    import sys as _sys
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(f"=== G29 + G30 -- IRG Salaires {sample.annee_imposition} ===")
    print(f"Employeur: {sample.raison_sociale}")
    print(f"NIF: {sample.nif}")
    print(f"Salaries: {len(sample.salaries)}")
    print()

    total_brut = 0
    total_irg = 0
    total_net = 0
    for emp in sample.salaries:
        irg = calculate_employee_irg(emp)
        net = emp.revenu_net_imposable - irg
        print(f"  {emp.nom_prenom}")
        print(f"    Brut imposable: {_fmt(emp.total_brut_imposable)} DA")
        print(f"    Cotisations:    {_fmt(emp.total_cotisations)} DA")
        print(f"    Net imposable:  {_fmt(emp.revenu_net_imposable)} DA")
        print(f"    IRG retenu:     {_fmt(irg)} DA")
        print(f"    Net verse:      {_fmt(net)} DA")
        print()
        total_brut += emp.total_brut_imposable
        total_irg += irg
        total_net += net

    print(f"  TOTAUX:")
    print(f"    Masse brute:   {_fmt(total_brut)} DA")
    print(f"    Total IRG:     {_fmt(total_irg)} DA")
    print(f"    Net verse:     {_fmt(total_net)} DA")

    # ── Generate HTML ──
    if "--html" in sys.argv:
        html = generate_g29(sample)
        out = f"g29_irg_salaires_{sample.annee_imposition}.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out}")

    # ── Export JSON ──
    if "--json" in sys.argv:
        out_json = f"g29_data_{sample.annee_imposition}.json"

        def _emp_to_dict(e: EmployeeData) -> dict:
            return {
                "nom_prenom": e.nom_prenom,
                "nif_salarie": e.nif_salarie,
                "date_naissance": e.date_naissance,
                "sexe": e.sexe,
                "situation_familiale": e.situation_familiale,
                "nombre_parts": e.nombre_parts,
                "categorie": e.categorie,
                "date_debut": e.date_debut,
                "date_fin": e.date_fin,
                "salaire_brut_base": e.salaire_brut_base,
                "indemnites_logement": e.indemnites_logement,
                "indemnites_transport": e.indemnites_transport,
                "indemnites_representation": e.indemnites_representation,
                "primes_gratifications": e.primes_gratifications,
                "avantages_en_nature": e.avantages_en_nature,
                "indemnite_experience_pro": e.indemnite_experience_pro,
                "heures_supplementaires": e.heures_supplementaires,
                "autres_indemnites": e.autres_indemnites,
                "epargne_salariale": e.epargne_salariale,
                "cotisations_cnas": e.cotisations_cnas,
                "cotisations_casnos": e.cotisations_casnos,
                "cotisations_ramed": e.cotisations_ramed,
                "autres_cotisations": e.autres_cotisations,
                "total_brut_imposable": e.total_brut_imposable,
                "total_cotisations": e.total_cotisations,
                "revenu_net_imposable": e.revenu_net_imposable,
                "irg_retenu": calculate_employee_irg(e),
                "salaire_net_verse": e.revenu_net_imposable - calculate_employee_irg(e),
            }

        export = {
            "g29": {
                "wilaya": sample.wilaya,
                "diw": sample.diw,
                "structure": sample.structure,
                "inspection": sample.inspection,
                "recette": sample.recette,
                "annee_imposition": sample.annee_imposition,
                "nif": sample.nif,
                "raison_sociale": sample.raison_sociale,
                "adresse": sample.adresse,
                "activite": sample.activite,
                "code_activite": sample.code_activite,
                "nombre_salaries": len(sample.salaries),
            },
            "salaries": [_emp_to_dict(e) for e in sample.salaries],
            "totaux": {
                "masse_salariale_brute": total_brut,
                "total_irg": total_irg,
                "masse_salariale_nette": total_net,
            },
        }
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(export, f, indent=2, ensure_ascii=False)
        print(f"JSON written to {out_json}")
