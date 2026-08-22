"""G12 Bis - Declaration definitive du chiffre d'affaires (Auto-entrepreneur IFU).

Imprime la declaration G12 Bis (Serie G N12 Bis) pour les auto-entrepreneurs
soumis a l'Impot Forfaitaire Unique (IFU) au taux de 0,5 %.
Ref. legale : Art. 282 quater du Code de l'Impot Direct et des Taxes Assimilees (CIDTA).

Usage:
    from g12_bis_generator import G12BisData, calculate_g12_bis, generate_g12_bis
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _esc(value, default=""):
    """Return an HTML-safe string for *value*."""
    if value is None:
        return _html_mod.escape(str(default))
    return _html_mod.escape(str(value))


def _field(value, width=40):
    """Right-pad *value* to *width* characters."""
    return str(value).ljust(width)


def _fmt(n):
    """Format a number with spaces as thousand-separators, no decimals."""
    if n is None or n == "":
        return "0"
    return f"{int(round(float(n))):,}".replace(",", " ")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class G12BisData:
    """All fields required to populate the G12 Bis form."""

    nom_prenoms: str = ""
    nif: str = ""
    nin: str = ""
    activite: str = ""
    date_debut: str = ""
    adresse: str = ""
    commune: str = ""
    wilaya: str = ""
    ca_previsionnel: float = 0          # CA declare au titre de l'AC
    ca_realise: float = 0               # CA realise au titre de l'annee
    nombre_salaries: int = 0
    salaires_brut: float = 0
    irg_annuel: float = 0
    year: int = datetime.now().year
    beneficiaire: str = ""


# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------

def calculate_g12_bis(data: G12BisData) -> dict:
    """Compute derived values for the G12 Bis declaration."""
    ifu_previsionnel = data.ca_previsionnel * 0.005
    ifu_minimum = 10_000
    ifu_previsionnel = max(ifu_previsionnel, ifu_minimum)

    ifu_realise = data.ca_realise * 0.005
    ifu_complementaire = max(0.0, ifu_realise - ifu_previsionnel)
    ifu_total = ifu_previsionnel + ifu_complementaire
    ca_ecart = data.ca_realise - data.ca_previsionnel
    revenu_net = data.ca_realise - ifu_total

    return {
        "ifu_previsionnel": ifu_previsionnel,
        "ifu_realise": ifu_realise,
        "ifu_minimum": ifu_minimum,
        "ifu_complementaire": ifu_complementaire,
        "ifu_total": ifu_total,
        "ca_ecart": ca_ecart,
        "revenu_net": revenu_net,
    }


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_g12_bis(data: G12BisData) -> str:
    """Return the full HTML document for the G12 Bis declaration."""
    c = calculate_g12_bis(data)

    html = ""
    html += "<!DOCTYPE html>"
    html += "<html lang='fr'>"
    html += "<head>"
    html += "<meta charset='UTF-8'>"
    html += "<title>G12 Bis - Declaration Definitive CA Auto-entrepreneur</title>"
    html += "<style>"
    html += "  * { box-sizing: border-box; margin: 0; padding: 0; }"
    html += "  body { font-family: 'Tahoma', 'Arial', sans-serif; font-size: 11pt; color: #000; background: #fff; padding: 20px; }"
    html += "  .page { width: 210mm; margin: 0 auto; border: 2px solid #000; padding: 15px; }"
    html += "  h1 { text-align: center; font-size: 14pt; margin-bottom: 2px; letter-spacing: 1px; }"
    html += "  h2 { text-align: center; font-size: 12pt; margin-bottom: 2px; }"
    html += "  h3 { text-align: center; font-size: 11pt; font-weight: normal; margin-bottom: 10px; color: #333; }"
    html += "  .section-title { background: #e8e8e8; border: 1px solid #000; padding: 4px 8px; font-weight: bold; font-size: 11pt; margin: 12px 0 6px 0; }"
    html += "  .field-row { display: flex; margin-bottom: 4px; }"
    html += "  .field-label { font-weight: bold; min-width: 180px; }"
    html += "  .field-value { border-bottom: 1px solid #999; flex: 1; padding-left: 4px; min-height: 18px; }"
    html += "  table { width: 100%; border-collapse: collapse; margin: 8px 0; }"
    html += "  th, td { border: 1px solid #000; padding: 5px 6px; text-align: center; font-size: 10pt; }"
    html += "  th { background: #d9d9d9; font-weight: bold; }"
    html += "  .text-left { text-align: left; }"
    html += "  .text-right { text-align: right; }"
    html += "  .attestation { margin-top: 16px; padding: 10px; border: 1px solid #000; font-size: 10pt; line-height: 1.5; }"
    html += "  .sig-block { margin-top: 20px; display: flex; justify-content: space-between; }"
    html += "  .sig-box { width: 45%; text-align: center; }"
    html += "  .sig-line { border-top: 1px solid #000; margin-top: 50px; padding-top: 4px; font-size: 10pt; }"
    html += "  .footer-note { margin-top: 10px; font-size: 8pt; color: #666; text-align: center; }"
    html += "  @media print { body { padding: 0; } .page { border: none; padding: 10mm; } }"
    html += "</style>"
    html += "</head>"
    html += "<body>"
    html += "<div class='page'>"

    # -- Header --
    html += "<h1>SERIE G N&deg;12 Bis</h1>"
    html += "<h2>R&Eacute;GIME DE L'IMP&Ocirc;T FORFAITAIRE UNIQUE (IFU)</h2>"
    html += "<h3>D&Eacute;CLARATION D&Eacute;FINITIVE DU CHIFFRE D'AFFAIRES &mdash; AUTO-ENTREPRENEUR</h3>"
    html += "<h3 style='font-size:10pt; margin-bottom:4px;'>Ann&eacute;e : " + _esc(str(data.year)) + "</h3>"

    # -- Section I: Identification --
    html += "<div class='section-title'>SECTION I &mdash; IDENTIFICATION DU D&Eacute;CLARANT</div>"

    def _row(label, value):
        return ("<div class='field-row'>"
                "<span class='field-label'>" + _esc(label) + " :</span>"
                "<span class='field-value'>" + _esc(value) + "</span>"
                "</div>")

    html += _row("Nom et Pr&eacute;noms", data.nom_prenoms)
    html += _row("NIF", data.nif)
    html += _row("NIN", data.nin)
    html += _row("Activit&eacute; exerc&eacute;e", data.activite)
    html += _row("Date de d&eacute;but d'activit&eacute;", data.date_debut)
    html += _row("Adresse du si&egrave;ge", data.adresse)
    html += _row("Commune", data.commune)
    html += _row("Wilaya", data.wilaya)

    # -- Section II: CA table --
    html += "<div class='section-title'>SECTION II &mdash; CHIFFRE D'AFFAIRES</div>"
    html += "<table>"
    html += "<tr>"
    html += "  <th class='text-left'>D&eacute;signation</th>"
    html += "  <th>Taux</th>"
    html += "  <th>CA Pr&eacute;visionnel</th>"
    html += "  <th>CA R&eacute;alis&eacute;</th>"
    html += "  <th>&Eacute;cart</th>"
    html += "  <th>IFU d&ucirc;</th>"
    html += "</tr>"
    html += "<tr>"
    html += "  <td class='text-left'>Activit&eacute;s exerc&eacute;es sous le statut d'auto-entrepreneur</td>"
    html += "  <td>0,5 %</td>"
    html += "  <td>" + _fmt(data.ca_previsionnel) + " DA</td>"
    html += "  <td>" + _fmt(data.ca_realise) + " DA</td>"
    html += "  <td>" + _fmt(c["ca_ecart"]) + " DA</td>"
    html += "  <td>" + _fmt(c["ifu_total"]) + " DA</td>"
    html += "</tr>"
    html += "</table>"

    # -- Section III: Complement IFU --
    html += "<div class='section-title'>SECTION III &mdash; COMPL&Eacute;MENT D'IFU</div>"
    html += "<table>"
    html += "<tr>"
    html += "  <th class='text-left'>D&eacute;signation</th>"
    html += "  <th>Montant (DA)</th>"
    html += "</tr>"
    html += "<tr>"
    html += "  <td class='text-left'>IFU vers&eacute; au titre de l'acompte provisionnel</td>"
    html += "  <td>" + _fmt(c["ifu_previsionnel"]) + " DA</td>"
    html += "</tr>"
    html += "<tr>"
    html += "  <td class='text-left'>IFU minimum (plafond auto-entrepreneur)</td>"
    html += "  <td>" + _fmt(c["ifu_minimum"]) + " DA</td>"
    html += "</tr>"
    html += "<tr>"
    html += "  <td class='text-left'>IFU sur CA r&eacute;alis&eacute;</td>"
    html += "  <td>" + _fmt(c["ifu_realise"]) + " DA</td>"
    html += "</tr>"
    html += "<tr>"
    html += "  <td class='text-left'><b>Compl&eacute;ment IFU &agrave; verser</b></td>"
    html += "  <td><b>" + _fmt(c["ifu_complementaire"]) + " DA</b></td>"
    html += "</tr>"
    html += "</table>"

    # -- Section IV: Revenu net --
    html += "<div class='section-title'>SECTION IV &mdash; REVENU NET</div>"
    html += "<table>"
    html += "<tr>"
    html += "  <th class='text-left'>D&eacute;signation</th>"
    html += "  <th>Montant (DA)</th>"
    html += "</tr>"
    html += "<tr>"
    html += "  <td class='text-left'>Chiffre d'affaires r&eacute;alis&eacute;</td>"
    html += "  <td>" + _fmt(data.ca_realise) + " DA</td>"
    html += "</tr>"
    html += "<tr>"
    html += "  <td class='text-left'>IFU total d&ucirc;</td>"
    html += "  <td>" + _fmt(c["ifu_total"]) + " DA</td>"
    html += "</tr>"
    html += "<tr>"
    html += "  <td class='text-left'><b>Revenu net</b></td>"
    html += "  <td><b>" + _fmt(c["revenu_net"]) + " DA</b></td>"
    html += "</tr>"
    html += "</table>"

    # -- Attestation --
    html += "<div class='attestation'>"
    html += "J'atteste de l'exactitude des renseignements portés sur la présente déclaration."
    html += " Je suis informé(e) que tout fait passible des sanctions prévues par les textes en vigueur"
    html += " pourra être relevé contre moi."
    html += "</div>"

    # -- Signature block --
    html += "<div class='sig-block'>"
    html += "  <div class='sig-box'>"
    html += "    <div class='sig-line'>Signature du déclarant</div>"
    html += "    <div style='font-size:9pt; margin-top:4px;'>Cachet</div>"
    html += "  </div>"
    html += "  <div class='sig-box'>"
    html += "    <div class='sig-line'>Cadre réservé à l'administration</div>"
    html += "    <div style='font-size:9pt; margin-top:4px;'>Cachet et signature</div>"
    html += "  </div>"
    html += "</div>"

    # -- Footer note --
    html += "<div class='footer-note'>"
    html += "G12 Bis &mdash; Série G N&deg;12 Bis &mdash; "
    html += "Régime de l'Impôt Forfaitaire Unique (IFU) &mdash; "
    html += "Art. 282 quater CIDTA"
    html += "</div>"

    html += "</div>"
    html += "</body>"
    html += "</html>"

    # Training data hook
    hook_generation(
        "g12_bis",
        {
            "nom_prenoms": data.nom_prenoms,
            "nif": data.nif,
            "nin": data.nin,
            "activite": data.activite,
            "ca_previsionnel": data.ca_previsionnel,
            "ca_realise": data.ca_realise,
            "year": data.year,
        },
        html,
    )

    return html


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    data = G12BisData(
        nom_prenoms="BENALI Ahmed",
        nif="123456789012345",
        nin="123456789012345678",
        activite="Prestations de services informatiques",
        date_debut="01/01/2024",
        adresse="123 Rue Didouche Mourad",
        commune="Alger",
        wilaya="16-Alger",
        ca_previsionnel=2_000_000,
        ca_realise=2_500_000,
        year=2026,
    )

    c = calculate_g12_bis(data)
    print("=== G12 Bis IFU ===")
    print(f"CA previsionnel: {c['ifu_previsionnel']:,.0f} DA")
    print(f"CA realise:      {c['ifu_realise']:,.0f} DA")
    print(f"Ecart:           {c['ca_ecart']:,.0f} DA")
    print(f"IFU prev.:       {c['ifu_previsionnel']:,.0f} DA")
    print(f"IFU realise:     {c['ifu_realise']:,.0f} DA")
    print(f"IFU complement:  {c['ifu_complementaire']:,.0f} DA")
    print(f"IFU total:       {c['ifu_total']:,.0f} DA")
    print(f"Revenu net:      {c['revenu_net']:,.0f} DA")

    if "--html" in sys.argv:
        html = generate_g12_bis(data)
        out_path = "g12_bis_output.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out_path}")
