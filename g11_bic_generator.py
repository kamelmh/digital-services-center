"""G11 BIC Official Form Generator — Annual Tax Declaration for Bénéfices Industriels et Commerciaux.

Generates G11 forms (Série G N°11) matching the official Algerian tax forms
from DGI (Direction Générale des Impôts) for persons physiques under régime réel.

Covers:
- Page 1: Identification du contribuable, associés, comptable
- Page 2: Chiffre d'affaires (Art. 224 CIDTA) + Résultat fiscal (réintégrations/déductions)
- Page 3: Liquidation de l'IRG/BIC + Signature

Who must file: Persons physiques with BIC under régime réel (CA > 30M DA or voluntary option).
Deadline: Before April 30 each year.
Legal reference: Articles 18 and 224 of the CIDTA.

IRG Rates for BIC (2026):
- 19% — production activities
- 23% — BTP, tourisme
- 26% — commerce, services
- Progressive barème also applies

Usage:
    from g11_bic_generator import G11Data, calculate_g11, generate_g11
    data = G11Data(nif="1234567890", ca_imposable=50_000_000, result_comptable_benefice=8_000_000)
    html = generate_g11(data)
"""

from __future__ import annotations

import html as _html_mod
from dataclasses import dataclass, field
from datetime import datetime


def _esc(value: object, default: str = "") -> str:
    """HTML-escape a value for safe rendering."""
    if value is None:
        return default
    return _html_mod.escape(str(value))
from typing import List, Optional


# ── Constants ─────────────────────────────────────────────────────────────────

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

# IRG Rates for BIC (2026)
IRG_RATES = {
    "production": {"label_fr": "Activités de production",
                   "label_ar": "أنشطة الإنتاج",
                   "rate": 0.19},
    "btp_tourisme": {"label_fr": "BTP et tourisme",
                     "label_ar": "البناء والأشغال العمومية والسياحة",
                     "rate": 0.23},
    "commerce_services": {"label_fr": "Commerce et services",
                          "label_ar": "التجارة والخدمات",
                          "rate": 0.26},
}

# Progressive IRG barème for BIC (annual, 2026)
# Art. 18 CIDTA — barème progressif applicable aux BIC
IRG_BAREME_BIC = [
    (200_000, 0.00),
    (1_200_000, 0.20),
    (3_600_000, 0.30),
    (10_000_000, 0.34),
    (20_000_000, 0.37),
    (float("inf"), 0.40),
]


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class Associe:
    """Identification d'un associé / partenaire."""
    nom_prenoms: str = ""
    pourcentage: float = 0.0
    adresse_domicile_fiscal: str = ""
    nif: str = ""


@dataclass
class G11Data:
    """Complete data for G11 BIC form generation."""
    # DGI hierarchy
    wilaya: str = ""
    diw: str = ""
    structure: str = ""
    inspection: str = ""
    recette: str = ""
    annee: int = datetime.now().year
    periode: str = ""

    # Section I — Identification de l'entreprise
    nif: str = ""
    nin: str = ""
    nom_prenoms: str = ""
    date_lieu_naissance: str = ""
    nature_activites: str = ""
    code_activite: str = ""
    registre_commerce: str = ""
    comptes_bancaires: str = ""
    adresse_siege_1er_janvier: str = ""
    adresse_siege_1er_janvier_n1: str = ""
    telephone: str = ""
    fax: str = ""
    email: str = ""
    adresse_etablissements_secondaires: str = ""

    # Activité exonérée
    exonere_anade: bool = False
    exonere_cnac: bool = False
    exonere_angem: bool = False
    exonere_autres: bool = False
    exonere_autres_details: str = ""

    # Section II — Identification des personnes imposables (associés)
    associes: List[Associe] = field(default_factory=list)

    # Section III — Identification du comptable/expert
    comptable_nom: str = ""
    comptable_adresse: str = ""
    comptable_nif: str = ""
    comptable_personnel_salarie: bool = False

    # Page 2 — Éléments servant à la détermination de la base imposable

    # 1. Volet relatif au chiffre d'affaires (Art. 224 CIDTA)
    # Opérations imposables
    ca_ventes_gros_droits_indirects: float = 0
    ca_ventes_detail_droits_indirects: float = 0
    ca_operations_ventes_gros: float = 0
    ca_autres_operations_refaction: float = 0
    ca_ventes_sans_refaction: float = 0

    # Opérations exonérées
    ca_producteurs_biens: float = 0
    ca_produits_large_consommation: float = 0
    ca_exportations: float = 0
    ca_lait_cru: float = 0
    ca_autres_exonerations: float = 0

    # 2. Volet relatif au résultat fiscal
    result_comptable_benefice: float = 0  # Bénéfice (ou perte si négatif)
    total_reintegrations: float = 0
    total_deductions: float = 0
    revenus_exoneres: float = 0

    # Type d'activité IRG
    type_activite_irg: str = "commerce_services"  # production, btp_tourisme, commerce_services
    use_barème_progressif: bool = False  # True = barème progressif, False = taux proportionnel

    # Page 3 — Liquidation de l'IRG/BIC
    acompte_1: float = 0
    acompte_2: float = 0

    # Signature
    lieu_declaration: str = ""
    date_declaration: str = ""
    beneficiaire: str = ""


@dataclass
class G11Calculations:
    """Calculated amounts for G11 form."""
    # Chiffre d'affaires
    ca_imposable: float = 0
    ca_exonere: float = 0
    ca_global: float = 0

    # Résultat fiscal
    resultat_fiscal: float = 0
    revenu_imposable: float = 0

    # IRG
    irg_taux_proportionnel: float = 0
    irg_bareme_progressif: float = 0
    irg_du: float = 0
    irg_taux_applique: float = 0

    # Liquidation
    total_acomptes: float = 0
    solde_liquidation: float = 0
    excedent_versement: float = 0


# ── Calculations ──────────────────────────────────────────────────────────────

def _calculate_irg_bareme_progressif(revenu_imposable: float) -> float:
    """Calculate IRG using progressive barème (Art. 18 CIDTA)."""
    if revenu_imposable <= 0:
        return 0.0

    remaining = revenu_imposable
    irg = 0.0
    prev_limit = 0.0

    for limit, rate in IRG_BAREME_BIC:
        bracket_size = limit - prev_limit
        taxable = min(remaining, bracket_size)
        irg += taxable * rate
        remaining -= taxable
        prev_limit = limit
        if remaining <= 0:
            break

    return irg


def calculate_g11(data: G11Data) -> G11Calculations:
    """Calculate all amounts for the G11 BIC form."""
    calc = G11Calculations()

    # ── Chiffre d'affaires ──
    calc.ca_imposable = (
        data.ca_ventes_gros_droits_indirects +
        data.ca_ventes_detail_droits_indirects +
        data.ca_operations_ventes_gros +
        data.ca_autres_operations_refaction +
        data.ca_ventes_sans_refaction
    )

    calc.ca_exonere = (
        data.ca_producteurs_biens +
        data.ca_produits_large_consommation +
        data.ca_exportations +
        data.ca_lait_cru +
        data.ca_autres_exonerations
    )

    calc.ca_global = calc.ca_imposable + calc.ca_exonere

    # ── Résultat fiscal ──
    # Art. 224 CIDTA: Résultat fiscal = Résultat comptable + Réintégrations - Déductions
    calc.resultat_fiscal = (
        data.result_comptable_benefice +
        data.total_reintegrations -
        data.total_deductions
    )

    # Revenu imposable = Résultat fiscal - Revenus exonérés
    calc.revenu_imposable = max(0, calc.resultat_fiscal - data.revenus_exoneres)

    # ── IRG ──
    rate_info = IRG_RATES.get(data.type_activite_irg, IRG_RATES["commerce_services"])
    calc.irg_taux_applique = rate_info["rate"]

    # Taux proportionnel (flat rate)
    calc.irg_taux_proportionnel = calc.revenu_imposable * calc.irg_taux_applique

    # Barème progressif (option)
    calc.irg_bareme_progressif = _calculate_irg_bareme_progressif(calc.revenu_imposable)

    # IRG dû = minimum of the two methods (taxpayer chooses the lower)
    if data.use_barème_progressif:
        calc.irg_du = calc.irg_bareme_progressif
    else:
        calc.irg_du = calc.irg_taux_proportionnel

    # ── Liquidation ──
    calc.total_acomptes = data.acompte_1 + data.acompte_2
    calc.solde_liquidation = max(0, calc.irg_du - calc.total_acomptes)
    calc.excedent_versement = max(0, calc.total_acomptes - calc.irg_du)

    return calc


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


def _blank(n: int = 20) -> str:
    """Blank line for unfilled fields."""
    return "." * n


def _checkbox(checked: bool) -> str:
    """Return checkbox character."""
    return "☑" if checked else "☐"


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css() -> str:
    """Complete CSS for official G11 form styling."""
    return """<style>
  @page { size: A4; margin: 12mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 9pt; color: #1a1a1a; margin: 0; padding: 15px;
    line-height: 1.3;
  }

  /* Header */
  .header {
    text-align: center; border: 2px solid #0A1628; padding: 6px 8px;
    margin-bottom: 8px; background: linear-gradient(180deg, #0A1628 0%, #162d54 100%);
    color: #fff;
  }
  .header .republique { font-size: 8pt; letter-spacing: 2px; text-transform: uppercase; }
  .header .dgi { font-size: 10pt; font-weight: bold; margin: 2px 0; color: #D4AF37; }
  .header .serie { font-size: 10pt; font-weight: bold; color: #D4AF37; margin: 2px 0; }
  .header h1 { font-size: 12pt; margin: 4px 0; color: #fff; }
  .header .subtitle { font-size: 8.5pt; color: #ccc; margin: 1px 0; }
  .header .deadline { font-size: 8pt; font-weight: bold; margin-top: 5px; padding: 3px 6px; border: 1px solid #D4AF37; background: rgba(212,175,55,0.1); color: #D4AF37; }

  /* DGI Hierarchy */
  .dgi-hierarchy { margin: 6px 0; }
  .dgi-hierarchy table { width: 100%; border-collapse: collapse; }
  .dgi-hierarchy td { padding: 2px 5px; font-size: 8pt; border: none; }
  .dgi-hierarchy .dgi-label { font-weight: bold; width: 30%; }
  .dgi-hierarchy .dgi-value { border-bottom: 1px dotted #999; width: 70%; }

  /* Section titles */
  .section-title {
    font-size: 9pt; font-weight: bold; color: #fff;
    background: linear-gradient(90deg, #0A1628, #162d54);
    padding: 3px 6px; margin: 8px 0 4px;
    border-bottom: 2px solid #0A1628;
  }
  .section-title-ar { font-size: 8pt; color: #666; text-align: right; direction: rtl; margin-bottom: 4px; }

  /* Identification table */
  .id-table { width: 100%; border-collapse: collapse; margin: 4px 0; }
  .id-table td { padding: 3px 5px; font-size: 8.5pt; vertical-align: top; }
  .id-table .field-label { font-weight: bold; width: 35%; }
  .id-table .field-value { border-bottom: 1px dotted #999; width: 65%; }
  .id-table .checkbox-cell { white-space: nowrap; font-size: 8pt; padding: 2px 8px; }
  .id-table .checkbox-table { border: none; }
  .id-table .checkbox-table td { border: none; padding: 2px 6px; font-size: 8pt; }

  /* Main tables */
  .g11-table { width: 100%; border-collapse: collapse; margin: 4px 0; }
  .g11-table th, .g11-table td { border: 1px solid #333; padding: 3px 5px; font-size: 8pt; text-align: center; }
  .g11-table th { background: #e8e8e8; font-weight: bold; font-size: 8pt; }
  .g11-table .desc { text-align: left; width: 40%; }
  .g11-table .desc .ar { font-size: 7pt; color: #888; direction: rtl; }
  .g11-table .num { font-family: 'Courier New', monospace; font-size: 8.5pt; width: 18%; }
  .g11-table .total-row { background: #f0f0f0; font-weight: bold; }
  .g11-table .subtotal-row { background: #f8f8f0; font-weight: bold; }

  /* Associes table */
  .associes-table { width: 100%; border-collapse: collapse; margin: 4px 0; }
  .associes-table th, .associes-table td { border: 1px solid #333; padding: 3px 5px; font-size: 8pt; }
  .associes-table th { background: #e8e8e8; font-weight: bold; }

  /* Comptable box */
  .comptable-box { border: 1px solid #ccc; padding: 6px; margin: 6px 0; }
  .comptable-box table { width: 100%; border-collapse: collapse; }
  .comptable-box td { padding: 2px 5px; font-size: 8.5pt; }
  .comptable-box .field-label { font-weight: bold; width: 35%; }
  .comptable-box .field-value { border-bottom: 1px dotted #999; width: 65%; }

  /* IRG liquidation */
  .irg-box { border: 2px solid #0A1628; padding: 8px; margin: 8px 0; }
  .irg-box .title { font-weight: bold; font-size: 9pt; margin-bottom: 5px; background: #0A1628; color: #fff; padding: 3px 6px; }
  .irg-box table { width: 100%; border-collapse: collapse; }
  .irg-box td { padding: 3px 5px; font-size: 8.5pt; }
  .irg-box .field-label { font-weight: bold; width: 45%; }
  .irg-box .field-value { border-bottom: 1px dotted #999; width: 55%; }
  .irg-box .total-line { background: #f0f0f0; font-weight: bold; font-size: 10pt; }

  /* Signature */
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 8.5pt; border-top: 1px solid #333; padding-top: 5px; }
  .admin-box { width: 45%; text-align: center; font-size: 8pt; border: 2px solid #0A1628; padding: 10px; }

  /* Notes */
  .note { font-size: 7.5pt; color: #666; font-style: italic; margin: 2px 0; }
  .highlight { background: #fffde7; font-weight: bold; }
  .amount { font-family: 'Courier New', monospace; font-weight: bold; }

  /* Print */
  @media print {
    body { padding: 0; font-size: 8pt; }
    .no-print { display: none; }
    .header { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .section-title { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>"""


# ── HTML Helpers ──────────────────────────────────────────────────────────────

def _header_html(data: G11Data) -> str:
    """Official DGI header for G11."""
    return f"""<div class="header">
  <div class="republique">République Algérienne Démocratique et Populaire</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <div class="serie">Série G N°11 — {data.annee}</div>
  <h1>DÉCLARATION DES BÉNÉFICES PROFESSIONNELS</h1>
  <div class="subtitle">IMPÔT SUR LE REVENU GLOBAL (Régime du Bénéfice Réel) + TAXE SUR L'ACTIVITÉ PROFESSIONNELLE</div>
  <div class="deadline">Déclaration à souscrire, au plus tard le 30 Avril de chaque année</div>
</div>"""


def _dgi_hierarchy_html(data: G11Data) -> str:
    """DGI institutional hierarchy fields."""
    return f"""<div class="dgi-hierarchy">
  <table>
    <tr>
      <td class="dgi-label">Wilaya :</td>
      <td class="dgi-value">{_esc(data.wilaya) or _blank(40)}</td>
      <td class="dgi-label">Année :</td>
      <td class="dgi-value">{data.annee}</td>
    </tr>
    <tr>
      <td class="dgi-label">DIW :</td>
      <td class="dgi-value">{_esc(data.diw) or _blank(40)}</td>
      <td class="dgi-label">Période :</td>
      <td class="dgi-value">{_esc(data.periode) or _blank(15)}</td>
    </tr>
    <tr>
      <td class="dgi-label">Structure :</td>
      <td class="dgi-value">{_esc(data.structure) or _blank(40)}</td>
      <td class="dgi-label"></td>
      <td class="dgi-value"></td>
    </tr>
    <tr>
      <td class="dgi-label">Inspection des impôts de :</td>
      <td class="dgi-value">{_esc(data.inspection) or _blank(40)}</td>
      <td class="dgi-label"></td>
      <td class="dgi-value"></td>
    </tr>
    <tr>
      <td class="dgi-label">Recette des Impôts de :</td>
      <td class="dgi-value">{_esc(data.recette) or _blank(40)}</td>
      <td class="dgi-label"></td>
      <td class="dgi-value"></td>
    </tr>
  </table>
</div>"""


def _section1_identification_html(data: G11Data) -> str:
    """Section I — Identification de l'entreprise."""
    # Activité exonérée checkboxes
    exo_checks = (
        f'<td class="checkbox-cell">{_checkbox(data.exonere_anade)} ANADE</td>'
        f'<td class="checkbox-cell">{_checkbox(data.exonere_cnac)} CNAC</td>'
        f'<td class="checkbox-cell">{_checkbox(data.exonere_angem)} ANGEM</td>'
        f'<td class="checkbox-cell">{_checkbox(data.exonere_autres)} Autres'
        f'{" (" + data.exonere_autres_details + ")" if data.exonere_autres and data.exonere_autres_details else ""}</td>'
    )

    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DE L'ENTREPRISE</div>
  <div class="section-title-ar">I — تحديد المؤسسة</div>
  <table class="id-table">
    <tr>
      <td class="field-label">NIF :</td>
      <td class="field-value">{_esc(data.nif) or _blank(25)}</td>
      <td class="field-label">N.I.N :</td>
      <td class="field-value">{_esc(data.nin) or _blank(20)}</td>
    </tr>
    <tr>
      <td class="field-label">Nom, Prénom / Raison sociale :</td>
      <td class="field-value" colspan="3">{_esc(data.nom_prenoms) or _blank(60)}</td>
    </tr>
    <tr>
      <td class="field-label">Date et lieu de Naissance :</td>
      <td class="field-value" colspan="3">{_esc(data.date_lieu_naissance) or _blank(40)}</td>
    </tr>
    <tr>
      <td class="field-label">Nature des activités exercées :</td>
      <td class="field-value" colspan="3">{_esc(data.nature_activites) or _blank(60)}</td>
    </tr>
    <tr>
      <td class="field-label">Code Activité :</td>
      <td class="field-value">{_esc(data.code_activite) or _blank(15)}</td>
      <td class="field-label">Registre de commerce :</td>
      <td class="field-value">{_esc(data.registre_commerce) or _blank(20)}</td>
    </tr>
    <tr>
      <td class="field-label">N° compte(s) bancaire(s) ou CCP :</td>
      <td class="field-value" colspan="3">{_esc(data.comptes_bancaires) or _blank(40)}</td>
    </tr>
    <tr>
      <td class="field-label">Adresse du siège au 1er janvier :</td>
      <td class="field-value" colspan="3">{_esc(data.adresse_siege_1er_janvier) or _blank(60)}</td>
    </tr>
    <tr>
      <td class="field-label">Adresse du siège au 1er janvier N+1 :</td>
      <td class="field-value" colspan="3">{_esc(data.adresse_siege_1er_janvier_n1) or _blank(60)}</td>
    </tr>
    <tr>
      <td class="field-label">Téléphone :</td>
      <td class="field-value">{_esc(data.telephone) or _blank(15)}</td>
      <td class="field-label">Fax :</td>
      <td class="field-value">{_esc(data.fax) or _blank(15)}</td>
    </tr>
    <tr>
      <td class="field-label">Email :</td>
      <td class="field-value" colspan="3">{_esc(data.email) or _blank(40)}</td>
    </tr>
    <tr>
      <td class="field-label">Adresse établissements secondaires :</td>
      <td class="field-value" colspan="3">{_esc(data.adresse_etablissements_secondaires) or _blank(60)}</td>
    </tr>
    <tr>
      <td class="field-label">Activité exonérée :</td>
      <td class="field-value" colspan="3">
        <table class="checkbox-table"><tr>{exo_checks}</tr></table>
      </td>
    </tr>
  </table>
</div>"""


def _section2_associes_html(data: G11Data) -> str:
    """Section II — Identification des personnes imposables (associés)."""
    if not data.associes:
        # Empty placeholder rows
        rows_html = ""
        for _ in range(3):
            rows_html += f"""<tr>
        <td>{_blank(25)}</td>
        <td class="num"></td>
        <td>{_blank(30)}</td>
        <td>{_blank(15)}</td>
      </tr>"""
    else:
        rows_html = ""
        for a in data.associes:
            rows_html += f"""<tr>
        <td>{_esc(a.nom_prenoms) or _blank(25)}</td>
        <td class="num">{a.pourcentage if a.pourcentage else ""}</td>
        <td>{_esc(a.adresse_domicile_fiscal) or _blank(30)}</td>
        <td>{_esc(a.nif) or _blank(15)}</td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">II — IDENTIFICATION DES PERSONNES IMPOSABLES</div>
  <div class="section-title-ar">II — تحديد الأشخاص الخاضعين للضريبة</div>
  <table class="associes-table">
    <thead>
      <tr>
        <th style="width:30%;">Nom, Prénoms</th>
        <th style="width:10%;">Part bénéfices (%)</th>
        <th style="width:35%;">Adresse domicile fiscal</th>
        <th style="width:25%;">NIF</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>"""


def _section3_comptable_html(data: G11Data) -> str:
    """Section III — Identification du comptable/expert."""
    salarie = _checkbox(data.comptable_personnel_salarie)
    return f"""<div class="section">
  <div class="section-title">III — IDENTIFICATION DU COMPTABLE / EXPERT</div>
  <div class="section-title-ar">III — تحديد المحاسب / الخبير</div>
  <div class="comptable-box">
    <table>
      <tr>
        <td class="field-label">Nom :</td>
      <td class="field-value">{_esc(data.comptable_nom) or _blank(30)}</td>
      <td class="field-label">NIF :</td>
      <td class="field-value">{_esc(data.comptable_nif) or _blank(15)}</td>
      </tr>
      <tr>
        <td class="field-label">Adresse :</td>
        <td class="field-value" colspan="3">{_esc(data.comptable_adresse) or _blank(50)}</td>
      </tr>
      <tr>
        <td class="field-label">Personnel salarié :</td>
        <td class="field-value">
          {salarie} Oui &nbsp;&nbsp; {"" if data.comptable_personnel_salarie else "☐"} Non
        </td>
        <td class="field-label"></td>
        <td class="field-value"></td>
      </tr>
    </table>
  </div>
</div>"""


def _ca_imposable_table_html(data: G11Data, calc: G11Calculations) -> str:
    """Table: Opérations imposables au chiffre d'affaires (Art. 224 CIDTA)."""
    return f"""<div class="section">
  <div class="section-title">1 — VOLET RELATIF AU CHIFFRE D'AFFAIRES (Art. 224 CIDTA)</div>
  <div class="section-title-ar">1 — الجزء المخصص لرقم الأعمال (المادة 224 من قانون الضرائب المباشرة)</div>

  <div style="font-weight:bold; font-size:8.5pt; margin:4px 0;">Opérations imposables :</div>
  <table class="g11-table">
    <thead>
      <tr>
        <th class="desc">Nature de l'opération</th>
        <th>Montant (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Ventes en gros (produits avec >50% droits indirects)<br><span class="ar">بيع بالجملة (منتجات بأكثر من 50% ضرائب غير مباشرة)</span></td>
        <td class="num">{_fmt_cell(data.ca_ventes_gros_droits_indirects)}</td>
      </tr>
      <tr>
        <td class="desc">Ventes au détail (produits avec >50% droits indirects)<br><span class="ar">بيع بالتجزئة (منتجات بأكثر من 50% ضرائب غير مباشرة)</span></td>
        <td class="num">{_fmt_cell(data.ca_ventes_detail_droits_indirects)}</td>
      </tr>
      <tr>
        <td class="desc">Opérations de ventes en gros<br><span class="ar">عمليات البيع بالجملة</span></td>
        <td class="num">{_fmt_cell(data.ca_operations_ventes_gros)}</td>
      </tr>
      <tr>
        <td class="desc">Autres opérations ouvrant droit à la réfaction<br><span class="ar">عمليات أخرى تفتح الحق في الخصم</span></td>
        <td class="num">{_fmt_cell(data.ca_autres_operations_refaction)}</td>
      </tr>
      <tr>
        <td class="desc">Ventes ne bénéficiant pas de réfaction<br><span class="ar">مبيعات لا تستفيد من الخصم</span></td>
        <td class="num">{_fmt_cell(data.ca_ventes_sans_refaction)}</td>
      </tr>
      <tr class="total-row">
        <td class="desc"><strong>MONTANT TOTAL CA IMPOSABLE (1)</strong></td>
        <td class="num"><strong>{_fmt(calc.ca_imposable)}</strong></td>
      </tr>
    </tbody>
  </table>

  <div style="font-weight:bold; font-size:8.5pt; margin:8px 0 4px;">Opérations exonérées :</div>
  <table class="g11-table">
    <thead>
      <tr>
        <th class="desc">Nature de l'exonération</th>
        <th>Montant (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Producteurs de biens<br><span class="ar">منتجو البضائع</span></td>
        <td class="num">{_fmt_cell(data.ca_producteurs_biens)}</td>
      </tr>
      <tr>
        <td class="desc">Produits de large consommation<br><span class="ar">منتجات الاستهلاك الواسع</span></td>
        <td class="num">{_fmt_cell(data.ca_produits_large_consommation)}</td>
      </tr>
      <tr>
        <td class="desc">Exportations<br><span class="ar">الصادرات</span></td>
        <td class="num">{_fmt_cell(data.ca_exportations)}</td>
      </tr>
      <tr>
        <td class="desc">Lait cru<br><span class="ar">الحليب الخام</span></td>
        <td class="num">{_fmt_cell(data.ca_lait_cru)}</td>
      </tr>
      <tr>
        <td class="desc">Autres exonérations<br><span class="ar">إعفاءات أخرى</span></td>
        <td class="num">{_fmt_cell(data.ca_autres_exonerations)}</td>
      </tr>
      <tr class="total-row">
        <td class="desc"><strong>MONTANT TOTAL CA EXONÉRÉ (2)</strong></td>
        <td class="num"><strong>{_fmt(calc.ca_exonere)}</strong></td>
      </tr>
    </tbody>
  </table>

  <div class="highlight" style="text-align:right; font-size:10pt; padding:6px; border:2px solid #0A1628; margin-top:6px;">
    <strong>MONTANT TOTAL CA GLOBAL (1)+(2) = {_fmt(calc.ca_global)} DA</strong>
  </div>
</div>"""


def _resultat_fiscal_html(data: G11Data, calc: G11Calculations) -> str:
    """Table: Résultat fiscal."""
    return f"""<div class="section">
  <div class="section-title">2 — VOLET RELATIF AU RÉSULTAT FISCAL</div>
  <div class="section-title-ar">2 — الجزء المخصص للنتيجة الجبائية</div>
  <table class="g11-table">
    <thead>
      <tr>
        <th class="desc">Rubrique</th>
        <th>Montant (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="desc">Résultat comptable (bénéfice ou perte)<br><span class="ar">النتيجة المحاسبية (ربح أو خسارة)</span></td>
        <td class="num">{_fmt_cell(data.result_comptable_benefice)}</td>
      </tr>
      <tr>
        <td class="desc">Total réintégrations (Tableau 9)<br><span class="ar">مجموع إعادة الدمج (الجدول 9)</span></td>
        <td class="num">{_fmt_cell(data.total_reintegrations)}</td>
      </tr>
      <tr>
        <td class="desc">Total déductions (Tableau 9)<br><span class="ar">مجموع الخصومات (الجدول 9)</span></td>
        <td class="num">{_fmt_cell(data.total_deductions)}</td>
      </tr>
      <tr class="subtotal-row">
        <td class="desc"><strong>Résultat fiscal = Résultat comptable + Réintégrations - Déductions</strong></td>
        <td class="num"><strong>{_fmt(calc.resultat_fiscal)}</strong></td>
      </tr>
      <tr>
        <td class="desc">Dont revenus exonérés<br><span class="ar">في ذلك الإيرادات المعفاة</span></td>
        <td class="num">{_fmt_cell(data.revenus_exoneres)}</td>
      </tr>
      <tr class="total-row">
        <td class="desc"><strong>Revenu imposable = Résultat fiscal - Revenus exonérés</strong></td>
        <td class="num"><strong>{_fmt(calc.revenu_imposable)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _irg_liquidation_html(data: G11Data, calc: G11Calculations) -> str:
    """Section V — Liquidation de l'IRG/BIC."""
    rate_info = IRG_RATES.get(data.type_activite_irg, IRG_RATES["commerce_services"])

    # Build barème progressif breakdown
    bareme_rows = ""
    if data.use_barème_progressif and calc.revenu_imposable > 0:
        remaining = calc.revenu_imposable
        prev_limit = 0
        bracket_num = 1
        for limit, rate in IRG_BAREME_BIC:
            bracket_size = limit - prev_limit
            taxable = min(remaining, bracket_size)
            if taxable > 0:
                irg_bracket = taxable * rate
                limit_str = _fmt(limit) if limit != float("inf") else "..."
                bareme_rows += f"""<tr>
          <td>Tranche {bracket_num} : {_fmt(prev_limit)} — {limit_str}</td>
          <td class="num">{_fmt(taxable)}</td>
          <td class="num">{rate*100:.0f}%</td>
          <td class="num">{_fmt(irg_bracket)}</td>
        </tr>"""
                remaining -= taxable
                bracket_num += 1
            prev_limit = limit
            if remaining <= 0:
                break

    barème_option = ""
    if data.use_barème_progressif:
        barème_option = f"""<div style="margin:4px 0; font-size:8pt;">
        <strong>Barème progressif appliqué :</strong> Oui
        <table class="g11-table" style="margin-top:3px;">
          <thead><tr><th class="desc">Tranche</th><th>Base</th><th>Taux</th><th>IRG</th></tr></thead>
          <tbody>{bareme_rows}
          <tr class="subtotal-row"><td colspan="3"><strong>Total IRG barème progressif</strong></td><td class="num"><strong>{_fmt(calc.irg_bareme_progressif)}</strong></td></tr>
          </tbody>
        </table>
      </div>"""
    else:
        barème_option = f"""<div style="margin:4px 0; font-size:8pt;">
        <strong>Barème progressif appliqué :</strong> Non — Taux proportionnel de {calc.irg_taux_applique*100:.0f}%
      </div>"""

    return f"""<div class="section" style="page-break-before:always;">
  <div class="section-title">V — DÉTERMINATION DU SOLDE DE LIQUIDATION / EXCÉDENT DE VERSEMENT</div>
  <div class="section-title-ar">V — تحديد رصيد التسوية / فائض الدفع</div>

  <div class="irg-box">
    <div class="title">IRG SUR LES BÉNÉFICES INDUSTRIELS ET COMMERCIAUX (BIC)</div>
    <table>
      <tr>
        <td class="field-label">Type d'activité :</td>
        <td class="field-value">{rate_info['label_fr']} ({rate_info['label_ar']})</td>
      </tr>
      <tr>
        <td class="field-label">Taux applicable :</td>
        <td class="field-value">{calc.irg_taux_applique*100:.0f}%</td>
      </tr>
      <tr>
        <td class="field-label">Revenu imposable :</td>
        <td class="field-value">{_fmt(calc.revenu_imposable)} DA</td>
      </tr>
      <tr>
        <td class="field-label">IRG au taux proportionnel ({calc.irg_taux_applique*100:.0f}%) :</td>
        <td class="field-value">{_fmt(calc.irg_taux_proportionnel)} DA</td>
      </tr>
    </table>

    {barème_option}

    <div style="border-top:2px solid #0A1628; margin-top:8px; padding-top:6px;">
      <table>
        <tr>
          <td class="field-label">IRG DÛ :</td>
          <td class="field-value" style="font-size:11pt;"><strong>{_fmt(calc.irg_du)} DA</strong></td>
        </tr>
      </table>
    </div>
  </div>

  <div class="irg-box" style="margin-top:8px;">
    <div class="title">SOLDE DE LIQUIDATION</div>
    <table>
      <tr>
        <td class="field-label">Impôt dû (IRG) :</td>
        <td class="field-value">{_fmt(calc.irg_du)} DA</td>
      </tr>
      <tr>
        <td class="field-label">1er acompte :</td>
        <td class="field-value">{_fmt_cell(data.acompte_1)} DA</td>
      </tr>
      <tr>
        <td class="field-label">2ème acompte :</td>
        <td class="field-value">{_fmt_cell(data.acompte_2)} DA</td>
      </tr>
      <tr>
        <td class="field-label">Total acomptes versés :</td>
        <td class="field-value">{_fmt(calc.total_acomptes)} DA</td>
      </tr>
      <tr class="total-line">
        <td class="field-label">Solde de liquidation à payer :</td>
        <td class="field-value">{_fmt(calc.solde_liquidation)} DA</td>
      </tr>
      <tr>
        <td class="field-label">Excédent de versement :</td>
        <td class="field-value">{_fmt(calc.excedent_versement)} DA</td>
      </tr>
    </table>
  </div>

  <div class="note" style="margin-top:8px; padding:5px; border:1px solid #ccc;">
    <strong>PRÉCISIONS :</strong> Le solde de liquidation doit être acquitté au plus tard le 20 Mai via le bordereau G50.
    Les acomptes d'IRG sont versés mensuellement ou trimestriellement selon le régime du contribuable.
  </div>
</div>"""


def _signature_html(data: G11Data) -> str:
    """Signature block and administrative frame."""
    lieu = _esc(data.lieu_declaration) or "..........................."
    date = _esc(data.date_declaration) or "....../....../......"
    beneficiaire = _esc(data.beneficiaire) or "..........................."

    return f"""<div class="section" style="margin-top:20px;">
  <div style="display:flex; justify-content:space-between;">
    <div style="width:45%;">
      <p style="font-size:9pt;">Fait à <strong>{lieu}</strong> le <strong>{date}</strong></p>
      <div style="margin-top:30px; text-align:center; font-size:9pt;">
        <strong>Signature du déclarant</strong><br>
        <div style="margin-top:40px; border-top:1px solid #333; width:60%; margin-left:auto; margin-right:auto; padding-top:5px;">
          Cachet et signature
        </div>
      </div>
    </div>
    <div class="admin-box">
      <strong>Cadre réservé à l'administration</strong><br><br>
      <div style="border:1px solid #ccc; height:80px; margin:5px;"></div>
      <div style="font-size:7pt;">Visa et observations</div>
    </div>
  </div>
</div>"""


def _legal_references_html() -> str:
    """Legal references footer."""
    return f"""<div class="section" style="margin-top:15px; page-break-inside:avoid;">
  <div style="background:#f8f8f0; padding:6px; border:1px solid #ccc; font-size:7.5pt;">
    <strong>RÉFÉRENCES LÉGALES :</strong><br>
    • Articles 18 et 224 du Code des Impôts Directs et Taxes Assimilées (CIDTA)<br>
    • Article 83 du CIDTA — obligation de déclaration annuelle des bénéfices professionnels<br>
    • Article 197 du CIDTA — obligations déclaratives des comptables/experts<br>
    • Taux d'IRG : 19% (production), 23% (BTP/tourisme), 26% (commerce/services) — Art. 18 CIDTA<br>
    • Barème progressif applicable sur option — Art. 18 alinéa 2 du CIDTA<br>
    • Dépôt obligatoire au plus tard le 30 Avril — Art. 83 du CIDTA<br>
    • Solde de liquidation payable via G50 au plus tard le 20 Mai
  </div>
</div>"""


# ── Main Generator ────────────────────────────────────────────────────────────

def generate_g11(data: G11Data) -> str:
    """Generate complete G11 BIC annual declaration form as HTML."""
    calc = calculate_g11(data)

    html = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G11 BIC — Déclaration des Bénéfices Professionnels {data.annee}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_dgi_hierarchy_html(data)}
{_section1_identification_html(data)}
{_section2_associes_html(data)}
{_section3_comptable_html(data)}

{_ca_imposable_table_html(data, calc)}

{_resultat_fiscal_html(data, calc)}

{_irg_liquidation_html(data, calc)}

{_signature_html(data)}

{_legal_references_html()}

</body>
</html>"""

    return html


def generate_g11_html(data: G11Data) -> str:
    """Alias for generate_g11."""
    return generate_g11(data)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    # Sample data for demonstration
    sample = G11Data(
        wilaya="32 - El Bayadh",
        diw="DIW D'EL BAYADH",
        structure="SARL",
        inspection="Inspection des Impôts d'El Bayadh Centre",
        recette="Recette des Impôts d'El Bayadh Centre",
        annee=2026,
        nif="1234567890",
        nin="199603061234567",
        nom_prenoms="SARL TECH SOLUTIONS EURL",
        date_lieu_naissance="06/03/1996 à El Bayadh",
        nature_activites="Prestation de services informatiques et conseil en technologie",
        code_activite="6201",
        registre_commerce="01/12/2024-0000123456",
        comptes_bancaires="00799999001234567890 — BNA El Bayadh",
        adresse_siege_1er_janvier="123 Rue Didouche Mourad, El Bayadh Centre",
        telephone="0555081718",
        fax="",
        email="contact@tech-solutions.dz",
        adresse_etablissements_secondaires="",
        # CA
        ca_ventes_gros_droits_indirects=0,
        ca_ventes_detail_droits_indirects=0,
        ca_operations_ventes_gros=0,
        ca_autres_operations_refaction=0,
        ca_ventes_sans_refaction=0,
        # Exonéré
        ca_producteurs_biens=0,
        ca_produits_large_consommation=0,
        ca_exportations=0,
        ca_lait_cru=0,
        ca_autres_exonerations=0,
        # Résultat fiscal
        result_comptable_benefice=8_500_000,
        total_reintegrations=250_000,
        total_deductions=150_000,
        revenus_exoneres=0,
        # IRG
        type_activite_irg="commerce_services",
        use_barème_progressif=False,
        # Acomptes
        acompte_1=500_000,
        acompte_2=500_000,
        # Signature
        lieu_declaration="El Bayadh",
        date_declaration="15/04/2026",
        beneficiaire="Ahmed Benali",
        # Associés
        associes=[
            Associe(nom_prenoms="Ahmed Benali", pourcentage=60.0,
                    adresse_domicile_fiscal="123 Rue Didouche Mourad, El Bayadh", nif="9876543210"),
            Associe(nom_prenoms="Fatima Zohra Benali", pourcentage=40.0,
                    adresse_domicile_fiscal="456 Rue Emir Abdelkader, El Bayadh", nif="9876543211"),
        ],
        # Comptable
        comptable_nom="Mohamed Saidi, Expert Comptable",
        comptable_adresse="789 Avenue de la République, El Bayadh",
        comptable_nif="1122334455",
        comptable_personnel_salarie=True,
    )

    # Activate progressive barème for demo
    if "--progressif" in sys.argv:
        sample.use_barème_progressif = True

    # Generate CA for services
    sample.ca_ventes_sans_refaction = 48_000_000

    calc = calculate_g11(sample)
    print(f"=== G11 BIC — Exercice {sample.annee} ===")
    print(f"CA Imposable:      {_fmt(calc.ca_imposable)} DA")
    print(f"CA Exonéré:        {_fmt(calc.ca_exonere)} DA")
    print(f"CA Global:         {_fmt(calc.ca_global)} DA")
    print(f"Résultat fiscal:   {_fmt(calc.resultat_fiscal)} DA")
    print(f"Revenu imposable:  {_fmt(calc.revenu_imposable)} DA")
    print(f"IRG dû ({calc.irg_taux_applique*100:.0f}%): {_fmt(calc.irg_du)} DA")
    print(f"Acomptes:          {_fmt(calc.total_acomptes)} DA")
    print(f"Solde liquidation: {_fmt(calc.solde_liquidation)} DA")

    if "--html" in sys.argv:
        html = generate_g11(sample)
        out = "g11_bic_official.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out}")
