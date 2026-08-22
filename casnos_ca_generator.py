"""CASNOS CA Declaration Generator — Déclaration du Chiffre d'Affaires.

Generates the annual CA declaration form for CASNOS contributors.
Used by liberal professionals to declare their annual revenue for
social security contribution calculation.

Legal reference: Loi 83-11 du 02/07/1983, Décret 94-08 du 26/01/1994.

Usage:
    from casnos_ca_generator import CasnosCAData, generate_casnos_ca

    data = CasnosCAData(nom="BENALI", ca_annee_courante=2_400_000)
    html = generate_casnos_ca(data)
"""

from __future__ import annotations
import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass
from datetime import datetime


def _esc(value, default=""):
    if value:
        return _html_mod.escape(str(value))
    return default


def _field(value, width=40):
    return _html_mod.escape(str(value)) if value else "." * width


def _fmt(n):
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


@dataclass
class CasnosCAData:
    nom: str = ""
    prenom: str = ""
    nif: str = ""
    nin: str = ""
    cnas_numero: str = ""
    activite: str = ""
    date_debut: str = ""
    adresse: str = ""
    commune: str = ""
    wilaya: str = ""
    ca_annee_courante: float = 0
    ca_annee_precedente: float = 0
    charges_locatives: float = 0
    charges_materiel: float = 0
    charges_assurance: float = 0
    charges_autres: float = 0
    year: int = datetime.now().year
    beneficiaire: str = ""


def calculate_casnos_ca(data: CasnosCAData) -> dict:
    """Calculate CASNOS contribution based on CA declaration."""
    taux = 0.15
    contribution_brute = data.ca_annee_courante * taux

    total_charges = (
        data.charges_locatives + data.charges_materiel
        + data.charges_assurance + data.charges_autres
    )

    deduction_charges = total_charges * 0.5
    contribution_nette = max(0, contribution_brute - deduction_charges)
    cotisation_annuelle = contribution_nette
    cotisation_mensuelle = cotisation_annuelle / 12
    minimum_mensuel = 3_000
    cotisation_mensuelle = max(cotisation_mensuelle, minimum_mensuel)

    return {
        "ca_annee": data.ca_annee_courante,
        "taux": taux,
        "contribution_brute": round(contribution_brute, 2),
        "total_charges": round(total_charges, 2),
        "deduction_charges": round(deduction_charges, 2),
        "contribution_nette": round(contribution_nette, 2),
        "cotisation_annuelle": round(cotisation_annuelle, 2),
        "cotisation_mensuelle": round(cotisation_mensuelle, 2),
        "minimum_mensuel": minimum_mensuel,
    }


def generate_casnos_ca(data: CasnosCAData) -> str:
    """Generate CASNOS CA declaration form as HTML."""
    calc = calculate_casnos_ca(data)

    html = (
        '<!DOCTYPE html>\n<html lang="fr" dir="ltr">\n<head>\n'
        '<meta charset="UTF-8">\n'
        f'<title>CASNOS — Déclaration CA {data.year} — {data.nom} {data.prenom}</title>\n'
        '<style>\n'
        '  @page { size: A4; margin: 15mm; }\n'
        "  body { font-family: 'Times New Roman', serif; font-size: 10pt; color: #1a1a1a; margin: 0; padding: 20px; line-height: 1.5; }\n"
        '  .header { text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 15px; }\n'
        '  .header .republique { font-size: 9pt; letter-spacing: 1px; }\n'
        '  .header .dgi { font-size: 11pt; font-weight: bold; margin: 4px 0; }\n'
        '  .header h1 { font-size: 14pt; margin: 6px 0; }\n'
        '  .header .subtitle { font-size: 10pt; color: #444; }\n'
        '  .section { margin: 12px 0; page-break-inside: avoid; }\n'
        '  .section-title { font-size: 10.5pt; font-weight: bold; border-bottom: 2px solid #000; padding-bottom: 3px; margin-bottom: 6px; }\n'
        '  .fields-table { width: 100%; border-collapse: collapse; }\n'
        '  .fields-table td { padding: 4px 5px; font-size: 9.5pt; vertical-align: top; }\n'
        '  .field-label { font-weight: bold; width: 38%; }\n'
        '  .field-value { border-bottom: 1px dotted #999; }\n'
        '  .ca-table { width: 100%; border-collapse: collapse; margin: 5px 0; }\n'
        '  .ca-table th, .ca-table td { border: 1px solid #000; padding: 5px 8px; font-size: 9pt; text-align: center; }\n'
        '  .ca-table th { background: #f0f0f0; }\n'
        "  .ca-table .num { font-family: 'Courier New', monospace; text-align: right; }\n"
        '  .total-row { background: #f8f8f8; font-weight: bold; }\n'
        '  .note { font-size: 8.5pt; color: #666; font-style: italic; margin-top: 5px; }\n'
        '  .signature-block { display: flex; justify-content: space-between; margin: 20px 0; }\n'
        '  .sig-box { width: 45%; text-align: center; font-size: 9.5pt; border-top: 1px solid #000; padding-top: 8px; min-height: 100px; }\n'
        '  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 8px; border: 1px solid #ccc; background: #fafafa; }\n'
        '  @media print { body { padding: 0; } }\n'
        '</style>\n</head>\n<body>\n\n'
        '<div class="header">\n'
        '  <div class="republique">REPUBLIQUE ALGERIENNE DEMOCRATIQUE ET POPULAIRE</div>\n'
        '  <div class="dgi">CAISSE NATIONALE DE SECURITE SOCIALE DES TRAVAILLEURS NON SALARIES</div>\n'
        '  <h1>DECLARATION DU CHIFFRE D\'AFFAIRES</h1>\n'
        f'  <div class="subtitle">Regime de la CASNOS — Annee {data.year}</div>\n'
        '</div>\n\n'

        '<div class="section">\n'
        '  <div class="section-title">I — IDENTITE DU CONTRIBUABLE</div>\n'
        '  <table class="fields-table">\n'
        f'    <tr><td class="field-label">Nom :</td><td class="field-value">{_field(data.nom, 30)}</td></tr>\n'
        f'    <tr><td class="field-label">Prenom :</td><td class="field-value">{_field(data.prenom, 30)}</td></tr>\n'
        f'    <tr><td class="field-label">NIF :</td><td class="field-value">{_field(data.nif, 25)}</td></tr>\n'
        f'    <tr><td class="field-label">NIN :</td><td class="field-value">{_field(data.nin, 25)}</td></tr>\n'
        f'    <tr><td class="field-label">N CNAS :</td><td class="field-value">{_field(data.cnas_numero, 25)}</td></tr>\n'
        f'    <tr><td class="field-label">Activite :</td><td class="field-value">{_field(data.activite, 40)}</td></tr>\n'
        f'    <tr><td class="field-label">Date debut activite :</td><td class="field-value">{_esc(data.date_debut) or "....../....../......"}</td></tr>\n'
        f'    <tr><td class="field-label">Adresse :</td><td class="field-value">{_field(data.adresse, 45)}</td></tr>\n'
        f'    <tr><td class="field-label">Commune :</td><td class="field-value">{_field(data.commune, 25)}</td></tr>\n'
        f'    <tr><td class="field-label">Wilaya :</td><td class="field-value">{_esc(data.wilaya) or "......"}</td></tr>\n'
        '  </table>\n</div>\n\n'

        '<div class="section">\n'
        '  <div class="section-title">II — CHIFFRE D\'AFFAIRES DECLARE</div>\n'
        '  <table class="ca-table">\n'
        '    <thead><tr><th>Element</th><th>Montant (DA)</th></tr></thead>\n'
        '    <tbody>\n'
        f'      <tr><td>CA annee {data.year} (courante)</td><td class="num">{_fmt(data.ca_annee_courante)}</td></tr>\n'
        f'      <tr><td>CA annee {data.year - 1} (precedente)</td><td class="num">{_fmt(data.ca_annee_precedente)}</td></tr>\n'
        '      <tr><td>Taux de cotisation</td><td class="num">15%</td></tr>\n'
        f'      <tr><td><strong>Contribution brute (15% x CA)</strong></td><td class="num"><strong>{_fmt(calc["contribution_brute"])}</strong></td></tr>\n'
        '    </tbody>\n  </table>\n</div>\n\n'

        '<div class="section">\n'
        '  <div class="section-title">III — CHARGES DEDUCTIBLES</div>\n'
        '  <table class="ca-table">\n'
        '    <thead><tr><th>Type de charge</th><th>Montant (DA)</th></tr></thead>\n'
        '    <tbody>\n'
        f'      <tr><td>Charges locatives</td><td class="num">{_fmt(data.charges_locatives)}</td></tr>\n'
        f'      <tr><td>Charges materiel</td><td class="num">{_fmt(data.charges_materiel)}</td></tr>\n'
        f'      <tr><td>Charges assurance</td><td class="num">{_fmt(data.charges_assurance)}</td></tr>\n'
        f'      <tr><td>Charges autres</td><td class="num">{_fmt(data.charges_autres)}</td></tr>\n'
        f'      <tr class="total-row"><td>Total charges</td><td class="num">{_fmt(calc["total_charges"])}</td></tr>\n'
        f'      <tr><td>Deduction (50% des charges)</td><td class="num">{_fmt(calc["deduction_charges"])}</td></tr>\n'
        '    </tbody>\n  </table>\n'
        '  <div class="note">Art. 33 du Décret 94-08 : les charges déductibles sont admises à hauteur de 50% du total déclaré.</div>\n'
        '</div>\n\n'

        '<div class="section">\n'
        '  <div class="section-title">IV — COTISATION A PAYER</div>\n'
        '  <table class="ca-table">\n'
        '    <thead><tr><th>Element</th><th>Montant (DA)</th></tr></thead>\n'
        '    <tbody>\n'
        f'      <tr><td>Contribution brute</td><td class="num">{_fmt(calc["contribution_brute"])}</td></tr>\n'
        f'      <tr><td>Deduction charges (50%)</td><td class="num">{_fmt(calc["deduction_charges"])}</td></tr>\n'
        f'      <tr class="total-row"><td><strong>Contribution nette annuelle</strong></td><td class="num"><strong>{_fmt(calc["contribution_nette"])}</strong></td></tr>\n'
        f'      <tr><td>Cotisation mensuelle</td><td class="num">{_fmt(calc["cotisation_mensuelle"])}</td></tr>\n'
        f'      <tr><td>Minimum mensuel applicable</td><td class="num">{_fmt(calc["minimum_mensuel"])}</td></tr>\n'
        '    </tbody>\n  </table>\n'
        '  <div class="note">La cotisation minimale mensuelle est fixée à 3 000 DA — Art. 23 de la Loi 83-11.</div>\n'
        '</div>\n\n'

        '<div class="section">\n'
        '  <div class="attestation">\n'
        '    Je soussigné(e), ' + _esc(data.prenom) + ' ' + _esc(data.nom) + ', déclare sur l\'honneur que les renseignements\n'
        '    fournis ci-dessus sont exacts et complets. Je m\'engage à signaler toute modification\n'
        '    survenue dans les éléments déclarés dans un délai de 30 jours suivant la modification.\n'
        '  </div>\n\n'

        '  <div class="signature-block">\n'
        '    <div class="sig-box">\n'
        '      <strong>Signature du déclarant</strong>\n'
        '      <br><br><br><br>\n'
        '      <div style="font-size:8pt; color:#999;">Cachet</div>\n'
        '    </div>\n'
        '    <div class="sig-box">\n'
        '      <strong>Agent CASNOS</strong>\n'
        '      <br><br><br><br>\n'
        '      <div style="font-size:8pt; color:#999;">Cachet et visa</div>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>\n\n'

        '</body>\n</html>'
    )

    hook_generation(
        "casnos_ca",
        {"nom": data.nom, "prenom": data.prenom, "nif": data.nif, "year": data.year},
        html,
    )
    return html


if __name__ == "__main__":
    import sys

    sample = CasnosCAData(
        nom="BENALI",
        prenom="Ahmed",
        nif="1234567890",
        nin="199003151234567",
        cnas_numero="CNAS-2024-00123",
        activite="Développeur web freelance",
        date_debut="01/01/2023",
        adresse="123 Rue Didouche Mourad",
        commune="Alger Centre",
        wilaya="16-Alger",
        ca_annee_courante=2_400_000,
        ca_annee_precedente=1_800_000,
        charges_locatives=360_000,
        charges_materiel=120_000,
        charges_assurance=48_000,
        charges_autres=36_000,
        beneficiaire="Ahmed Benali",
    )

    calc = calculate_casnos_ca(sample)
    print(f"CA declare     : {_fmt(calc['ca_annee'])} DA")
    print(f"Contribution   : {_fmt(calc['contribution_nette'])} DA")
    print(f"Mensuelle      : {_fmt(calc['cotisation_mensuelle'])} DA/mois")

    if "--html" in sys.argv:
        html = generate_casnos_ca(sample)
        with open("casnos_ca.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML written to casnos_ca.html")
