"""G51 Generator — Attestation de Regularite Fiscale (Tax Clearance Certificate).

Generates G51 forms as HTML matching the official DGI printable form.
The G51 is a request for a tax clearance certificate proving a business
has no outstanding tax debts. Required for public tenders, license renewals,
and certain contracts.

Legal reference: Article 85 of the Code des Procedures Fiscales (CPF).

Usage:
    from g51_generator import G51Data, generate_g51, calculate_g51

    data = G51Data(nom="SARL Exemple", nif="1234567890")
    html = generate_g51(data)
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass
from datetime import datetime


def _esc(value: object, default: str = "") -> str:
    """HTML-escape a value for safe rendering."""
    if value is None:
        return default
    return _html_mod.escape(str(value))


def _field(value: str, width: int = 40) -> str:
    """Return filled value or dotted line placeholder (HTML-escaped)."""
    if value:
        return _html_mod.escape(str(value))
    return "." * width


def _fmt(n: float) -> str:
    """Format number with thousand separators (spaces)."""
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _checkbox(condition: bool) -> str:
    """Return a checked or unchecked checkbox."""
    if condition:
        return "\u2611"
    return "\u2610"


# -- Data Classes ------------------------------------------------------------

@dataclass
class G51Data:
    """Input data for G51 Attestation de Regularite Fiscale."""

    nom: str = ""
    nif: str = ""
    nin: str = ""
    rc_number: str = ""
    activite: str = ""
    adresse: str = ""
    commune: str = ""
    wilaya: str = ""
    telephone: str = ""
    email: str = ""
    annees_concernees: str = ""
    motif: str = ""
    date_signature: str = ""
    beneficiaire: str = ""
    year: int = datetime.now().year


# -- Calculations ------------------------------------------------------------

def calculate_g51(data: G51Data) -> dict:
    """Calculate G51 fees and status.

    Returns a dict with:
        - frais_timbre: stamp duty for the request
        - frais_dossier: file processing fee
        - total_frais: total fees
        - impots_payes: always True (this is a request form)
        - annees: list of year strings parsed from annees_concernees
    """
    annees = [a.strip() for a in data.annees_concernees.split(",") if a.strip()]

    frais_timbre = 1_000
    frais_dossier = 2_000
    total_frais = frais_timbre + frais_dossier

    return {
        "frais_timbre": frais_timbre,
        "frais_dossier": frais_dossier,
        "total_frais": total_frais,
        "impots_payes": True,
        "annees": annees,
    }


# -- CSS ---------------------------------------------------------------------

def _css() -> str:
    """Complete CSS for official G51 form styling."""
    c = "<style>\n"
    c += "  @page { size: A4; margin: 12mm; }\n"
    c += "  * { box-sizing: border-box; }\n"
    c += "  body {\n"
    c += "    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;\n"
    c += "    font-size: 10pt; color: #1a1a1a; margin: 0; padding: 15px;\n"
    c += "    line-height: 1.4;\n"
    c += "  }\n"
    c += "  .header { text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 12px; }\n"
    c += "  .republique { font-size: 9pt; letter-spacing: 1px; }\n"
    c += "  .dgi { font-size: 11pt; font-weight: bold; margin: 4px 0; }\n"
    c += "  .header h1 { font-size: 16pt; margin: 6px 0 2px; letter-spacing: 2px; }\n"
    c += "  .title { font-size: 13pt; font-weight: bold; margin: 4px 0; }\n"
    c += "  .serie { font-size: 11pt; font-weight: bold; margin: 4px 0; color: #0A1628; }\n"
    c += "  .deadline { font-size: 9pt; font-weight: bold; margin-top: 6px; padding: 5px; border: 1px solid #000; background: #f8f8f8; }\n"
    c += "  .section { margin: 12px 0; page-break-inside: avoid; }\n"
    c += "  .section-title {\n"
    c += "    font-size: 10.5pt; font-weight: bold; border-bottom: 2px solid #000;\n"
    c += "    padding-bottom: 3px; margin-bottom: 6px;\n"
    c += "  }\n"
    c += "  .section-title-ar { font-size: 9.5pt; color: #666; margin-bottom: 6px; text-align: right; direction: rtl; }\n"
    c += "  .fields-table { width: 100%; border-collapse: collapse; }\n"
    c += "  .fields-table td { padding: 4px 5px; font-size: 9.5pt; vertical-align: top; }\n"
    c += "  .field-label { font-weight: bold; width: 38%; }\n"
    c += "  .field-label-ar { font-weight: normal; font-size: 8.5pt; color: #555; width: 22%; text-align: right; direction: rtl; }\n"
    c += "  .field-value { border-bottom: 1px dotted #999; }\n"
    c += "  .checkbox-table { border: none; }\n"
    c += "  .checkbox-table td { border: none; padding: 3px 10px; font-size: 9pt; }\n"
    c += "  .checkbox-cell { white-space: nowrap; }\n"
    c += "  .engagement-text { margin: 8px 0; padding: 8px; border: 1px solid #ccc; background: #fafafa; }\n"
    c += "  .engagement-text p { margin: 5px 0; text-align: justify; }\n"
    c += "  .engagement-text .ar { font-size: 9pt; direction: rtl; text-align: right; color: #444; }\n"
    c += "  .signature-section { margin-top: 15px; }\n"
    c += "  .fait-line { font-size: 10pt; margin-bottom: 12px; }\n"
    c += "  .signature-block { display: flex; justify-content: space-between; gap: 15px; }\n"
    c += "  .sig-box {\n"
    c += "    width: 45%; text-align: center; font-size: 9.5pt;\n"
    c += "    border-top: 1px solid #000; padding-top: 8px;\n"
    c += "    min-height: 120px;\n"
    c += "  }\n"
    c += "  .sig-box.reserved { border: 1px solid #999; background: #f8f8f8; }\n"
    c += "  .cachet-area {\n"
    c += "    margin-top: 10px; padding: 8px; border: 1px dashed #ccc;\n"
    c += "    font-size: 8pt; color: #999; font-style: italic;\n"
    c += "  }\n"
    c += "  .fees-table { width: 100%; border-collapse: collapse; margin: 8px 0; }\n"
    c += "  .fees-table th, .fees-table td { border: 1px solid #333; padding: 4px 6px; font-size: 9pt; }\n"
    c += "  .fees-table th { background: #e8e8e8; font-weight: bold; }\n"
    c += "  .fees-table .total-line { background: #0A1628; color: #fff; font-weight: bold; }\n"
    c += "  .fees-table .num { text-align: right; font-family: 'Courier New', monospace; }\n"
    c += "  .ar { font-size: 8.5pt; color: #666; }\n"
    c += "  .note { font-size: 8pt; color: #666; font-style: italic; margin: 4px 0; }\n"
    c += "  .motif-check { margin: 8px 0; padding: 6px; border: 1px solid #ccc; font-size: 9pt; background: #fafafa; }\n"
    c += "  @media print {\n"
    c += "    body { padding: 0; margin: 0; }\n"
    c += "    .no-print { display: none; }\n"
    c += "    .section { page-break-inside: avoid; }\n"
    c += "    .header { page-break-after: avoid; }\n"
    c += "  }\n"
    c += "</style>"
    return c


# -- HTML Helpers ------------------------------------------------------------

def _header_html(data: G51Data) -> str:
    """Official DGI header for G51."""
    h = '<div class="header">\n'
    h += '  <div class="republique">REPUBLIQUE ALGERIENNE DEMOCRATIQUE ET POPULAIRE</div>\n'
    h += '  <div class="dgi">DIRECTION GENERALE DES IMPOTS</div>\n'
    h += '  <h1>ATTESTATION DE REGULARITE FISCALE</h1>\n'
    h += '  <div class="serie">G N\u00b051</div>\n'
    h += '  <div class="deadline">Demande d\u2019attestation de r\u00e9gularit\u00e9 fiscale \u2014 Article 85 du Code des Proc\u00e9dures Fiscales</div>\n'
    h += "</div>\n"
    return h


def _section1_identification_html(data: G51Data) -> str:
    """Section I -- Identification du contribuable."""
    h = '<div class="section">\n'
    h += '  <div class="section-title">I \u2014 IDENTIFICATION DU CONTRIBUABLE</div>\n'
    h += '  <div class="section-title-ar">\u0627\u0644\u0645\u0639\u0631\u0641\u0629 \u0628\u0627\u0644\u0645\u062e\u0644\u0651\u0641</div>\n'
    h += '  <table class="fields-table">\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">Nom / Raison sociale :</td>\n'
    h += '      <td class="field-value" colspan="2">' + _field(data.nom, 50) + '</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">NIF :</td>\n'
    h += '      <td class="field-value">' + _field(data.nif, 30) + '</td>\n'
    h += '      <td class="field-label-ar">\u0631\u0642\u0645 \u0627\u0644\u062a\u0639\u0631\u064a\u0641 \u0627\u0644\u062c\u0628\u0627\u0626\u064a :</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">NIN :</td>\n'
    h += '      <td class="field-value">' + _field(data.nin, 30) + '</td>\n'
    h += '      <td class="field-label-ar">\u0631\u0642\u0645 \u0627\u0644\u062a\u0639\u0631\u064a\u0641 \u0627\u0644\u0648\u0637\u0646\u064a :</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">Num\u00e9ro Registre de Commerce :</td>\n'
    h += '      <td class="field-value">' + _field(data.rc_number, 30) + '</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">Activit\u00e9 :</td>\n'
    h += '      <td class="field-value" colspan="2">' + _field(data.activite, 50) + '</td>\n'
    h += '    </tr>\n'
    h += '  </table>\n'
    h += '</div>\n'
    return h


def _section2_adresse_html(data: G51Data) -> str:
    """Section II -- Adresse et contact."""
    h = '<div class="section">\n'
    h += '  <div class="section-title">II \u2014 ADRESSE ET CONTACT</div>\n'
    h += '  <div class="section-title-ar">\u0627\u0644\u0639\u0646\u0648\u0627\u0646 \u0648\u0627\u0644\u0627\u062a\u0635\u0627\u0644</div>\n'
    h += '  <table class="fields-table">\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">Adresse du si\u00e8ge :</td>\n'
    h += '      <td class="field-value" colspan="2">' + _field(data.adresse, 50) + '</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">Commune :</td>\n'
    h += '      <td class="field-value">' + _field(data.commune, 25) + '</td>\n'
    h += '      <td class="field-label-ar">\u0627\u0644\u0628\u0644\u062f\u064a\u0629 :</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">Wilaya :</td>\n'
    h += '      <td class="field-value">' + _field(data.wilaya, 25) + '</td>\n'
    h += '      <td class="field-label-ar">\u0627\u0644\u0648\u0644\u0627\u064a\u0629 :</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">T\u00e9l\u00e9phone :</td>\n'
    h += '      <td class="field-value">' + _field(data.telephone, 25) + '</td>\n'
    h += '      <td class="field-label">Email :</td>\n'
    h += '      <td class="field-value">' + _field(data.email, 30) + '</td>\n'
    h += '    </tr>\n'
    h += '  </table>\n'
    h += '</div>\n'
    return h


def _section3_motif_html(data: G51Data) -> str:
    """Section III -- Motif de la demande."""
    motif_lower = data.motif.lower() if data.motif else ""
    marche = "march" in motif_lower or "tender" in motif_lower
    renouvellement = "renouvellement" in motif_lower or "rc" in motif_lower
    autre = "autre" in motif_lower or "other" in motif_lower
    if not marche and not renouvellement and not autre:
        marche = True

    h = '<div class="section">\n'
    h += '  <div class="section-title">III \u2014 MOTIF DE LA DEMANDE</div>\n'
    h += '  <div class="section-title-ar">\u0633\u0628\u0628 \u0627\u0644\u0637\u0644\u0628</div>\n'
    h += '  <div class="motif-check">\n'
    h += '    <table class="checkbox-table"><tr>\n'
    h += '      <td class="checkbox-cell">' + _checkbox(marche) + ' March\u00e9s publics</td>\n'
    h += '      <td class="checkbox-cell">' + _checkbox(renouvellement) + ' Renouvellement RC</td>\n'
    h += '      <td class="checkbox-cell">' + _checkbox(autre) + ' Autres : ' + _field(data.motif if autre else "", 20) + '</td>\n'
    h += '    </tr></table>\n'
    h += '  </div>\n'
    h += '</div>\n'
    return h


def _section4_periode_html(data: G51Data) -> str:
    """Section IV -- Periode concernee."""
    h = '<div class="section">\n'
    h += '  <div class="section-title">IV \u2014 PERIODE CONCERNEE</div>\n'
    h += '  <div class="section-title-ar">\u0627\u0644\u0641\u062a\u0631\u0629 \u0627\u0644\u0645\u0639\u0646\u064a\u0629</div>\n'
    h += '  <table class="fields-table">\n'
    h += '    <tr>\n'
    h += '      <td class="field-label">Ann\u00e9es concern\u00e9es :</td>\n'
    h += '      <td class="field-value">' + _field(data.annees_concernees, 50) + '</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td class="field-label" colspan="2">\n'
    h += '        <em class="note">(Exemple : 2022, 2023, 2024)</em>\n'
    h += '      </td>\n'
    h += '    </tr>\n'
    h += '  </table>\n'
    h += '</div>\n'
    return h


def _section5_engagement_html(data: G51Data) -> str:
    """Section V -- Engagement + Signature."""
    h = '<div class="section">\n'
    h += '  <div class="section-title">V \u2014 ENGAGEMENT</div>\n'
    h += '  <div class="section-title-ar">\u0627\u0644\u062a\u0632\u0645</div>\n'
    h += '  <div class="engagement-text">\n'
    h += '    <p>Je soussign\u00e9(e), certifie que je suis en r\u00e8gle vis-\u00e0-vis de mes obligations fiscales pour les ann\u00e9es mentionn\u00e9es ci-dessus.</p>\n'
    h += '    <p class="ar">\u0623\u0646\u0627 \u0627\u0644\u0645\u0648\u0642\u0639(\u0629) \u0622\u0633\u0641\u0644\u0647\u060c \u0623\u0634\u0647\u062f \u0623\u0646\u0646\u064a \u0645\u0637\u0628\u0648\u0639(\u0629) \u0644\u062f\u064a\u0648\u0646\u064a \u0627\u0644\u062c\u0628\u0627\u0626\u064a\u0629 \u0644\u0644\u0633\u0646\u0648\u0627\u062a \u0627\u0644\u0645\u0630\u0643\u0648\u0631 \u0623\u0639\u0644\u0627\u0647\u0627.</p>\n'
    h += '  </div>\n'

    h += '  <div class="signature-section">\n'
    h += '    <div class="fait-line">Fait \u00e0 ' + _field(data.beneficiaire or data.commune, 20) + ' le ' + _field(data.date_signature, 15) + '</div>\n'
    h += '    <div class="signature-block">\n'
    h += '      <div class="sig-box">\n'
    h += '        <strong>Signature du d\u00e9clarant</strong><br>\n'
    h += '        <br><br><br><br>\n'
    h += '        <div class="cachet-area">Cachet</div>\n'
    h += '      </div>\n'
    h += '      <div class="sig-box reserved">\n'
    h += '        <strong>Cadre r\u00e9serv\u00e9 \u00e0 l\u2019administration</strong><br>\n'
    h += '        <br><br><br><br>\n'
    h += '        <div class="cachet-area">Cachet + Visa</div>\n'
    h += '      </div>\n'
    h += '    </div>\n'
    h += '  </div>\n'
    h += '</div>\n'
    return h


def _fees_table_html(result: dict) -> str:
    """Fees summary table."""
    h = '<div class="section">\n'
    h += '  <div class="section-title">FRAIS DE DOSSIER</div>\n'
    h += '  <table class="fees-table">\n'
    h += '    <tr>\n'
    h += '      <th style="text-align:left;width:70%;">D\u00e9signation</th>\n'
    h += '      <th style="text-align:right;width:30%;">Montant (DA)</th>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td>Frais de timbre fiscal</td>\n'
    h += '      <td class="num">' + _fmt(result["frais_timbre"]) + '</td>\n'
    h += '    </tr>\n'
    h += '    <tr>\n'
    h += '      <td>Frais de traitement du dossier</td>\n'
    h += '      <td class="num">' + _fmt(result["frais_dossier"]) + '</td>\n'
    h += '    </tr>\n'
    h += '    <tr class="total-line">\n'
    h += '      <td><strong>TOTAL</strong></td>\n'
    h += '      <td class="num"><strong>' + _fmt(result["total_frais"]) + ' DA</strong></td>\n'
    h += '    </tr>\n'
    h += '  </table>\n'
    h += '</div>\n'
    return h


def _tax_status_html(data: G51Data, result: dict) -> str:
    """Tax status attestation section per year."""
    annees = result.get("annees", [])
    if not annees:
        return ""

    h = '<div class="section">\n'
    h += '  <div class="section-title">\u00c9TAT DES OBLIGATIONS FISCALES PAR ANN\u00c9E</div>\n'
    h += '  <table class="fees-table">\n'
    h += '    <tr>\n'
    h += '      <th style="text-align:left;width:30%;">Ann\u00e9e</th>\n'
    h += '      <th style="text-align:left;width:40%;">Imp\u00f4ts</th>\n'
    h += '      <th style="text-align:center;width:30%;">Statut</th>\n'
    h += '    </tr>\n'

    for annee in annees:
        status = "\u2611 En r\u00e8gle" if result["impots_payes"] else "\u2610 Non r\u00e9guli\u00e9"
        h += '    <tr>\n'
        h += '      <td><strong>' + _esc(annee) + '</strong></td>\n'
        h += '      <td>IBS / IRG / TVA / TAP</td>\n'
        h += '      <td style="text-align:center;">' + status + '</td>\n'
        h += '    </tr>\n'

    h += '  </table>\n'
    h += '</div>\n'
    return h


# -- Main Generator ----------------------------------------------------------

def generate_g51(data: G51Data) -> str:
    """Generate complete G51 Attestation de Regularite Fiscale as HTML.

    Args:
        data: G51Data instance with all form fields.

    Returns:
        Complete HTML document ready for printing.
    """
    result = calculate_g51(data)

    html = "<!DOCTYPE html>\n"
    html += '<html lang="fr" dir="ltr">\n'
    html += '<head>\n'
    html += '<meta charset="UTF-8">\n'
    html += '<title>G N\u00b051 \u2014 Attestation de R\u00e9gularit\u00e9 Fiscale \u2014 ' + _esc(data.nom) + '</title>\n'
    html += _css()
    html += '\n</head>\n'
    html += '<body>\n\n'

    html += _header_html(data)
    html += _section1_identification_html(data)
    html += _section2_adresse_html(data)
    html += _section3_motif_html(data)
    html += _section4_periode_html(data)
    html += _tax_status_html(data, result)
    html += _fees_table_html(result)
    html += _section5_engagement_html(data)

    html += '\n</body>\n'
    html += '</html>'

    hook_generation("g51", {"nom": data.nom, "nif": data.nif}, html)
    return html


def generate_g51_html(data: G51Data) -> str:
    """Alias for generate_g51 -- backward compatibility."""
    return generate_g51(data)


# -- CLI ---------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    sample = G51Data(
        nom="SARL SERVICES DIGITAUX",
        nif="1234567890",
        nin="12345678901234",
        rc_number="03/00/26/54321",
        activite="Prestations de services informatiques",
        adresse="42 Rue Didouche Mourad",
        commune="El Bayadh Centre",
        wilaya="32 - El Bayadh",
        telephone="0555081718",
        email="contact@services-dz.com",
        annees_concernees="2022, 2023, 2024, 2025",
        motif="March\u00e9s publics",
        date_signature="01/08/2026",
        beneficiaire="El Bayadh",
    )

    print("G N\u00b051 \u2014 Attestation de R\u00e9gularit\u00e9 Fiscale")
    print("=" * 45)
    print(f"  Nom: {sample.nom}")
    print(f"  NIF: {sample.nif}")
    print(f"  Activit\u00e9: {sample.activite}")
    print(f"  Ann\u00e9es: {sample.annees_concernees}")
    print(f"  Motif: {sample.motif}")

    result = calculate_g51(sample)
    print(f"  Frais timbre: {_fmt(result['frais_timbre'])} DA")
    print(f"  Frais dossier: {_fmt(result['frais_dossier'])} DA")
    print(f"  Total frais: {_fmt(result['total_frais'])} DA")
    print()

    if "--html" in sys.argv:
        html = generate_g51(sample)
        out = "g51_attestation_official.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML written to {out}")
    else:
        print("Usage: python g51_generator.py --html")
        print("  --html    Generate HTML file")
