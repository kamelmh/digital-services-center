"""G50 Official Form Generator — matches DGI printable forms exactly.

Generates G50 (Série G N°50) multi-tax monthly declaration forms
matching the official Algerian tax forms from DGI (Direction Générale des Impôts).

Covers:
- Table 1: TAP (supprimée depuis LF 2024)
- Table 2: Acomptes IBS
- Table 3: IRG Salaires et autres retenues à la source
- Table 4: Droits et Taxes Indirects
- Table 5: Chiffre d'affaires / Droit de Timbre
- Table 6: Taxe sur la Valeur Ajoutée (TVA)
- Récapitulation + Signatures

Usage:
    from g50_generator import generate_g50
    html = generate_g50({
        "nif": "1234567890",
        "business_name": "SARL Exemple",
        "month": 6,
        "year": 2026,
        "tva_collectee_19": 190_000,
        "tva_deductible_19": 114_000,
    })
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass, field
from datetime import datetime


def _esc(value: object, default: str = "") -> str:
    """HTML-escape a value for safe rendering."""
    if value is None:
        return default
    return _html_mod.escape(str(value))
from typing import Optional


# ── Constants ─────────────────────────────────────────────────────────────────

MONTHS_FR = [
    "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]

MONTHS_AR = [
    "", "جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان",
    "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]

TVA_RATE_STANDARD = 0.19
TVA_RATE_REDUIT = 0.09
TVA_RATE_ZERO = 0.00

# IRG Brackets 2025 (annual)
IRG_BRACKETS = [
    (180_000, 0.00),
    (360_000, 0.20),
    (720_000, 0.30),
    (float("inf"), 0.35),
]

# IBS Acompte months
IBS_ACOMPTE_MONTHS = [3, 6, 11]  # mars, juin, nov


def calculate_irg_mensuel(salaire_annuel: float) -> float:
    """Calculate monthly IRG from annual salary (barème progressif)."""
    monthly = salaire_annuel / 12
    remaining = monthly
    irg = 0
    prev_limit = 0
    for limit, rate in IRG_BRACKETS:
        bracket_size = (limit - prev_limit) / 12
        taxable = min(remaining, bracket_size)
        irg += taxable * rate
        remaining -= taxable
        prev_limit = limit
        if remaining <= 0:
            break
    return round(irg)


def calculate_irg_annuel(salaire_annuel: float) -> float:
    """Calculate annual IRG."""
    return calculate_irg_mensuel(salaire_annuel) * 12


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class G50Data:
    """Input data for G50 form generation."""
    # DGI hierarchy
    wilaya: str = ""
    inspection: str = ""
    recette: str = ""
    mois: str = ""
    annee: str = ""
    service_cdi: str = ""

    # Identification
    nif: str = ""
    code_activite: str = ""
    article_imposition: str = ""
    nom_prenom: str = ""
    activite: str = ""
    adresse: str = ""
    commune: str = ""

    # Period
    month: int = datetime.now().month
    year: int = datetime.now().year

    # Table 1 — TAP (supprimée LF2024)
    tap_montant: float = 0

    # Table 2 — Acomptes IBS
    ibs_acompte: float = 0

    # Table 3 — IRG / IBS retenues à la source
    irg_salaires_revenus: float = 0
    irg_salaires_irg: float = 0
    irg_location_commerciale_revenus: float = 0
    irg_location_commerciale_irg: float = 0
    irg_location_salles_revenus: float = 0
    irg_location_salles_irg: float = 0
    irg_bons_caisse_revenus: float = 0
    irg_bons_caisse_irg: float = 0
    irg_autres_ras_revenus: float = 0
    irg_autres_ras_irg: float = 0
    ibs_prestations_revenus: float = 0
    ibs_prestations_irg: float = 0
    ibs_autres_ras_revenus: float = 0
    ibs_autres_ras_irg: float = 0

    # Table 4 — Droits et Taxes Indirects
    tic_recharges_base: float = 0
    tic_recharges_irg: float = 0
    tic_tv_base: float = 0
    tic_tv_irg: float = 0

    # Table 5 — Chiffre d'affaires / Droit de Timbre
    timbre_formation_base: float = 0
    timbre_formation_montant: float = 0
    timbre_apprentissage_base: float = 0
    timbre_apprentissage_montant: float = 0
    timbre_vehicules_neufs_base: float = 0
    timbre_vehicules_neufs_montant: float = 0
    timbre_concessionnaires_base: float = 0
    timbre_concessionnaires_montant: float = 0
    timbre_habitation_base: float = 0
    timbre_habitation_montant: float = 0
    timbre_pneus_base: float = 0
    timbre_pneus_montant: float = 0
    timbre_jeux_base: float = 0
    timbre_jeux_montant: float = 0
    timbre_huiles_base: float = 0
    timbre_huiles_montant: float = 0
    timbre_mobile_base: float = 0
    timbre_mobile_montant: float = 0
    timbre_medicaments_base: float = 0
    timbre_medicaments_montant: float = 0
    timbre_publicite_base: float = 0
    timbre_publicite_montant: float = 0
    timbre_boissons_base: float = 0
    timbre_boissons_montant: float = 0
    timbre_vp_base: float = 0
    timbre_vp_montant: float = 0
    timbre_carburant_base: float = 0
    timbre_carburant_montant: float = 0
    timbre_electricite_base: float = 0
    timbre_electricite_montant: float = 0
    timbre_rc_base: float = 0
    timbre_rc_montant: float = 0
    timbre_cereales_base: float = 0
    timbre_cereales_montant: float = 0
    timbre_tourisme_base: float = 0
    timbre_tourisme_montant: float = 0
    timbre_radiodiffusion_base: float = 0
    timbre_radiodiffusion_montant: float = 0
    timbre_energie_base: float = 0
    timbre_energie_montant: float = 0
    timbre_pub_contrat_base: float = 0
    timbre_pub_contrat_montant: float = 0

    # TVA — Chiffres d'affaires imposables
    # 9% Taux réduit
    tva_9_biens_total: float = 0
    tva_9_biens_exonere: float = 0
    tva_9_prestations_total: float = 0
    tva_9_prestations_exonere: float = 0
    tva_9_immobilier_total: float = 0
    tva_9_immobilier_exonere: float = 0
    tva_9_medical_total: float = 0
    tva_9_medical_exonere: float = 0
    tva_9_commission_total: float = 0
    tva_9_commission_exonere: float = 0
    tva_9_energie_total: float = 0
    tva_9_energie_exonere: float = 0
    tva_9_autres_total: float = 0
    tva_9_autres_exonere: float = 0

    # 19% Taux normal
    tva_19_production_total: float = 0
    tva_19_production_exonere: float = 0
    tva_19_revente_total: float = 0
    tva_19_revente_exonere: float = 0
    tva_19_travaux_total: float = 0
    tva_19_travaux_exonere: float = 0
    tva_19_liberales_total: float = 0
    tva_19_liberales_exonere: float = 0
    tva_19_banques_total: float = 0
    tva_19_banques_exonere: float = 0
    tva_19_telephone_total: float = 0
    tva_19_telephone_exonere: float = 0
    tva_19_autres_serv_total: float = 0
    tva_19_autres_serv_exonere: float = 0
    tva_19_boissons_total: float = 0
    tva_19_boissons_exonere: float = 0
    tva_19_prod_biens_total: float = 0
    tva_19_prod_biens_exonere: float = 0
    tva_19_revente_etat_total: float = 0
    tva_19_revente_etat_exonere: float = 0
    tva_19_tabacs_total: float = 0
    tva_19_tabacs_exonere: float = 0
    tva_19_spectacles_total: float = 0
    tva_19_spectacles_exonere: float = 0
    tva_19_autres_art21_total: float = 0
    tva_19_autres_art21_exonere: float = 0
    tva_19_consommation_total: float = 0
    tva_19_consommation_exonere: float = 0

    # Non imposables (Art. 9 CTCA)
    tva_ni_petrole_total: float = 0
    tva_ni_petrole_exonere: float = 0
    tva_ni_premiere_necessite_total: float = 0
    tva_ni_premiere_necessite_exonere: float = 0
    tva_ni_credit_bail_total: float = 0
    tva_ni_credit_bail_exonere: float = 0
    tva_ni_reassurance_total: float = 0
    tva_ni_reassurance_exonere: float = 0
    tva_ni_assurances_total: float = 0
    tva_ni_assurances_exonere: float = 0
    tva_ni_intragroupe_total: float = 0
    tva_ni_intragroupe_exonere: float = 0
    tva_ni_exportation_total: float = 0
    tva_ni_exportation_exonere: float = 0
    tva_ni_medicaments_total: float = 0
    tva_ni_medicaments_exonere: float = 0
    tva_ni_autres_ni_total: float = 0
    tva_ni_autres_ni_exonere: float = 0

    # Exonéré
    tva_exo_petrole_total: float = 0
    tva_exo_petrole_exonere: float = 0
    tva_exo_andi_total: float = 0
    tva_exo_andi_exonere: float = 0
    tva_exo_ansej_total: float = 0
    tva_exo_ansej_exonere: float = 0
    tva_exo_angem_total: float = 0
    tva_exo_angem_exonere: float = 0
    tva_exo_cnac_total: float = 0
    tva_exo_cnac_exonere: float = 0
    tva_exo_exportation_total: float = 0
    tva_exo_exportation_exonere: float = 0

    # TVA — Déductions
    tva_precompte_anterieur: float = 0
    tva_achats_matieres: float = 0
    tva_achats_amortissables: float = 0
    tva_regularisation_prorata: float = 0
    tva_factures_annulees: float = 0
    tva_autres_deductions: float = 0

    # TVA — Régularisations
    tva_regularisation_prorata_plus: float = 0
    tva_regularisation_acomptes: float = 0
    tva_reversement_deduction: float = 0
    tva_a_rappeler: float = 0
    tva_auto_liquidee: float = 0

    # Payment section
    cheque_banque_numero: str = ""
    cheque_banque_date: str = ""
    cheque_banque_agence: str = ""
    cheque_postal_numero: str = ""
    numeraire: float = 0
    quittance_numero: str = ""

    # Metadata
    beneficiaire: str = ""


@dataclass
class G50Result:
    """Calculated G50 results."""
    # Table 2 — IBS
    ibs_acompte: float
    ibs_applicable: bool

    # Table 3 — IRG / RAS
    irg_salaires: float
    irg_location_commerciale: float
    irg_location_salles: float
    irg_bons_caisse: float
    irg_autres_ras: float
    ibs_prestations: float
    ibs_autres_ras: float
    total_table3: float

    # Table 4 — TIC
    tic_recharges: float
    tic_tv: float
    total_table4: float

    # Table 5 — Timbre / Taxes
    total_table5: float

    # TVA
    tva_9_total: float
    tva_9_imposable: float
    tva_19_total: float
    tva_19_imposable: float
    tva_ni_total: float
    tva_ni_imposable: float
    tva_exo_total: float
    tva_exo_imposable: float
    tva_ca_total: float
    tva_ca_imposable_total: float
    tva_deductions_total: float
    tva_a_payer: float
    tva_precompte_report: float

    # Global
    total_a_payer: float
    total_a_payer_label: str


def calculate_g50(data: G50Data) -> G50Result:
    """Calculate G50 totals from input data."""
    # Table 2 — IBS
    ibs_applicable = data.month in IBS_ACOMPTE_MONTHS
    ibs_acompte = data.ibs_acompte if ibs_applicable else 0

    # Table 3 — IRG / IBS retenues
    irg_salaires = data.irg_salaires_irg
    irg_location_commerciale = data.irg_location_commerciale_irg
    irg_location_salles = data.irg_location_salles_irg
    irg_bons_caisse = data.irg_bons_caisse_irg
    irg_autres_ras = data.irg_autres_ras_irg
    ibs_prestations = data.ibs_prestations_irg
    ibs_autres_ras = data.ibs_autres_ras_irg
    total_table3 = (irg_salaires + irg_location_commerciale + irg_location_salles +
                    irg_bons_caisse + irg_autres_ras + ibs_prestations + ibs_autres_ras)

    # Table 4 — TIC
    tic_recharges = data.tic_recharges_irg
    tic_tv = data.tic_tv_irg
    total_table4 = tic_recharges + tic_tv

    # Table 5 — Timbre / Taxes
    total_table5 = (
        data.timbre_formation_montant + data.timbre_apprentissage_montant +
        data.timbre_vehicules_neufs_montant + data.timbre_concessionnaires_montant +
        data.timbre_habitation_montant + data.timbre_pneus_montant +
        data.timbre_jeux_montant + data.timbre_huiles_montant +
        data.timbre_mobile_montant + data.timbre_medicaments_montant +
        data.timbre_publicite_montant + data.timbre_boissons_montant +
        data.timbre_vp_montant + data.timbre_carburant_montant +
        data.timbre_electricite_montant + data.timbre_rc_montant +
        data.timbre_cereales_montant + data.timbre_tourisme_montant +
        data.timbre_radiodiffusion_montant + data.timbre_energie_montant +
        data.timbre_pub_contrat_montant
    )

    # TVA — 9% totals
    tva_9_total = (
        data.tva_9_biens_total + data.tva_9_prestations_total +
        data.tva_9_immobilier_total + data.tva_9_medical_total +
        data.tva_9_commission_total + data.tva_9_energie_total +
        data.tva_9_autres_total
    )
    tva_9_exonere = (
        data.tva_9_biens_exonere + data.tva_9_prestations_exonere +
        data.tva_9_immobilier_exonere + data.tva_9_medical_exonere +
        data.tva_9_commission_exonere + data.tva_9_energie_exonere +
        data.tva_9_autres_exonere
    )
    tva_9_imposable = tva_9_total - tva_9_exonere

    # TVA — 19% totals
    tva_19_total = (
        data.tva_19_production_total + data.tva_19_revente_total +
        data.tva_19_travaux_total + data.tva_19_liberales_total +
        data.tva_19_banques_total + data.tva_19_telephone_total +
        data.tva_19_autres_serv_total + data.tva_19_boissons_total +
        data.tva_19_prod_biens_total + data.tva_19_revente_etat_total +
        data.tva_19_tabacs_total + data.tva_19_spectacles_total +
        data.tva_19_autres_art21_total + data.tva_19_consommation_total
    )
    tva_19_exonere = (
        data.tva_19_production_exonere + data.tva_19_revente_exonere +
        data.tva_19_travaux_exonere + data.tva_19_liberales_exonere +
        data.tva_19_banques_exonere + data.tva_19_telephone_exonere +
        data.tva_19_autres_serv_exonere + data.tva_19_boissons_exonere +
        data.tva_19_prod_biens_exonere + data.tva_19_revente_etat_exonere +
        data.tva_19_tabacs_exonere + data.tva_19_spectacles_exonere +
        data.tva_19_autres_art21_exonere + data.tva_19_consommation_exonere
    )
    tva_19_imposable = tva_19_total - tva_19_exonere

    # TVA — Non imposables
    tva_ni_total = (
        data.tva_ni_petrole_total + data.tva_ni_premiere_necessite_total +
        data.tva_ni_credit_bail_total + data.tva_ni_reassurance_total +
        data.tva_ni_assurances_total + data.tva_ni_intragroupe_total +
        data.tva_ni_exportation_total + data.tva_ni_medicaments_total +
        data.tva_ni_autres_ni_total
    )
    tva_ni_exonere = (
        data.tva_ni_petrole_exonere + data.tva_ni_premiere_necessite_exonere +
        data.tva_ni_credit_bail_exonere + data.tva_ni_reassurance_exonere +
        data.tva_ni_assurances_exonere + data.tva_ni_intragroupe_exonere +
        data.tva_ni_exportation_exonere + data.tva_ni_medicaments_exonere +
        data.tva_ni_autres_ni_exonere
    )
    tva_ni_imposable = tva_ni_total - tva_ni_exonere

    # TVA — Exonéré
    tva_exo_total = (
        data.tva_exo_petrole_total + data.tva_exo_andi_total +
        data.tva_exo_ansej_total + data.tva_exo_angem_total +
        data.tva_exo_cnac_total + data.tva_exo_exportation_total
    )
    tva_exo_exonere = (
        data.tva_exo_petrole_exonere + data.tva_exo_andi_exonere +
        data.tva_exo_ansej_exonere + data.tva_exo_angem_exonere +
        data.tva_exo_cnac_exonere + data.tva_exo_exportation_exonere
    )
    tva_exo_imposable = tva_exo_total - tva_exo_exonere

    # TVA — CA totals
    tva_ca_total = tva_9_total + tva_19_total + tva_ni_total + tva_exo_total
    tva_ca_imposable_total = tva_9_imposable + tva_19_imposable + tva_ni_imposable + tva_exo_imposable

    # TVA — Déductions
    tva_deductions_total = (
        data.tva_precompte_anterieur + data.tva_achats_matieres +
        data.tva_achats_amortissables + data.tva_regularisation_prorata +
        data.tva_factures_annulees + data.tva_autres_deductions
    )

    # TVA — Calcul
    tva_collectee_19 = tva_19_imposable * TVA_RATE_STANDARD
    tva_collectee_9 = tva_9_imposable * TVA_RATE_REDUIT
    tva_collectee = tva_collectee_19 + tva_collectee_9

    tva_deductible = tva_deductions_total
    tva_a_payer_brut = tva_collectee - tva_deductible
    tva_regularisation_plus = data.tva_regularisation_prorata_plus
    tva_regularisation_acomptes = data.tva_regularisation_acomptes
    tva_reversement = data.tva_reversement_deduction
    tva_a_rappeler = data.tva_a_rappeler
    tva_total_c = tva_a_payer_brut + tva_regularisation_plus + tva_regularisation_acomptes + tva_reversement + tva_a_rappeler

    tva_deductions_b = tva_deductions_total
    if tva_total_c >= tva_deductions_b:
        tva_a_payer = tva_total_c - tva_deductions_b
        tva_precompte_report = 0
    else:
        tva_a_payer = 0
        tva_precompte_report = tva_deductions_b - tva_total_c

    tva_auto_liquidee = data.tva_auto_liquidee

    # Global total
    total = (
        data.tap_montant + ibs_acompte + total_table3 +
        total_table4 + total_table5 + tva_a_payer + tva_auto_liquidee
    )

    total_label = "Montant total à payer" if total > 0 else "Aucun paiement requis"

    return G50Result(
        ibs_acompte=ibs_acompte,
        ibs_applicable=ibs_applicable,
        irg_salaires=irg_salaires,
        irg_location_commerciale=irg_location_commerciale,
        irg_location_salles=irg_location_salles,
        irg_bons_caisse=irg_bons_caisse,
        irg_autres_ras=irg_autres_ras,
        ibs_prestations=ibs_prestations,
        ibs_autres_ras=ibs_autres_ras,
        total_table3=total_table3,
        tic_recharges=tic_recharges,
        tic_tv=tic_tv,
        total_table4=total_table4,
        total_table5=total_table5,
        tva_9_total=tva_9_total,
        tva_9_imposable=tva_9_imposable,
        tva_19_total=tva_19_total,
        tva_19_imposable=tva_19_imposable,
        tva_ni_total=tva_ni_total,
        tva_ni_imposable=tva_ni_imposable,
        tva_exo_total=tva_exo_total,
        tva_exo_imposable=tva_exo_imposable,
        tva_ca_total=tva_ca_total,
        tva_ca_imposable_total=tva_ca_imposable_total,
        tva_deductions_total=tva_deductions_total,
        tva_a_payer=tva_a_payer,
        tva_precompte_report=tva_precompte_report,
        total_a_payer=total,
        total_a_payer_label=total_label,
    )


def _fmt(n: float) -> str:
    """Format number with thousand separators."""
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


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css() -> str:
    """Complete CSS for official G50 form styling."""
    return """<style>
  @page { size: A4; margin: 10mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 9pt; color: #1a1a1a; margin: 0; padding: 10px;
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
  .header h1 { font-size: 13pt; margin: 4px 0; color: #fff; }
  .header .serie { font-size: 10pt; font-weight: bold; color: #D4AF37; margin: 2px 0; }
  .header .subtitle { font-size: 8.5pt; color: #ccc; margin: 1px 0; }
  .header .deadline { font-size: 8pt; font-weight: bold; margin-top: 5px; padding: 3px 6px; border: 1px solid #D4AF37; background: rgba(212,175,55,0.1); color: #D4AF37; }

  /* DGI Hierarchy */
  .dgi-hierarchy { margin: 6px 0; }
  .dgi-hierarchy table { width: 100%; border-collapse: collapse; }
  .dgi-hierarchy td { padding: 2px 5px; font-size: 8pt; border: none; }
  .dgi-hierarchy .dgi-label { font-weight: bold; width: 35%; }
  .dgi-hierarchy .dgi-value { border-bottom: 1px dotted #999; width: 65%; }

  /* Identification */
  .identification { margin: 6px 0; border: 1px solid #0A1628; padding: 6px; }
  .identification table { width: 100%; border-collapse: collapse; }
  .identification td { padding: 2px 5px; font-size: 8.5pt; }
  .identification .field-label { font-weight: bold; width: 30%; }
  .identification .field-value { border-bottom: 1px dotted #999; width: 70%; }

  /* Section titles */
  .section-title {
    font-size: 9pt; font-weight: bold; color: #0A1628;
    border-bottom: 2px solid #0A1628; padding-bottom: 2px; margin: 8px 0 4px;
    background: linear-gradient(90deg, #0A1628, #162d54); color: #fff;
    padding: 3px 6px;
  }
  .section-title-ar { font-size: 8pt; color: #666; text-align: right; direction: rtl; margin-bottom: 4px; }

  /* Tables */
  .g50-table { width: 100%; border-collapse: collapse; margin: 4px 0; }
  .g50-table th, .g50-table td {
    border: 1px solid #333; padding: 3px 5px; font-size: 8pt; text-align: center;
  }
  .g50-table th { background: #e8e8e8; font-weight: bold; font-size: 8pt; }
  .g50-table .code { width: 10%; text-align: left; font-size: 7.5pt; color: #555; }
  .g50-table .desc { text-align: left; width: 35%; }
  .g50-table .desc .ar { font-size: 7pt; color: #888; direction: rtl; }
  .g50-table .num { font-family: 'Courier New', monospace; font-size: 8pt; width: 15%; }
  .g50-table .total-row { background: #f0f0f0; font-weight: bold; }
  .g50-table .subtotal-row { background: #f8f8f0; font-weight: bold; }
  .g50-table .note { font-size: 7pt; color: #888; font-style: italic; font-weight: normal; }

  /* Notes */
  .note { font-size: 7.5pt; color: #666; font-style: italic; margin: 2px 0; }

  /* Récapitulation */
  .recap { margin: 8px 0; }
  .recap table { width: 100%; border-collapse: collapse; }
  .recap th, .recap td { border: 1px solid #333; padding: 3px 5px; font-size: 8pt; }
  .recap th { background: #e8e8e8; font-weight: bold; }
  .recap .total-line { background: #0A1628; color: #fff; font-weight: bold; font-size: 10pt; }

  /* Signature */
  .signature-block { display: flex; justify-content: space-between; margin: 12px 0; }
  .sig-box { width: 30%; text-align: center; font-size: 8pt; border-top: 1px solid #333; padding-top: 4px; }
  .sig-box .title { font-weight: bold; margin-bottom: 5px; }

  /* Payment */
  .payment-section { margin: 8px 0; border: 1px solid #ccc; padding: 6px; }
  .payment-section table { width: 100%; border-collapse: collapse; }
  .payment-section td { padding: 2px 5px; font-size: 8pt; }
  .payment-section .field-label { font-weight: bold; width: 35%; }
  .payment-section .field-value { border-bottom: 1px dotted #999; width: 65%; }

  /* Attestation */
  .attestation { font-size: 8pt; font-style: italic; margin: 8px 0; padding: 5px; border: 1px solid #ccc; text-align: center; }

  /* Highlight */
  .highlight { background: #fffde7; font-weight: bold; }
  .negative { color: #c62828; }
  .positive { color: #2e7d32; }
  .amount { font-family: 'Courier New', monospace; font-weight: bold; }

  /* Print */
  @media print {
    body { padding: 0; font-size: 8pt; }
    .no-print { display: none; }
    .header { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .section-title { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .recap .total-line { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>"""


# ── HTML Helpers ──────────────────────────────────────────────────────────────

def _header_html(data: G50Data) -> str:
    """Official DGI header for G50."""
    return f"""<div class="header">
  <div class="republique">République Algérienne Démocratique et Populaire</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h1>IMPÔTS ET TAXES PERÇUS AU COMPTANT OU PAR VOIE DE RETENUE À LA SOURCE</h1>
  <div class="serie">Série G N°50 — {data.year}</div>
  <div class="subtitle">DÉCLARATION TENANT LIEU DE BORDEREAU — AVIS DE VERSEMENT</div>
  <div class="deadline">La présente déclaration doit être déposée à la recette des impôts dans les VINGT PREMIERS JOURS DU MOIS</div>
</div>"""


def _dgi_hierarchy_html(data: G50Data) -> str:
    """DGI institutional hierarchy fields."""
    return f"""<div class="dgi-hierarchy">
  <table>
    <tr>
      <td class="dgi-label">Wilaya de :</td>
      <td class="dgi-value">{_esc(data.wilaya) or _blank(40)}</td>
      <td class="dgi-label">Mois :</td>
      <td class="dgi-value">{MONTHS_FR[data.month] if data.month else _blank(15)}</td>
    </tr>
    <tr>
      <td class="dgi-label">Inspection des impôts de :</td>
      <td class="dgi-value">{_esc(data.inspection) or _blank(40)}</td>
      <td class="dgi-label">Année :</td>
      <td class="dgi-value">{data.year or _blank(15)}</td>
    </tr>
    <tr>
      <td class="dgi-label">Recette des impôts de :</td>
      <td class="dgi-value">{_esc(data.recette) or _blank(40)}</td>
      <td class="dgi-label">Service CDI :</td>
      <td class="dgi-value">{_esc(data.service_cdi) or _blank(15)}</td>
    </tr>
  </table>
</div>"""


def _identification_html(data: G50Data) -> str:
    """Identification section."""
    return f"""<div class="identification">
  <table>
    <tr>
      <td class="field-label">NIF :</td>
      <td class="field-value">{_esc(data.nif) or _blank(25)}</td>
      <td class="field-label">Code Activité :</td>
      <td class="field-value">{_esc(data.code_activite) or _blank(20)}</td>
    </tr>
    <tr>
      <td class="field-label">Article d'imposition :</td>
      <td class="field-value" colspan="3">{_esc(data.article_imposition) or _blank(50)}</td>
    </tr>
    <tr>
      <td class="field-label">M. / Nom et Prénom / Raison sociale :</td>
      <td class="field-value" colspan="3">{_esc(data.nom_prenom) or _blank(50)}</td>
    </tr>
    <tr>
      <td class="field-label">Activité / Profession :</td>
      <td class="field-value" colspan="3">{_esc(data.activite) or _blank(50)}</td>
    </tr>
    <tr>
      <td class="field-label">Adresse :</td>
      <td class="field-value" colspan="3">{_esc(data.adresse) or _blank(50)}</td>
    </tr>
    <tr>
      <td class="field-label">Commune :</td>
      <td class="field-value" colspan="3">{_esc(data.commune) or _blank(50)}</td>
    </tr>
  </table>
</div>"""


def _table1_tap_html(data: G50Data) -> str:
    """Table 1 — TAP (supprimée depuis LF 2024)."""
    return f"""<div class="section">
  <div class="section-title">TABLEAU 1 — IMPÔT SUR L'ACTIVITÉ PROFESSIONNELLE (TAP) / الضرائب على النشاط المهني</div>
  <div class="section-title-ar">TABLEAU 1 — TAP</div>
  <table class="g50-table">
    <thead>
      <tr>
        <th class="code">Code</th>
        <th class="desc">Nature de la taxe</th>
        <th>Base d'imposition</th>
        <th>Tarif</th>
        <th>Montant à payer (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="code">C/500026/A</td>
        <td class="desc">Taxe sur l'activité professionnelle (TAP)<br><span class="ar">الضريبة على النشاط المهني</span></td>
        <td class="num">{_fmt_cell(data.tap_montant)}</td>
        <td class="num">—</td>
        <td class="num">{_fmt_cell(data.tap_montant)}</td>
      </tr>
      <tr>
        <td colspan="5" class="note" style="text-align:center;">⚠ TAP supprimée depuis la Loi de Finances 2024 — Article 8 du CGI</td>
      </tr>
    </tbody>
  </table>
</div>"""


def _table2_ibs_html(data: G50Data, result: G50Result) -> str:
    """Table 2 — Acomptes IBS."""
    applicable = "Oui (Mars / Juin / Novembre)" if result.ibs_applicable else "Non (hors période d'acompte)"
    return f"""<div class="section">
  <div class="section-title">TABLEAU 2 — ACOMPTES ET SOLDE I.B.S / الدفعة المقدمة ورصيد الضريبة على الدخل</div>
  <div class="section-title-ar">TABLEAU 2 — ACOMPTES IBS</div>
  <table class="g50-table">
    <thead>
      <tr>
        <th class="code">Code</th>
        <th class="desc">Acomptes et solde I.B.S</th>
        <th>Montant (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="code">E1M10</td>
        <td class="desc">Acompte provisionnel<br><span class="ar">الدفعة المقدمة التقريبية</span></td>
        <td class="num">{_fmt_cell(result.ibs_acompte)}</td>
      </tr>
      <tr>
        <td colspan="3" class="note" style="text-align:center;">Période : {applicable} — 3 acomptes (mars, juin, nov) = 30% de l'IBS des années antérieures</td>
      </tr>
    </tbody>
  </table>
</div>"""


def _table3_irg_html(data: G50Data, result: G50Result) -> str:
    """Table 3 — IRG Salaires et autres retenues à la source."""
    return f"""<div class="section">
  <div class="section-title">TABLEAU 3 — IRG SALAIRES ET AUTRES RETENUES À LA SOURCE (IRG / IBS)</div>
  <div class="section-title-ar">TABLEAU 3 — ضريبة الدخل الاستقطاعية على الأجور والمكافآت</div>
  <table class="g50-table">
    <thead>
      <tr>
        <th class="code">Code</th>
        <th class="desc">Catégorie de revenus soumis à la retenue à la source</th>
        <th>Revenus imposables</th>
        <th>Taux</th>
        <th>Montant à payer (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="code">E1L20</td>
        <td class="desc">IRG / Traitements, salaires, pensions et rentes viagères<br><span class="ar">ضريبة الدخل / الأشغال والأجور والمعاشات</span></td>
        <td class="num">{_fmt_cell(data.irg_salaires_revenus)}</td>
        <td class="num">Barème</td>
        <td class="num">{_fmt_cell(result.irg_salaires)}</td>
      </tr>
      <tr>
        <td class="code">E1L30</td>
        <td class="desc">IRG / Location de locaux à usage commercial ou professionnel<br><span class="ar">ضريبة الدخل / إيجار محلات商用 أو مهني</span></td>
        <td class="num">{_fmt_cell(data.irg_location_commerciale_revenus)}</td>
        <td class="num">15%</td>
        <td class="num">{_fmt_cell(result.irg_location_commerciale)}</td>
      </tr>
      <tr>
        <td class="code">E1L40</td>
        <td class="desc">IRG / Les revenus issus de la location de salles des fêtes<br><span class="ar">ضريبة الدخل / إيرادات استئجار قاعات الأفراح</span></td>
        <td class="num">{_fmt_cell(data.irg_location_salles_revenus)}</td>
        <td class="num">15%</td>
        <td class="num">{_fmt_cell(result.irg_location_salles)}</td>
      </tr>
      <tr>
        <td class="code">E1L60</td>
        <td class="desc">IRG / Revenus des bons de caisse anonymes<br><span class="ar">ضريبة الدخل / إيرادات سندات الخزينة المجهولة</span></td>
        <td class="num">{_fmt_cell(data.irg_bons_caisse_revenus)}</td>
        <td class="num">50%</td>
        <td class="num">{_fmt_cell(result.irg_bons_caisse)}</td>
      </tr>
      <tr>
        <td class="code">E1L80</td>
        <td class="desc">IRG / Autres retenues à la source<br><span class="ar">ضريبة الدخل / استقطاعات أخرى</span></td>
        <td class="num">{_fmt_cell(data.irg_autres_ras_revenus)}</td>
        <td class="num">10%</td>
        <td class="num">{_fmt_cell(result.irg_autres_ras)}</td>
      </tr>
      <tr>
        <td class="code">E1M30</td>
        <td class="desc">IBS / Entreprises étrangères non installées (Prest. services)<br><span class="ar">الضريبة على الدخل / المؤسسات الأجنبية غير المقيمة</span></td>
        <td class="num">{_fmt_cell(data.ibs_prestations_revenus)}</td>
        <td class="num">24%</td>
        <td class="num">{_fmt_cell(result.ibs_prestations)}</td>
      </tr>
      <tr>
        <td class="code">E1M40</td>
        <td class="desc">IBS / Autres retenues à la source<br><span class="ar">الضريبة على الدخل / استقطاعات أخرى</span></td>
        <td class="num">{_fmt_cell(data.ibs_autres_ras_revenus)}</td>
        <td class="num">25%</td>
        <td class="num">{_fmt_cell(result.ibs_autres_ras)}</td>
      </tr>
      <tr class="total-row">
        <td class="code"></td>
        <td class="desc"><strong>TOTAL</strong></td>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"><strong>{_fmt(result.total_table3)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _table4_tic_html(data: G50Data, result: G50Result) -> str:
    """Table 4 — Droits et Taxes Indirects."""
    return f"""<div class="section">
  <div class="section-title">TABLEAU 4 — DROITS ET TAXES INDIRECTS / الضرائب غير المباشرة</div>
  <div class="section-title-ar">TABLEAU 4 — DROITS ET TAXES INDIRECTS</div>
  <table class="g50-table">
    <thead>
      <tr>
        <th class="code">Code</th>
        <th class="desc">Droits et Taxes Indirects</th>
        <th>Base d'imposition</th>
        <th>Tarif</th>
        <th>Montant à payer (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td colspan="5" style="background:#f0f0f0;font-weight:bold;text-align:left;font-size:8pt;">Section A — Impôts sur le produit</td>
      </tr>
      <tr>
        <td colspan="5" class="note" style="text-align:center;">Alcools, sucres, vins, tabacs, bières, pétrole — Codes C/500001 à C/500025</td>
      </tr>
      <tr>
        <td colspan="5" style="background:#f0f0f0;font-weight:bold;text-align:left;font-size:8pt;">Section B — Taxe intérieure de consommation (TIC)</td>
      </tr>
      <tr>
        <td colspan="5" class="note" style="text-align:center;">Taxe intérieure de consommation — Codes C/500027 à C/500039</td>
      </tr>
      <tr>
        <td colspan="5" style="background:#f0f0f0;font-weight:bold;text-align:left;font-size:8pt;">Section C — Autres contributions indirectes</td>
      </tr>
      <tr>
        <td class="code">E2E11</td>
        <td class="desc">Taxe sur les recharges téléphoniques<br><span class="ar">ضريبة إعادة شحن الهواتف النقالة</span></td>
        <td class="num">{_fmt_cell(data.tic_recharges_base)}</td>
        <td class="num">7%</td>
        <td class="num">{_fmt_cell(result.tic_recharges)}</td>
      </tr>
      <tr>
        <td class="code">E2E12</td>
        <td class="desc">Taxe pour usage des appareils récepteurs de radiodiffusion et télévision<br><span class="ar">ضريبة استعمال أجهزة الاستقبال</span></td>
        <td class="num">{_fmt_cell(data.tic_tv_base)}</td>
        <td class="num">DA</td>
        <td class="num">{_fmt_cell(result.tic_tv)}</td>
      </tr>
      <tr class="subtotal-row">
        <td class="code"></td>
        <td class="desc"><strong>Sous Total</strong></td>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"><strong>{_fmt(result.total_table4)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _table5_timbre_html(data: G50Data, result: G50Result) -> str:
    """Table 5 — Chiffre d'affaires / Droit de Timbre."""
    rows = [
        ("E2E13", "Taxe de formation", "1%", data.timbre_formation_base, data.timbre_formation_montant),
        ("E2E14", "Taxe d'apprentissage", "1%", data.timbre_apprentissage_base, data.timbre_apprentissage_montant),
        ("E2E15", "Taxe sur les véhicules neufs", "Barème", data.timbre_vehicules_neufs_base, data.timbre_vehicules_neufs_montant),
        ("E2E16", "Contribution des concessionnaires", "1%", data.timbre_concessionnaires_base, data.timbre_concessionnaires_montant),
        ("E2E17", "Taxe d'habitation", "Barème", data.timbre_habitation_base, data.timbre_habitation_montant),
        ("E2E18", "Taxe sur les pneus neufs ou importés", "10DA ou 5DA/unité", data.timbre_pneus_base, data.timbre_pneus_montant),
        ("E2E19", "Prélèvement sur les recettes des jeux à gains et divertissement", "40%", data.timbre_jeux_base, data.timbre_jeux_montant),
        ("E2E20", "Taxe sur les huiles, lubrifiants", "12500DA/T", data.timbre_huiles_base, data.timbre_huiles_montant),
        ("E2E21", "Taxe sur le CA des opérations de téléphonie mobile", "1%", data.timbre_mobile_base, data.timbre_mobile_montant),
        ("E2E22", "Taxe sur les bénéfices nets des importateurs et distributeurs en gros médicaments", "5%", data.timbre_medicaments_base, data.timbre_medicaments_montant),
        ("E2E23", "Taxe de publicité", "1%", data.timbre_publicite_base, data.timbre_publicite_montant),
        ("E2E24", "Taxe sur le CA des entreprises de production et d'importation de boissons gazeuses", "0,50%", data.timbre_boissons_base, data.timbre_boissons_montant),
        ("E2E25", "Autres voitures particulières (VP) de moins de cinq (5) années figurant dans le bilan des sociétés", "Barème d'âge", data.timbre_vp_base, data.timbre_vp_montant),
        ("E2E26", "Taxe sur carburant", "Barème", data.timbre_carburant_base, data.timbre_carburant_montant),
        ("E2E27", "Taxe sur la vente d'Electricité et du gaz", "Barème", data.timbre_electricite_base, data.timbre_electricite_montant),
        ("E2E28", "Taxe annuelle pour tous opérations économiques algériens inscrits au registre de commerce", "200/500/1000", data.timbre_rc_base, data.timbre_rc_montant),
        ("E2E29", "Redevance sur les céréales", "Barème", data.timbre_cereales_base, data.timbre_cereales_montant),
        ("E2E30", "Taxe appui à l'investissement des activités touristiques", "0,50%", data.timbre_tourisme_base, data.timbre_tourisme_montant),
        ("E2E31", "Taxe sur l'usage des appareils récepteurs de radiodiffusion et de télévision", "Barème", data.timbre_radiodiffusion_base, data.timbre_radiodiffusion_montant),
        ("E2E32", "Taxe d'efficacité énergétique (sans classification)", "LF2017", data.timbre_energie_base, data.timbre_energie_montant),
        ("E2E33", "Taxe d'efficacité énergétique (avec classification)", "LF2017", 0, 0),
        ("E2E34", "Taxe sur contrats de production et diffusion de publicité", "10%", data.timbre_pub_contrat_base, data.timbre_pub_contrat_montant),
    ]

    rows_html = ""
    for code, desc, tarif, base, montant in rows:
        if montant > 0 or base > 0:
            rows_html += f"""<tr>
        <td class="code">{code}</td>
        <td class="desc">{desc}</td>
        <td class="num">{_fmt_cell(base)}</td>
        <td class="num">{tarif}</td>
        <td class="num">{_fmt_cell(montant)}</td>
      </tr>"""

    if not rows_html:
        rows_html = """<tr>
        <td class="code">E2E13</td>
        <td class="desc">Taxe de formation</td>
        <td class="num"></td>
        <td class="num">1%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E14</td>
        <td class="desc">Taxe d'apprentissage</td>
        <td class="num"></td>
        <td class="num">1%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E15</td>
        <td class="desc">Taxe sur les véhicules neufs</td>
        <td class="num"></td>
        <td class="num">Barème</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E16</td>
        <td class="desc">Contribution des concessionnaires</td>
        <td class="num"></td>
        <td class="num">1%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E17</td>
        <td class="desc">Taxe d'habitation</td>
        <td class="num"></td>
        <td class="num">Barème</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E18</td>
        <td class="desc">Taxe sur les pneus neufs ou importés</td>
        <td class="num"></td>
        <td class="num">10DA ou 5DA/unité</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E19</td>
        <td class="desc">Prélèvement sur les recettes des jeux à gains et divertissement</td>
        <td class="num"></td>
        <td class="num">40%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E20</td>
        <td class="desc">Taxe sur les huiles, lubrifiants</td>
        <td class="num"></td>
        <td class="num">12500DA/T</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E21</td>
        <td class="desc">Taxe sur le CA des opérations de téléphonie mobile</td>
        <td class="num"></td>
        <td class="num">1%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E22</td>
        <td class="desc">Taxe sur les bénéfices nets des importateurs et distributeurs en gros médicaments</td>
        <td class="num"></td>
        <td class="num">5%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E23</td>
        <td class="desc">Taxe de publicité</td>
        <td class="num"></td>
        <td class="num">1%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E24</td>
        <td class="desc">Taxe sur le CA des entreprises de production et d'importation de boissons gazeuses</td>
        <td class="num"></td>
        <td class="num">0,50%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E25</td>
        <td class="desc">Autres voitures particulières (VP) de moins de cinq (5) années figurant dans le bilan des sociétés</td>
        <td class="num"></td>
        <td class="num">Barème d'âge</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E26</td>
        <td class="desc">Taxe sur carburant</td>
        <td class="num"></td>
        <td class="num">Barème</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E27</td>
        <td class="desc">Taxe sur la vente d'Electricité et du gaz</td>
        <td class="num"></td>
        <td class="num">Barème</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E28</td>
        <td class="desc">Taxe annuelle pour tous opérations économiques algériens inscrits au registre de commerce</td>
        <td class="num"></td>
        <td class="num">200/500/1000</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E29</td>
        <td class="desc">Redevance sur les céréales</td>
        <td class="num"></td>
        <td class="num">Barème</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E30</td>
        <td class="desc">Taxe appui à l'investissement des activités touristiques</td>
        <td class="num"></td>
        <td class="num">0,50%</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E31</td>
        <td class="desc">Taxe sur l'usage des appareils récepteurs de radiodiffusion et de télévision</td>
        <td class="num"></td>
        <td class="num">Barème</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E32</td>
        <td class="desc">Taxe d'efficacité énergétique (sans classification)</td>
        <td class="num"></td>
        <td class="num">LF2017</td>
        <td class="num"></td>
      </tr>
      <tr>
        <td class="code">E2E34</td>
        <td class="desc">Taxe sur contrats de production et diffusion de publicité</td>
        <td class="num"></td>
        <td class="num">10%</td>
        <td class="num"></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">TABLEAU 5 — CHIFFRE D'AFFAIRES / DROIT DE TIMBRE / رسم الطوابع</div>
  <div class="section-title-ar">TABLEAU 5 — رقم الأعمال / رسم الطوابع</div>
  <table class="g50-table">
    <thead>
      <tr>
        <th class="code">Code</th>
        <th class="desc">Opérations imposables</th>
        <th>Chiffre d'affaires imposable</th>
        <th>Taux</th>
        <th>Montant à payer (DA)</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
      <tr class="subtotal-row">
        <td class="code"></td>
        <td class="desc"><strong>Sous Total</strong></td>
        <td class="num"></td>
        <td class="num"></td>
        <td class="num"><strong>{_fmt(result.total_table5)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _recap_page1_html(data: G50Data, result: G50Result) -> str:
    """Récapitulation at bottom of Page 1."""
    return f"""<div class="section recap">
  <div class="section-title">RÉCAPITULATIF — MONTANTS DES DROITS DÉCLARÉS</div>
  <table>
    <thead>
      <tr>
        <th style="width:15%;">Rubrique</th>
        <th style="width:40%;">Cadre réservé au contribuable</th>
        <th style="width:22%;">Cadre réservé à la recette des impôts</th>
        <th style="width:23%;">Cadre réservé à l'inspection</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="font-weight:bold;">1 — TAP</td>
        <td class="num">{_fmt(data.tap_montant)}</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td style="font-weight:bold;">2 — AP / IBS</td>
        <td class="num">{_fmt(result.ibs_acompte)}</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td style="font-weight:bold;">3.1 — IRG / Salaires</td>
        <td class="num">{_fmt(result.irg_salaires)}</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td style="font-weight:bold;">3.2 — IRG / Autres retenues</td>
        <td class="num">{_fmt(result.irg_location_commerciale + result.irg_location_salles + result.irg_bons_caisse + result.irg_autres_ras)}</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td style="font-weight:bold;">3.3 — IBS / Ret. à la source</td>
        <td class="num">{_fmt(result.ibs_prestations + result.ibs_autres_ras)}</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td style="font-weight:bold;">4 — TIC / Autres</td>
        <td class="num">{_fmt(result.total_table4)}</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td style="font-weight:bold;">5 — Droit de timbre</td>
        <td class="num">{_fmt(result.total_table5)}</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td style="font-weight:bold;">6 — TVA</td>
        <td class="num">{_fmt(result.tva_a_payer)}</td>
        <td></td>
        <td></td>
      </tr>
      <tr class="total-line">
        <td colspan="2" style="font-size:10pt;"><strong>MONTANT TOTAL À PAYER</strong></td>
        <td colspan="2" class="num" style="font-size:12pt;"><strong>{_fmt(result.total_a_payer)} DA</strong></td>
      </tr>
    </tbody>
  </table>
  <div class="attestation">
    Certifie sincère et véritable le contenu de la présente déclaration conforme aux documents comptables
  </div>
</div>"""


def _page2_tva_header_html() -> str:
    """TVA page header."""
    return """<div class="section" style="page-break-before:always;">
  <div class="section-title">TABLEAU 6 — TAXE SUR LA VALEUR AJOUTÉE (TVA) / ضريبة القيمة المضافة</div>
  <div class="section-title-ar">TABLEAU 6 — TVA</div>
</div>"""


def _tva_ca_table_html(data: G50Data, result: G50Result) -> str:
    """TVA — Chiffres d'affaires imposables (Part A)."""
    # Helper to build a row
    def _row(code, desc, total, exonere, taux):
        imposable = total - exonere
        montant = imposable * taux
        return f"""<tr>
        <td class="code">{code}</td>
        <td class="desc">{desc}</td>
        <td class="num">{_fmt_cell(total)}</td>
        <td class="num">{_fmt_cell(exonere)}</td>
        <td class="num">{_fmt_cell(imposable)}</td>
        <td class="num">{taux*100:.0f}%</td>
        <td class="num">{_fmt_cell(montant)}</td>
      </tr>"""

    rows_9 = [
        ("E3B11", "Biens produits et denrées (art. 23 du CTVA)", data.tva_9_biens_total, data.tva_9_biens_exonere, TVA_RATE_REDUIT),
        ("E3B12", "Prestations de services (art. 23 du CTVA)", data.tva_9_prestations_total, data.tva_9_prestations_exonere, TVA_RATE_REDUIT),
        ("E3B13", "Opérations immobilières (art. 23 du CTVA)", data.tva_9_immobilier_total, data.tva_9_immobilier_exonere, TVA_RATE_REDUIT),
        ("E3B14", "Actes Médicaux", data.tva_9_medical_total, data.tva_9_medical_exonere, TVA_RATE_REDUIT),
        ("E3B15", "Commissionnaires et courtiers", data.tva_9_commission_total, data.tva_9_commission_exonere, TVA_RATE_REDUIT),
        ("E3B16", "Fourniture d'énergie", data.tva_9_energie_total, data.tva_9_energie_exonere, TVA_RATE_REDUIT),
        ("E3B17", "Autres", data.tva_9_autres_total, data.tva_9_autres_exonere, TVA_RATE_REDUIT),
    ]

    rows_19 = [
        ("E3B21", "Production : biens, produits et denrées (art. 21 CTCA)", data.tva_19_production_total, data.tva_19_production_exonere, TVA_RATE_STANDARD),
        ("E3B22", "Revente en l'état : biens, produits et denrées (art. 21 CTCA)", data.tva_19_revente_total, data.tva_19_revente_exonere, TVA_RATE_STANDARD),
        ("E3B23", "Travaux immobiliers autres que ceux soumis au taux 7%", data.tva_19_travaux_total, data.tva_19_travaux_exonere, TVA_RATE_STANDARD),
        ("E3B24", "Professions libérales", data.tva_19_liberales_total, data.tva_19_liberales_exonere, TVA_RATE_STANDARD),
        ("E3B25", "Opérations de banques et assurances", data.tva_19_banques_total, data.tva_19_banques_exonere, TVA_RATE_STANDARD),
        ("E3B26", "Prestations de téléphone et télex", data.tva_19_telephone_total, data.tva_19_telephone_exonere, TVA_RATE_STANDARD),
        ("E3B28", "Autres prestations de services", data.tva_19_autres_serv_total, data.tva_19_autres_serv_exonere, TVA_RATE_STANDARD),
        ("E3B31", "Débits de boissons", data.tva_19_boissons_total, data.tva_19_boissons_exonere, TVA_RATE_STANDARD),
        ("E3B32", "Production biens et denrées (art. 21 CTCA)", data.tva_19_prod_biens_total, data.tva_19_prod_biens_exonere, TVA_RATE_STANDARD),
        ("E3B33", "Reventes en l'état (art. 21 CTCA)", data.tva_19_revente_etat_total, data.tva_19_revente_etat_exonere, TVA_RATE_STANDARD),
        ("E3B34", "Tabacs et allumettes", data.tva_19_tabacs_total, data.tva_19_tabacs_exonere, TVA_RATE_STANDARD),
        ("E3B35", "Spectacles, jeux et divertissements autres", data.tva_19_spectacles_total, data.tva_19_spectacles_exonere, TVA_RATE_STANDARD),
        ("E3B36", "Autres prestations (art. 21 CTCA)", data.tva_19_autres_art21_total, data.tva_19_autres_art21_exonere, TVA_RATE_STANDARD),
        ("E3B37", "Consommations sur place", data.tva_19_consommation_total, data.tva_19_consommation_exonere, TVA_RATE_STANDARD),
    ]

    rows_ni = [
        ("E3B41", "Secteur pétrolier art 9/9 du CTCA", data.tva_ni_petrole_total, data.tva_ni_petrole_exonere, 0),
        ("E3B42", "Produits de première nécessité Art 9/2 du CTCA", data.tva_ni_premiere_necessite_total, data.tva_ni_premiere_necessite_exonere, 0),
        ("E3B43", "Opérations de crédit bail", data.tva_ni_credit_bail_total, data.tva_ni_credit_bail_exonere, 0),
        ("E3B44", "Opération de réassurance", data.tva_ni_reassurance_total, data.tva_ni_reassurance_exonere, 0),
        ("E3B45", "Opération d'assurances des personnes", data.tva_ni_assurances_total, data.tva_ni_assurances_exonere, 0),
        ("E3B46", "Opérations Intragroupe(*)", data.tva_ni_intragroupe_total, data.tva_ni_intragroupe_exonere, 0),
        ("E3B47", "Exportation", data.tva_ni_exportation_total, data.tva_ni_exportation_exonere, 0),
        ("E3B48", "Médicament", data.tva_ni_medicaments_total, data.tva_ni_medicaments_exonere, 0),
        ("E3B49", "Autres", data.tva_ni_autres_ni_total, data.tva_ni_autres_ni_exonere, 0),
    ]

    rows_exo = [
        ("E3B51", "Secteur pétrolier", data.tva_exo_petrole_total, data.tva_exo_petrole_exonere, 0),
        ("E3B52", "Andi", data.tva_exo_andi_total, data.tva_exo_andi_exonere, 0),
        ("E3B53", "Ansej", data.tva_exo_ansej_total, data.tva_exo_ansej_exonere, 0),
        ("E3B54", "Angem", data.tva_exo_angem_total, data.tva_exo_angem_exonere, 0),
        ("E3B55", "Cnac", data.tva_exo_cnac_total, data.tva_exo_cnac_exonere, 0),
        ("E3B56", "Exportation", data.tva_exo_exportation_total, data.tva_exo_exportation_exonere, 0),
    ]

    html_rows = ""
    html_rows += '<tr><td colspan="7" style="background:#0A1628;color:#fff;font-weight:bold;text-align:left;font-size:8pt;padding:4px;">9% — Taux réduit</td></tr>'
    for r in rows_9:
        html_rows += _row(*r)

    html_rows += '<tr><td colspan="7" style="background:#0A1628;color:#fff;font-weight:bold;text-align:left;font-size:8pt;padding:4px;">19% — Taux normal</td></tr>'
    for r in rows_19:
        html_rows += _row(*r)

    html_rows += '<tr><td colspan="7" style="background:#D4AF37;color:#0A1628;font-weight:bold;text-align:left;font-size:8pt;padding:4px;">Non imposables (Article 9 du CTCA)</td></tr>'
    for r in rows_ni:
        html_rows += _row(*r)

    html_rows += '<tr><td colspan="7" style="background:#D4AF37;color:#0A1628;font-weight:bold;text-align:left;font-size:8pt;padding:4px;">Exonéré</td></tr>'
    for r in rows_exo:
        html_rows += _row(*r)

    # Total general
    html_rows += f"""<tr class="total-row">
        <td class="code"></td>
        <td class="desc"><strong>TOTAL GENERAL DES C.A</strong></td>
        <td class="num"><strong>{_fmt(result.tva_ca_total)}</strong></td>
        <td class="num"><strong></strong></td>
        <td class="num"><strong>{_fmt(result.tva_ca_imposable_total)}</strong></td>
        <td class="num"></td>
        <td class="num"><strong>{_fmt(result.tva_9_imposable * TVA_RATE_REDUIT + result.tva_19_imposable * TVA_RATE_STANDARD)}</strong></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">A/ Chiffres d'affaires imposables — رقم الأعمال الخاضع للضريبة</div>
  <table class="g50-table">
    <thead>
      <tr>
        <th class="code">Code</th>
        <th class="desc">Opérations assujetties à la TVA</th>
        <th>Total</th>
        <th>Exonéré</th>
        <th>Imposable</th>
        <th>Taux</th>
        <th>Montant des droits (DA)</th>
      </tr>
    </thead>
    <tbody>
      {html_rows}
    </tbody>
  </table>
</div>"""


def _tva_deductions_html(data: G50Data, result: G50Result) -> str:
    """TVA — Déductions à opérer (Part B)."""
    return f"""<div class="section">
  <div class="section-title">B/ Déductions à opérer — الخصومات المراد القيام بها</div>
  <table class="g50-table">
    <thead>
      <tr>
        <th class="code">Code</th>
        <th class="desc" style="width:55%;">NATURE DES DÉDUCTIONS</th>
        <th>Montant (DA)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="code">E3B91</td>
        <td class="desc">Précompte antérieur<br><span class="ar">اقتطاع سابق</span></td>
        <td class="num">{_fmt_cell(data.tva_precompte_anterieur)}</td>
      </tr>
      <tr>
        <td class="code">E3B92</td>
        <td class="desc">TVA / achats de matières et services (art.29 CTCA)<br><span class="ar">ضريبة القيمة المضافة / مشتريات المواد والخدمات</span></td>
        <td class="num">{_fmt_cell(data.tva_achats_matieres)}</td>
      </tr>
      <tr>
        <td class="code">E3B93</td>
        <td class="desc">TVA / achats biens amortissables (art.38 CTCA)<br><span class="ar">ضريبة القيمة المضافة / مشتريات الأصول المستهلكة</span></td>
        <td class="num">{_fmt_cell(data.tva_achats_amortissables)}</td>
      </tr>
      <tr>
        <td class="code">E3B94</td>
        <td class="desc">Régularisation prorata déduction (art.40 CTCA)<br><span class="ar">تنقيط النسبة المخصومة</span></td>
        <td class="num">{_fmt_cell(data.tva_regularisation_prorata)}</td>
      </tr>
      <tr>
        <td class="code">E3B95</td>
        <td class="desc">TVA / factures annulées ou impayées (art.18 CTCA)<br><span class="ar">ضريبة القيمة المضافة / فواتير ملغاة أو غير مدفوعة</span></td>
        <td class="num">{_fmt_cell(data.tva_factures_annulees)}</td>
      </tr>
      <tr>
        <td class="code">E3B96</td>
        <td class="desc">Autres déductions (Notification de précomptes, etc.)<br><span class="ar">خصومات أخرى</span></td>
        <td class="num">{_fmt_cell(data.tva_autres_deductions)}</td>
      </tr>
      <tr class="total-row">
        <td class="code"></td>
        <td class="desc"><strong>Total des déductions à opérer (B)</strong></td>
        <td class="num"><strong>{_fmt(result.tva_deductions_total)}</strong></td>
      </tr>
    </tbody>
  </table>
</div>"""


def _tva_calcul_html(data: G50Data, result: G50Result) -> str:
    """TVA — Calcul (Part C)."""
    tva_collectee = result.tva_9_imposable * TVA_RATE_REDUIT + result.tva_19_imposable * TVA_RATE_STANDARD
    tva_a_payer_brut = tva_collectee - result.tva_deductions_total

    return f"""<div class="section">
  <div class="section-title">C/ TVA à Payer — ضريبة القيمة المضافة المدفوعة</div>
  <table class="g50-table">
    <tbody>
      <tr>
        <td class="code" style="width:12%;">E3B97</td>
        <td class="desc" style="width:55%;">Régularisation du prorata (art.40 C/TCA)(+)(Déduction excédentaire)<br><span class="ar">تنقيط النسبة / خصم إضافي</span></td>
        <td class="num">{_fmt_cell(data.tva_regularisation_prorata_plus)}</td>
      </tr>
      <tr>
        <td class="code">E3B98</td>
        <td class="desc">Régularisation (régime des acomptes)<br><span class="ar">تنقيط (نظام الدفعات المقدمة)</span></td>
        <td class="num">{_fmt_cell(data.tva_regularisation_acomptes)}</td>
      </tr>
      <tr>
        <td class="code">E3B99</td>
        <td class="desc">Reversement de la déduction (art 38 C/TCA)<br><span class="ar">إعادة خصم</span></td>
        <td class="num">{_fmt_cell(data.tva_reversement_deduction)}</td>
      </tr>
      <tr>
        <td class="code">E3B100</td>
        <td class="desc">(+) total à rappeler (C)<br><span class="ar">إجمالي المبلغ المستحق</span></td>
        <td class="num">{_fmt_cell(tva_a_payer_brut)}</td>
      </tr>
      <tr>
        <td class="code">E3B110</td>
        <td class="desc">Total des déductions à opérer (B)<br><span class="ar">إجمالي الخصومات</span></td>
        <td class="num">{_fmt_cell(result.tva_deductions_total)}</td>
      </tr>
      <tr class="total-row">
        <td class="code">E3B120</td>
        <td class="desc"><strong>TVA à payer au titre du mois (C - B)</strong><br><span class="ar">ضريبة القيمة المضافة المدفوعة عن الشهر</span></td>
        <td class="num"><strong>{_fmt(result.tva_a_payer)}</strong></td>
      </tr>
      <tr>
        <td class="code">E3B130</td>
        <td class="desc">Précompte à reporter sur le mois suivant (B - C)<br><span class="ar">اقتطاع تأجيل للشهر التالي</span></td>
        <td class="num">{_fmt_cell(result.tva_precompte_report)}</td>
      </tr>
      <tr>
        <td class="code">E3B140</td>
        <td class="desc">TVA auto-liquidée à payer (article 83 du CTCA)<br><span class="ar">ضريبة القيمة المضافة الذاتية</span></td>
        <td class="num">{_fmt_cell(data.tva_auto_liquidee)}</td>
      </tr>
    </tbody>
  </table>
</div>"""


def _recap_page3_html(data: G50Data, result: G50Result) -> str:
    """Page 3 — Récapitulation + Signatures."""
    return f"""<div class="section" style="page-break-before:always;">
  <div class="section-title">RÉCAPITULATIF GÉNÉRAL — MONTANT TOTAL À PAYER</div>

  <table class="g50-table">
    <thead>
      <tr>
        <th style="width:50%;">Désignation</th>
        <th style="width:25%;">Montant (DA)</th>
        <th style="width:25%;">Code</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align:left;">1 — TAP (supprimée LF2024)</td>
        <td class="num">{_fmt(data.tap_montant)}</td>
        <td class="code">C/500026/A</td>
      </tr>
      <tr>
        <td style="text-align:left;">2 — Acomptes IBS</td>
        <td class="num">{_fmt(result.ibs_acompte)}</td>
        <td class="code">E1M10</td>
      </tr>
      <tr>
        <td style="text-align:left;">3.1 — IRG Salaires</td>
        <td class="num">{_fmt(result.irg_salaires)}</td>
        <td class="code">E1L20</td>
      </tr>
      <tr>
        <td style="text-align:left;">3.2 — IRG Autres retenues</td>
        <td class="num">{_fmt(result.irg_location_commerciale + result.irg_location_salles + result.irg_bons_caisse + result.irg_autres_ras)}</td>
        <td class="code">E1L30-E1L80</td>
      </tr>
      <tr>
        <td style="text-align:left;">3.3 — IBS Retenues à la source</td>
        <td class="num">{_fmt(result.ibs_prestations + result.ibs_autres_ras)}</td>
        <td class="code">E1M30-E1M40</td>
      </tr>
      <tr>
        <td style="text-align:left;">4 — Droits et Taxes Indirects</td>
        <td class="num">{_fmt(result.total_table4)}</td>
        <td class="code">E2E11-E2E12</td>
      </tr>
      <tr>
        <td style="text-align:left;">5 — Droit de Timbre / Taxes</td>
        <td class="num">{_fmt(result.total_table5)}</td>
        <td class="code">E2E13-E2E34</td>
      </tr>
      <tr>
        <td style="text-align:left;">6 — TVA</td>
        <td class="num">{_fmt(result.tva_a_payer)}</td>
        <td class="code">E3B120</td>
      </tr>
      <tr class="total-row" style="background:#0A1628;color:#fff;">
        <td style="text-align:left;font-size:10pt;"><strong>MONTANT TOTAL À PAYER</strong></td>
        <td class="num" style="font-size:12pt;"><strong>{_fmt(result.total_a_payer)} DA</strong></td>
        <td class="code" style="color:#D4AF37;"><strong></strong></td>
      </tr>
    </tbody>
  </table>

  <div class="attestation" style="margin-top:10px;">
    Certifie sincère et véritable le contenu de la présente déclaration conforme aux documents comptables
  </div>
</div>"""


def _payment_section_html(data: G50Data, result: G50Result) -> str:
    """Payment section."""
    return f"""<div class="section">
  <div class="section-title">MODE DE PAIEMENT — طريقة الدفع</div>
  <div class="payment-section">
    <table>
      <tr>
        <td class="field-label">Payée par Chq banque N° :</td>
        <td class="field-value">{_esc(data.cheque_banque_numero) or _blank(25)}</td>
        <td class="field-label">du :</td>
        <td class="field-value">{_esc(data.cheque_banque_date) or '....../....../......'}</td>
      </tr>
      <tr>
        <td class="field-label">tiré sur l'Agence :</td>
        <td class="field-value" colspan="3">{_esc(data.cheque_banque_agence) or _blank(50)}</td>
      </tr>
      <tr>
        <td class="field-label">par Chèque postal N° :</td>
        <td class="field-value" colspan="3">{_esc(data.cheque_postal_numero) or _blank(50)}</td>
      </tr>
      <tr>
        <td class="field-label">En numéraire :</td>
        <td class="field-value">{_fmt_cell(data.numeraire)}</td>
        <td class="field-label">Prise en recette par quittance N° :</td>
        <td class="field-value">{_esc(data.quittance_numero) or _blank(25)}</td>
      </tr>
    </table>
  </div>
</div>"""


def _signature_blocks_html(data: G50Data) -> str:
    """Three signature blocks."""
    now = datetime.now().strftime("%d/%m/%Y")
    return f"""<div class="signature-block">
  <div class="sig-box">
    <div class="title">Le Contribuable</div>
    <br><br><br><br>
    Cachet et signature<br>
    {_esc(data.beneficiaire) or _esc(data.nom_prenom) or '________________'}<br>
    Le {now}
  </div>
  <div class="sig-box">
    <div class="title">Le Receveur des Impôts</div>
    <br><br><br><br>
    Reçu ce jour la présente déclaration<br>
    enregistrée sous le n°...<br>
    Cachet et signature<br>
    Le {now}
  </div>
  <div class="sig-box">
    <div class="title">L'Inspection des Impôts</div>
    <br><br><br><br>
    Déclaration enregistrée le...<br>
    Observations éventuelles :<br>
    <br><br>
    Signature
  </div>
</div>"""


def _footer_html() -> str:
    """Footer with generation info."""
    now = datetime.now()
    return f"""<div style="text-align:center;font-size:7pt;color:#999;margin-top:15px;border-top:1px solid #D4AF37;padding-top:4px;">
  Document généré le {now.strftime("%d/%m/%Y à %H:%M")} — Série G N°50 Official Form Generator
</div>"""


# ── Main Generator ────────────────────────────────────────────────────────────

def generate_g50(data: G50Data) -> str:
    """Generate complete G50 form as HTML string.

    Args:
        data: G50Data instance with all form fields.

    Returns:
        Complete HTML string ready for rendering or printing.
    """
    if isinstance(data, dict):
        data = G50Data(**data)

    result = calculate_g50(data)

    html = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G50 — Série G N°50 — {MONTHS_FR[data.month]} {data.year}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_dgi_hierarchy_html(data)}
{_identification_html(data)}

{_table1_tap_html(data)}
{_table2_ibs_html(data, result)}
{_table3_irg_html(data, result)}
{_table4_tic_html(data, result)}
{_table5_timbre_html(data, result)}

{_recap_page1_html(data, result)}

{_page2_tva_header_html()}
{_tva_ca_table_html(data, result)}
{_tva_deductions_html(data, result)}
{_tva_calcul_html(data, result)}

{_recap_page3_html(data, result)}
{_payment_section_html(data, result)}
{_signature_blocks_html(data)}

{_footer_html()}

</body>
</html>"""

    hook_generation("g50", {"month": data.month, "year": data.year, "nif": data.nif}, html)
    return html


def generate_g50_html(data) -> str:
    """Alias for generate_g50 — returns HTML string."""
    return generate_g50(data)


def generate_g50_text(data: G50Data) -> str:
    """Generate filled G50 as plain text."""
    if isinstance(data, dict):
        data = G50Data(**data)

    result = calculate_g50(data)
    month_name_fr = MONTHS_FR[data.month]

    lines = [
        "=" * 70,
        "DIRECTION GÉNÉRALE DES IMPÔTS",
        f"SÉRIE G N°50 — {data.year}",
        "IMPÔTS ET TAXES PERÇUS AU COMPTANT OU PAR VOIE DE RETENUE À LA SOURCE",
        "DÉCLARATION TENANT LIEU DE BORDEREAU — AVIS DE VERSEMENT",
        f"Période : {month_name_fr} {data.year}",
        "=" * 70,
        "",
        "IDENTIFICATION",
        "-" * 40,
        f"  NIF:                    {data.nif or _blank(25)}",
        f"  Code Activité:          {data.code_activite or _blank(25)}",
        f"  Nom/Prénom/Raison:      {data.nom_prenom or _blank(25)}",
        f"  Activité:               {data.activite or _blank(25)}",
        f"  Adresse:                {data.adresse or _blank(25)}",
        f"  Commune:                {data.commune or _blank(25)}",
        "",
        "TABLEAU 1 — TAP (supprimée LF2024)",
        "-" * 40,
        f"  TAP:                    {_fmt(data.tap_montant):>15} DA",
        "",
        "TABLEAU 2 — ACOMPTES IBS",
        "-" * 40,
        f"  Acompte IBS:            {_fmt(result.ibs_acompte):>15} DA",
        f"  Applicable:             {'Oui' if result.ibs_applicable else 'Non'}",
        "",
        "TABLEAU 3 — IRG / IBS RETENUES À LA SOURCE",
        "-" * 40,
        f"  IRG Salaires:           {_fmt(result.irg_salaires):>15} DA",
        f"  IRG Location commerc.:  {_fmt(result.irg_location_commerciale):>15} DA",
        f"  IRG Location salles:    {_fmt(result.irg_location_salles):>15} DA",
        f"  IRG Bons de caisse:     {_fmt(result.irg_bons_caisse):>15} DA",
        f"  IRG Autres RAS:         {_fmt(result.irg_autres_ras):>15} DA",
        f"  IBS Prestations:        {_fmt(result.ibs_prestations):>15} DA",
        f"  IBS Autres RAS:         {_fmt(result.ibs_autres_ras):>15} DA",
        f"  ─────────────────────────────────────",
        f"  TOTAL Tableau 3:        {_fmt(result.total_table3):>15} DA",
        "",
        "TABLEAU 4 — DROITS ET TAXES INDIRECTS",
        "-" * 40,
        f"  TIC Recharges:          {_fmt(result.tic_recharges):>15} DA",
        f"  TIC TV:                 {_fmt(result.tic_tv):>15} DA",
        f"  TOTAL Tableau 4:        {_fmt(result.total_table4):>15} DA",
        "",
        "TABLEAU 5 — DROIT DE TIMBRE / TAXES",
        "-" * 40,
        f"  TOTAL Tableau 5:        {_fmt(result.total_table5):>15} DA",
        "",
        "TABLEAU 6 — TVA",
        "-" * 40,
        f"  CA Imposable 9%:        {_fmt(result.tva_9_imposable):>15} DA",
        f"  CA Imposable 19%:       {_fmt(result.tva_19_imposable):>15} DA",
        f"  TVA Collectée:          {_fmt(result.tva_9_imposable * TVA_RATE_REDUIT + result.tva_19_imposable * TVA_RATE_STANDARD):>15} DA",
        f"  Déductions (B):         {_fmt(result.tva_deductions_total):>15} DA",
        f"  TVA à payer (C-B):      {_fmt(result.tva_a_payer):>15} DA",
        "",
        "=" * 70,
        f"  MONTANT TOTAL À PAYER:  {_fmt(result.total_a_payer):>15} DA",
        "=" * 70,
        "",
        f"  Date limite: avant le 20/{data.month:02d}/{data.year}",
        "",
    ]

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = G50Data(
        wilaya="32 - El Bayadh",
        inspection="Inspection des Impôts d'El Bayadh",
        recette="Recette des Impôts d'El Bayadh Centre",
        nif="1234567890",
        code_activite="6201",
        article_imposition="1234",
        nom_prenom="SARL TECH SOLUTIONS",
        activite="Prestation de services informatiques",
        adresse="123 Rue Didouche Mourad",
        commune="El Bayadh Centre",
        month=7,
        year=2026,
        # Table 3 — IRG Salaires
        irg_salaires_revenus=400_000,
        irg_salaires_irg=28_000,
        # Table 4 — TIC
        tic_recharges_base=500_000,
        tic_recharges_irg=35_000,
        # TVA
        tva_19_production_total=2_000_000,
        tva_19_production_exonere=0,
        tva_19_autres_serv_total=800_000,
        tva_19_autres_serv_exonere=0,
        # TVA Deductions
        tva_precompte_anterieur=50_000,
        tva_achats_matieres=100_000,
        # Beneficiary
        beneficiaire="Kamel Mahi",
    )

    result = calculate_g50(sample)
    print(f"TVA à payer: {_fmt(result.tva_a_payer)} DA")
    print(f"IRG Salaires: {_fmt(result.irg_salaires)} DA")
    print(f"TIC: {_fmt(result.total_table4)} DA")
    print(f"Total à payer: {_fmt(result.total_a_payer)} DA")

    if "--html" in sys.argv:
        html = generate_g50(sample)
        out = "g50_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out}")
    else:
        print()
        print(generate_g50_text(sample))
