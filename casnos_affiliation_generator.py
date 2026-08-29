"""CASNOS Affiliation Generator — Demande d'affiliation au régime de la CNAS.

Generates the affiliation request form for liberal professionals and
auto-entrepreneurs registering with CASNOS (Caisse Nationale de Sécurité
Sociale des Travailleurs Non Salariés).

Legal reference: Loi 83-11 du 02/07/1983 modifiée, Décret 94-08 du 26/01/1994.

Usage:
    from casnos_affiliation_generator import CasnosAffiliationData, generate_casnos_affiliation

    data = CasnosAffiliationData(nom="BENALI", prenom="Ahmed", activite="Médecin")
    html = generate_casnos_affiliation(data)
"""

from __future__ import annotations
import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass
from datetime import datetime

from policy_constants import CASNOS_MIN_MONTHLY, CASNOS_RATE


def _esc(value, default=""):
    if value:
        return _html_mod.escape(str(value))
    return default


def _field(value, width=40):
    return _html_mod.escape(str(value)) if value else "." * width


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

CATEGORIES_ACTIVITE = [
    "Professions libérales (médecin, avocat, expert-comptable...)",
    "Professions paramédicales (infirmier, kinésithérapeute...)",
    "Enseignants et formateurs",
    "Commerçants",
    "Artisans",
    "Industriels",
    "Agriculteurs",
    "Activités informatiques et digitales",
    "Autres activités non salariées",
]


@dataclass
class CasnosAffiliationData:
    # Identité
    nom: str = ""
    prenom: str = ""
    date_naissance: str = ""
    lieu_naissance: str = ""
    nin: str = ""
    sit_familiale: str = "Célibataire"

    # Activité
    activite_principale: str = ""
    category_activite: str = ""
    date_debut_activite: str = ""
    numero_rc: str = ""
    nif: str = ""

    # Adresse
    adresse_siege: str = ""
    commune: str = ""
    wilaya: str = ""
    telephone: str = ""
    email: str = ""

    # Revenus
    revenu_annuel_previsionnel: float = 0
    revenu_annuel_n_1: float = 0

    # Banque
    banque: str = ""
    rib: str = ""

    # Signature
    date_signature: str = ""
    beneficiaire: str = ""

    year: int = datetime.now().year


def calculate_casnos_affiliation(data: CasnosAffiliationData) -> dict:
    """Calculate CASNOS affiliation fees and monthly contributions."""
    # Contribution = CASNOS_RATE of annual revenue
    contribution_annuelle = data.revenu_annuel_previsionnel * CASNOS_RATE
    # Minimum: CASNOS_MIN_MONTHLY (15% of SMIG ≈ 20,000 DA/month SMIG) — annualized as CASNOS_MIN_MONTHLY * 12
    minimum_mensuel = CASNOS_MIN_MONTHLY  # compatibility alias
    minimum_annuel = CASNOS_MIN_MONTHLY * 12  # keep annualization visible, no flat annual literal
    contribution_annuelle = max(contribution_annuelle, minimum_annuel)
    contribution_mensuelle = contribution_annuelle / 12

    # Frais d'affiliation (one-time)
    frais_affiliation = 5_000

    return {
        "revenu_annuel": data.revenu_annuel_previsionnel,
        "taux": CASNOS_RATE,  # compatibility alias
        "contribution_annuelle": round(contribution_annuelle, 2),
        "contribution_mensuelle": round(contribution_mensuelle, 2),
        "minimum_mensuel": minimum_mensuel,
        "frais_affiliation": frais_affiliation,
        "cotisation_arriere": round(max(0, (datetime.now().month - 1) * contribution_mensuelle), 2),
    }


def generate_casnos_affiliation(data: CasnosAffiliationData) -> str:
    """Generate CASNOS affiliation request form as HTML."""
    calc = calculate_casnos_affiliation(data)

    html = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>CASNOS — Demande d'affiliation — {data.nom} {data.prenom}</title>
<style>
  @page {{ size: A4; margin: 15mm; }}
  body {{ font-family: 'Times New Roman', serif; font-size: 10pt; color: #1a1a1a; margin: 0; padding: 20px; line-height: 1.5; }}
  .header {{ text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 15px; }}
  .header .republique {{ font-size: 9pt; letter-spacing: 1px; }}
  .header .dgi {{ font-size: 11pt; font-weight: bold; margin: 4px 0; }}
  .header h1 {{ font-size: 14pt; margin: 6px 0; }}
  .header .subtitle {{ font-size: 10pt; color: #444; }}
  .section {{ margin: 12px 0; page-break-inside: avoid; }}
  .section-title {{ font-size: 10.5pt; font-weight: bold; border-bottom: 2px solid #000; padding-bottom: 3px; margin-bottom: 6px; }}
  .fields-table {{ width: 100%; border-collapse: collapse; }}
  .fields-table td {{ padding: 4px 5px; font-size: 9.5pt; vertical-align: top; }}
  .field-label {{ font-weight: bold; width: 38%; }}
  .field-value {{ border-bottom: 1px dotted #999; }}
  .ca-table {{ width: 100%; border-collapse: collapse; margin: 5px 0; }}
  .ca-table th, .ca-table td {{ border: 1px solid #000; padding: 5px 8px; font-size: 9pt; text-align: center; }}
  .ca-table th {{ background: #f0f0f0; }}
  .ca-table .num {{ font-family: 'Courier New', monospace; text-align: right; }}
  .note {{ font-size: 8.5pt; color: #666; font-style: italic; margin-top: 5px; }}
  .signature-block {{ display: flex; justify-content: space-between; margin: 20px 0; }}
  .sig-box {{ width: 45%; text-align: center; font-size: 9.5pt; border-top: 1px solid #000; padding-top: 8px; min-height: 100px; }}
  .attestation {{ font-size: 9pt; font-style: italic; margin: 10px 0; padding: 8px; border: 1px solid #ccc; background: #fafafa; }}
  @media print {{ body {{ padding: 0; }} }}
</style>
</head>
<body>

<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">CAISSE NATIONALE DE SÉCURITÉ SOCIALE DES TRAVAILLEURS NON SALARIÉS</div>
  <h1>DEMANDE D'AFFILIATION</h1>
  <div class="subtitle">Régime de la CNAS — Travailleurs Non Salariés</div>
  <div class="subtitle">Année {data.year}</div>
</div>

<div class="section">
  <div class="section-title">I — IDENTITÉ DU DEMANDEUR</div>
  <table class="fields-table">
    <tr><td class="field-label">Nom :</td><td class="field-value">{_field(data.nom, 30)}</td></tr>
    <tr><td class="field-label">Prénom :</td><td class="field-value">{_field(data.prenom, 30)}</td></tr>
    <tr><td class="field-label">Date et lieu de naissance :</td><td class="field-value">{_esc(data.date_naissance) or '....../....../......'} à {_field(data.lieu_naissance, 20)}</td></tr>
    <tr><td class="field-label">NIN (Numéro d'Identification Nationale) :</td><td class="field-value">{_field(data.nin, 30)}</td></tr>
    <tr><td class="field-label">Situation familiale :</td><td class="field-value">{_esc(data.sit_familiale)}</td></tr>
  </table>
</div>

<div class="section">
  <div class="section-title">II — ACTIVITÉ</div>
  <table class="fields-table">
    <tr><td class="field-label">Activité principale :</td><td class="field-value" colspan="2">{_field(data.activite_principale, 50)}</td></tr>
    <tr><td class="field-label">Catégorie :</td><td class="field-value" colspan="2">{_esc(data.category_activite) or 'Sélectionner...'}</td></tr>
    <tr><td class="field-label">Date de début d'activité :</td><td class="field-value">{_esc(data.date_debut_activite) or '....../....../......'}</td></tr>
    <tr><td class="field-label">Numéro RC (le cas échéant) :</td><td class="field-value">{_field(data.numero_rc, 25)}</td></tr>
    <tr><td class="field-label">NIF :</td><td class="field-value">{_field(data.nif, 25)}</td></tr>
  </table>
</div>

<div class="section">
  <div class="section-title">III — ADRESSE DU SIÈGE</div>
  <table class="fields-table">
    <tr><td class="field-label">Adresse :</td><td class="field-value" colspan="2">{_field(data.adresse_siege, 50)}</td></tr>
    <tr><td class="field-label">Commune :</td><td class="field-value">{_field(data.commune, 25)}</td></tr>
    <tr><td class="field-label">Wilaya :</td><td class="field-value">{_esc(data.wilaya) or '......'}</td></tr>
    <tr><td class="field-label">Téléphone :</td><td class="field-value">{_esc(data.telephone) or '................'}</td></tr>
    <tr><td class="field-label">Email :</td><td class="field-value">{_field(data.email, 35)}</td></tr>
  </table>
</div>

<div class="section">
  <div class="section-title">IV — REVENUS ET Cotisations</div>
  <table class="ca-table">
    <thead>
      <tr><th>Élément</th><th>Montant (DA)</th></tr>
    </thead>
    <tbody>
      <tr><td>Revenu annuel prévu (N)</td><td class="num">{data.revenu_annuel_previsionnel:,.0f}</td></tr>
      <tr><td>Revenu N-1 (le cas échéant)</td><td class="num">{data.revenu_annuel_n_1:,.0f}</td></tr>
      <tr><td>Taux de cotisation</td><td class="num">15%</td></tr>
      <tr><td><strong>Cotisation annuelle</strong></td><td class="num"><strong>{calc['contribution_annuelle']:,.0f}</strong></td></tr>
      <tr><td><strong>Cotisation mensuelle</strong></td><td class="num"><strong>{calc['contribution_mensuelle']:,.0f}</strong></td></tr>
      <tr><td>Frais d'affiliation (one-time)</td><td class="num">{calc['frais_affiliation']:,.0f}</td></tr>
    </tbody>
  </table>
  <div class="note">La cotisation minimale mensuelle est fixée à 3 000 DA — Art. 23 de la Loi 83-11.</div>
</div>

<div class="section">
  <div class="section-title">V — COORDONNÉES BANCAIRES</div>
  <table class="fields-table">
    <tr><td class="field-label">Banque :</td><td class="field-value">{_field(data.banque, 35)}</td></tr>
    <tr><td class="field-label">RIB :</td><td class="field-value">{_field(data.rib, 30)}</td></tr>
  </table>
</div>

<div class="section">
  <div class="attestation">
    Je soussigné(e), {_esc(data.prenom)} {_esc(data.nom)}, certifie l'exactitude des renseignements fournis ci-dessus.
    Je m'engage à déclarer toute modification survenue dans les éléments déclarés dans les 30 jours suivant la modification.
  </div>

  <div class="signature-block">
    <div class="sig-box">
      <strong>Signature du demandeur</strong><br><br><br><br>
      <div style="font-size:8pt; color:#999;">Cachet</div>
    </div>
    <div class="sig-box">
      <strong>Agent CNAS</strong><br><br><br><br>
      <div style="font-size:8pt; color:#999;">Cachet et signature</div>
    </div>
  </div>
</div>

</body>
</html>"""

    hook_generation("casnos_affiliation", {"nom": data.nom, "prenom": data.prenom, "nif": data.nif}, html)
    return html


if __name__ == "__main__":
    import sys
    sample = CasnosAffiliationData(
        nom="BENALI", prenom="Ahmed",
        date_naissance="15/03/1990", lieu_naissance="Alger",
        nin="199003151234567", sit_familiale="Marié(e)",
        activite_principale="Développeur web freelance",
        category_activite="Activités informatiques et digitales",
        date_debut_activite="01/01/2024",
        nif="1234567890",
        adresse_siege="123 Rue Didouche Mourad, Alger",
        commune="Alger Centre", wilaya="16-Alger",
        telephone="0555081718", email="ahmed.benali@email.com",
        revenu_annuel_previsionnel=2_400_000,
        banque="BNA", rib="00799999001234567890",
        beneficiaire="Ahmed Benali",
    )
    calc = calculate_casnos_affiliation(sample)
    print(f"Cotisation annuelle: {calc['contribution_annuelle']:,.0f} DA")
    print(f"Cotisation mensuelle: {calc['contribution_mensuelle']:,.0f} DA")
    if "--html" in sys.argv:
        html = generate_casnos_affiliation(sample)
        with open("casnos_affiliation.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML written to casnos_affiliation.html")
