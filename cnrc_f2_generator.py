"""CNRC F2 Generator — Registre du Commerce (Personne Physique).

Generates the commercial registration form for individual traders
(formulaire d'immatriculation commerçant), filed with the CNRC on
paper or via SIDJILCOM.

Who must file:
- Individual merchants (personne physique) before starting commercial activity

Usage:
    from cnrc_f2_generator import F2Data, calculate_f2, generate_f2

Reference: knowledge_base/forms/catalog.md (F2)
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass
from datetime import datetime


def _esc(value: object, default: str = "") -> str:
    if value is None:
        return default
    return _html_mod.escape(str(value))


# ── Constants ─────────────────────────────────────────────────────────────────

TIMBRE_FISCAL_DA = 4_000  # Same droit fixe as F1 (timbre fiscal)

SITUATIONS_MATRIMONIALES = ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve"]

REGIMES_MATRIMONIAUX = [
    "Séparation de biens",
    "Communauté de biens",
    "Autre",
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


@dataclass
class F2Data:
    """Data for CNRC F2 individual merchant registration."""
    # CNRC hierarchy
    wilaya: str = ""
    centre_cnrc: str = ""

    # Merchant identity
    nom: str = ""
    prenom: str = ""
    nin: str = ""                      # 18 digits
    date_naissance: str = ""           # JJ/MM/AAAA
    lieu_naissance: str = ""
    situation_matrimoniale: str = SITUATIONS_MATRIMONIALES[0]
    regime_matrimonial: str = ""       # Only if marié(e)
    conjoint_nom: str = ""             # Required when married (community regime)
    nom_commercial: str = ""           # Nom sous lequel le commerce est exploité (enseigne)
    activite: str = ""                 # Detailed commercial activity
    nationalite: str = "Algérienne"

    # Address
    adresse_personnelle: str = ""
    adresse_commerce: str = ""
    commune_commerce: str = ""
    nature_local: str = "Local loué"   # Local loué / Propriété / Domicile / Autre
    duree_bail_annees: int | None = None  # If rented

    # Metadata
    fait_a: str = ""
    date_declaration: str = ""


# ── Calculation ───────────────────────────────────────────────────────────────

def calculate_f2(data: F2Data) -> dict:
    """Compute derived fields and validation flags.

    Returns dict with: nom_complet, timbre_cost, needs_conjoint_info,
    needs_bail, age_at_declaration.
    """
    nom_complet = f"{data.nom} {data.prenom}".strip()

    married = data.situation_matrimoniale == "Marié(e)"
    community_regime = married and (
        not data.regime_matrimonial or data.regime_matrimonial == "Communauté de biens"
    )
    renting = data.nature_local == "Local loué"

    age = None
    dob = None
    try:
        dob = datetime.strptime(data.date_naissance.strip(), "%d/%m/%Y")
        ref = data.date_declaration or ""
        try:
            ref_date = datetime.strptime(ref.strip(), "%d/%m/%Y")
            age = round((ref_date - dob).days / 365.25, 0)
        except Exception:
            age = round((datetime.now() - dob).days / 365.25, 0)
    except Exception:
        pass

    return {
        "nom_complet": nom_complet,
        "timbre_cost": TIMBRE_FISCAL_DA,
        "married": married,
        "needs_conjoint_info": community_regime,
        "needs_bail": renting,
        "age": int(age) if age is not None else None,
        "age_ok": (age is not None and age >= 18),
    }


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt(n: float) -> str:
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _checkbox(selected: str, value: str) -> str:
    return "☑" if selected == value else "☐"


def _blank(n: int = 30) -> str:
    return "." * n


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css() -> str:
    return """<style>
  @page { size: A4; margin: 12mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', 'Noto Sans Arabic', serif;
    font-size: 10pt; color: #1a1a1a; margin: 0; padding: 15px;
    line-height: 1.4; direction: ltr;
  }
  .header { text-align: center; border: 2px solid #000; padding: 8px; margin-bottom: 10px; }
  .republique { font-size: 9pt; letter-spacing: 1px; }
  .cnrc { font-size: 10pt; font-weight: bold; margin: 3px 0; }
  .header h1 { font-size: 14pt; margin: 5px 0; }
  .subtitle { font-size: 9pt; }
  .deadline { font-size: 9pt; font-weight: bold; margin-top: 5px; padding: 4px; border: 1px solid #000; background: #f8f8f8; }
  .section { margin: 10px 0; page-break-inside: avoid; }
  .section-title { font-size: 10pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 3px; margin-bottom: 5px; }
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 3px 5px; font-size: 9pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 35%; }
  .field-value { border-bottom: 1px dotted #999; width: 40%; }
  .checkbox-line { font-size: 9pt; margin: 3px 0; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 55%; }
  .summary-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .summary-table .total-row { background: #e8e8e8; font-weight: bold; font-size: 10pt; }
  .warn { background: #fff3cd; font-weight: bold; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }
  .legal-page p { font-size: 8.5pt; text-align: justify; margin: 5px 0; line-height: 1.5; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


# ── HTML section builders ─────────────────────────────────────────────────────

def _header_html(data: F2Data) -> str:
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="cnrc">CENTRE NATIONAL DU REGISTRE DE COMMERCE (CNRC)</div>
  <h1>FORMULAIRE F N°2</h1>
  <div class="subtitle">IMMATRICULATION AU REGISTRE DU COMMERCE — PERSONNE PHYSIQUE</div>
  <div class="deadline">Timbre fiscal : {_fmt(TIMBRE_FISCAL_DA)} DA — À déposer avant le début d'activité</div>
</div>"""


def _identity_html(data: F2Data, calc: dict) -> str:
    situations = "".join(
        f'<span style="margin-right:12px;">{_checkbox(data.situation_matrimoniale, s)} {s}</span>'
        for s in SITUATIONS_MATRIMONIALES
    )
    conjoint_block = ""
    if calc["married"]:
        regimes = "".join(
            f'<span style="margin-right:12px;">{_checkbox(data.regime_matrimonial or "", r)} {r}</span>'
            for r in REGIMES_MATRIMONIAUX
        )
        conjoint_line = (
            f'<tr><td class="field-label">Nom et prénom du conjoint :</td>'
            f'<td class="field-value">{_esc(data.conjoint_nom) or _blank()}</td></tr>'
            if calc["needs_conjoint_info"] else ""
        )
        conjoint_block = f"""<p style="font-weight:bold;font-size:9pt;margin-bottom:2px;">Régime matrimonial :</p>
  <div>{regimes}</div>
  <table class="fields-table">{conjoint_line}</table>"""

    age_warn = (
        '<div class="note" style="color:#b00;">⚠ Le demandeur semble mineur — '
        'autorisation parentale ou émancipation requise.</div>'
        if calc["age"] is not None and not calc["age_ok"] else ""
    )

    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DU DEMANDEUR</div>
  <table class="fields-table">
    <tr><td class="field-label">Nom :</td><td class="field-value">{_esc(data.nom) or _blank()}</td></tr>
    <tr><td class="field-label">Prénom :</td><td class="field-value">{_esc(data.prenom) or _blank()}</td></tr>
    <tr><td class="field-label">NIN (18 chiffres) :</td><td class="field-value">{_esc(data.nin) or _blank()}</td></tr>
    <tr><td class="field-label">Date et lieu de naissance :</td><td class="field-value">{_esc(data.date_naissance) or '....../....../......'} à {_esc(data.lieu_naissance) or '....................'}</td></tr>
    <tr><td class="field-label">Nationalité :</td><td class="field-value">{_esc(data.nationalite)}</td></tr>
    <tr><td class="field-label">Adresse personnelle :</td><td class="field-value">{_esc(data.adresse_personnelle) or _blank()}</td></tr>
  </table>
  <p style="font-weight:bold;font-size:9pt;margin-bottom:2px;">Situation matrimoniale :</p>
  <div>{situations}</div>
  {conjoint_block}
  {age_warn}
</div>"""


def _commerce_html(data: F2Data) -> str:
    locaux = ["Local loué", "Propriété", "Domicile", "Emplacement dans marché/foire"]
    locaux_lines = "".join(
        f'<span style="margin-right:12px;">{_checkbox(data.nature_local, l)} {l}</span>'
        for l in locaux
    )
    bail_line = (
        f'<table class="fields-table"><tr><td class="field-label">Durée du bail (années) :</td>'
        f'<td class="field-value">{data.duree_bail_annees or _blank(15)}</td></tr></table>'
        if data.nature_local == "Local loué" else ""
    )
    bail_note = (
        '<div class="note">⚠ Bail de 3 ans minimum requis pour l\'immatriculation '
        '(contrat de bail enregistré).</div>'
        if data.nature_local == "Local loué" and (data.duree_bail_annees or 0) < 3 else ""
    )

    return f"""<div class="section">
  <div class="section-title">II — LE FONDS DE COMMERCE</div>
  <table class="fields-table">
    <tr><td class="field-label">Nom commercial (enseigne) :</td><td class="field-value">{_esc(data.nom_commercial) or _blank()}</td></tr>
    <tr><td class="field-label">Activité détaillée :</td><td class="field-value">{_esc(data.activite) or _blank()}</td></tr>
    <tr><td class="field-label">Adresse du commerce :</td><td class="field-value">{_esc(data.adresse_commerce) or _blank()}</td></tr>
    <tr><td class="field-label">Commune :</td><td class="field-value">{_esc(data.commune_commerce) or _blank(20)}</td></tr>
  </table>
  <p style="font-weight:bold;font-size:9pt;margin-bottom:2px;">Nature d'occupation du local :</p>
  <div>{locaux_lines}</div>
  {bail_line}
  {bail_note}
</div>"""


def _documents_html(calc: dict) -> str:
    docs = [
        "Demande signée sur papier libre ou formulaire CNRC",
        "Extrait de naissance (moins de 3 mois pour les étrangers)",
        "Pièce d'identité nationale (copie)",
        "Certificat de résidence (moins de 3 mois)",
        "Casier judiciaire n°3 (moins de 3 mois)",
        "Justificatif d'occupation du local : contrat de bail enregistré OU acte de propriété OU attestation de domiciliation",
        "Deux photos d'identité",
    ]
    items = "".join(f'<div class="checkbox-line">☐ {d}</div>' for d in docs)
    extra = []
    if calc["needs_conjoint_info"]:
        extra.append("Acte de mariage (régime communautaire)")
    if calc["needs_bail"]:
        extra.append("Contrat de bail enregistré (bail ≥ 3 ans)")
    extra_items = "".join(f'<div class="checkbox-line">☐ {d}</div>' for d in extra)

    return f"""<div class="section">
  <div class="section-title">III — PIÈCES CONSTITUTIVES DU DOSSIER</div>
  {items}
  {extra_items}
  <div class="note">Cochez les pièces jointes au dossier. Toutes sont obligatoires.</div>
</div>"""


def _payment_html(calc: dict) -> str:
    return f"""<div class="section">
  <div class="section-title">IV — DROITS DE TIMBRE</div>
  <table class="summary-table">
    <tr><td class="label">Droit fixe d'immatriculation (timbre fiscal) :</td><td class="amount">{_fmt(calc['timbre_cost'])} DA</td></tr>
    <tr class="total-row"><td class="label"><strong>Total à payer :</strong></td><td class="amount"><strong>{_fmt(calc['timbre_cost'])} DA</strong></td></tr>
  </table>
</div>"""


def _signature_html(data: F2Data) -> str:
    return f"""<div class="section">
  <div class="attestation">
    Je soussigné(e) demande mon immatriculation au registre du commerce en qualité de
    commerçant (personne physique) et certifie l'exactitude des renseignements fournis,
    m'engageant à exercer une activité commerciale conformément à la législation en vigueur.
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {_esc(data.fait_a) or '....................'} <strong>le</strong> {_esc(data.date_declaration) or '....../....../......'}
  </div>
  <div class="signature-block">
    <div class="sig-box">Signature du demandeur<br><br><br>(précédée de « Lu et approuvé »)</div>
    <div class="sig-box">Cadre réservé au CNRC<br><br><br>Cachet et signature</div>
  </div>
</div>"""


def _legal_html() -> str:
    return """<div class="section legal-page">
  <div class="page-header">RÉFÉRENCES LÉGALES — REGISTRE DU COMMERCE</div>
  <p>Base légale : Loi n°05-06 du 23 février 2005 modifiant l'ordonnance n°75-59 relative
  au registre du commerce ; Décret exécutif n°07-161 du 27 mai 2007.</p>
  <p>Sont tenus de s'immatriculer : toutes les personnes physiques qui exercent des actes
  de commerce et requièrent la qualité de commerçant, avant le commencement de l'activité.</p>
  <p>L'immatriculation se fait auprès du Centre National du Registre de Commerce (CNRC)
  ou via le portail SIDJILCOM. Le défaut d'immatriculation est sanctionné pénalement ;
  la capacité commerciale est exigée (majorité, non-interdiction d'exercer).</p>
</div>"""


# ── Main generator ────────────────────────────────────────────────────────────

def generate_f2(data: F2Data) -> str:
    """Generate complete CNRC F2 form as HTML."""
    calc = calculate_f2(data)

    body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>CNRC F2 — Immatriculation {calc['nom_complet'] or 'Commerçant'}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_identity_html(data, calc)}
{_commerce_html(data)}
{_documents_html(calc)}
{_payment_html(calc)}
{_signature_html(data)}
{_legal_html()}

</body>
</html>"""

    hook_generation(
        "cnrc_f2",
        {"nom_commercial": data.nom_commercial, "wilaya": data.wilaya},
        body,
    )
    return body


generate_f2_html = generate_f2


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = F2Data(
        wilaya="32-El Bayadh",
        centre_cnrc="CNRC — guichet El Bayadh",
        nom="Mahi",
        prenom="Kamel Abdelghani",
        nin="199603061234567890",
        date_naissance="06/03/1996",
        lieu_naissance="El Bayadh",
        situation_matrimoniale="Marié(e)",
        regime_matrimonial="Séparation de biens",
        nom_commercial="Épicerie El Baraka",
        activite="Commerce de détail alimentaire général",
        adresse_personnelle="Centre-ville, El Bayadh",
        adresse_commerce="Rue de la République, El Bayadh",
        commune_commerce="El Bayadh",
        nature_local="Local loué",
        duree_bail_annees=5,
        fait_a="El Bayadh",
        date_declaration="10/02/2026",
    )

    calc = calculate_f2(sample)
    print("=== CNRC F2 — Immatriculation Personne Physique ===")
    print(f"Demandeur : {calc['nom_complet']} ({calc['age']} ans)")
    print(f"Nom commercial : {sample.nom_commercial}")
    print(f"Bail requis ≥3 ans : {calc['needs_bail']}, durée déclarée : {sample.duree_bail_annees}")
    print(f"Info conjoint requise : {calc['needs_conjoint_info']}")
    print(f"Timbre : {_fmt(calc['timbre_cost'])} DA")

    if "--html" in sys.argv:
        html = generate_f2(sample)
        out = "cnrc_f2_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out} ({len(html):,} chars)")
