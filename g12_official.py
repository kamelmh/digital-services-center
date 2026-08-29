"""G12 Official Form Generator — matches DGI printable forms exactly.

Generates G12 Prévisionnelle (forecast) and G12 Définitive (final) forms
matching the official Algerian tax forms from DGI (Direction Générale des Impôts).

Covers:
- G12 Prévisionnelle: CA forecast + IFU calculation + payment (integral/fractionné)
- G12 Définitive: Payroll section + forecast vs actual CA + IFU complémentaire

Legal references: Articles 282, 282ter, 282quater, 282sexies, 365, 365bis CIDTA

Usage:
    from g12_official import G12Form, generate_g12_prévisionnelle, generate_g12_définitive
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from policy_constants import (
    IFU_AUTO_ENTREPRENEUR_RATE,
    IFU_PRODUCTION_RATE,
    IFU_SERVICES_RATE,
    WILAYAS,
)


def _esc(value: object, default: str = "") -> str:
    """HTML-escape a value for safe rendering."""
    if value is None:
        return default
    return _html_mod.escape(str(value))


# ── Constants ─────────────────────────────────────────────────────────────────

IFU_RATES = {
    "production_vente": {"label_fr": "Activités de production ou de vente de marchandises",
                         "label_ar": "أنشطة الإنتاج أو بيع البضائع",
                         "rate": IFU_PRODUCTION_RATE, "min": 30_000},
    "services": {"label_fr": "Prestations de services ou autres activités",
                  "label_ar": "الخدمات أو الأنشطة الأخرى",
                  "rate": IFU_SERVICES_RATE, "min": 30_000},
    "auto_entrepreneur": {"label_fr": "Activités exercées sous le statut d'auto-entrepreneur",
                           "label_ar": "أنشطة مؤسسة فردية",
                           "rate": IFU_AUTO_ENTREPRENEUR_RATE, "min": 10_000},
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class G12FormData:
    """Complete data for G12 form generation."""
    # DGI hierarchy
    diw: str = ""  # Direction InterWilaya des Impôts
    recette: str = ""  # Recette des Impôts
    commune: str = ""  # Commune
    structure: str = ""  # Structure

    # Section I — Identification
    nom_prenoms: str = ""  # Nom, Prénoms / Raison sociale
    activite_exercee: str = ""  # Activité(s) exercée(s)
    date_debut: str = ""  # Date du début d'activité
    exonere: bool = False
    exoneration_type: str = ""  # ANADE, CNAC, ANGEM, artisanale, autre
    adresse_activite: str = ""  # Adresse du lieu d'exercice
    wilaya_activite: str = ""  # Wilaya de l'activité
    adresse_domicile: str = ""  # Adresse du domicile
    wilaya_domicile: str = ""  # Wilaya du domicile
    nif: str = ""  # Numéro d'Identification Fiscale
    nin: str = ""  # Numéro d'Identification National
    article_imposition: str = ""  # Numéro d'article d'imposition
    telephone: str = ""  # Numéro de téléphone (Définitive only)
    nouveau_contribuable: bool = False  # Nouveau contribuable checkbox

    # Section II — CA Prévisionnel (Prévisionnelle) or Définitif (Définitive)
    ca_production_imposable: float = 0
    ca_production_exonere: float = 0
    ca_services_imposable: float = 0
    ca_services_exonere: float = 0
    ca_auto_entrepreneur_imposable: float = 0
    ca_auto_entrepreneur_exonere: float = 0

    # Section II — Salaires (Définitive only)
    nombre_salaries: int = 0
    salaires_brut: float = 0
    charges_sociales: float = 0
    irg_annuel: float = 0

    # Section III — CA Réalisé (Définitive only)
    ca_realise_production_imposable: float = 0
    ca_realise_production_exonere: float = 0
    ca_realise_services_imposable: float = 0
    ca_realise_services_exonere: float = 0
    ca_realise_auto_imposable: float = 0
    ca_realise_auto_exonere: float = 0

    # Section IV — Marge bénéficiaire (produits réglementés)
    marge_realisee: float = 0
    marge_previsionnelle: float = 0

    # Payment
    mode_paiement: str = "integral"  # integral or fractionne
    year: int = datetime.now().year
    quittance_1: str = ""
    date_quittance_1: str = ""
    quittance_2: str = ""
    date_quittance_2: str = ""
    quittance_3: str = ""
    date_quittance_3: str = ""

    # Metadata
    beneficiaire: str = ""  # Name of person signing


@dataclass
class G12Calculations:
    """Calculated IFU amounts."""
    # Prévisionnel
    ifu_production: float = 0
    ifu_services: float = 0
    ifu_auto: float = 0
    ifu_total: float = 0
    ifu_minimum: float = 30_000

    # Définitif
    ca_realise_total: float = 0
    ca_previsionnel_total: float = 0
    ca_complementaire: float = 0
    ifu_complementaire: float = 0
    ifu_total_definitif: float = 0

    # Marge
    marge_complementaire: float = 0
    ifu_marge: float = 0

    # Revenu net
    revenu_net: float = 0

    # Fractionné
    tranche_1: float = 0
    tranche_2: float = 0
    tranche_3: float = 0


def calculate_g12(data: G12FormData, is_definitive: bool = False) -> G12Calculations:
    """Calculate all IFU amounts for the G12 form."""
    calc = G12Calculations()

    # ── Prévisionnel IFU ──
    calc.ifu_production = data.ca_production_imposable * IFU_RATES["production_vente"]["rate"]
    calc.ifu_services = data.ca_services_imposable * IFU_RATES["services"]["rate"]
    calc.ifu_auto = data.ca_auto_entrepreneur_imposable * IFU_RATES["auto_entrepreneur"]["rate"]
    calc.ifu_total = calc.ifu_production + calc.ifu_services + calc.ifu_auto

    # Minimum
    if data.ca_auto_entrepreneur_imposable > 0 and data.ca_production_imposable == 0 and data.ca_services_imposable == 0:
        calc.ifu_minimum = 10_000
    else:
        calc.ifu_minimum = 30_000

    calc.ifu_total = max(calc.ifu_total, calc.ifu_minimum)

    # Fractionné
    calc.tranche_1 = int(calc.ifu_total * 0.50)
    calc.tranche_2 = int(calc.ifu_total * 0.25)
    calc.tranche_3 = int(calc.ifu_total - calc.tranche_1 - calc.tranche_2)

    if is_definitive:
        # ── Définitif ──
        calc.ca_realise_total = (
            data.ca_realise_production_imposable + data.ca_realise_production_exonere +
            data.ca_realise_services_imposable + data.ca_realise_services_exonere +
            data.ca_realise_auto_imposable + data.ca_realise_auto_exonere
        )
        calc.ca_previsionnel_total = (
            data.ca_production_imposable + data.ca_production_exonere +
            data.ca_services_imposable + data.ca_services_exonere +
            data.ca_auto_entrepreneur_imposable + data.ca_auto_entrepreneur_exonere
        )
        calc.ca_complementaire = calc.ca_realise_total - calc.ca_previsionnel_total

        # IFU complémentaire (if realized > forecast)
        ifu_realise = (
            data.ca_realise_production_imposable * IFU_RATES["production_vente"]["rate"] +
            data.ca_realise_services_imposable * IFU_RATES["services"]["rate"] +
            data.ca_realise_auto_imposable * IFU_RATES["auto_entrepreneur"]["rate"]
        )
        calc.ifu_complementaire = max(0, ifu_realise - calc.ifu_total)
        calc.ifu_total_definitif = calc.ifu_total + calc.ifu_complementaire

        # Marge complémentaire
        calc.marge_complementaire = data.marge_realisee - data.marge_previsionnelle
        calc.ifu_marge = max(0, calc.marge_complementaire * IFU_RATES["production_vente"]["rate"])

        # Revenu net = total IFU - IFU marge (simplified)
        calc.revenu_net = calc.ifu_total_definitif

    return calc


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


# ── Legal Text ────────────────────────────────────────────────────────────────

LEGAL_TEXT = """Rappel du régime de l'Impôt Forfaitaire Unique (IFU)

• L'IFU s'applique aux personnes physiques exerçant une activité industrielle, commerciale,
  non commerciale, artisanale ainsi que les coopératives d'art et d'artisanat traditionnelles
  et les sociétés civiles professionnelles, dont le chiffre d'affaires ou les recettes
  professionnelles annuels n'excèdent pas le seuil prévu à l'article 282ter du Code des
  Impôts Directs et Taxes Assimilées (CIDTA), à l'exception de celles ayant opté pour le
  régime d'imposition d'après le bénéfice réel ou le régime simplifié des professions non
  commerciales.

• L'IFU s'applique également aux personnes physiques exerçant sous le statut de
  l'auto-entrepreneur, dont le chiffre d'affaires annuel n'excède pas le seuil prévu à
  l'article 51 de la loi de finances pour 2023.

• Pour les contribuables commercialisant des produits de large consommation, dont le prix
  ou la marge bénéficiaire sont réglementés ou plafonnés, la base imposable à retenir
  pour cet impôt est constituée par la marge bénéficiaire réalisée relative à ces produits
  (Article 282 quater du CIDTA).

• Le taux de l'IFU est fixé comme suit : 5% pour les activités de production et de vente
  de biens, 12% pour les autres activités et 0,5% pour les activités exercées sous le
  statut de l'auto-entrepreneur (Article 282sexies du CIDTA).

• Les contribuables soumis à l'IFU sont tenus de déposer une déclaration prévisionnelle,
  au plus tard le 30 juin de chaque année (Article 1er du Code des Procédures Fiscales
  « CPF »), reprenant le montant annuel prévisionnel du chiffre d'affaires ou des recettes
  professionnelles que le contribuable envisage de réaliser au titre de l'exercice objet
  de déclaration.

• Les contribuables soumis à l'IFU doivent procéder eux-mêmes au calcul de l'impôt dû
  et de reverser le montant intégral de l'impôt à la recette des impôts dont ils
  relèvent, au moment du dépôt de la déclaration. Ces derniers peuvent recourir au
  paiement fractionné de l'impôt, à condition que la déclaration soit déposée dans le
  délai imparti (Article 365 du CIDTA). Dans ce cas, ils doivent s'acquitter, lors du
  dépôt de la déclaration prévisionnelle, de 50% du montant de l'Impôt Forfaitaire
  Unique (IFU). Pour les 50% restants, leur paiement s'effectue en deux versements
  égaux, du 1er au 15 septembre et du 1er au 15 décembre.

• Le minimum d'imposition doit être acquitté intégralement au plus tard le 30 juin de
  l'année concernée (Article 365 bis du CIDTA).

• Les contribuables soumis à l'IFU sont tenus de souscrire, au plus tard le 20 janvier
  de l'année N+1 une déclaration définitive, reprenant le chiffre d'affaires ou les
  recettes professionnelles effectivement réalisées. Dans le cas où le chiffre d'affaires
  ou les recettes professionnelles réalisés dépassent ceux déclarés au titre de la
  déclaration prévisionnelle, le contribuable doit payer l'impôt complémentaire y
  relatif, au moment de la souscription de la déclaration définitive (Article 282
  quater du CIDTA).

• Les nouveaux contribuables sont tenus de souscrire la déclaration définitive prévue
  à l'article 282 quater du CIDTA et de s'acquitter intégralement du montant de l'impôt
  forfaitaire unique dû, lequel ne peut être inférieur au minimum d'imposition fixé à
  30.000 DA. Toutefois, pour les activités exercées sous le statut d'auto-entrepreneur,
  ce montant est fixé à 10.000 DA. Cette déclaration doit être souscrite, au plus tard,
  le 20 janvier de l'année qui suit celle du début de leur activité. Ces contribuables
  ne sont pas concernés par la souscription de la déclaration prévisionnelle (Article
  3 bis du CPF).

• Les contribuables soumis à l'IFU doivent tenir, un registre côté et paraphé par les
  services fiscaux, récapitulé par année, contenant le détail de leurs achats, appuyé
  des factures et de toutes pièces justificatives. Ils doivent également tenir dans les
  formes prescrites par les textes en vigueur, un registre de recettes (Article 282
  du CIDTA)."""


# ── HTML Generators ───────────────────────────────────────────────────────────

def _header_html(form_type: str, year: int) -> str:
    """Official DGI header."""
    if form_type == "prévisionnelle":
        title = "SÉRIE G N°12"
        regime = "RÉGIME DE L'IMPÔT FORFAITAIRE UNIQUE (IFU)"
        label = "DÉCLARATION PRÉVISIONNELLE DU CHIFFRE D'AFFAIRES OU DES RECETTES PROFESSIONNELLES"
        ref = "(Art 1er du Code des Procédures Fiscales)"
        deadline = f"A souscrire auprès de la recette des impôts au plus tard le 30 juin de l'année {year}."
    else:
        title = "SÉRIE G N°12 Bis"
        regime = "Régime de l'Impôt Forfaitaire Unique (IFU)"
        label = "DÉCLARATION DÉFINITIVE DU CHIFFRE D'AFFAIRES OU DES RECETTES PROFESSIONNELLES"
        ref = "(Art 282 quater du CIDTA)"
        deadline = f"A souscrire auprès de la recette des impôts au plus tard le 20 janvier de l'année N+1."

    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h1>{title}</h1>
  <div class="subtitle">{regime}</div>
  <div class="subtitle">{label}</div>
  <div class="subtitle">DE L'ANNÉE {year}</div>
  <div class="legal-ref">{ref}</div>
  <div class="deadline">{deadline}</div>
</div>"""


def _dgi_hierarchy_html(data: G12FormData) -> str:
    """DGI institutional hierarchy fields."""
    return f"""<div class="section">
  <div class="dgi-fields">
    <table class="dgi-table">
      <tr>
        <td class="dgi-label">DIW DE :</td>
        <td class="dgi-value">{_esc(data.diw) or '...................................................'}</td>
      </tr>
      <tr>
        <td class="dgi-label">Structure :</td>
        <td class="dgi-value">{_esc(data.structure) or '...................................................'}</td>
      </tr>
      <tr>
        <td class="dgi-label">Recette des Impôts de :</td>
        <td class="dgi-value">{_esc(data.recette) or '...................................................'}</td>
      </tr>
      <tr>
        <td class="dgi-label">Commune de :</td>
        <td class="dgi-value">{_esc(data.commune) or '...................................................'}</td>
      </tr>
    </table>
  </div>
</div>"""


def _identification_html(data: G12FormData, show_phone: bool = False, show_nouveau: bool = False) -> str:
    """Section I — Identification du contribuable."""
    exoneration_checks = ""
    types = [("ANADE (Ex-ANSEJ)", "anade"), ("CNAC", "cnac"), ("ANGEM", "angem"),
             ("Exonération des activités artisanales", "artisanale"), ("Autres exonérations", "autre")]
    for label, key in types:
        checked = "☑" if data.exoneration_type == key else "☐"
        exoneration_checks += f'<td class="checkbox-cell">{checked} {label}</td>'

    nouveau = ""
    if show_nouveau:
        checked = "☑" if data.nouveau_contribuable else "☐"
        nouveau = f'<div class="nouveau-box">{checked} Si vous êtes un nouveau contribuable, cocher la case suivante</div>'

    phone = ""
    if show_phone:
        phone = f"""<tr>
          <td class="field-label">Numéro de téléphone :</td>
          <td class="field-value">{_esc(data.telephone) or '................................'}</td>
          <td class="field-label">الهاتف :</td>
        </tr>"""

    return f"""<div class="section">
  <div class="section-title">I - IDENTIFICATION DU CONTRIBUABLE</div>
  <div class="section-title-ar">I — تحديد المكلّف</div>
  <table class="fields-table">
    <tr>
      <td class="field-label">Nom, Prénoms / Raison sociale :</td>
      <td class="field-value" colspan="2">{_esc(data.nom_prenoms) or '................................'}</td>
      <td class="field-label">الاسم واللقب / الاسم التجاري :</td>
    </tr>
    <tr>
      <td class="field-label">Activité(s) exercée(s) :</td>
      <td class="field-value" colspan="2">{_esc(data.activite_exercee) or '................................'}</td>
      <td class="field-label">النشاط(ات) الممارسة :</td>
    </tr>
    <tr>
      <td class="field-label">Date du début d'activité :</td>
      <td class="field-value">{_esc(data.date_debut) or '....../....../......'}</td>
      <td class="field-label">تاريخ بدء النشاط :</td>
    </tr>
    <tr>
      <td class="field-label">Activité exonérée :</td>
      <td class="field-value" colspan="2">
        <table class="checkbox-table"><tr>{exoneration_checks}</tr></table>
      </td>
      <td class="field-label">النشاط معفى :</td>
    </tr>
    <tr>
      <td class="field-label">Adresse du lieu d'exercice de l'activité :</td>
      <td class="field-value" colspan="2">{_esc(data.adresse_activite) or '................................'}</td>
      <td class="field-label">عنوان ممارسة النشاط :</td>
    </tr>
    <tr>
      <td class="field-label">Wilaya :</td>
      <td class="field-value">{_esc(data.wilaya_activite) or '......'}</td>
      <td class="field-label">الولاية :</td>
    </tr>
    <tr>
      <td class="field-label">Adresse du domicile du contribuable :</td>
      <td class="field-value" colspan="2">{_esc(data.adresse_domicile) or '................................'}</td>
      <td class="field-label">عنوان إقامة المكلف :</td>
    </tr>
    <tr>
      <td class="field-label">Wilaya :</td>
      <td class="field-value">{_esc(data.wilaya_domicile) or '......'}</td>
      <td class="field-label">الولاية :</td>
    </tr>
    <tr>
      <td class="field-label">Numéro d'Identification Fiscale (NIF) :</td>
      <td class="field-value">{_esc(data.nif) or '................................'}</td>
      <td class="field-label">رقم التعريف الجبائي :</td>
    </tr>
    <tr>
      <td class="field-label">Numéro d'Identification National (NIN) :</td>
      <td class="field-value">{_esc(data.nin) or '................................'}</td>
      <td class="field-label">رقم التعريف الوطني :</td>
    </tr>
    <tr>
      <td class="field-label">Numéro d'article d'imposition :</td>
      <td class="field-value">{_esc(data.article_imposition) or '................................'}</td>
      <td class="field-label">رقم المقالة الجبائية :</td>
    </tr>
    {phone}
  </table>
  {nouveau}
</div>"""


def _ca_table_html(
    ca_prod_imp: float, ca_prod_exo: float,
    ca_serv_imp: float, ca_serv_exo: float,
    ca_auto_imp: float, ca_auto_exo: float,
    calc: G12Calculations,
    title: str = "II — CHIFFRE D'AFFAIRES / RECETTES PROFESSIONNELLES PRÉVISIONNELS (DA)",
    title_ar: str = "II — رقم الأعمال / الإيرادات المهنية التقديرية (دج)",
    show_complementaire: bool = False,
    ca_realise: tuple = None,
) -> str:
    """CA table — matches official form layout."""
    # Totals
    total_imp = ca_prod_imp + ca_serv_imp + ca_auto_imp
    total_exo = ca_prod_exo + ca_serv_exo + ca_auto_exo
    total_global = total_imp + total_exo

    # IFU per line
    ifu_prod = ca_prod_imp * IFU_RATES["production_vente"]["rate"]
    ifu_serv = ca_serv_imp * IFU_RATES["services"]["rate"]
    ifu_auto = ca_auto_imp * IFU_RATES["auto_entrepreneur"]["rate"]
    ifu_total = calc.ifu_total if calc and calc.ifu_total else (ifu_prod + ifu_serv + ifu_auto)

    complementaire_cols = ""
    if show_complementaire and ca_realise:
        r_prod_imp, r_prod_exo, r_serv_imp, r_serv_exo, r_auto_imp, r_auto_exo = ca_realise
        r_total_imp = r_prod_imp + r_serv_imp + r_auto_imp
        r_total_exo = r_prod_exo + r_serv_exo + r_auto_exo
        r_global = r_total_imp + r_total_exo
        comp_imp = r_total_imp - total_imp
        comp_exo = r_total_exo - total_exo
        comp_global = r_global - total_global
        ifu_comp = max(0, r_prod_imp * IFU_RATES["production_vente"]["rate"] + r_serv_imp * IFU_RATES["services"]["rate"] + r_auto_imp * IFU_RATES["auto_entrepreneur"]["rate"] - ifu_total)

        complementaire_cols = f"""
        <th>CA/Réalisé<br>Imposable</th>
        <th>CA/Réalisé<br>Exonéré</th>
        <th>CA/Réalisé<br>Global</th>
        <th>CA<br>Complémentaire<br>(3)=(1)-(2)</th>
        <th>IFU<br>Complémentaire<br>(A)</th>"""

    comp_data = ""
    if show_complementaire and ca_realise:
        r_prod_imp, r_prod_exo, r_serv_imp, r_serv_exo, r_auto_imp, r_auto_exo = ca_realise
        comp_prod = (r_prod_imp + r_prod_exo) - (ca_prod_imp + ca_prod_exo)
        comp_serv = (r_serv_imp + r_serv_exo) - (ca_serv_imp + ca_serv_exo)
        comp_auto = (r_auto_imp + r_auto_exo) - (ca_auto_imp + ca_auto_exo)
        r_total_imp = r_prod_imp + r_serv_imp + r_auto_imp
        comp_total_imp = r_total_imp - total_imp
        ifu_comp = max(0, r_prod_imp * IFU_RATES["production_vente"]["rate"] + r_serv_imp * IFU_RATES["services"]["rate"] + r_auto_imp * IFU_RATES["auto_entrepreneur"]["rate"] - ifu_total)

        comp_data = f"""
        <td class="num">{_fmt_cell(r_prod_imp)}</td>
        <td class="num">{_fmt_cell(r_prod_exo)}</td>
        <td class="num">{_fmt_cell(r_prod_imp + r_prod_exo)}</td>
        <td class="num">{_fmt_cell(comp_prod)}</td>
        <td class="num">{_fmt_cell(max(0, r_prod_imp * IFU_RATES["production_vente"]["rate"] - ifu_prod))}</td>"""

        comp_dataServ = f"""
        <td class="num">{_fmt_cell(r_serv_imp)}</td>
        <td class="num">{_fmt_cell(r_serv_exo)}</td>
        <td class="num">{_fmt_cell(r_serv_imp + r_serv_exo)}</td>
        <td class="num">{_fmt_cell(comp_serv)}</td>
        <td class="num">{_fmt_cell(max(0, r_serv_imp * IFU_RATES["services"]["rate"] - ifu_serv))}</td>"""

        comp_dataAuto = f"""
        <td class="num">{_fmt_cell(r_auto_imp)}</td>
        <td class="num">{_fmt_cell(r_auto_exo)}</td>
        <td class="num">{_fmt_cell(r_auto_imp + r_auto_exo)}</td>
        <td class="num">{_fmt_cell(comp_auto)}</td>
        <td class="num">{_fmt_cell(max(0, r_auto_imp * IFU_RATES["auto_entrepreneur"]["rate"] - ifu_auto))}</td>"""

        comp_dataTotal = f"""
        <td class="num">{_fmt_cell(r_total_imp)}</td>
        <td class="num">{_fmt_cell(r_total_exo)}</td>
        <td class="num">{_fmt_cell(r_global)}</td>
        <td class="num">{_fmt_cell(comp_total_imp)}</td>
        <td class="num">{_fmt_cell(ifu_comp)}</td>"""
    else:
        comp_data = comp_dataServ = comp_dataAuto = comp_dataTotal = ""

    return f"""<div class="section">
  <div class="section-title">{title}</div>
  <div class="section-title-ar">{title_ar}</div>
  <table class="ca-table">
    <thead>
      <tr>
        <th rowspan="2">Nature de l'activité</th>
        <th rowspan="2">Taux<br>IFU</th>
        <th colspan="3">CA Prévisionnels</th>
        <th rowspan="2">IFU<br>dû (A)</th>
        {f'<th colspan="3">CA Réalisés</th>' if show_complementaire else ''}
        {f'<th colspan="2">Complément</th>' if show_complementaire else ''}
      </tr>
      <tr>
        <th>Imposable</th>
        <th>Exonéré</th>
        <th>Global</th>
        {f'<th>Imposable</th><th>Exonéré</th><th>Global</th>' if show_complementaire else ''}
        {f'<th>CA (3)</th><th>IFU (A)</th>' if show_complementaire else ''}
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="activity">Activités de production ou de vente de marchandises<br><span class="ar">أنشطة الإنتاج أو بيع البضائع</span></td>
        <td class="rate">5%</td>
        <td class="num">{_fmt_cell(ca_prod_imp)}</td>
        <td class="num">{_fmt_cell(ca_prod_exo)}</td>
        <td class="num">{_fmt_cell(ca_prod_imp + ca_prod_exo)}</td>
        <td class="num">{_fmt_cell(ifu_prod)}</td>
        {comp_data}
      </tr>
      <tr>
        <td class="activity">Prestations de services ou autres activités<br><span class="ar">الخدمات أو الأنشطة الأخرى</span></td>
        <td class="rate">12%</td>
        <td class="num">{_fmt_cell(ca_serv_imp)}</td>
        <td class="num">{_fmt_cell(ca_serv_exo)}</td>
        <td class="num">{_fmt_cell(ca_serv_imp + ca_serv_exo)}</td>
        <td class="num">{_fmt_cell(ifu_serv)}</td>
        {comp_dataServ if show_complementaire else ''}
      </tr>
      <tr>
        <td class="activity">Activités exercées sous le statut d'auto-entrepreneur<br><span class="ar">أنشطة مؤسسة فردية</span></td>
        <td class="rate">0,5%</td>
        <td class="num">{_fmt_cell(ca_auto_imp)}</td>
        <td class="num">{_fmt_cell(ca_auto_exo)}</td>
        <td class="num">{_fmt_cell(ca_auto_imp + ca_auto_exo)}</td>
        <td class="num">{_fmt_cell(ifu_auto)}</td>
        {comp_dataAuto if show_complementaire else ''}
      </tr>
      <tr class="total-row">
        <td class="activity"><strong>Total</strong></td>
        <td class="rate"></td>
        <td class="num"><strong>{_fmt_cell(total_imp)}</strong></td>
        <td class="num"><strong>{_fmt_cell(total_exo)}</strong></td>
        <td class="num"><strong>{_fmt_cell(total_global)}</strong></td>
        <td class="num"><strong>{_fmt(ifu_total)}</strong></td>
        {comp_dataTotal if show_complementaire else ''}
      </tr>
    </tbody>
  </table>
  <div class="note">(1) Chiffres d'affaires soumis à l'IFU suivant le mode d'imposition à la marge bénéficiaire</div>
  <div class="note">(**) Le minimum d'imposition est fixé à 30.000 DA (10.000 DA pour les auto-entrepreneurs) — Art. 365bis du CIDTA</div>
</div>"""


def _marge_html(data: G12FormData, calc: G12Calculations = None, is_definitive: bool = False) -> str:
    """Section IV — Marge bénéficiaire (Définitive only)."""
    if not is_definitive:
        return ""

    marge_comp = data.marge_realisee - data.marge_previsionnelle
    ifu_marge = max(0, marge_comp * IFU_RATES["production_vente"]["rate"])
    ifu_total_payer = (calc.ifu_total_definitif + ifu_marge) if calc else 0

    return f"""<div class="section">
  <div class="section-title">IV - MARGE BÉNÉFICIAIRE (EN DA)</div>
  <div class="section-title-ar">IV - الهامش الإجمالي (دج)</div>
  <table class="ca-table">
    <thead>
      <tr>
        <th rowspan="2">Nature de l'activité</th>
        <th rowspan="2">Taux<br>IFU</th>
        <th colspan="2">Marge bénéficiaire</th>
        <th rowspan="2">Marge<br>Complémentaire<br>(3)=(1)-(2)</th>
        <th rowspan="2">IFU<br>Marge<br>(B)</th>
      </tr>
      <tr>
        <th>Réalisée (1)</th>
        <th>Prévisionnelle (2)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="activity">Activités de production ou de vente<br><span class="ar">أنشطة الإنتاج أو البيع</span></td>
        <td class="rate">5%</td>
        <td class="num">{_fmt_cell(data.marge_realisee)}</td>
        <td class="num">{_fmt_cell(data.marge_previsionnelle)}</td>
        <td class="num">{_fmt_cell(marge_comp)}</td>
        <td class="num">{_fmt_cell(ifu_marge)}</td>
      </tr>
    </tbody>
  </table>
  <div class="ifu-total-line"><strong>IFU A PAYER (A)+(B) :</strong> {_fmt(ifu_total_payer)} DA</div>
  <div class="note">(1) Chiffres d'affaires soumis à l'IFU suivant le mode d'imposition à la marge bénéficiaire</div>
</div>"""


def _salaires_html(data: G12FormData) -> str:
    """Section II — Volet réservé aux salaires (Définitive only)."""
    return f"""<div class="section">
  <div class="section-title">II - VOLET RÉSERVÉ AUX SALAIRES</div>
  <div class="section-title-ar">II - الجزء المخصص للأجور</div>
  <table class="fields-table">
    <tr>
      <td class="field-label">Nombre de salariés :</td>
      <td class="field-value">{_esc(data.nombre_salaries) or '......'}</td>
      <td class="field-label">عدد الموظفين :</td>
    </tr>
    <tr>
      <td class="field-label">Montant global brut des salaires versés* :</td>
      <td class="field-value">{_fmt_cell(data.salaires_brut)}</td>
      <td class="field-label">إجمالي الأجور المصروفة* :</td>
    </tr>
    <tr>
      <td class="field-label">Montant des charges sociales versées* :</td>
      <td class="field-value">{_fmt_cell(data.charges_sociales)}</td>
      <td class="field-label">الاشتراكات الاجتماعية المدفوعة* :</td>
    </tr>
    <tr>
      <td class="field-label">Montant annuel de l'IRG acquitté* :</td>
      <td class="field-value">{_fmt_cell(data.irg_annuel)}</td>
      <td class="field-label">إجمالي ضريبة الدخل المدفوعة* :</td>
    </tr>
  </table>
  <div class="note">(*) Ces informations concernent l'année N</div>
</div>"""


def _payment_integral_html(calc: G12Calculations, data: G12FormData) -> str:
    """Payment intégral section."""
    return f"""<div class="section">
  <div class="section-title">PAIEMENT DE L'IFU</div>
  <div class="payment-box">
    <div class="payment-option">
      <strong>Paiement intégral de l'IFU</strong>
      <div class="payment-detail">
        Paiement total des droits dus lors du dépôt de la déclaration prévisionnelle
        au plus tard le 30 juin de l'année {data.year}.
      </div>
      <table class="payment-table">
        <tr>
          <td class="field-label">Montant total de l'IFU acquitté :</td>
          <td class="field-value"><strong>{_fmt(calc.ifu_total)} DA</strong></td>
        </tr>
        <tr>
          <td class="field-label">En chiffres :</td>
          <td class="field-value">{_fmt(calc.ifu_total)} DA</td>
        </tr>
        <tr>
          <td class="field-label">En lettres :</td>
          <td class="field-value">........................................................</td>
        </tr>
        <tr>
          <td class="field-label">Quittance N° :</td>
          <td class="field-value">{_esc(data.quittance_1) or '................................'}</td>
        </tr>
        <tr>
          <td class="field-label">du :</td>
          <td class="field-value">{_esc(data.date_quittance_1) or '....../....../......'}</td>
        </tr>
      </table>
      <div class="signature-block">
        <div class="sig-box">Le Contribuable<br><br><br>Cachet et signature</div>
        <div class="sig-box">Le Caissier<br><br><br>Cachet et signature</div>
      </div>
    </div>
  </div>
  {_minimum_ifu_html(calc, data)}
</div>"""


def _minimum_ifu_html(calc: G12Calculations, data: G12FormData) -> str:
    """Minimum IFU payment section (appears on page 2 of official form)."""
    return f"""<div class="payment-box" style="margin-top: 10px;">
    <div class="payment-option">
      <strong>Paiement intégral du minimum d'imposition au plus tard le 30 juin de l'année {data.year}</strong>
      <table class="payment-table">
        <tr>
          <td class="field-label">Montant du minimum d'imposition/IFU acquitté :</td>
          <td class="field-value">{_fmt(calc.ifu_minimum)} DA</td>
        </tr>
        <tr>
          <td class="field-label">Quittance N° :</td>
          <td class="field-value">................................</td>
        </tr>
        <tr>
          <td class="field-label">du :</td>
          <td class="field-value">....../....../......</td>
        </tr>
      </table>
      <div class="signature-block">
        <div class="sig-box">Le Contribuable<br><br><br>Cachet et signature</div>
        <div class="sig-box">Le Caissier<br><br><br>Cachet et signature</div>
      </div>
    </div>
  </div>"""


def _payment_fractionne_html(calc: G12Calculations, data: G12FormData) -> str:
    """Payment fractionné section."""
    year = data.year
    return f"""<div class="section">
  <div class="section-title">PAIEMENT DE L'IFU</div>
  <div class="payment-box">
    <div class="payment-option">
      <strong>Paiement fractionné de l'IFU (*)</strong>

      <div class="tranche">
        <strong>Paiement de la 1ère tranche de 50% des droits au dépôt de la déclaration au plus tard le 30 juin de l'année {year}</strong>
        <table class="payment-table">
          <tr><td class="field-label">Montant total de l'IFU acquitté :</td><td class="field-value"><strong>{_fmt(calc.tranche_1)} DA</strong></td></tr>
          <tr><td class="field-label">En chiffres :</td><td class="field-value">{_fmt(calc.tranche_1)} DA</td></tr>
          <tr><td class="field-label">En lettres :</td><td class="field-value">........................................................</td></tr>
          <tr><td class="field-label">Quittance N° :</td><td class="field-value">{_esc(data.quittance_1) or '................................'}</td></tr>
          <tr><td class="field-label">du :</td><td class="field-value">{_esc(data.date_quittance_1) or '....../....../......'}</td></tr>
        </table>
        <div class="signature-block">
          <div class="sig-box">Le Contribuable<br><br><br>Cachet et signature</div>
          <div class="sig-box">Le Caissier<br><br><br>Cachet et signature</div>
        </div>
      </div>

      <div class="tranche">
        <strong>Paiement de la 2ème tranche de 25% des droits du 1er au 15 Septembre de l'année {year}</strong>
        <table class="payment-table">
          <tr><td class="field-label">Montant total de l'IFU acquitté :</td><td class="field-value"><strong>{_fmt(calc.tranche_2)} DA</strong></td></tr>
          <tr><td class="field-label">En chiffres :</td><td class="field-value">{_fmt(calc.tranche_2)} DA</td></tr>
          <tr><td class="field-label">En lettres :</td><td class="field-value">........................................................</td></tr>
          <tr><td class="field-label">Quittance N° :</td><td class="field-value">{_esc(data.quittance_2) or '................................'}</td></tr>
          <tr><td class="field-label">du :</td><td class="field-value">{_esc(data.date_quittance_2) or '....../....../......'}</td></tr>
        </table>
        <div class="signature-block">
          <div class="sig-box">Le Contribuable<br><br><br>Cachet et signature</div>
          <div class="sig-box">Le Caissier<br><br><br>Cachet et signature</div>
        </div>
      </div>

      <div class="tranche">
        <strong>Paiement de la 3ème tranche de 25% des droits du 1er au 15 Décembre de l'année {year}</strong>
        <table class="payment-table">
          <tr><td class="field-label">Montant total de l'IFU acquitté :</td><td class="field-value"><strong>{_fmt(calc.tranche_3)} DA</strong></td></tr>
          <tr><td class="field-label">En chiffres :</td><td class="field-value">{_fmt(calc.tranche_3)} DA</td></tr>
          <tr><td class="field-label">En lettres :</td><td class="field-value">........................................................</td></tr>
          <tr><td class="field-label">Quittance N° :</td><td class="field-value">{_esc(data.quittance_3) or '................................'}</td></tr>
          <tr><td class="field-label">du :</td><td class="field-value">{_esc(data.date_quittance_3) or '....../....../......'}</td></tr>
        </table>
        <div class="signature-block">
          <div class="sig-box">Le Contribuable<br><br><br>Cachet et signature</div>
          <div class="sig-box">Le Caissier<br><br><br>Cachet et signature</div>
        </div>
      </div>

      <div class="note">(*) Sont exclus du paiement fractionné, les contribuables n'ayant pas souscrit leurs déclarations dans le délai imparti.</div>
    </div>
  </div>
  {_minimum_ifu_html(calc, data)}
</div>"""


def _revenu_net_html(calc: G12Calculations, data: G12FormData) -> str:
    """Section IV — Revenu net (Définitive only)."""
    return f"""<div class="section">
  <div class="section-title">IV - REVENU NET CORRESPONDANT AU CHIFFRE D'AFFAIRES DÉCLARÉ (EN DA)</div>
  <div class="section-title-ar">IV - صافي الدخل المقابل لرقم الأعمال المصرح به (دج)</div>
  <table class="fields-table">
    <tr>
      <td class="field-label">Revenu net :</td>
      <td class="field-value"><strong>{_fmt(calc.revenu_net)} DA</strong></td>
      <td class="field-label">صافي الدخل :</td>
    </tr>
  </table>
  <div class="attestation">
    J'atteste de l'exactitude des renseignements portés sur la présente déclaration.
  </div>
  <div class="signature-block">
    <div class="sig-box">Le Contribuable<br><br><br>Cachet et signature</div>
    <div class="sig-box">L'Inspecteur des Impôts<br><br><br>Cachet et signature</div>
  </div>
</div>"""


def _legal_page_html() -> str:
    """Legal text page."""
    paragraphs = LEGAL_TEXT.split("\n\n")
    content = ""
    for p in paragraphs:
        if p.startswith("Rappel"):
            content += f"<h3>{p}</h3>"
        else:
            content += f"<p>{p}</p>"
    return f"""<div class="page legal-page">
  <div class="page-header">SÉRIE G N°12 - RAPPEL DU RÉGIME IFU</div>
  {content}
</div>"""


def _css() -> str:
    """Complete CSS for official form styling."""
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
  .legal-ref { font-size: 8pt; color: #666; margin-top: 3px; }
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
  .checkbox-table td { border: none; padding: 2px 8px; font-size: 8pt; }
  .checkbox-cell { white-space: nowrap; }
  .nouveau-box { margin: 5px 0; padding: 5px; border: 1px solid #ccc; font-size: 9pt; }

  /* CA Table */
  .ca-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .ca-table th, .ca-table td { border: 1px solid #000; padding: 4px 6px; font-size: 8.5pt; text-align: center; }
  .ca-table th { background: #f0f0f0; font-weight: bold; }
  .ca-table .activity { text-align: left; }
  .ca-table .rate { font-weight: bold; }
  .ca-table .num { font-family: 'Courier New', monospace; font-size: 9pt; }
  .ca-table .ar { font-size: 8pt; color: #666; direction: rtl; }
  .ca-table .total-row { background: #f8f8f8; font-weight: bold; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .ifu-total-line { font-size: 11pt; font-weight: bold; text-align: right; margin: 10px 0; padding: 8px; border: 2px solid #000; background: #f0f0f0; }

  /* Payment */
  .payment-box { border: 1px solid #ccc; padding: 10px; margin: 8px 0; }
  .payment-option { margin: 5px 0; }
  .payment-detail { font-size: 9pt; color: #555; margin: 3px 0; }
  .tranche { border: 1px solid #ddd; padding: 8px; margin: 8px 0; background: #fafafa; }
  .payment-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .payment-table td { padding: 3px 5px; font-size: 9pt; border: none; }

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


# ── Main Generators ───────────────────────────────────────────────────────────

def generate_g12_prévisionnelle(data: G12FormData) -> str:
    """Generate complete G12 Prévisionnelle (forecast) form as HTML."""
    calc = calculate_g12(data, is_definitive=False)

    html = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G12 Prévisionnelle — IFU {data.year}</title>
{_css()}
</head>
<body>

{_header_html("prévisionnelle", data.year)}
{_dgi_hierarchy_html(data)}
{_identification_html(data, show_phone=False, show_nouveau=False)}

{_ca_table_html(
    data.ca_production_imposable, data.ca_production_exonere,
    data.ca_services_imposable, data.ca_services_exonere,
    data.ca_auto_entrepreneur_imposable, data.ca_auto_entrepreneur_exonere,
    calc,
    title="II - CHIFFRE D'AFFAIRES / RECETTES PROFESSIONNELLES PRÉVISIONNELS (DA)",
    title_ar="II - رقم الأعمال / الإيرادات المهنية التقديرية (دج)",
)}

{_payment_integral_html(calc, data) if data.mode_paiement == "integral" else _payment_fractionne_html(calc, data)}

{_legal_page_html()}

</body>
</html>"""

    hook_generation("g12_previsionnelle", {"year": data.year, "nif": data.nif}, html)
    return html


def generate_g12_définitive(data: G12FormData) -> str:
    """Generate complete G12 Définitive (final) form as HTML."""
    calc = calculate_g12(data, is_definitive=True)

    html = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G12 Définitive — IFU {data.year}</title>
{_css()}
</head>
<body>

{_header_html("définitive", data.year)}
{_dgi_hierarchy_html(data)}
{_identification_html(data, show_phone=True, show_nouveau=True)}
{_salaires_html(data)}

{_ca_table_html(
    data.ca_production_imposable, data.ca_production_exonere,
    data.ca_services_imposable, data.ca_services_exonere,
    data.ca_auto_entrepreneur_imposable, data.ca_auto_entrepreneur_exonere,
    calc,
    title="III - CHIFFRE D'AFFAIRES / RECETTES PROFESSIONNELLES DÉFINITIFS (EN DA)",
    title_ar="III - رقم الأعمال / الإيرادات المهنية النهائية (دج)",
    show_complementaire=True,
    ca_realise=(
        data.ca_realise_production_imposable, data.ca_realise_production_exonere,
        data.ca_realise_services_imposable, data.ca_realise_services_exonere,
        data.ca_realise_auto_imposable, data.ca_realise_auto_exonere,
    ),
)}

{_marge_html(data, calc, is_definitive=True)}

{_revenu_net_html(calc, data)}

{_legal_page_html()}

</body>
</html>"""

    hook_generation("g12_definitive", {"year": data.year, "nif": data.nif}, html)
    return html


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = G12FormData(
        diw="DIW D'EL BAYADH",
        recette="Recette des Impôts d'El Bayadh Centre",
        commune="El Bayadh Centre",
        nom_prenoms="SARL TECH SOLUTIONS",
        activite_exercee="Prestation de services informatiques",
        date_debut="01/01/2024",
        adresse_activite="123 Rue Didouche Mourad, El Bayadh",
        wilaya_activite="32 - El Bayadh",
        adresse_domicile="123 Rue Didouche Mourad, El Bayadh",
        wilaya_domicile="32 - El Bayadh",
        nif="1234567890",
        nin="199603061234567",
        article_imposition="1234",
        telephone="0555081718",
        ca_services_imposable=4_800_000,
        year=2025,
        mode_paiement="fractionne",
        beneficiaire="Ahmed Benali",
    )

    calc = calculate_g12(sample, is_definitive=False)
    print(f"IFU Total: {_fmt(calc.ifu_total)} DA")
    print(f"  Production: {_fmt(calc.ifu_production)} DA")
    print(f"  Services: {_fmt(calc.ifu_services)} DA")
    print(f"  Auto: {_fmt(calc.ifu_auto)} DA")
    print(f"  Minimum: {_fmt(calc.ifu_minimum)} DA")
    print(f"Mode: {sample.mode_paiement}")
    if sample.mode_paiement == "fractionne":
        print(f"  1ère: {_fmt(calc.tranche_1)} DA")
        print(f"  2ème: {_fmt(calc.tranche_2)} DA")
        print(f"  3ème: {_fmt(calc.tranche_3)} DA")

    if "--html" in sys.argv:
        html = generate_g12_prévisionnelle(sample)
        out = "g12_prévisionnelle_official.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out}")

        # Also generate définitive
        sample.ca_realise_services_imposable = 5_500_000
        sample.nombre_salaries = 4
        sample.salaires_brut = 4_800_000
        sample.charges_sociales = 1_248_000
        sample.irg_annuel = 336_000
        html2 = generate_g12_définitive(sample)
        out2 = "g12_définitive_official.html"
        with open(out2, "w", encoding="utf-8") as f:
            f.write(html2)
        print(f"HTML written to {out2}")
