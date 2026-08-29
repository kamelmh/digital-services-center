"""G1 GGR Official Form Generator — Déclaration Générale des Revenus.

Generates the official G N°1 (GGR) annual income declaration form as HTML,
matching the DGI printable form for individual taxpayers.

Who must file:
- All individuals with taxable income (IRG)
- Persons with no taxable income (negative declaration)

Deadline: Before April 30 each year.
Legal references: Articles 18, 20, 22, 24, 33, 34, 36, 37, 38, 39, 40, 42,
44, 47, 48, 50, 51, 52, 53, 55, 57, 66, 68, 80 of the CIDTA.

Usage:
    from g1_ggr_generator import G1Data, calculate_g1, generate_g1
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from policy_constants import IRG_ANNUAL_BRACKETS, WILAYAS


def _esc(value: object, default: str = "") -> str:
    """HTML-escape a value for safe rendering."""
    if value is None:
        return default
    return _html_mod.escape(str(value))


# ── Constants ─────────────────────────────────────────────────────────────────

IRG_BAREME = list(IRG_ANNUAL_BRACKETS)  # Canonical: policy_constants.IRG_ANNUAL_BRACKETS — Art. 104 CIDTA unified 6-tranche

SITUATION_FAMILIALE = {
    "celibataire": "Célibataire",
    "marie": "Marié(e)",
    "divorce": "Divorcé(e)",
    "veuf": "Veuf(ve)",
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class SalaireData:
    """Employer income line (Section 1 — Revenus salariaux, Art. 18)."""
    nif_employeur: str = ""
    nom_employeur: str = ""
    salaire_brut: float = 0.0
    cotisations_salarié: float = 0.0
    cotisations_employeur: float = 0.0
    abattement_10: float = 0.0
    net_imposable: float = 0.0
    irg_retenu: float = 0.0

    def compute(self) -> None:
        """Auto-compute derived fields."""
        self.abattement_10 = self.salaire_brut * 0.10
        self.net_imposable = max(0, self.salaire_brut - self.cotisations_salarié - self.abattement_10)


@dataclass
class FoncierData:
    """Property income line (Section 2 — Revenus fonciers, Art. 33-34)."""
    adresse: str = ""
    loyer_annuel: float = 0.0
    charges_deductibles: float = 0.0
    revenu_net: float = 0.0

    def compute(self) -> None:
        self.revenu_net = self.loyer_annuel - self.charges_deductibles


@dataclass
class BICData:
    """Industrial/commercial profits line (Section 3 — BIC, Art. 36)."""
    activite: str = ""
    regime: str = "réel"  # "forfait" or "réel"
    chiffre_affaires: float = 0.0
    charges: float = 0.0
    resultat_fiscal: float = 0.0

    def compute(self) -> None:
        self.resultat_fiscal = self.chiffre_affaires - self.charges


@dataclass
class BNCData:
    """Non-commercial profits line (Section 4 — BNC, Art. 37)."""
    nature: str = ""
    recettes: float = 0.0
    charges: float = 0.0
    resultat_fiscal: float = 0.0

    def compute(self) -> None:
        self.resultat_fiscal = self.recettes - self.charges


@dataclass
class CapitauxData:
    """Movable capital income line (Section 5, Art. 40-42)."""
    nature: str = ""  # dividendes, intérêts, droits d'auteur, etc.
    montant: float = 0.0
    irg_retenu: float = 0.0


@dataclass
class PlusValueData:
    """Capital gains line (Section 6, Art. 44)."""
    nature: str = ""  # immobilière, cession de parts, etc.
    montant: float = 0.0


@dataclass
class AgricoleData:
    """Agricultural income line (Section 7, Art. 47-48)."""
    superficie: float = 0.0  # hectares
    culture: str = ""
    production: str = ""
    recettes: float = 0.0
    charges: float = 0.0
    resultat: float = 0.0

    def compute(self) -> None:
        self.resultat = self.recettes - self.charges


@dataclass
class G1Data:
    """Complete data for G1 GGR form generation."""
    # DGI hierarchy
    wilaya: str = ""
    diw: str = ""
    structure: str = ""
    inspection: str = ""
    recette: str = ""
    annee_imposition: int = datetime.now().year

    # Identification
    nif: str = ""
    nin: str = ""
    nom_prenoms: str = ""
    date_naissance: str = ""
    situation_familiale: str = "celibataire"  # celibataire, marie, divorce, veuf
    nombre_parts: float = 1.0
    activite_principale: str = ""
    adresse_domicile: str = ""
    code_commune: str = ""
    telephone: str = ""
    email: str = ""

    # État civil (marié)
    date_mariage: str = ""
    nom_conjoint: str = ""
    nif_conjoint: str = ""

    # Sections revenus
    salaires: List[SalaireData] = field(default_factory=list)
    fonciers: List[FoncierData] = field(default_factory=list)
    bics: List[BICData] = field(default_factory=list)
    bncs: List[BNCData] = field(default_factory=list)
    capitaux: List[CapitauxData] = field(default_factory=list)
    plus_values: List[PlusValueData] = field(default_factory=list)
    agricoles: List[AgricoleData] = field(default_factory=list)

    # Section 8 — Revenus non commerciaux (Art. 50-51)
    revenus_non_commerciaux: float = 0.0

    # Charges déductibles
    pension_alimentaire: float = 0.0
    cotisations_sociales: float = 0.0
    dons: float = 0.0
    autres_charges: float = 0.0

    # Acomptes versés / retenues à la source
    acomptes_verses: float = 0.0
    retenues_source: float = 0.0

    # Metadata
    fait_a: str = ""
    date_declaration: str = ""
    beneficiaire: str = ""


@dataclass
class G1Calculations:
    """Calculated amounts for the G1 form."""
    # Totals by section
    total_salaires: float = 0.0
    total_fonciers: float = 0.0
    total_bic: float = 0.0
    total_bnc: float = 0.0
    total_capitaux: float = 0.0
    total_plus_values: float = 0.0
    total_agricoles: float = 0.0
    total_non_commerciaux: float = 0.0

    # Revenu global
    revenu_global: float = 0.0
    total_charges_deductibles: float = 0.0
    revenu_net_imposable: float = 0.0

    # Liquidation impôt
    nombre_parts: float = 1.0
    revenu_par_part: float = 0.0
    impot_brut: float = 0.0
    reductions_abattements: float = 0.0
    credits_impot: float = 0.0
    impot_net: float = 0.0
    solde_payer: float = 0.0
    solde_remboursement: float = 0.0


# ── Calculations ──────────────────────────────────────────────────────────────

def calculate_g1(data: G1Data) -> G1Calculations:
    """Calculate all amounts for the G1 GGR form."""
    calc = G1Calculations()

    # Compute individual line items
    for s in data.salaires:
        s.compute()
    for f in data.fonciers:
        f.compute()
    for b in data.bics:
        b.compute()
    for b in data.bncs:
        b.compute()
    for a in data.agricoles:
        a.compute()

    # Section totals
    calc.total_salaires = sum(s.net_imposable for s in data.salaires)
    calc.total_fonciers = sum(f.revenu_net for f in data.fonciers)
    calc.total_bic = sum(b.resultat_fiscal for b in data.bics)
    calc.total_bnc = sum(b.resultat_fiscal for b in data.bncs)
    calc.total_capitaux = sum(c.montant for c in data.capitaux)
    calc.total_plus_values = sum(p.montant for p in data.plus_values)
    calc.total_agricoles = sum(a.resultat for a in data.agricoles)
    calc.total_non_commerciaux = data.revenus_non_commerciaux

    # Revenu global (1)
    calc.revenu_global = (
        calc.total_salaires + calc.total_fonciers + calc.total_bic +
        calc.total_bnc + calc.total_capitaux + calc.total_plus_values +
        calc.total_agricoles + calc.total_non_commerciaux
    )

    # Charges déductibles
    calc.total_charges_deductibles = (
        data.pension_alimentaire + data.cotisations_sociales +
        data.dons + data.autres_charges
    )

    # Revenu net imposable (2)
    calc.revenu_net_imposable = max(0, calc.revenu_global - calc.total_charges_deductibles)

    # Liquidation de l'impôt
    calc.nombre_parts = data.nombre_parts
    calc.revenu_par_part = calc.revenu_net_imposable / calc.nombre_parts if calc.nombre_parts > 0 else 0

    # Impôt brut by tranche
    calc.impot_brut = _calculate_irg(calc.revenu_par_part) * calc.nombre_parts

    # Impôt net
    calc.impot_net = max(0, calc.impot_brut - calc.reductions_abattements - calc.credits_impot)

    # Solde
    total_deja_paye = data.acomptes_verses + data.retenues_source
    if calc.impot_net > total_deja_paye:
        calc.solde_payer = calc.impot_net - total_deja_paye
    else:
        calc.solde_remboursement = total_deja_paye - calc.impot_net

    return calc


def _calculate_irg(revenu_par_part: float) -> float:
    """Apply IRG progressive tax scale to revenue per share."""
    tax = 0.0
    prev_limit = 0
    for limit, rate in IRG_BAREME:
        if revenu_par_part <= prev_limit:
            break
        taxable = min(revenu_par_part, limit) - prev_limit
        if taxable > 0:
            tax += taxable * rate
        prev_limit = limit
    return tax


# ── Formatting ────────────────────────────────────────────────────────────────

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
    """Return checked/unchecked checkbox character."""
    return "☑" if selected == value else "☐"


# ── HTML Generators ───────────────────────────────────────────────────────────

def _css() -> str:
    """Complete CSS matching g12_official.py style."""
    return """<style>
  @page { size: A4; margin: 12mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 10pt; color: #1a1a1a; margin: 0; padding: 15px;
    line-height: 1.4;
  }

  /* Header */
  .header { text-align: center; border: 2px solid #000; padding: 8px; margin-bottom: 10px; }
  .republique { font-size: 9pt; letter-spacing: 1px; }
  .dgi { font-size: 10pt; font-weight: bold; margin: 3px 0; }
  .header h1 { font-size: 14pt; margin: 5px 0; }
  .subtitle { font-size: 9pt; }
  .deadline { font-size: 9pt; font-weight: bold; margin-top: 5px; padding: 4px; border: 1px solid #000; background: #f8f8f8; }

  /* DGI Hierarchy */
  .dgi-table { width: 100%; border: none; }
  .dgi-table td { border: none; padding: 2px 5px; font-size: 9pt; }
  .dgi-label { font-weight: bold; width: 30%; }
  .dgi-value { border-bottom: 1px dotted #999; }

  /* Sections */
  .section { margin: 10px 0; page-break-inside: avoid; }
  .section-title { font-size: 10pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 3px; margin-bottom: 5px; }
  .section-title-ar { font-size: 9pt; color: #666; margin-bottom: 5px; text-align: right; direction: rtl; }

  /* Fields table */
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 3px 5px; font-size: 9pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 35%; }
  .field-value { border-bottom: 1px dotted #999; width: 40%; }
  .checkbox-table { border: none; }
  .checkbox-table td { border: none; padding: 2px 8px; font-size: 9pt; }
  .checkbox-cell { white-space: nowrap; }

  /* Revenue tables */
  .rev-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .rev-table th, .rev-table td { border: 1px solid #000; padding: 4px 6px; font-size: 8.5pt; text-align: center; }
  .rev-table th { background: #f0f0f0; font-weight: bold; }
  .rev-table .num { font-family: 'Courier New', monospace; font-size: 9pt; }
  .rev-table .activity { text-align: left; }
  .rev-table .total-row { background: #f8f8f8; font-weight: bold; }

  /* Summary table */
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 55%; }
  .summary-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .summary-table .highlight { background: #f0f0f0; font-weight: bold; font-size: 10pt; }
  .summary-table .result { background: #e8e8e8; font-weight: bold; font-size: 11pt; }

  /* Impôt calculation */
  .impot-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .impot-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .impot-table .label { font-weight: bold; width: 55%; }
  .impot-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .impot-table .highlight { background: #f0f0f0; font-weight: bold; }
  .impot-table .result { background: #e8e8e8; font-weight: bold; font-size: 10pt; }

  /* Notes */
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }

  /* Signature */
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }

  /* Legal page */
  .page { page-break-before: always; }
  .page-header { font-size: 10pt; font-weight: bold; text-align: center; margin-bottom: 10px; }
  .legal-page h3 { font-size: 10pt; margin: 10px 0 5px; }
  .legal-page p { font-size: 8.5pt; text-align: justify; margin: 5px 0; line-height: 1.5; }

  /* Print */
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


def _header_html(year: int) -> str:
    """Official DGI header for G1."""
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h1>Série G N°1</h1>
  <div class="subtitle">DÉCLARATION GÉNÉRALE DES REVENUS</div>
  <div class="subtitle">(GGR)</div>
  <div class="deadline">Déclaration à souscrire, au plus tard le 30 Avril de chaque année</div>
</div>"""


def _dgi_hierarchy_html(data: G1Data) -> str:
    """DGI institutional hierarchy fields."""
    return f"""<div class="section">
  <table class="dgi-table">
    <tr>
      <td class="dgi-label">Wilaya :</td>
      <td class="dgi-value">{_esc(data.wilaya) or '...................................................'}</td>
    </tr>
    <tr>
      <td class="dgi-label">DIW :</td>
      <td class="dgi-value">{_esc(data.diw) or '...................................................'}</td>
    </tr>
    <tr>
      <td class="dgi-label">Structure :</td>
      <td class="dgi-value">{_esc(data.structure) or '...................................................'}</td>
    </tr>
    <tr>
      <td class="dgi-label">Inspection :</td>
      <td class="dgi-value">{_esc(data.inspection) or '...................................................'}</td>
    </tr>
    <tr>
      <td class="dgi-label">Recette :</td>
      <td class="dgi-value">{_esc(data.recette) or '...................................................'}</td>
    </tr>
    <tr>
      <td class="dgi-label">Année d'imposition :</td>
      <td class="dgi-value">{data.annee_imposition}</td>
    </tr>
  </table>
</div>"""


def _identification_html(data: G1Data) -> str:
    """Section — Identification du contribuable."""
    sf = data.situation_familiale

    return f"""<div class="section">
  <div class="section-title">IDENTIFICATION DU CONTRIBUABLE</div>
  <table class="fields-table">
    <tr>
      <td class="field-label">NIF :</td>
      <td class="field-value">{_esc(data.nif) or '................................'}</td>
    </tr>
    <tr>
      <td class="field-label">NIN (Numéro Identification Nationale) :</td>
      <td class="field-value">{_esc(data.nin) or '................................'}</td>
    </tr>
    <tr>
      <td class="field-label">Nom et Prénom :</td>
      <td class="field-value">{_esc(data.nom_prenoms) or '................................'}</td>
    </tr>
    <tr>
      <td class="field-label">Date de naissance :</td>
      <td class="field-value">{_esc(data.date_naissance) or '....../....../......'}</td>
    </tr>
    <tr>
      <td class="field-label">Situation familiale :</td>
      <td class="field-value">
        <table class="checkbox-table"><tr>
          <td class="checkbox-cell">{_checkbox(sf, 'celibataire')} Célibataire</td>
          <td class="checkbox-cell">{_checkbox(sf, 'marie')} Marié(e)</td>
          <td class="checkbox-cell">{_checkbox(sf, 'divorce')} Divorcé(e)</td>
          <td class="checkbox-cell">{_checkbox(sf, 'veuf')} Veuf(ve)</td>
        </tr></table>
      </td>
    </tr>
    <tr>
      <td class="field-label">Nombre de parts :</td>
      <td class="field-value">{data.nombre_parts if data.nombre_parts != 1.0 else '......'}</td>
    </tr>
    <tr>
      <td class="field-label">Activité principale :</td>
      <td class="field-value">{_esc(data.activite_principale) or '................................'}</td>
    </tr>
    <tr>
      <td class="field-label">Adresse du domicile fiscal :</td>
      <td class="field-value">{_esc(data.adresse_domicile) or '................................'}</td>
    </tr>
    <tr>
      <td class="field-label">Code Commune :</td>
      <td class="field-value">{_esc(data.code_commune) or '......'}</td>
    </tr>
    <tr>
      <td class="field-label">Téléphone / Email :</td>
      <td class="field-value">{_esc(data.telephone) or '................................'} {('/ ' + _esc(data.email)) if data.email else ''}</td>
    </tr>
  </table>
  <div class="section" style="margin-top: 5px; padding: 5px; border: 1px solid #ccc;">
    <div class="section-title" style="font-size: 9pt;">État civil (si marié(e))</div>
    <table class="fields-table">
      <tr>
        <td class="field-label">Date de mariage :</td>
        <td class="field-value">{_esc(data.date_mariage) or '....../....../......'}</td>
      </tr>
      <tr>
        <td class="field-label">Nom du conjoint :</td>
        <td class="field-value">{_esc(data.nom_conjoint) or '................................'}</td>
      </tr>
      <tr>
        <td class="field-label">NIF du conjoint :</td>
        <td class="field-value">{_esc(data.nif_conjoint) or '................................'}</td>
      </tr>
    </table>
  </div>
</div>"""


def _section1_salaires_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 1 — Revenus salariaux (Art. 18 CIDTA)."""
    rows = ""
    for i, s in enumerate(data.salaires, 1):
        rows += f"""<tr>
        <td class="num">{i}</td>
        <td class="num">{_esc(s.nif_employeur) or ''}</td>
        <td style="text-align:left">{_esc(s.nom_employeur) or ''}</td>
        <td class="num">{_fmt_cell(s.salaire_brut)}</td>
        <td class="num">{_fmt_cell(s.cotisations_salarié)}</td>
        <td class="num">{_fmt_cell(s.cotisations_employeur)}</td>
        <td class="num">{_fmt_cell(s.abattement_10)}</td>
        <td class="num">{_fmt_cell(s.net_imposable)}</td>
        <td class="num">{_fmt_cell(s.irg_retenu)}</td>
      </tr>"""
    if not data.salaires:
        rows = """<tr>
        <td>1</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
      </tr>
      <tr>
        <td>2</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">SECTION 1 — REVENUS SALARIAUX (Art. 18 CIDTA)</div>
  <table class="rev-table">
    <thead>
      <tr>
        <th>N°</th>
        <th>NIF Employeur</th>
        <th>Nom de l'employeur</th>
        <th>Salaire brut</th>
        <th>Cotisations salarié</th>
        <th>Cotisations employeur</th>
        <th>Abattement 10%</th>
        <th>Net imposable</th>
        <th>IRG retenu</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr class="total-row">
        <td colspan="3"><strong>Total revenus salariaux</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(s.salaire_brut for s in data.salaires))}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(s.cotisations_salarié for s in data.salaires))}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(s.cotisations_employeur for s in data.salaires))}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(s.abattement_10 for s in data.salaires))}</strong></td>
        <td class="num"><strong>{_fmt(calc.total_salaires)}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(s.irg_retenu for s in data.salaires))}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section2_fonciers_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 2 — Revenus fonciers (Art. 33-34 CIDTA)."""
    rows = ""
    for i, f in enumerate(data.fonciers, 1):
        rows += f"""<tr>
        <td class="num">{i}</td>
        <td style="text-align:left">{f.adresse or ''}</td>
        <td class="num">{_fmt_cell(f.loyer_annuel)}</td>
        <td class="num">{_fmt_cell(f.charges_deductibles)}</td>
        <td class="num">{_fmt_cell(f.revenu_net)}</td>
      </tr>"""
    if not data.fonciers:
        rows = """<tr>
        <td>1</td><td></td><td></td><td></td><td></td>
      </tr>
      <tr>
        <td>2</td><td></td><td></td><td></td><td></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">SECTION 2 — REVENUS FONCIERS (Art. 33-34 CIDTA)</div>
  <table class="rev-table">
    <thead>
      <tr>
        <th>N°</th>
        <th>Adresse de l'immeuble</th>
        <th>Loyer annuel</th>
        <th>Charges déductibles</th>
        <th>Revenu net</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr class="total-row">
        <td colspan="2"><strong>Total revenus fonciers</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(f.loyer_annuel for f in data.fonciers))}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(f.charges_deductibles for f in data.fonciers))}</strong></td>
        <td class="num"><strong>{_fmt(calc.total_fonciers)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section3_bic_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 3 — Bénéfices Industriels et Commerciaux (Art. 36 CIDTA)."""
    rows = ""
    for i, b in enumerate(data.bics, 1):
        regime_label = "Forfait" if b.regime == "forfait" else "Réel"
        rows += f"""<tr>
        <td class="num">{i}</td>
        <td style="text-align:left">{b.activite or ''}</td>
        <td>{regime_label}</td>
        <td class="num">{_fmt_cell(b.chiffre_affaires)}</td>
        <td class="num">{_fmt_cell(b.charges)}</td>
        <td class="num">{_fmt_cell(b.resultat_fiscal)}</td>
      </tr>"""
    if not data.bics:
        rows = """<tr>
        <td>1</td><td></td><td></td><td></td><td></td><td></td>
      </tr>
      <tr>
        <td>2</td><td></td><td></td><td></td><td></td><td></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">SECTION 3 — BÉNÉFICES INDUSTRIELS ET COMMERCIAUX (BIC) (Art. 36 CIDTA)</div>
  <table class="rev-table">
    <thead>
      <tr>
        <th>N°</th>
        <th>Activité</th>
        <th>Régime</th>
        <th>Chiffre d'affaires</th>
        <th>Charges</th>
        <th>Résultat fiscal</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr class="total-row">
        <td colspan="3"><strong>Total BIC</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(b.chiffre_affaires for b in data.bics))}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(b.charges for b in data.bics))}</strong></td>
        <td class="num"><strong>{_fmt(calc.total_bic)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section4_bnc_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 4 — Bénéfices Non Commerciaux (Art. 37 CIDTA)."""
    rows = ""
    for i, b in enumerate(data.bncs, 1):
        rows += f"""<tr>
        <td class="num">{i}</td>
        <td style="text-align:left">{b.nature or ''}</td>
        <td class="num">{_fmt_cell(b.recettes)}</td>
        <td class="num">{_fmt_cell(b.charges)}</td>
        <td class="num">{_fmt_cell(b.resultat_fiscal)}</td>
      </tr>"""
    if not data.bncs:
        rows = """<tr>
        <td>1</td><td></td><td></td><td></td><td></td>
      </tr>
      <tr>
        <td>2</td><td></td><td></td><td></td><td></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">SECTION 4 — BÉNÉFICES NON COMMERCIAUX (BNC) (Art. 37 CIDTA)</div>
  <table class="rev-table">
    <thead>
      <tr>
        <th>N°</th>
        <th>Nature de l'activité</th>
        <th>Recettes</th>
        <th>Charges</th>
        <th>Résultat fiscal</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr class="total-row">
        <td colspan="2"><strong>Total BNC</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(b.recettes for b in data.bncs))}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(b.charges for b in data.bncs))}</strong></td>
        <td class="num"><strong>{_fmt(calc.total_bnc)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section5_capitaux_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 5 — Revenus des capitaux mobiliers (Art. 40-42 CIDTA)."""
    rows = ""
    for i, c in enumerate(data.capitaux, 1):
        rows += f"""<tr>
        <td class="num">{i}</td>
        <td style="text-align:left">{c.nature or ''}</td>
        <td class="num">{_fmt_cell(c.montant)}</td>
        <td class="num">{_fmt_cell(c.irg_retenu)}</td>
      </tr>"""
    if not data.capitaux:
        rows = """<tr>
        <td>1</td><td></td><td></td><td></td>
      </tr>
      <tr>
        <td>2</td><td></td><td></td><td></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">SECTION 5 — REVENUS DES CAPITAUX MOBILIERS (Art. 40-42 CIDTA)</div>
  <table class="rev-table">
    <thead>
      <tr>
        <th>N°</th>
        <th>Nature (dividendes, intérêts, droits d'auteur, etc.)</th>
        <th>Montant</th>
        <th>IRG retenu</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr class="total-row">
        <td colspan="2"><strong>Total revenus capitaux mobiliers</strong></td>
        <td class="num"><strong>{_fmt(calc.total_capitaux)}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(c.irg_retenu for c in data.capitaux))}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section6_plus_values_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 6 — Plus-values (Art. 44 CIDTA)."""
    rows = ""
    for i, p in enumerate(data.plus_values, 1):
        rows += f"""<tr>
        <td class="num">{i}</td>
        <td style="text-align:left">{p.nature or ''}</td>
        <td class="num">{_fmt_cell(p.montant)}</td>
      </tr>"""
    if not data.plus_values:
        rows = """<tr>
        <td>1</td><td></td><td></td>
      </tr>
      <tr>
        <td>2</td><td></td><td></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">SECTION 6 — PLUS-VALUES (Art. 44 CIDTA)</div>
  <table class="rev-table">
    <thead>
      <tr>
        <th>N°</th>
        <th>Nature (immobilière, cession de parts, etc.)</th>
        <th>Montant</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr class="total-row">
        <td colspan="2"><strong>Total plus-values</strong></td>
        <td class="num"><strong>{_fmt(calc.total_plus_values)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section7_agricoles_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 7 — Revenus agricoles (Art. 47-48 CIDTA)."""
    rows = ""
    for i, a in enumerate(data.agricoles, 1):
        rows += f"""<tr>
        <td class="num">{i}</td>
        <td class="num">{a.superficie if a.superficie else ''}</td>
        <td style="text-align:left">{_esc(a.culture) or ''}</td>
        <td style="text-align:left">{_esc(a.production) or ''}</td>
        <td class="num">{_fmt_cell(a.recettes)}</td>
        <td class="num">{_fmt_cell(a.charges)}</td>
        <td class="num">{_fmt_cell(a.resultat)}</td>
      </tr>"""
    if not data.agricoles:
        rows = """<tr>
        <td>1</td><td></td><td></td><td></td><td></td><td></td><td></td>
      </tr>
      <tr>
        <td>2</td><td></td><td></td><td></td><td></td><td></td><td></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">SECTION 7 — REVENUS AGRICOLES (Art. 47-48 CIDTA)</div>
  <table class="rev-table">
    <thead>
      <tr>
        <th>N°</th>
        <th>Superficie (ha)</th>
        <th>Culture</th>
        <th>Production</th>
        <th>Recettes</th>
        <th>Charges</th>
        <th>Résultat</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr class="total-row">
        <td colspan="4"><strong>Total revenus agricoles</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(a.recettes for a in data.agricoles))}</strong></td>
        <td class="num"><strong>{_fmt_cell(sum(a.charges for a in data.agricoles))}</strong></td>
        <td class="num"><strong>{_fmt(calc.total_agricoles)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section8_non_commerciaux_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 8 — Revenus non commerciaux (Art. 50-51 CIDTA)."""
    return f"""<div class="section">
  <div class="section-title">SECTION 8 — REVENUS NON COMMERCIAUX (Art. 50-51 CIDTA)</div>
  <table class="fields-table">
    <tr>
      <td class="field-label">Montant :</td>
      <td class="field-value">{_fmt_cell(data.revenus_non_commerciaux)}</td>
    </tr>
  </table>
  <div class="note">Total revenus non commerciaux : {_fmt(calc.total_non_commerciaux)} DA</div>
</div>"""


def _section9_revenu_global_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 9 — Revenu global imposable."""
    return f"""<div class="section">
  <div class="section-title">SECTION 9 — REVENU GLOBAL IMPOSABLE</div>
  <table class="summary-table">
    <tr>
      <td class="label">Total revenus salariaux :</td>
      <td class="amount">{_fmt_cell(calc.total_salaires)} DA</td>
    </tr>
    <tr>
      <td class="label">Total revenus fonciers :</td>
      <td class="amount">{_fmt_cell(calc.total_fonciers)} DA</td>
    </tr>
    <tr>
      <td class="label">Total BIC :</td>
      <td class="amount">{_fmt_cell(calc.total_bic)} DA</td>
    </tr>
    <tr>
      <td class="label">Total BNC :</td>
      <td class="amount">{_fmt_cell(calc.total_bnc)} DA</td>
    </tr>
    <tr>
      <td class="label">Total revenus capitaux mobiliers :</td>
      <td class="amount">{_fmt_cell(calc.total_capitaux)} DA</td>
    </tr>
    <tr>
      <td class="label">Total plus-values :</td>
      <td class="amount">{_fmt_cell(calc.total_plus_values)} DA</td>
    </tr>
    <tr>
      <td class="label">Total revenus agricoles :</td>
      <td class="amount">{_fmt_cell(calc.total_agricoles)} DA</td>
    </tr>
    <tr>
      <td class="label">Total revenus non commerciaux :</td>
      <td class="amount">{_fmt_cell(calc.total_non_commerciaux)} DA</td>
    </tr>
    <tr class="highlight">
      <td class="label">REVENU GLOBAL (1) :</td>
      <td class="amount">{_fmt(calc.revenu_global)} DA</td>
    </tr>
    <tr>
      <td class="label">Charges déductibles (pension alimentaire, cotisations, etc.) :</td>
      <td class="amount">{_fmt_cell(calc.total_charges_deductibles)} DA</td>
    </tr>
    <tr class="result">
      <td class="label">REVENU NET IMPOSABLE (2) :</td>
      <td class="amount">{_fmt(calc.revenu_net_imposable)} DA</td>
    </tr>
  </table>
  <div class="note">Détail charges déductibles : Pension alimentaire {_fmt_cell(data.pension_alimentaire)} +
  Cotisations {_fmt_cell(data.cotisations_sociales)} + Dons {_fmt_cell(data.dons)} +
  Autres {_fmt_cell(data.autres_charges)} = {_fmt(calc.total_charges_deductibles)} DA</div>
</div>"""


def _section10_liquidation_html(data: G1Data, calc: G1Calculations) -> str:
    """Section 10 — Liquidation de l'impôt."""
    total_deja_paye = data.acomptes_verses + data.retenues_source

    if calc.solde_payer > 0:
        solde_label = "SOLDE D'IMPÔT À PAYER"
        solde_value = _fmt(calc.solde_payer)
    elif calc.solde_remboursement > 0:
        solde_label = "SOLDE D'IMPÔT À REMBOURSEMENT"
        solde_value = _fmt(calc.solde_remboursement)
    else:
        solde_label = "IMPÔT TOTALEMENT ACQUITTÉ"
        solde_value = "0"

    return f"""<div class="section">
  <div class="section-title">SECTION 10 — LIQUIDATION DE L'IMPÔT</div>
  <table class="impot-table">
    <tr>
      <td class="label">Revenu net imposable :</td>
      <td class="amount">{_fmt(calc.revenu_net_imposable)} DA</td>
    </tr>
    <tr>
      <td class="label">Nombre de parts :</td>
      <td class="amount">{calc.nombre_parts}</td>
    </tr>
    <tr>
      <td class="label">Revenu imposable par part :</td>
      <td class="amount">{_fmt(calc.revenu_par_part)} DA</td>
    </tr>
    <tr>
      <td class="label">Impôt brut (barème progressif) :</td>
      <td class="amount">{_fmt(calc.impot_brut)} DA</td>
    </tr>
    <tr>
      <td class="label">Réductions / Abattements :</td>
      <td class="amount">{_fmt_cell(calc.reductions_abattements)} DA</td>
    </tr>
    <tr>
      <td class="label">Crédits d'impôt :</td>
      <td class="amount">{_fmt_cell(calc.credits_impot)} DA</td>
    </tr>
    <tr class="highlight">
      <td class="label">Impôt sur le revenu net (3) :</td>
      <td class="amount">{_fmt(calc.impot_net)} DA</td>
    </tr>
    <tr>
      <td class="label">Acomptes versés :</td>
      <td class="amount">{_fmt_cell(data.acomptes_verses)} DA</td>
    </tr>
    <tr>
      <td class="label">Retenues à la source :</td>
      <td class="amount">{_fmt_cell(data.retenues_source)} DA</td>
    </tr>
    <tr>
      <td class="label">Total déjà payé :</td>
      <td class="amount">{_fmt(total_deja_paye)} DA</td>
    </tr>
    <tr class="result">
      <td class="label">{solde_label} :</td>
      <td class="amount">{solde_value} DA</td>
    </tr>
  </table>
</div>"""


def _bareme_html() -> str:
    """IRG tax scale reference table."""
    return """<div class="section">
  <div class="section-title">BARÈME PROGRESSIF DE L'IMPÔT SUR LE REVENU (IRG) — ANNÉE 2026</div>
  <table class="rev-table">
    <thead>
      <tr>
        <th>Tranche annuelle (par part)</th>
        <th>Taux</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>≤ 120 000 DA</td><td>0%</td></tr>
      <tr><td>120 001 — 360 000 DA</td><td>20%</td></tr>
      <tr><td>360 001 — 1 440 000 DA</td><td>30%</td></tr>
      <tr><td>> 1 440 000 DA</td><td>35%</td></tr>
    </tbody>
  </table>
  <div class="note">Parts fiscales : Célibataire 1 part — Marié(e) 2 parts — +0,5 part/enfant (max 3) — +0,5 part/parent à charge (max 2)</div>
</div>"""


def _signature_html(data: G1Data) -> str:
    """Signature block at end of form."""
    fait_a = data.fait_a or "...................."
    date_decl = data.date_declaration or "....../....../......"

    return f"""<div class="section">
  <div class="attestation">
    J'atteste de l'exactitude des renseignements portés sur la présente déclaration.
    Je suis informé(e) que tout fait passible des sanctions prévues par les textes en vigueur
    pourra être relevé contre moi.
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {fait_a} <strong>le</strong> {date_decl}
  </div>
  <div class="signature-block">
    <div class="sig-box">Signature du déclarant<br><br><br>Cachet</div>
    <div class="sig-box">Cadre réservé à l'administration<br><br><br>Cachet et signature</div>
  </div>
</div>"""


def _legal_page_html() -> str:
    """Legal references page."""
    return """<div class="page legal-page">
  <div class="page-header">RÉFÉRENCES LÉGALES — DÉCLARATION GÉNÉRALE DES REVENUS (GGR)</div>

  <h3>Base légale</h3>
  <p>La présente déclaration est établie conformément aux dispositions du Code des Impôts
  Directs et Taxes Assimilées (CIDTA), notamment :</p>
  <p>• <strong>Art. 18</strong> — Revenus salariaux<br>
  • <strong>Art. 20</strong> — Revenus des agents de l'État<br>
  • <strong>Art. 22</strong> — Pension et retraite<br>
  • <strong>Art. 24</strong> — Revenus de source étrangère<br>
  • <strong>Art. 33-34</strong> — Revenus fonciers<br>
  • <strong>Art. 36</strong> — Bénéfices industriels et commerciaux (BIC)<br>
  • <strong>Art. 37</strong> — Bénéfices non commerciaux (BNC)<br>
  • <strong>Art. 38</strong> — Régime du bénéfice réel<br>
  • <strong>Art. 39</strong> — Régime forfaitaire<br>
  • <strong>Art. 40-42</strong> — Revenus des capitaux mobiliers<br>
  • <strong>Art. 44</strong> — Plus-values<br>
  • <strong>Art. 47-48</strong> — Revenus agricoles<br>
  • <strong>Art. 50-51</strong> — Revenus non commerciaux<br>
  • <strong>Art. 52-53</strong> — Revenus divers<br>
  • <strong>Art. 55</strong> — Charges déductibles<br>
  • <strong>Art. 57</strong> — Réductions d'impôt<br>
  • <strong>Art. 66</strong> — Liquidation de l'impôt<br>
  • <strong>Art. 68</strong> — Barème progressif<br>
  • <strong>Art. 80</strong> — Déclaration des revenus</p>

  <h3>Obligations du contribuable</h3>
  <p>Toute personne physique percevant des revenus imposables en Algérie est tenue de souscrire
  une déclaration générale des revenus (GGR) au plus tard le 30 avril de chaque année, auprès
  de la recette des impôts dont elle relève.</p>

  <p>Les personnes ne percevant aucun revenu imposable doivent également souscrire une
  <strong>déclaration négative</strong> (revenu net imposable = 0 DA).</p>

  <h3>Sanctions</h3>
  <p>Le défaut de déclaration ou la déclaration inexacte est passible de majorations et amendes
  conformément aux dispositions du Code des Procédures Fiscales (CPF) et du CIDTA.</p>
</div>"""


# ── Main Generator ────────────────────────────────────────────────────────────

def generate_g1(data: G1Data) -> str:
    """Generate complete G1 GGR form as HTML."""
    calc = calculate_g1(data)

    html = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G1 GGR — Déclaration Générale des Revenus {data.annee_imposition}</title>
{_css()}
</head>
<body>

{_header_html(data.annee_imposition)}
{_dgi_hierarchy_html(data)}
{_identification_html(data)}
{_bareme_html()}

{_section1_salaires_html(data, calc)}
{_section2_fonciers_html(data, calc)}
{_section3_bic_html(data, calc)}
{_section4_bnc_html(data, calc)}
{_section5_capitaux_html(data, calc)}
{_section6_plus_values_html(data, calc)}
{_section7_agricoles_html(data, calc)}
{_section8_non_commerciaux_html(data, calc)}

{_section9_revenu_global_html(data, calc)}
{_section10_liquidation_html(data, calc)}

{_signature_html(data)}
{_legal_page_html()}

</body>
</html>"""

    hook_generation("g1_ggr", {"annee_imposition": data.annee_imposition, "nif": data.nif}, html)
    return html


# Alias for backward compatibility
generate_g1_html = generate_g1


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = G1Data(
        wilaya="32 - El Bayadh",
        diw="DIW D'EL BAYADH",
        structure="Bureau des Impôts d'El Bayadh Centre",
        inspection="Inspection des Impôts d'El Bayadh",
        recette="Recette des Impôts d'El Bayadh Centre",
        annee_imposition=2026,
        nif="1234567890A",
        nin="199603061234567",
        nom_prenoms="KAMEL MAHI",
        date_naissance="06/03/1996",
        situation_familiale="marie",
        nombre_parts=2.5,
        activite_principale="Enseignant / Formateur",
        adresse_domicile="El Bayadh Centre, Wilaya d'El Bayadh",
        code_commune="3201",
        telephone="0555081718",
        email="kamelmahi71@gmail.com",
        date_mariage="15/06/2020",
        nom_conjoint="FATIMA ZOHRA",
        nif_conjoint="9876543210B",
        # Salaire
        salaires=[
            SalaireData(
                nif_employeur="19876543210",
                nom_employeur="Direction de l'Education d'El Bayadh",
                salaire_brut=600_000,
                cotisations_salarié=120_000,
                cotisations_employeur=180_000,
            ),
        ],
        # Foncier
        fonciers=[
            FoncierData(
                adresse="Rue Didouche Mourad, El Bayadh",
                loyer_annuel=120_000,
                charges_deductibles=24_000,
            ),
        ],
        # Charges
        pension_alimentaire=0,
        cotisations_sociales=120_000,
        dons=0,
        autres_charges=0,
        # Acomptes
        acomptes_verses=0,
        retenues_source=0,
        # Metadata
        fait_a="El Bayadh",
        date_declaration="30/04/2026",
        beneficiaire="KAMEL MAHI",
    )

    calc = calculate_g1(sample)
    print(f"=== G1 GGR — {sample.annee_imposition} ===")
    print(f"Revenu global: {_fmt(calc.revenu_global)} DA")
    print(f"Charges déductibles: {_fmt(calc.total_charges_deductibles)} DA")
    print(f"Revenu net imposable: {_fmt(calc.revenu_net_imposable)} DA")
    print(f"Nombre de parts: {calc.nombre_parts}")
    print(f"Revenu par part: {_fmt(calc.revenu_par_part)} DA")
    print(f"Impôt brut: {_fmt(calc.impot_brut)} DA")
    print(f"Impôt net: {_fmt(calc.impot_net)} DA")
    if calc.solde_payer > 0:
        print(f"Solde à payer: {_fmt(calc.solde_payer)} DA")
    elif calc.solde_remboursement > 0:
        print(f"Solde à rembourser: {_fmt(calc.solde_remboursement)} DA")
    else:
        print("Impôt totalement acquitté")

    if "--html" in sys.argv:
        html = generate_g1(sample)
        out = "g1_ggr_official.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out}")
