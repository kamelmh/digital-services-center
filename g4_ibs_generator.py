"""G4 Official Form Generator — Impôt sur les Bénéfices des Sociétés (IBS).

Annual tax declaration for companies subject to IBS (SARL, EURL, SPA, SNC, EPE, EPIC, cooperatives).
Matches the official DGI printable form (Série G N°4).

Legal references: Articles 18 and 224 of the CIDTA.

Usage:
    from g4_ibs_generator import G4Data, calculate_g4, generate_g4
    data = G4Data(nif="1234567890", raison_sociale="SARL Example", ...)
    html = generate_g4(data)
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def _esc(value: object, default: str = "") -> str:
    """HTML-escape a value for safe rendering."""
    if value is None:
        return default
    return _html_mod.escape(str(value))


# ── Constants ─────────────────────────────────────────────────────────────────

IBS_RATES = {
    "production": {
        "label_fr": "Production industrielle",
        "label_ar": "الإنتاج الصناعي",
        "rate": 0.19,
    },
    "btp_tourisme": {
        "label_fr": "BTP et Tourisme (sauf agences de voyage)",
        "label_ar": "الأشغال العمومية والسياحة (عدا وكالات الأسفار)",
        "rate": 0.23,
    },
    "commerce_services": {
        "label_fr": "Commerce, Services et autres activités",
        "label_ar": "التجارة والخدمات والأنشطة الأخرى",
        "rate": 0.26,
    },
}

FORMES_JURIDIQUES = [
    "SARL", "EURL", "SPA", "SNC", "SA", "SAS", "SCS",
    "Société civile", "Coopérative", "EPE", "EPIC", "Autre",
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
class G4Data:
    """Complete data for G4 IBS form generation."""
    # DGI hierarchy
    wilaya: str = ""
    diw: str = ""
    structure: str = ""
    inspection: str = ""
    recette: str = ""
    annee_imposition: int = datetime.now().year
    periode_debut: str = ""
    periode_fin: str = ""

    # Section A — Identification
    nif: str = ""
    raison_sociale: str = ""
    forme_juridique: str = ""
    activites: str = ""
    activite_principale: str = ""
    code_activite: str = ""
    numero_rc: str = ""
    comptes_bancaires: str = ""
    adresse_siege_janvier: str = ""
    adresse_siege_fin_annee: str = ""
    telephone: str = ""
    fax: str = ""
    email: str = ""
    adresse_etablissements_secondaires: str = ""
    representant_legal: str = ""
    adresse_representant: str = ""

    # Section B — Détermination du résultat fiscal (Tableau 9)
    resultat_comptable: float = 0  # Bénéfice ou perte comptable
    reintegrations_detail: str = ""  # Détail des réintégrations
    reintegrations_montant: float = 0  # Total réintégrations
    deductions_detail: str = ""  # Détail des déductions
    deductions_montant: float = 0  # Total déductions
    reports_deficitaires: float = 0  # Reports déficitaires déductibles
    benefices_exoneres: float = 0
    taux_exoneration: float = 0
    benefices_reinvestis: float = 0

    # Section C — Récapitulation des éléments d'imposition
    ibs_revenu_comptable: float = 0
    ibs_revenu_fiscal: float = 0
    ibs_benefice_taux_x: float = 0  # Montant bénéfice taxé au taux de X%
    ibs_benefice_consolid: float = 0  # Bénéfice consolidé (régime de groupe)
    ibs_benefice_exonere: float = 0
    ibs_montant_reinvesti: float = 0
    ibs_regime_groupe: str = ""  # Oui / Non
    ibs_benefice_imposable: float = 0
    ibs_type_activite: str = "commerce_services"  # clé dans IBS_RATES

    # Section D — Taxe sur l'activité professionnelle (TAP)
    # (TAP supprimée depuis LF 2024 — mais reste sur le formulaire)
    ca_ventes_gros_droits: float = 0
    ca_ventes_detail_droits: float = 0
    ca_operations_gros: float = 0
    ca_autres_refaction: float = 0
    ca_ventes_non_refaction: float = 0
    ca_exonere: float = 0
    sous_traitance_designation: str = ""
    sous_traitance_nif: str = ""
    sous_traitance_montant: float = 0

    # Section E — Imputation
    credit_ibs_ras: float = 0
    credit_ibs_retenue_rcm: float = 0
    credit_ibs_creances: float = 0
    credit_ibs_depoits: float = 0
    autres_credits_imputables: float = 0

    # Section F — Rémunérations versées aux membres
    # (For SARL, sociétés en commandite par actions, sociétés civiles en SPA)
    remunerations: list = field(default_factory=list)

    # IBS Acomptes
    acompte_1: float = 0
    acompte_1_date: str = ""
    acompte_1_quittance: str = ""
    acompte_2: float = 0
    acompte_2_date: str = ""
    acompte_2_quittance: str = ""
    acompte_3: float = 0
    acompte_3_date: str = ""
    acompte_3_quittance: str = ""

    # Signature
    lieu_declaration: str = ""
    date_declaration: str = ""
    beneficiaire: str = ""

    # Metadata
    year: int = datetime.now().year


@dataclass
class G4Calculations:
    """Calculated IBS amounts."""
    resultat_fiscal: float = 0

    # IBS per rate
    ibs_19: float = 0
    ibs_23: float = 0
    ibs_26: float = 0
    ibs_total_taux: float = 0

    # Minimum IBS
    ca_total_imposable: float = 0
    ibs_minimum: float = 0

    # Credits & imputations
    total_credits: float = 0
    total_imputations: float = 0

    # Acomptes
    total_acomptes: float = 0

    # Final
    ibs_net_a_payer: float = 0
    ibs_avant_imputations: float = 0


def calculate_g4(data: G4Data) -> G4Calculations:
    """Calculate all IBS amounts for the G4 form."""
    calc = G4Calculations()

    # ── Résultat fiscal ──
    calc.resultat_fiscal = (
        data.resultat_comptable
        + data.reintegrations_montant
        - data.deductions_montant
        - data.reports_deficitaires
    )

    # ── Résultat imposable ──
    ibs_revenu_fiscal = data.ibs_revenu_fiscal if data.ibs_revenu_fiscal else calc.resultat_fiscal
    ibs_benefice_imposable = max(0, ibs_revenu_fiscal)

    # ── IBS by rate ──
    taux = IBS_RATES.get(data.ibs_type_activite, IBS_RATES["commerce_services"])["rate"]

    if data.ibs_type_activite == "production":
        calc.ibs_19 = ibs_benefice_imposable * 0.19
        calc.ibs_23 = 0
        calc.ibs_26 = 0
    elif data.ibs_type_activite == "btp_tourisme":
        calc.ibs_19 = 0
        calc.ibs_23 = ibs_benefice_imposable * 0.23
        calc.ibs_26 = 0
    else:
        calc.ibs_19 = 0
        calc.ibs_23 = 0
        calc.ibs_26 = ibs_benefice_imposable * 0.26

    calc.ibs_total_taux = calc.ibs_19 + calc.ibs_23 + calc.ibs_26

    # ── Minimum IBS (3% of CA imposable, or 30,000 DA minimum) ──
    calc.ca_total_imposable = (
        data.ca_ventes_gros_droits + data.ca_ventes_detail_droits +
        data.ca_operations_gros + data.ca_autres_refaction +
        data.ca_ventes_non_refaction
    )
    calc.ibs_minimum = max(calc.ca_total_imposable * 0.03, 30_000) if calc.ca_total_imposable > 0 else 30_000

    # IBS before imputations = max(total by rate, minimum)
    calc.ibs_avant_imputations = max(calc.ibs_total_taux, calc.ibs_minimum)

    # ── Credits & imputations ──
    calc.total_credits = (
        data.credit_ibs_ras + data.credit_ibs_retenue_rcm +
        data.credit_ibs_creances + data.credit_ibs_depoits
    )
    calc.total_imputations = calc.total_credits + data.autres_credits_imputables

    # ── Acomptes versés ──
    calc.total_acomptes = data.acompte_1 + data.acompte_2 + data.acompte_3

    # ── Solde IBS à payer ──
    calc.ibs_net_a_payer = max(0, calc.ibs_avant_imputations - calc.total_imputations - calc.total_acomptes)

    return calc


# ── Formatting Helpers ────────────────────────────────────────────────────────

def _fmt(n: float) -> str:
    """Format number with spaces as thousand separators."""
    if n == 0:
        return ""
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _fmt_cell(n: float) -> str:
    """Format for table cell — empty if zero."""
    if n == 0:
        return ""
    return _fmt(n)


def _blank(n: int = 30) -> str:
    """Blank line for unfilled fields."""
    return "." * n


def _checkbox(selected: bool) -> str:
    """Return checkbox character."""
    return "☑" if selected else "☐"


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css() -> str:
    """Complete CSS for official G4 form styling."""
    return """<style>
  @page { size: A4; margin: 12mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 9pt; color: #1a1a1a; margin: 0; padding: 12px;
    line-height: 1.35;
  }

  /* Header */
  .header {
    text-align: center; border: 2px solid #0A1628; padding: 6px 8px;
    margin-bottom: 8px; background: linear-gradient(180deg, #0A1628 0%, #162d54 100%);
    color: #fff;
  }
  .header .republique { font-size: 8pt; letter-spacing: 2px; text-transform: uppercase; }
  .header .dgi { font-size: 10pt; font-weight: bold; margin: 2px 0; color: #D4AF37; }
  .header h1 { font-size: 13pt; margin: 4px 0; color: #fff; }
  .header .serie { font-size: 10pt; font-weight: bold; color: #D4AF37; margin: 2px 0; }
  .header .subtitle { font-size: 8.5pt; color: #ccc; margin: 1px 0; }
  .header .deadline {
    font-size: 8pt; font-weight: bold; margin-top: 5px; padding: 3px 6px;
    border: 1px solid #D4AF37; background: rgba(212,175,55,0.1); color: #D4AF37;
  }

  /* DGI Hierarchy */
  .dgi-hierarchy { margin: 6px 0; }
  .dgi-hierarchy table { width: 100%; border-collapse: collapse; }
  .dgi-hierarchy td { padding: 2px 5px; font-size: 8pt; border: none; }
  .dgi-hierarchy .dgi-label { font-weight: bold; width: 30%; }
  .dgi-hierarchy .dgi-value { border-bottom: 1px dotted #999; width: 70%; }

  /* Section titles */
  .section-title {
    font-size: 9pt; font-weight: bold;
    background: linear-gradient(90deg, #0A1628, #162d54); color: #fff;
    padding: 3px 6px; margin: 8px 0 4px;
  }
  .section-title-ar { font-size: 8pt; color: #666; text-align: right; direction: rtl; margin-bottom: 4px; }

  /* Section */
  .section { margin: 8px 0; page-break-inside: avoid; }
  .page-break { page-break-before: always; }

  /* Identification table */
  .identification { margin: 6px 0; border: 1px solid #0A1628; padding: 6px; }
  .identification table { width: 100%; border-collapse: collapse; }
  .identification td { padding: 2px 5px; font-size: 8.5pt; vertical-align: top; }
  .identification .field-label { font-weight: bold; width: 30%; }
  .identification .field-value { border-bottom: 1px dotted #999; width: 70%; }

  /* Main tables */
  .g4-table { width: 100%; border-collapse: collapse; margin: 4px 0; }
  .g4-table th, .g4-table td {
    border: 1px solid #333; padding: 3px 5px; font-size: 8pt; text-align: center;
  }
  .g4-table th { background: #e8e8e8; font-weight: bold; font-size: 8pt; }
  .g4-table .desc { text-align: left; width: 30%; }
  .g4-table .desc .ar { font-size: 7pt; color: #888; direction: rtl; }
  .g4-table .num { font-family: 'Courier New', monospace; font-size: 8.5pt; width: 18%; }
  .g4-table .total-row { background: #f0f0f0; font-weight: bold; }
  .g4-table .highlight-row { background: #fffde7; font-weight: bold; }

  /* Fields table (for filled-in data) */
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 3px 5px; font-size: 8.5pt; vertical-align: top; }
  .fields-table .field-label { font-weight: bold; width: 35%; }
  .fields-table .field-value { border-bottom: 1px dotted #999; width: 65%; }

  /* Notes */
  .note { font-size: 7.5pt; color: #666; font-style: italic; margin: 2px 0; }
  .note-box {
    font-size: 8pt; color: #555; padding: 5px; margin: 5px 0;
    border: 1px solid #ccc; background: #fafafa;
  }

  /* Signature */
  .signature-block { display: flex; justify-content: space-between; margin: 12px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 8pt; border-top: 1px solid #333; padding-top: 4px; }
  .sig-box .title { font-weight: bold; margin-bottom: 5px; }
  .admin-box {
    width: 100%; border: 2px solid #0A1628; padding: 8px; margin-top: 10px;
    text-align: center; font-size: 8pt; min-height: 80px;
  }

  /* Attestation */
  .attestation {
    font-size: 8pt; font-style: italic; margin: 8px 0; padding: 5px;
    border: 1px solid #ccc; text-align: center;
  }

  /* Highlight */
  .amount { font-family: 'Courier New', monospace; font-weight: bold; }
  .negative { color: #c62828; }
  .positive { color: #2e7d32; }
  .result-line {
    font-size: 10pt; font-weight: bold; text-align: right; margin: 8px 0;
    padding: 6px; border: 2px solid #0A1628; background: #f0f0f0;
  }

  /* Print */
  @media print {
    body { padding: 0; font-size: 8pt; }
    .no-print { display: none; }
    .header { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .section-title { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .result-line { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>"""


# ── HTML Section Builders ─────────────────────────────────────────────────────

def _header_html(data: G4Data) -> str:
    """Official DGI header for G4 IBS."""
    return f"""<div class="header">
  <div class="republique">République Algérienne Démocratique et Populaire</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <div class="serie">Série G N°4</div>
  <h1>DÉCLARATION DE L'IMPÔT SUR LES BÉNÉFICES DES SOCIÉTÉS</h1>
  <div class="subtitle">IBS — Impôt sur les Bénéfices des Sociétés</div>
  <div class="deadline">Déclaration à souscrire, au plus tard le 30 Avril de chaque année</div>
</div>"""


def _dgi_hierarchy_html(data: G4Data) -> str:
    """DGI institutional hierarchy fields."""
    return f"""<div class="dgi-hierarchy">
  <table>
    <tr>
      <td class="dgi-label">Wilaya de :</td>
      <td class="dgi-value">{_esc(data.wilaya) or _blank(35)}</td>
      <td class="dgi-label">Année d'imposition :</td>
      <td class="dgi-value">{data.annee_imposition or _blank(15)}</td>
    </tr>
    <tr>
      <td class="dgi-label">DIW de :</td>
      <td class="dgi-value">{_esc(data.diw) or _blank(35)}</td>
      <td class="dgi-label">Période du :</td>
      <td class="dgi-value">{_esc(data.periode_debut) or '....../....../......'} au {_esc(data.periode_fin) or '....../....../......'}</td>
    </tr>
    <tr>
      <td class="dgi-label">Structure :</td>
      <td class="dgi-value">{_esc(data.structure) or _blank(35)}</td>
      <td class="dgi-label"></td>
      <td class="dgi-value"></td>
    </tr>
    <tr>
      <td class="dgi-label">Inspection des impôts de :</td>
      <td class="dgi-value">{_esc(data.inspection) or _blank(35)}</td>
      <td class="dgi-label"></td>
      <td class="dgi-value"></td>
    </tr>
    <tr>
      <td class="dgi-label">Recette des impôts de :</td>
      <td class="dgi-value">{_esc(data.recette) or _blank(35)}</td>
      <td class="dgi-label"></td>
      <td class="dgi-value"></td>
    </tr>
  </table>
</div>"""


def _section_a_identification_html(data: G4Data) -> str:
    """Section A — Identification de l'entreprise."""
    return f"""<div class="section">
  <div class="section-title">SECTION A — IDENTIFICATION DE L'ENTREPRISE</div>
  <div class="section-title-ar">القسم أ — تحديد المؤسسة</div>
  <div class="identification">
    <table>
      <tr>
        <td class="field-label">NIF :</td>
        <td class="field-value">{_esc(data.nif) or _blank(25)}</td>
      </tr>
      <tr>
        <td class="field-label">Raison sociale et forme juridique :</td>
        <td class="field-value">{_esc(data.raison_sociale) or _blank(25)} — {_esc(data.forme_juridique) or _blank(15)}</td>
      </tr>
      <tr>
        <td class="field-label">Activités exercées (souligner l'activité principale) :</td>
        <td class="field-value">{_esc(data.activites) or _blank(45)}</td>
      </tr>
      <tr>
        <td class="field-label">Code Activité :</td>
        <td class="field-value">{_esc(data.code_activite) or _blank(20)}</td>
      </tr>
      <tr>
        <td class="field-label">Numéro du Registre de Commerce :</td>
        <td class="field-value">{_esc(data.numero_rc) or _blank(25)}</td>
      </tr>
      <tr>
        <td class="field-label">Numéro(s) de compte(s) bancaire(s) ou CCP :</td>
        <td class="field-value">{_esc(data.comptes_bancaires) or _blank(35)}</td>
      </tr>
      <tr>
        <td class="field-label">Adresse du siège social — Au 1er janvier :</td>
        <td class="field-value">{_esc(data.adresse_siege_janvier) or _blank(45)}</td>
      </tr>
      <tr>
        <td class="field-label">Adresse du siège social — Au 1er janvier de l'année N+1 :</td>
        <td class="field-value">{_esc(data.adresse_siege_fin_annee) or _blank(45)}</td>
      </tr>
      <tr>
        <td class="field-label">Téléphone / Fax / Email :</td>
        <td class="field-value">{_esc(data.telephone) or _blank(15)} / {_esc(data.fax) or _blank(15)} / {_esc(data.email) or _blank(25)}</td>
      </tr>
      <tr>
        <td class="field-label">Adresse des établissements secondaires :</td>
        <td class="field-value">{_esc(data.adresse_etablissements_secondaires) or _blank(45)}</td>
      </tr>
      <tr>
        <td class="field-label">Nom, Prénom et Adresse du représentant légal :</td>
        <td class="field-value">{_esc(data.representant_legal) or _blank(25)} — {_esc(data.adresse_representant) or _blank(25)}</td>
      </tr>
    </table>
  </div>
</div>"""


def _section_b_resultat_fiscal_html(data: G4Data, calc: G4Calculations) -> str:
    """Section B — Détermination du résultat fiscal (Tableau 9)."""
    return f"""<div class="section">
  <div class="section-title">SECTION B — DÉTERMINATION DU RÉSULTAT FISCAL (TABLEAU 9)</div>
  <div class="section-title-ar">القسم ب — تحديد النتيجة الضريبية (الجدول 9)</div>
  <table class="g4-table">
    <thead>
      <tr>
        <th class="desc">Désignation</th>
        <th>Montant (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Résultat comptable (bénéfice ou perte)<br><span class="ar">النتيجة المحاسبية (ربح أو خسارة)</span></td>
        <td class="num">{_fmt_cell(data.resultat_comptable)}</td>
      </tr>
      <tr>
        <td class="desc">Réintégrations (corrections en plus)<br><span class="ar">إعادة الدمج (تصحيحات إضافية)</span></td>
        <td class="num">{_fmt_cell(data.reintegrations_montant)}</td>
      </tr>
      <tr>
        <td class="desc" style="padding-left:20px;font-size:7.5pt;">Détail des réintégrations :</td>
        <td class="desc" style="font-size:7.5pt;text-align:left;">{_esc(data.reintegrations_detail) or _blank(40)}</td>
      </tr>
      <tr>
        <td class="desc">Déductions (corrections en moins)<br><span class="ar">الخصوم (تصحيحات تناقصية)</span></td>
        <td class="num">{_fmt_cell(data.deductions_montant)}</td>
      </tr>
      <tr>
        <td class="desc" style="padding-left:20px;font-size:7.5pt;">Détail des déductions :</td>
        <td class="desc" style="font-size:7.5pt;text-align:left;">{_esc(data.deductions_detail) or _blank(40)}</td>
      </tr>
      <tr>
        <td class="desc">Reports déficitaires déductibles<br><span class="ar">الخسائر العالقة القابلة للخصم</span></td>
        <td class="num">{_fmt_cell(data.reports_deficitaires)}</td>
      </tr>
      <tr class="highlight-row">
        <td class="desc"><strong>Résultat fiscal = Comptable + Réintégrations − Déductions − Reports</strong><br><span class="ar">النتيجة الضريبية = المحاسبية + إعادة الدمج − الخصوم − العالق</span></td>
        <td class="num"><strong>{_fmt(calc.resultat_fiscal)}</strong></td>
      </tr>
      <tr>
        <td class="desc">Dont bénéfices exonérés (taux d'exonération : __%)<br><span class="ar">منها الأرباح المعفاة (نسبة الإعفاء: __%)</span></td>
        <td class="num">{_fmt_cell(data.benefices_exoneres)}</td>
      </tr>
      <tr>
        <td class="desc">Bénéfices réinvestis au cours de l'exercice<br><span class="ar">الأرباح المستثمرة أثناء الفترة</span></td>
        <td class="num">{_fmt_cell(data.benefices_reinvestis)}</td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section_c_recap_html(data: G4Data, calc: G4Calculations) -> str:
    """Section C — Récapitulation des éléments d'imposition + IBS calculation."""
    # Determine which rate label to show
    rate_info = IBS_RATES.get(data.ibs_type_activite, IBS_RATES["commerce_services"])

    return f"""<div class="section">
  <div class="section-title">SECTION C — RÉCAPITULATION DES ÉLÉMENTS D'IMPOSITION</div>
  <div class="section-title-ar">القسم ج — ملخص عناصر الضرائب</div>

  <table class="g4-table">
    <thead>
      <tr>
        <th class="desc" style="width:55%;">1 — Impôt sur les Bénéfices des Sociétés</th>
        <th style="width:20%;">Montant (DA)</th>
        <th style="width:25%;">Observations</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Résultat comptable (bénéfice/perte)<br><span class="ar">النتيجة المحاسبية</span></td>
        <td class="num">{_fmt_cell(data.ibs_revenu_comptable)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Résultat fiscal (bénéfice/perte)<br><span class="ar">النتيجة الضريبية</span></td>
        <td class="num">{_fmt_cell(calc.resultat_fiscal)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Dont bénéfice taxé au taux de {rate_info['rate']*100:.0f}%<br><span class="ar">منها الأرباح الخاضعة بنسبة {rate_info['rate']*100:.0f}%</span></td>
        <td class="num">{_fmt_cell(data.ibs_benefice_taux_x)}</td>
        <td>{rate_info['label_fr']}</td>
      </tr>
      <tr>
        <td class="desc">Bénéfice consolidé (régime de groupe)<br><span class="ar">الربح المconsolidé (نظام المجموعة)</span></td>
        <td class="num">{_fmt_cell(data.ibs_benefice_consolid)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Bénéfice exonéré (taux d'exonération %)<br><span class="ar">الربح المعفى</span></td>
        <td class="num">{_fmt_cell(data.ibs_benefice_exonere)}</td>
        <td>{data.taux_exoneration:.0f}%</td>
      </tr>
      <tr>
        <td class="desc">Montants réinvestis au cours de l'exercice<br><span class="ar">المبالغ المستثمرة</span></td>
        <td class="num">{_fmt_cell(data.ibs_montant_reinvesti)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">La société relève du régime fiscal des groupes de sociétés (mère/membre)<br><span class="ar">الشركة خاضعة لنظام الضرائب لمجموعات الشركات</span></td>
        <td class="desc" colspan="2" style="text-align:left;">{_checkbox(data.ibs_regime_groupe == "Oui")} Oui  {_checkbox(data.ibs_regime_groupe == "Non")} Non</td>
      </tr>
    </tbody>
  </table>

  <div class="note-box" style="margin-top:10px;">
    <strong>Calcul de l'IBS — Art. 18 et 224 du CIDTA</strong><br>
    <strong> Calcul de lIBA — المادة 18 و 224 من قانون الضرائب المباشرة والرسوم المماثلة</strong>
  </div>

  <table class="g4-table">
    <thead>
      <tr>
        <th class="desc" style="width:55%;">Calcul de l'IBS</th>
        <th style="width:25%;">Base imposable (DA)</th>
        <th style="width:20%;">IBS dû (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Bénéfice imposable<br><span class="ar">الربح الخاضع للضريبة</span></td>
        <td class="num">{_fmt_cell(data.ibs_benefice_imposable)}</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="desc">IBS au taux de 19% — Production industrielle<br><span class="ar">الضريبة على الدخل بنسبة 19% — الإنتاج الصناعي</span></td>
        <td class="num">{_fmt_cell(data.ibs_benefice_imposable if data.ibs_type_activite == 'production' else 0)}</td>
        <td class="num">{_fmt_cell(calc.ibs_19)}</td>
      </tr>
      <tr>
        <td class="desc">IBS au taux de 23% — BTP, Tourisme (sauf agences de voyage)<br><span class="ar">الضريبة على الدخل بنسبة 23% — الأشغال العمومية والسياحة</span></td>
        <td class="num">{_fmt_cell(data.ibs_benefice_imposable if data.ibs_type_activite == 'btp_tourisme' else 0)}</td>
        <td class="num">{_fmt_cell(calc.ibs_23)}</td>
      </tr>
      <tr>
        <td class="desc">IBS au taux de 26% — Commerce, Services et autres activités<br><span class="ar">الضريبة على الدخل بنسبة 26% — التجارة والخدمات والأنشطة الأخرى</span></td>
        <td class="num">{_fmt_cell(data.ibs_benefice_imposable if data.ibs_type_activite == 'commerce_services' else 0)}</td>
        <td class="num">{_fmt_cell(calc.ibs_26)}</td>
      </tr>
      <tr class="total-row">
        <td class="desc"><strong>Total IBS selon taux applicable</strong></td>
        <td class="num"></td>
        <td class="num"><strong>{_fmt(calc.ibs_total_taux)}</strong></td>
      </tr>
      <tr>
        <td class="desc">Minimum d'impôt (3% du CA ou 30,000 DA minimum)<br><span class="ar">الحد الأدنى للضريبة (3% من رقم الأعمال أو 30,000 دج)</span></td>
        <td class="num">{_fmt_cell(calc.ca_total_imposable)}</td>
        <td class="num">{_fmt_cell(calc.ibs_minimum)}</td>
      </tr>
      <tr class="highlight-row">
        <td class="desc"><strong>IBS retenu = max(IBS taux, minimum d'impôt)</strong></td>
        <td class="num"></td>
        <td class="num"><strong>{_fmt(calc.ibs_avant_imputations)}</strong></td>
      </tr>
      <tr>
        <td class="desc">Crédit d'impôt (retenue à la source, RCM, créances, dépôts)<br><span class="ar">الدائن الضريبي (الاستقطاعات، الإيداعات)</span></td>
        <td class="num"></td>
        <td class="num">{_fmt_cell(calc.total_credits)}</td>
      </tr>
      <tr>
        <td class="desc">Autres crédits imputables<br><span class="ar">مبالغ أخرى قابلة للخصم</span></td>
        <td class="num"></td>
        <td class="num">{_fmt_cell(data.autres_credits_imputables)}</td>
      </tr>
      <tr>
        <td class="desc">Acomptes versés (trimestriels)<br><span class="ar">الدفعات المقدمة</span></td>
        <td class="num"></td>
        <td class="num">{_fmt_cell(calc.total_acomptes)}</td>
      </tr>
      <tr class="highlight-row">
        <td class="desc"><strong>SOLDE I.B.S. À PAYER</strong><br><span class="ar">رصيد الضريبة على الدخل المدفوعة</span></td>
        <td class="num"></td>
        <td class="num"><strong style="font-size:10pt;">{_fmt(calc.ibs_net_a_payer)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section_d_ca_html(data: G4Data, calc: G4Calculations) -> str:
    """Section D — Taxe sur l'activité professionnelle (TAP) — Chiffre d'affaires."""
    ca_imposable = (
        data.ca_ventes_gros_droits + data.ca_ventes_detail_droits +
        data.ca_operations_gros + data.ca_autres_refaction +
        data.ca_ventes_non_refaction
    )
    ca_global = ca_imposable + data.ca_exonere

    return f"""<div class="section page-break">
  <div class="section-title">SECTION D — TAXE SUR L'ACTIVITÉ PROFESSIONNELLE (TAP)</div>
  <div class="section-title-ar">القسم د — الضريبة على النشاط المهني</div>
  <div class="note-box">
    ⚠ TAP supprimée depuis la Loi de Finances 2024 — Article 8 du CGI. Ce volet reste sur le formulaire à titre informatif.
  </div>

  <table class="g4-table">
    <thead>
      <tr>
        <th class="desc" style="width:60%;">Opérations imposables</th>
        <th style="width:20%;">Montant (DA)</th>
        <th style="width:20%;">Observations</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Ventes en gros portant sur produits avec >50% droits indirects<br><span class="ar">بيع بالجملة يتعلق بمنتجات بأكثر من 50% من الضرائب غير المباشرة</span></td>
        <td class="num">{_fmt_cell(data.ca_ventes_gros_droits)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Ventes au détail portant sur produits avec >50% droits indirects<br><span class="ar">بيع بالتجزئة يتعلق بمنتجات بأكثر من 50% من الضرائب غير المباشرة</span></td>
        <td class="num">{_fmt_cell(data.ca_ventes_detail_droits)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Opérations de ventes en gros<br><span class="ar">عمليات البيع بالجملة</span></td>
        <td class="num">{_fmt_cell(data.ca_operations_gros)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Autres opérations ouvrant droit à la réfaction<br><span class="ar">عمليات أخرى تفتح حق في الخصم</span></td>
        <td class="num">{_fmt_cell(data.ca_autres_refaction)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Ventes et opérations ne bénéficiant pas de réfaction<br><span class="ar">المبيعات والعمليات التي لا تستفيد من الخصم</span></td>
        <td class="num">{_fmt_cell(data.ca_ventes_non_refaction)}</td>
        <td></td>
      </tr>
      <tr class="total-row">
        <td class="desc"><strong>MONTANT TOTAL DU CHIFFRE D'AFFAIRES IMPOSABLE (1)</strong><br><span class="ar">إجمالي رقم الأعمال الخاضع للضريبة (1)</span></td>
        <td class="num"><strong>{_fmt(ca_imposable)}</strong></td>
        <td></td>
      </tr>
    </tbody>
  </table>

  <table class="g4-table" style="margin-top:8px;">
    <thead>
      <tr>
        <th class="desc" style="width:60%;">Opérations exonérées</th>
        <th style="width:20%;">Montant (DA)</th>
        <th style="width:20%;">Observations</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc" style="height:30px;"></td>
        <td class="num"></td>
        <td></td>
      </tr>
      <tr class="total-row">
        <td class="desc"><strong>MONTANT TOTAL DU CHIFFRE D'AFFAIRES EXONÉRÉ (2)</strong><br><span class="ar">إجمالي رقم الأعمال المعفي (2)</span></td>
        <td class="num"><strong>{_fmt(data.ca_exonere)}</strong></td>
        <td></td>
      </tr>
    </tbody>
  </table>

  <div class="result-line">
    <strong>MONTANT DU CHIFFRE D'AFFAIRES GLOBAL RÉALISÉ (1) + (2) :</strong> {_fmt(ca_global)} DA
  </div>

  <table class="g4-table" style="margin-top:8px;">
    <thead>
      <tr>
        <th class="desc" style="width:35%;">Sous-traitance</th>
        <th style="width:25%;">NIF</th>
        <th style="width:20%;">Désignation</th>
        <th style="width:20%;">Montant (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Sous-traitant(s)<br><span class="ar">المقاولون من الباطن</span></td>
        <td class="desc">{_esc(data.sous_traitance_nif) or _blank(20)}</td>
        <td class="desc">{_esc(data.sous_traitance_designation) or _blank(20)}</td>
        <td class="num">{_fmt_cell(data.sous_traitance_montant)}</td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section_e_imputation_html(data: G4Data, calc: G4Calculations) -> str:
    """Section E — Imputation des crédits."""
    return f"""<div class="section">
  <div class="section-title">SECTION E — IMPUTATION DES CRÉDITS</div>
  <div class="section-title-ar">القسم ه — احتساب الدائن</div>
  <table class="g4-table">
    <thead>
      <tr>
        <th class="desc" style="width:60%;">Nature du crédit</th>
        <th style="width:20%;">Montant (DA)</th>
        <th style="width:20%;">Observations</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Crédit d'impôt IBS — Retenue à la source (RCM, créances, dépôts)<br><span class="ar">الدائن الضريبي — الاستقطاعات (رسوم التسجيل، الإيداعات)</span></td>
        <td class="num">{_fmt_cell(data.credit_ibs_ras)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Retenue à la source sur commissions et courtages (RCM)<br><span class="ar">الاستقطاع على العمولات ووسطاء البورصة</span></td>
        <td class="num">{_fmt_cell(data.credit_ibs_retenue_rcm)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Créances fiscales reportées<br><span class="ar">الديون الضريبية المنقولة</span></td>
        <td class="num">{_fmt_cell(data.credit_ibs_creances)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Dépôts de garantie<br><span class="ar">إيداعات الضمان</span></td>
        <td class="num">{_fmt_cell(data.credit_ibs_depoits)}</td>
        <td></td>
      </tr>
      <tr>
        <td class="desc">Autres crédits imputables<br><span class="ar">مبالغ أخرى قابلة للخصم</span></td>
        <td class="num">{_fmt_cell(data.autres_credits_imputables)}</td>
        <td></td>
      </tr>
      <tr class="total-row">
        <td class="desc"><strong>TOTAL DES IMPUTATIONS</strong><br><span class="ar">إجمالي الخصوم</span></td>
        <td class="num"><strong>{_fmt(calc.total_imputations)}</strong></td>
        <td></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _section_f_remunerations_html(data: G4Data) -> str:
    """Section F — Rémunérations versées aux membres (SARL, sociétés en commandite, SPA)."""
    rows = ""
    if data.remunerations:
        for r in data.remunerations:
            rows += f"""<tr>
        <td class="num">{r.get('nif', '')}</td>
        <td class="num">{r.get('parts_sociales', '')}</td>
        <td class="num">{r.get('annee_versement', '')}</td>
        <td class="num">{_fmt_cell(r.get('traitements', 0))}</td>
        <td class="num">{_fmt_cell(r.get('indemnites_represent', 0))}</td>
        <td class="num">{_fmt_cell(r.get('remboursements', 0))}</td>
        <td class="num">{_fmt_cell(r.get('indemnites_frais_pro', 0))}</td>
        <td class="num">{_fmt_cell(r.get('autres_frais_pro', 0))}</td>
      </tr>"""
    else:
        rows = """<tr>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">SECTION F — RÉMUNÉRATIONS VERSÉES AUX MEMBRES DU CONSEIL D'ADMINISTRATION / GÉRANCE</div>
  <div class="section-title-ar">القسم و — المكافآت المدفوعة لأعضاء مجلس الإدارة / الإدارة</div>
  <div class="note-box">
    applicable aux SARL, sociétés en commandite par actions, sociétés civiles professionnelles en SPA
  </div>
  <table class="g4-table">
    <thead>
      <tr>
        <th>NIF</th>
        <th>Parts sociales</th>
        <th>Année de<br>versement</th>
        <th>Traitements/<br>émoluments</th>
        <th>Indemnités<br>représentation</th>
        <th>Remboursements</th>
        <th>Indemnités<br>frais pro</th>
        <th>Autres<br>frais pro</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</div>"""


def _acomptes_html(data: G4Data, calc: G4Calculations) -> str:
    """IBS quarterly acomptes section."""
    return f"""<div class="section">
  <div class="section-title">ACOMPTES TRIMESTRIELS DE L'IBS</div>
  <div class="section-title-ar">الدفعات المقدمة للضريبة على الدخل</div>
  <div class="note-box">
    3 acomptes trimestriels = 30% de l'IBS de l'année précédente chacun (total = 90%)
  </div>
  <table class="g4-table">
    <thead>
      <tr>
        <th class="desc" style="width:30%;">Acompte</th>
        <th style="width:25%;">Montant (DA)</th>
        <th style="width:20%;">Date de versement</th>
        <th style="width:25%;">N° Quittance</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">1er acompte (Mars)<br><span class="ar">الدفعة الأولى (مارس)</span></td>
        <td class="num">{_fmt_cell(data.acompte_1)}</td>
        <td class="desc">{_esc(data.acompte_1_date) or '....../....../......'}</td>
        <td class="desc">{_esc(data.acompte_1_quittance) or _blank(20)}</td>
      </tr>
      <tr>
        <td class="desc">2ème acompte (Juin)<br><span class="ar">الدفعة الثانية (جوان)</span></td>
        <td class="num">{_fmt_cell(data.acompte_2)}</td>
        <td class="desc">{_esc(data.acompte_2_date) or '....../....../......'}</td>
        <td class="desc">{_esc(data.acompte_2_quittance) or _blank(20)}</td>
      </tr>
      <tr>
        <td class="desc">3ème acompte (Novembre)<br><span class="ar">الدفعة الثالثة (نوفمبر)</span></td>
        <td class="num">{_fmt_cell(data.acompte_3)}</td>
        <td class="desc">{_esc(data.acompte_3_date) or '....../....../......'}</td>
        <td class="desc">{_esc(data.acompte_3_quittance) or _blank(20)}</td>
      </tr>
      <tr class="total-row">
        <td class="desc"><strong>TOTAL ACOMPTES VERSÉS</strong></td>
        <td class="num"><strong>{_fmt(calc.total_acomptes)}</strong></td>
        <td colspan="2"></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _signature_html(data: G4Data, calc: G4Calculations) -> str:
    """Signature block and admin frame."""
    return f"""<div class="section page-break">
  <div class="attestation">
    Je soussigné(e), certifie l'exactitude des renseignements donnés dans la présente déclaration.
    <br>
    أ undersigned hereby certify the accuracy of the information provided in this declaration.
  </div>

  <div style="display:flex;justify-content:space-between;margin:10px 0;">
    <div style="width:45%;">
      <strong>Fait à</strong> {_esc(data.lieu_declaration) or _blank(25)} <strong>le</strong> {_esc(data.date_declaration) or '....../....../......'}
    </div>
    <div style="width:45%;text-align:right;">
    </div>
  </div>

  <div class="signature-block">
    <div class="sig-box">
      <div class="title">Signature du déclarant</div>
      <div class="title" style="font-size:7pt;color:#888;">توقيع المعلن</div>
      <br><br><br><br>
      Cachet et signature
    </div>
    <div class="sig-box">
      <div class="title">Cachet de la société</div>
      <br><br><br><br>
      (Timbre de l'entreprise)
    </div>
  </div>

  <div class="admin-box">
    <strong>CADRE RÉSERVÉ À L'ADMINISTRATION</strong>
    <br>
    <span style="font-size:7pt;color:#888;">الإطار المخصص للإدارة</span>
    <br><br><br>
    <div style="display:flex;justify-content:space-between;padding:0 20px;">
      <div>Inspection des impôts :</div>
      <div>Date de réception :</div>
      <div>N° d'enregistrement :</div>
    </div>
    <br>
    <div style="display:flex;justify-content:space-between;padding:0 20px;">
      <div>Vérification :</div>
      <div>Observations :</div>
      <div>Signature :</div>
    </div>
  </div>
</div>"""


def _legal_page_html() -> str:
    """Legal references page."""
    return """<div class="section page-break">
  <div class="section-title">RÉFÉRENCES LÉGALES — IMPÔT SUR LES BÉNÉFICES DES SOCIÉTÉS</div>

  <div class="note-box">
    <h3 style="margin:5px 0;font-size:9pt;">Article 18 du CIDTA — Taux de l'IBS</h3>
    <p style="font-size:8pt;text-align:justify;">
    L'impôt sur les bénéfices des sociétés est appliqué aux bénéfices réalisés par les sociétés
    de capitaux et les personnes morales de droit privé ayant un objet lucratif, à quelque titre
    et sous quelque forme que ce soit. Le taux de l'IBS est fixé comme suit :
    </p>
    <ul style="font-size:8pt;margin:5px 0 5px 20px;">
      <li><strong>19%</strong> — Bénéfices provenant des activités industrielles et de production</li>
      <li><strong>23%</strong> — Bénéfices provenant des travaux publics et du bâtiment (BTP), et des opérations touristiques (sauf les agences de voyage et de tourisme)</li>
      <li><strong>26%</strong> — Bénéfices provenant des activités commerciales, des prestations de services et autres activités</li>
    </ul>
  </div>

  <div class="note-box">
    <h3 style="margin:5px 0;font-size:9pt;">Article 224 du CIDTA — Déclaration annuelle</h3>
    <p style="font-size:8pt;text-align:justify;">
    Les sociétés soumises à l'IBS sont tenues de souscrire, au plus tard le 30 avril de chaque année,
    une déclaration du résultat fiscal de l'année précédente. Cette déclaration doit être accompagnée
    du bilan, du compte de résultat et des annexes comptables.
    </p>
  </div>

  <div class="note-box">
    <h3 style="margin:5px 0;font-size:9pt;">Minimum d'impôt</h3>
    <p style="font-size:8pt;text-align:justify;">
    Le minimum d'impôt est égal au plus élevé des deux montants suivants :
    3% du chiffre d'affaires imposable de l'exercice ou le montant forfaitaire de 30 000 DA.
    Ce minimum est dû même en cas de résultat déficitaire.
    </p>
  </div>

  <div class="note-box">
    <h3 style="margin:5px 0;font-size:9pt;">Acomptes trimestriels</h3>
    <p style="font-size:8pt;text-align:justify;">
    Les sociétés soumises à l'IBS doivent verser des acomptes trimestriels égaux à 30% de l'IBS
    acquitté au titre de l'année précédente. Les acomptes sont versés en mars, juin et novembre.
    Le total des acomptes représente 90% de l'IBS de l'année précédente.
    </p>
  </div>

  <div class="note-box">
    <h3 style="margin:5px 0;font-size:9pt;">Pénalités de retard</h3>
    <p style="font-size:8pt;text-align:justify;">
    En cas de retard dans le dépôt de la déclaration ou de versement de l'impôt, des pénalités
    de retard sont appliquées conformément aux dispositions du Code des Procédures Fiscales (CPF).
    Le taux de l'intérêt de retard est fixé à 0,2% par jour de retard.
    </p>
  </div>
</div>"""


# ── Main Generator ────────────────────────────────────────────────────────────

def generate_g4(data: G4Data) -> str:
    """Generate complete G4 IBS form as HTML.
    
    Args:
        data: G4Data instance with all form fields.
        
    Returns:
        Complete HTML string for the G4 IBS declaration form.
    """
    calc = calculate_g4(data)

    html = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G N°4 IBS — Déclaration IBS {data.annee_imposition}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_dgi_hierarchy_html(data)}
{_section_a_identification_html(data)}
{_section_b_resultat_fiscal_html(data, calc)}
{_section_c_recap_html(data, calc)}

<div class="page-break"></div>

{_section_d_ca_html(data, calc)}
{_section_e_imputation_html(data, calc)}
{_section_f_remunerations_html(data)}
{_acomptes_html(data, calc)}
{_signature_html(data, calc)}
{_legal_page_html()}

</body>
</html>"""

    hook_generation("g4_ibs", {"annee_imposition": data.annee_imposition, "nif": data.nif}, html)
    return html


# Alias for consistency with other generators
generate_g4_html = generate_g4


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import io

    # Fix encoding on Windows
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    sample = G4Data(
        # DGI hierarchy
        wilaya="32 - El Bayadh",
        diw="DIW D'EL BAYADH",
        structure="Structure d'El Bayadh Centre",
        inspection="Inspection des Impôts d'El Bayadh",
        recette="Recette des Impôts d'El Bayadh Centre",
        annee_imposition=2025,
        periode_debut="01/01/2025",
        periode_fin="31/12/2025",

        # Section A
        nif="1234567890",
        raison_sociale="SARL TECH SOLUTIONS ALGÉRIE",
        forme_juridique="SARL",
        activites="Prestation de services informatiques, conseil en management, formation",
        activite_principale="Prestation de services informatiques",
        code_activite="6201",
        numero_rc="09/00-12345678 B 25",
        comptes_bancaires="00799999 0001234567 89 — BNA El Bayadh",
        adresse_siege_janvier="123 Rue Didouche Mourad, El Bayadh",
        adresse_siege_fin_annee="",
        telephone="0555081718",
        fax="0555081719",
        email="contact@tech-solutions.dz",
        adresse_etablissements_secondaires="",
        representant_legal="",
        adresse_representant="",

        # Section B — Résultat fiscal
        resultat_comptable=4_500_000,
        reintegrations_detail="Amortissements non déductibles, provisions non admises",
        reintegrations_montant=350_000,
        deductions_detail="Reprises sur provisions, plus-values exonérées",
        deductions_montant=200_000,
        reports_deficitaires=0,
        benefices_exoneres=500_000,
        taux_exoneration=10,
        benefices_reinvestis=2_000_000,

        # Section C
        ibs_revenu_comptable=4_500_000,
        ibs_revenu_fiscal=4_650_000,
        ibs_benefice_taux_x=4_150_000,
        ibs_benefice_exonere=500_000,
        ibs_montant_reinvesti=2_000_000,
        ibs_regime_groupe="Non",
        ibs_benefice_imposable=4_650_000,
        ibs_type_activite="commerce_services",

        # Section D — CA
        ca_ventes_gros_droits=0,
        ca_ventes_detail_droits=0,
        ca_operations_gros=0,
        ca_autres_refaction=0,
        ca_ventes_non_refaction=6_000_000,
        ca_exonere=0,
        sous_traitance_designation="",
        sous_traitance_nif="",
        sous_traitance_montant=0,

        # Section E — Imputation
        credit_ibs_ras=120_000,
        credit_ibs_retenue_rcm=0,
        credit_ibs_creances=0,
        credit_ibs_depoits=0,
        autres_credits_imputables=0,

        # Section F — Rémunérations
        remunerations=[
            {
                "nif": "1234567891",
                "parts_sociales": "50%",
                "annee_versement": "2025",
                "traitements": 600_000,
                "indemnites_represent": 50_000,
                "remboursements": 20_000,
                "indemnites_frais_pro": 30_000,
                "autres_frais_pro": 10_000,
            },
        ],

        # Acomptes
        acompte_1=350_000,
        acompte_1_date="15/03/2025",
        acompte_1_quittance="Q-2025-001",
        acompte_2=350_000,
        acompte_2_date="15/06/2025",
        acompte_2_quittance="Q-2025-002",
        acompte_3=350_000,
        acompte_3_date="15/11/2025",
        acompte_3_quittance="Q-2025-003",

        # Signature
        lieu_declaration="El Bayadh",
        date_declaration="15/04/2026",
        beneficiaire="Ahmed Benali",

        year=2025,
    )

    calc = calculate_g4(sample)

    print("=== G N4 - IBS Calculation Summary ===")
    print(f"NIF: {sample.nif}")
    print(f"Raison sociale: {sample.raison_sociale}")
    print(f"Année: {sample.annee_imposition}")
    print()
    print(f"Résultat comptable:  {_fmt(sample.resultat_comptable)} DA")
    print(f"Réintégrations:      {_fmt(sample.reintegrations_montant)} DA")
    print(f"Déductions:          {_fmt(sample.deductions_montant)} DA")
    print(f"Résultat fiscal:     {_fmt(calc.resultat_fiscal)} DA")
    print()
    print(f"Bénéfice imposable:  {_fmt(sample.ibs_benefice_imposable)} DA")
    print(f"IBS 19% (production): {_fmt(calc.ibs_19)} DA")
    print(f"IBS 23% (BTP):        {_fmt(calc.ibs_23)} DA")
    print(f"IBS 26% (services):   {_fmt(calc.ibs_26)} DA")
    print(f"IBS total (taux):     {_fmt(calc.ibs_total_taux)} DA")
    print(f"Minimum IBS:          {_fmt(calc.ibs_minimum)} DA")
    print(f"IBS retenu:           {_fmt(calc.ibs_avant_imputations)} DA")
    print()
    print(f"Crédits IBS:          {_fmt(calc.total_credits)} DA")
    print(f"Acomptes versés:      {_fmt(calc.total_acomptes)} DA")
    print(f"Solde IBS à payer:    {_fmt(calc.ibs_net_a_payer)} DA")

    if "--html" in sys.argv:
        html = generate_g4(sample)
        out = "g4_ibs_official.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out}")
