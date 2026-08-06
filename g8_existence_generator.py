"""G8 Official Form Generator — Déclaration d'Existence.

Generates G8 forms as HTML matching the official DGI printable form.
All businesses and self-employed must declare existence within 30 days
of starting activity.

Legal reference: Article 10 of the Code des Impôts Directs et Taxes Assimilées (CIDTA).

Usage:
    from g8_existence_generator import G8Data, generate_g8, generate_g8_html

    data = G8Data(nom="BENALI", prenom="Ahmed", activite="Commerce")
    html = generate_g8(data)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


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

SITUATIONS_FAMILIALES = ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"]

NATURES_ACTIVITE = [
    "Commerciale", "Industrielle", "Libérale", "Agricole", "Autre",
]


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class G8Data:
    """Complete data for G8 Déclaration d'Existence form."""

    # DGI hierarchy
    wilaya_dgi: str = ""
    diw: str = ""
    structure: str = ""
    inspection: str = ""
    recette: str = ""

    # Section 1 — Identification du contribuable
    nif: str = ""
    nouveau_contribuable: bool = True  # Default: most G8 filers are new
    nin: str = ""  # Numéro d'Identification Nationale
    nom: str = ""
    prenom: str = ""
    date_naissance: str = ""
    lieu_naissance: str = ""
    situation_familiale: str = ""  # Célibataire / Marié(e) / Divorcé(e) / Veuf(ve)
    activite_principale: str = ""
    code_activite: str = ""  # Code NNA ou NSAF
    date_debut_activite: str = ""
    numero_registre_commerce: str = ""
    numero_compte_bancaire: str = ""

    # Section 2 — Adresse
    adresse_siege: str = ""
    adresse_domicile: str = ""
    commune: str = ""
    wilaya_adresse: str = ""
    code_commune: str = ""
    code_wilaya: str = ""
    telephone: str = ""
    fax: str = ""
    email: str = ""

    # Section 3 — Activite
    description_activite: str = ""
    nature_activite: str = ""  # Commerciale / Industrielle / Libérale / Agricole / Autre
    forme_juridique: str = ""
    date_constitution: str = ""
    capital_social: str = ""
    nombre_salaries: str = ""
    superficie: str = ""

    # Section 4 — Etablissements
    siege_social: str = ""
    etablissements_secondaires: list[str] = field(default_factory=list)

    # Section 5 — Representant legal
    rep_nom: str = ""
    rep_prenom: str = ""
    rep_qualite: str = ""  # Gérant / Président / Administrateur / Tuteur / Mandataire
    rep_adresse: str = ""
    rep_nif: str = ""

    # Signature
    ville_signature: str = ""
    date_signature: str = ""
    beneficiaire: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _checkbox(condition: bool) -> str:
    return "☑" if condition else "☐"


def _field(value: str, width: int = 40) -> str:
    """Return filled value or dotted line placeholder."""
    if value:
        return value
    return "." * width


def _date_field(value: str) -> str:
    if value:
        return value
    return "....../....../......"


def _wilaya_field(value: str) -> str:
    if value:
        return value
    return "......"


def _phone_field(value: str) -> str:
    if value:
        return value
    return "................"


# ── HTML Generators ───────────────────────────────────────────────────────────

def _header_html() -> str:
    """Official DGI header for G8."""
    return """<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h1>Série G N°8</h1>
  <div class="title">DÉCLARATION D'EXISTENCE</div>
  <div class="subtitle-ar">تصريح بالوجود</div>
  <div class="deadline">Déclaration à souscrire dans les 30 jours suivant le commencement de l'activité</div>
</div>"""


def _dgi_hierarchy_html(data: G8Data) -> str:
    """DGI institutional hierarchy fields."""
    return f"""<div class="section">
  <div class="dgi-fields">
    <table class="dgi-table">
      <tr>
        <td class="dgi-label">Wilaya :</td>
        <td class="dgi-value">{_field(data.wilaya_dgi, 30)}</td>
      </tr>
      <tr>
        <td class="dgi-label">Direction InterWilaya des Impôts (DIW) :</td>
        <td class="dgi-value">{_field(data.diw, 30)}</td>
      </tr>
      <tr>
        <td class="dgi-label">Structure :</td>
        <td class="dgi-value">{_field(data.structure, 30)}</td>
      </tr>
      <tr>
        <td class="dgi-label">Inspection des Impôts :</td>
        <td class="dgi-value">{_field(data.inspection, 30)}</td>
      </tr>
      <tr>
        <td class="dgi-label">Recette des Impôts :</td>
        <td class="dgi-value">{_field(data.recette, 30)}</td>
      </tr>
    </table>
  </div>
</div>"""


def _identification_html(data: G8Data) -> str:
    """Section 1 — Identification du contribuable."""
    nouveau_check = _checkbox(data.nouveau_contribuable)
    deja_check = _checkbox(not data.nouveau_contribuable)

    return f"""<div class="section">
  <div class="section-title">1 — IDENTIFICATION DU CONTRIBUABLE</div>
  <div class="section-title-ar">١ — تحديد المكلّف</div>

  <table class="fields-table">
    <tr>
      <td class="field-label">NIF :</td>
      <td class="field-value">{_field(data.nif, 30)}</td>
      <td class="field-label-ar">رقم التعريف الجبائي :</td>
    </tr>
    <tr>
      <td class="field-label">NIN (Numéro d'Identification Nationale) :</td>
      <td class="field-value">{_field(data.nin, 30)}</td>
      <td class="field-label-ar">رقم التعريف الوطني :</td>
    </tr>
    <tr>
      <td class="field-label">Nom et Prénom :</td>
      <td class="field-value" colspan="2">{_field(data.nom + " " + data.prenom, 40)}</td>
    </tr>
    <tr>
      <td class="field-label">Date et lieu de naissance :</td>
      <td class="field-value">{_date_field(data.date_naissance)} à {_field(data.lieu_naissance, 20)}</td>
    </tr>
    <tr>
      <td class="field-label">Situation familiale :</td>
      <td class="field-value" colspan="2">
        <table class="checkbox-table"><tr>
          {" ".join(f'<td class="checkbox-cell">{_checkbox(data.situation_familiale == s)} {s}</td>' for s in SITUATIONS_FAMILIALES)}
        </tr></table>
      </td>
    </tr>
    <tr>
      <td class="field-label">Activité principale :</td>
      <td class="field-value">{_field(data.activite_principale, 40)}</td>
    </tr>
    <tr>
      <td class="field-label">Code activité (NNA/NSAF) :</td>
      <td class="field-value">{_field(data.code_activite, 20)}</td>
    </tr>
    <tr>
      <td class="field-label">Date de commencement d'activité :</td>
      <td class="field-value">{_date_field(data.date_debut_activite)}</td>
    </tr>
    <tr>
      <td class="field-label">Numéro du Registre de Commerce :</td>
      <td class="field-value">{_field(data.numero_registre_commerce, 30)}</td>
    </tr>
    <tr>
      <td class="field-label">Numéro(s) de compte(s) bancaire(s) ou CCP :</td>
      <td class="field-value">{_field(data.numero_compte_bancaire, 30)}</td>
    </tr>
  </table>

  <div class="regime-check">
    <table class="checkbox-table"><tr>
      <td class="checkbox-cell">{nouveau_check} Je suis nouveau contribuable / أنا مكلّف جديد</td>
      <td class="checkbox-cell">{deja_check} Je suis déjà enregistré sous le NIF indiqué ci-dessus / أنا مسجّل مسبقاً</td>
    </tr></table>
  </div>
</div>"""


def _adresse_html(data: G8Data) -> str:
    """Section 2 — Adresse."""
    return f"""<div class="section">
  <div class="section-title">2 — ADRESSE</div>
  <div class="section-title-ar">٢ — العنوان</div>

  <table class="fields-table">
    <tr>
      <td class="field-label">Adresse du siège :</td>
      <td class="field-value">{_field(data.adresse_siege, 40)}</td>
      <td class="field-label-ar">عنوان المقر الرئيسي :</td>
    </tr>
    <tr>
      <td class="field-label">Adresse du domicile personnel :</td>
      <td class="field-value">{_field(data.adresse_domicile, 40)}</td>
      <td class="field-label-ar">عنوان الإقامة الشخصية :</td>
    </tr>
    <tr>
      <td class="field-label">Commune :</td>
      <td class="field-value">{_field(data.commune, 25)}</td>
      <td class="field-label-ar">البلدية :</td>
    </tr>
    <tr>
      <td class="field-label">Wilaya :</td>
      <td class="field-value">{_wilaya_field(data.wilaya_adresse)}</td>
      <td class="field-label-ar">الولاية :</td>
    </tr>
    <tr>
      <td class="field-label">Code commune :</td>
      <td class="field-value">{_field(data.code_commune, 10)}</td>
    </tr>
    <tr>
      <td class="field-label">Code wilaya :</td>
      <td class="field-value">{_field(data.code_wilaya, 10)}</td>
    </tr>
    <tr>
      <td class="field-label">Téléphone :</td>
      <td class="field-value">{_phone_field(data.telephone)}</td>
      <td class="field-label">Fax :</td>
      <td class="field-value">{_phone_field(data.fax)}</td>
    </tr>
    <tr>
      <td class="field-label">Email :</td>
      <td class="field-value" colspan="2">{_field(data.email, 40)}</td>
    </tr>
  </table>
</div>"""


def _activite_html(data: G8Data) -> str:
    """Section 3 — Activité."""
    nature_checks = " ".join(
        f'<td class="checkbox-cell">{_checkbox(data.nature_activite == n)} {n}</td>'
        for n in NATURES_ACTIVITE
    )

    return f"""<div class="section">
  <div class="section-title">3 — ACTIVITÉ</div>
  <div class="section-title-ar">٣ — النشاط</div>

  <table class="fields-table">
    <tr>
      <td class="field-label">Description de l'activité :</td>
      <td class="field-value" colspan="2">{_field(data.description_activite, 50)}</td>
    </tr>
    <tr>
      <td class="field-label">Nature de l'activité :</td>
      <td class="field-value" colspan="2">
        <table class="checkbox-table"><tr>{nature_checks}</tr></table>
      </td>
    </tr>
    <tr>
      <td class="field-label">Forme juridique (si entreprise) :</td>
      <td class="field-value">{_field(data.forme_juridique, 30)}</td>
      <td class="field-label-ar">الشكل القانوني :</td>
    </tr>
    <tr>
      <td class="field-label">Date de constitution :</td>
      <td class="field-value">{_date_field(data.date_constitution)}</td>
    </tr>
    <tr>
      <td class="field-label">Capital social :</td>
      <td class="field-value">{_field(data.capital_social, 20)}</td>
      <td class="field-label">DA</td>
    </tr>
    <tr>
      <td class="field-label">Nombre de salariés :</td>
      <td class="field-value">{_field(data.nombre_salaries, 10)}</td>
    </tr>
    <tr>
      <td class="field-label">Superficie de l'établissement :</td>
      <td class="field-value">{_field(data.superficie, 15)}</td>
      <td class="field-label">m²</td>
    </tr>
  </table>
</div>"""


def _etablissements_html(data: G8Data) -> str:
    """Section 4 — Établissements."""
    etabs_rows = ""
    for i, etab in enumerate(data.etablissements_secondaires, start=1):
        etabs_rows += f"""      <tr>
        <td class="num">{i}</td>
        <td class="field-value">{etab}</td>
      </tr>"""

    # Always show at least 3 empty rows for handwriting
    remaining = max(0, 3 - len(data.etablissements_secondaires))
    for i in range(remaining):
        etabs_rows += f"""      <tr>
        <td class="num">{len(data.etablissements_secondaires) + i + 1}</td>
        <td class="field-value">&nbsp;</td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">4 — ÉTABLISSEMENTS</div>
  <div class="section-title-ar">٤ — المؤسسات</div>

  <table class="fields-table">
    <tr>
      <td class="field-label">Siège social :</td>
      <td class="field-value">{_field(data.siege_social, 50)}</td>
      <td class="field-label-ar">المقر الرئيسي :</td>
    </tr>
  </table>

  <div class="sub-label">Établissements secondaires :</div>
  <table class="etab-table">
    <thead>
      <tr>
        <th>N°</th>
        <th>Adresse de l'établissement</th>
      </tr>
    </thead>
    <tbody>
{etabs_rows}
    </tbody>
  </table>
</div>"""


def _representant_html(data: G8Data) -> str:
    """Section 5 — Représentant légal."""
    return f"""<div class="section">
  <div class="section-title">5 — REPRÉSENTANT LÉGAL</div>
  <div class="section-title-ar">٥ — الممثل القانوني</div>

  <table class="fields-table">
    <tr>
      <td class="field-label">Nom et Prénom :</td>
      <td class="field-value" colspan="2">{_field(data.rep_nom + " " + data.rep_prenom, 40)}</td>
    </tr>
    <tr>
      <td class="field-label">Qualité :</td>
      <td class="field-value">{_field(data.rep_qualite, 30)}</td>
      <td class="field-label-ar">الصفة :</td>
    </tr>
    <tr>
      <td class="field-label">Adresse :</td>
      <td class="field-value">{_field(data.rep_adresse, 40)}</td>
    </tr>
    <tr>
      <td class="field-label">NIF :</td>
      <td class="field-value">{_field(data.rep_nif, 20)}</td>
    </tr>
  </table>
</div>"""


def _engagement_html(data: G8Data) -> str:
    """Section 6 — Engagement / Attestation."""
    return f"""<div class="section">
  <div class="section-title">6 — ENGAGEMENT</div>
  <div class="section-title-ar">٦ — التعهد</div>

  <div class="engagement-text">
    <p>Je soussigné(e), certifie que les renseignements fournis ci-dessus sont exacts et complets.</p>
    <p class="ar">أنا الموقع(ة) أسفله، أشهد أن المعلومات المقدمة أعلاه صحيحة وكاملة.</p>

    <p>Je m'engage à déclarer toute modification survenue dans les éléments déclarés dans les 30 jours suivant la modification.</p>
    <p class="ar">أتعهد بالإبلاغ عن أي تغيير في العناصر المصرح بها خلال 30 يوماً من تاريخ التغيير.</p>
  </div>

  <div class="signature-section">
    <div class="fait-line">Fait à {_field(data.ville_signature, 20)} le {_date_field(data.date_signature)}</div>

    <div class="signature-block">
      <div class="sig-box">
        <strong>Signature du déclarant</strong><br>
        <span class="ar">توقيع الم declared</span><br><br><br><br>
        <div class="cachet-area">Cachet</div>
      </div>
      <div class="sig-box reserved">
        <strong>Cadre réservé à l'administration</strong><br>
        <span class="ar">الإطار المحجوز للإدارة</span><br><br><br><br>
        <div class="cachet-area">Cachet</div>
      </div>
    </div>
  </div>
</div>"""


def _css() -> str:
    """Complete CSS for official G8 form styling."""
    return """<style>
  @page { size: A4; margin: 12mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 10pt; color: #1a1a1a; margin: 0; padding: 15px;
    line-height: 1.4;
  }

  /* Header */
  .header { text-align: center; border: 2px solid #000; padding: 10px; margin-bottom: 12px; }
  .republique { font-size: 9pt; letter-spacing: 1px; }
  .dgi { font-size: 11pt; font-weight: bold; margin: 4px 0; }
  .header h1 { font-size: 16pt; margin: 6px 0 2px; letter-spacing: 2px; }
  .title { font-size: 13pt; font-weight: bold; margin: 4px 0; }
  .subtitle-ar { font-size: 12pt; direction: rtl; margin: 3px 0; }
  .deadline { font-size: 9pt; font-weight: bold; margin-top: 6px; padding: 5px; border: 1px solid #000; background: #f8f8f8; }

  /* DGI Hierarchy */
  .dgi-fields { margin: 5px 0; }
  .dgi-table { width: 100%; border: none; }
  .dgi-table td { border: none; padding: 2px 5px; font-size: 9pt; }
  .dgi-label { font-weight: bold; width: 45%; }
  .dgi-value { border-bottom: 1px dotted #999; }

  /* Sections */
  .section { margin: 12px 0; page-break-inside: avoid; }
  .section-title {
    font-size: 10.5pt; font-weight: bold; border-bottom: 2px solid #000;
    padding-bottom: 3px; margin-bottom: 6px;
  }
  .section-title-ar { font-size: 9.5pt; color: #666; margin-bottom: 6px; text-align: right; direction: rtl; }

  /* Fields table */
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 4px 5px; font-size: 9.5pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 38%; }
  .field-label-ar { font-weight: normal; font-size: 8.5pt; color: #555; width: 22%; text-align: right; direction: rtl; }
  .field-value { border-bottom: 1px dotted #999; }

  /* Checkboxes */
  .checkbox-table { border: none; }
  .checkbox-table td { border: none; padding: 3px 10px; font-size: 9pt; }
  .checkbox-cell { white-space: nowrap; }
  .regime-check { margin: 8px 0; padding: 6px; border: 1px solid #ccc; font-size: 9pt; background: #fafafa; }

  /* Etablissements table */
  .sub-label { font-weight: bold; font-size: 9.5pt; margin: 6px 0 3px; }
  .etab-table { width: 100%; border-collapse: collapse; margin: 4px 0; }
  .etab-table th, .etab-table td { border: 1px solid #000; padding: 4px 6px; font-size: 9pt; }
  .etab-table th { background: #f0f0f0; font-weight: bold; text-align: center; }
  .etab-table .num { text-align: center; width: 40px; }

  /* Engagement */
  .engagement-text { margin: 8px 0; padding: 8px; border: 1px solid #ccc; background: #fafafa; }
  .engagement-text p { margin: 5px 0; text-align: justify; }
  .engagement-text .ar { font-size: 9pt; direction: rtl; text-align: right; color: #444; }

  /* Signature */
  .signature-section { margin-top: 15px; }
  .fait-line { font-size: 10pt; margin-bottom: 12px; }
  .signature-block { display: flex; justify-content: space-between; gap: 15px; }
  .sig-box {
    width: 45%; text-align: center; font-size: 9.5pt;
    border-top: 1px solid #000; padding-top: 8px;
    min-height: 120px;
  }
  .sig-box.reserved { border: 1px solid #999; background: #f8f8f8; }
  .cachet-area {
    margin-top: 10px; padding: 8px; border: 1px dashed #ccc;
    font-size: 8pt; color: #999; font-style: italic;
  }
  .ar { font-size: 8.5pt; color: #666; }

  /* Print */
  @media print {
    body { padding: 0; margin: 0; }
    .no-print { display: none; }
    .section { page-break-inside: avoid; }
    .header { page-break-after: avoid; }
  }
</style>"""


# ── Main Generator ────────────────────────────────────────────────────────────

def generate_g8(data: G8Data) -> str:
    """Generate complete G8 Déclaration d'Existence form as HTML.

    Args:
        data: G8Data instance with all form fields.

    Returns:
        Complete HTML document ready for printing.
    """
    return f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G N°8 — Déclaration d'Existence — {data.nom} {data.prenom}</title>
{_css()}
</head>
<body>

{_header_html()}
{_dgi_hierarchy_html(data)}
{_identification_html(data)}
{_adresse_html(data)}
{_activite_html(data)}
{_etablissements_html(data)}
{_representant_html(data)}
{_engagement_html(data)}

</body>
</html>"""


def generate_g8_html(data: G8Data) -> str:
    """Alias for generate_g8 — backward compatibility."""
    return generate_g8(data)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = G8Data(
        # DGI hierarchy
        wilaya_dgi="32 — El Bayadh",
        diw="DIW D'EL BAYADH",
        structure="SIS El Bayadh Centre",
        inspection="Inspection des Impôts d'El Bayadh",
        recette="Recette des Impôts d'El Bayadh Centre",

        # Identification
        nouveau_contribuable=True,
        nom="BENALI",
        prenom="Ahmed",
        date_naissance="15/03/1990",
        lieu_naissance="El Bayadh",
        situation_familiale="Marié(e)",
        activite_principale="Commerce de produits alimentaires",
        code_activite="47111",
        date_debut_activite="01/08/2026",
        numero_registre_commerce="03/00/26/12345",
        numero_compte_bancaire="00799999001234567890",

        # Adresse
        adresse_siege="123 Rue Didouche Mourad, El Bayadh",
        adresse_domicile="123 Rue Didouche Mourad, El Bayadh",
        commune="El Bayadh Centre",
        wilaya_adresse="32 — El Bayadh",
        code_commune="3201",
        code_wilaya="32",
        telephone="0555081718",
        email="ahmed.benali@email.com",

        # Activite
        description_activite="Commerce de détail de produits alimentaires et boissons",
        nature_activite="Commerciale",
        forme_juridique="Entreprise individuelle",
        date_constitution="01/07/2026",
        capital_social="500 000",
        nombre_salaries="2",
        superficie="80",

        # Etablissements
        siege_social="123 Rue Didouche Mourad, El Bayadh",
        etablissements_secondaires=[
            "456 Avenue de la République, El Bayadh",
        ],

        # Representant
        rep_nom="BENALI",
        rep_prenom="Ahmed",
        rep_qualite="Gérant",
        rep_adresse="123 Rue Didouche Mourad, El Bayadh",

        # Signature
        ville_signature="El Bayadh",
        date_signature="01/08/2026",
    )

    print("G N°8 — Déclaration d'Existence")
    print("=" * 40)
    print(f"  Nom: {sample.nom} {sample.prenom}")
    print(f"  Activité: {sample.activite_principale}")
    print(f"  Date début: {sample.date_debut_activite}")
    print(f"  Nouveau contribuable: {'Oui' if sample.nouveau_contribuable else 'Non'}")
    print()

    if "--html" in sys.argv:
        html = generate_g8(sample)
        out = "g8_existence_official.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML written to {out}")
    else:
        print("Usage: python g8_existence_generator.py --html")
        print("  --html    Generate HTML file")
