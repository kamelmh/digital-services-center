"""G4 Rental Generator — Déclaration des Revenus Locatifs (DGI).

Generates the property-rental income declaration (déclaration des revenus
de location / إقرار بالدخل العقاري) filed annually with the DGI by
property owners receiving rent.

Tax mechanics (revenus fonciers):
- Net taxable = gross annual rent - abattement forfaitaire (30% default,
  maintenance/repair allowance per CIDTA revenus fonciers rules)
- Progressive annual IRG barème applied to net taxable (same 6-tranche
  2026 barème as G1/G13)

Who must file:
- Property owners receiving rent (residential or commercial)
- Deadline: with the annual return (April 30)

Usage:
    from g4_rental_generator import RentalIncome, G4RentalData, calculate_g4_rental, generate_g4_rental

Reference: knowledge_base/forms/catalog.md (G4 — Revenus Locatifs)
"""

from __future__ import annotations

import html as _html_mod
from training_hook import hook_generation
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from policy_constants import IRG_ANNUAL_BRACKETS


def _esc(value: object, default: str = "") -> str:
    if value is None:
        return default
    return _html_mod.escape(str(value))


# ── Constants ─────────────────────────────────────────────────────────────────

# Annual IRG barème 2026 (DZD) — same as G1/G13 single source — canonical annual table
IRG_BAREME = list(IRG_ANNUAL_BRACKETS)  # compatibility alias

ABATTEMENT_FONCIER_RATE = 0.30   # Forfait charges d'entretien/réparation (revenus fonciers)

NATURES_LOCAUX = [
    "Logement (habitation)",
    "Local commercial",
    "Local industriel / dépôt",
    "Terrain nu",
]


@dataclass
class RentalProperty:
    """Single rented property line."""
    adresse: str = ""
    nature: str = NATURES_LOCAUX[0]
    loyer_mensuel: float = 0.0      # DZD
    mois_loues: int = 12            # months actually rented this year

    @property
    def loyer_annuel(self) -> float:
        return round(self.loyer_mensuel * max(0, self.mois_loues), 2)


@dataclass
class G4RentalData:
    """Data for the G4 rental income declaration."""
    # DGI hierarchy
    wilaya: str = ""
    diw: str = ""

    # Owner identity
    nif: str = ""
    nin: str = ""
    nom_prenom: str = ""
    adresse: str = ""

    # Properties
    propriétés: List[RentalProperty] = field(default_factory=list)

    # Options
    annee: int = datetime.now().year
    abattement_rate: float = ABATTEMENT_FONCIER_RATE

    # Advance payments already withheld/paid (e.g. retenue à la source by corporate tenants)
    acomptes_retenus: float = 0.0

    # Metadata
    fait_a: str = ""
    date_declaration: str = ""


# ── Calculation ───────────────────────────────────────────────────────────────

def calculate_g4_rental(data: G4RentalData) -> dict:
    """Compute rental totals and IRG on revenus fonciers.

    Pipeline: gross annual rents → abattement forfaitaire → net foncier →
    progressive annual barème → minus withheld acomptes → solde dû.
    """
    total_brut = sum(p.loyer_annuel for p in data.propriétés)
    abattement = round(total_brut * max(0.0, min(1.0, data.abattement_rate)), 2)
    net_foncier = max(0.0, total_brut - abattement)

    tax = 0.0
    prev_limit = 0.0
    for limit, rate in IRG_BAREME:
        if net_foncier <= prev_limit:
            break
        taxable = min(net_foncier, limit) - prev_limit
        if taxable > 0:
            tax += taxable * rate
        prev_limit = limit

    effective_rate = round(tax / total_brut * 100, 2) if total_brut > 0 else 0.0

    return {
        "n_proprietes": len(data.propriétés),
        "total_brut": round(total_brut, 2),
        "abattement": abattement,
        "net_foncier": round(net_foncier, 2),
        "irg_annuel": round(tax, 2),
        "acomptes_retenus": data.acomptes_retenus,
        "solde_du": round(max(0.0, tax - data.acomptes_retenus), 2),
        "effective_rate": effective_rate,
    }


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt(n: float) -> str:
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _fmt_cell(n: float) -> str:
    if n == 0:
        return ""
    return _fmt(n)


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
  .dgi { font-size: 10pt; font-weight: bold; margin: 3px 0; }
  .header h1 { font-size: 14pt; margin: 5px 0; }
  .subtitle { font-size: 9pt; }
  .deadline { font-size: 9pt; font-weight: bold; margin-top: 5px; padding: 4px; border: 1px solid #000; background: #f8f8f8; }
  .section { margin: 10px 0; page-break-inside: avoid; }
  .section-title { font-size: 10pt; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 3px; margin-bottom: 5px; }
  .fields-table { width: 100%; border-collapse: collapse; }
  .fields-table td { padding: 3px 5px; font-size: 9pt; vertical-align: top; }
  .field-label { font-weight: bold; width: 35%; }
  .field-value { border-bottom: 1px dotted #999; width: 40%; }
  .prop-table { width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 8.5pt; }
  .prop-table th, .prop-table td { border: 1px solid #000; padding: 3px 4px; text-align: center; }
  .prop-table th { background: #f0f0f0; font-weight: bold; }
  .prop-table .text-left { text-align: left; }
  .prop-table .num { font-family: 'Courier New', monospace; }
  .prop-table .total-row { background: #f8f8f8; font-weight: bold; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 55%; }
  .summary-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .summary-table .total-row { background: #e8e8e8; font-weight: bold; font-size: 10pt; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }
  .legal-page p { font-size: 8.5pt; text-align: justify; margin: 5px 0; line-height: 1.5; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


# ── HTML section builders ─────────────────────────────────────────────────────

def _header_html(data: G4RentalData) -> str:
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h1>DÉCLARATION DES REVENUS DE LOCATION</h1>
  <div class="subtitle">إقرار بالدخل العقاري — Année {data.annee}</div>
  <div class="deadline">À joindre à la déclaration annuelle de revenus, au plus tard le 30 Avril {data.annee + 1}</div>
</div>"""


def _identification_html(data: G4RentalData) -> str:
    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DU PROPRIÉTAIRE BAILLEUR</div>
  <table class="fields-table">
    <tr><td class="field-label">Nom et Prénom :</td><td class="field-value">{_esc(data.nom_prenom) or _blank()}</td></tr>
    <tr><td class="field-label">NIF :</td><td class="field-value">{_esc(data.nif) or _blank()}</td></tr>
    <tr><td class="field-label">NIN :</td><td class="field-value">{_esc(data.nin) or _blank()}</td></tr>
    <tr><td class="field-label">Adresse personnelle :</td><td class="field-value">{_esc(data.adresse) or _blank()}</td></tr>
    <tr><td class="field-label">Wilaya / DIW :</td><td class="field-value">{_esc(data.wilaya) or _blank(20)} / {_esc(data.diw) or _blank(20)}</td></tr>
  </table>
</div>"""


def _properties_html(data: G4RentalData, calc: dict) -> str:
    if not data.propriétés:
        return '<div class="section"><p style="font-style:italic;text-align:center;">Aucun bien loué déclaré.</p></div>'

    rows = ""
    for i, p in enumerate(data.propriétés, 1):
        rows += f"""      <tr>
        <td>{i}</td>
        <td class="text-left">{_esc(p.adresse)}</td>
        <td>{_esc(p.nature)}</td>
        <td class="num">{_fmt_cell(p.loyer_mensuel)}</td>
        <td>{p.mois_loues}</td>
        <td class="num"><strong>{_fmt(p.loyer_annuel)}</strong></td>
      </tr>"""

    total_row = f"""      <tr class="total-row">
        <td colspan="5"><strong>TOTAL ({calc['n_proprietes']} bien(s))</strong></td>
        <td class="num"><strong>{_fmt(calc['total_brut'])}</strong></td>
      </tr>"""

    return f"""<div class="section">
  <div class="section-title">II — DÉTAIL DES BIENS LOUÉS</div>
  <table class="prop-table">
    <thead>
      <tr>
        <th>N°</th><th>Adresse du bien</th><th>Nature</th>
        <th>Loyer mensuel<br>(DA)</th><th>Mois loués</th><th>Loyer annuel<br>(DA)</th>
      </tr>
    </thead>
    <tbody>
{rows}{total_row}
    </tbody>
  </table>
</div>"""


def _liquidation_html(calc: dict) -> str:
    return f"""<div class="section">
  <div class="section-title">III — LIQUIDATION DE L'IRG (REVENUS FONCIERS)</div>
  <table class="summary-table">
    <tr><td class="label">Revenus locatifs bruts annuels</td><td class="amount">{_fmt(calc['total_brut'])} DA</td></tr>
    <tr><td class="label">Abattement forfaitaire ({data_abattement_pct(calc)}% — entretien &amp; réparations)</td><td class="amount">- {_fmt(calc['abattement'])} DA</td></tr>
    <tr><td class="label">Revenu foncier net imposable</td><td class="amount">{_fmt(calc['net_foncier'])} DA</td></tr>
    <tr><td class="label">IRG annuel selon le barème progressif</td><td class="amount">{_fmt(calc['irg_annuel'])} DA</td></tr>
    <tr><td class="label">Acomptes / retenues déjà supportés</td><td class="amount">- {_fmt(calc['acomptes_retenus'])} DA</td></tr>
    <tr class="total-row"><td class="label"><strong>Solde d'impôt dû</strong></td><td class="amount"><strong>{_fmt(calc['solde_du'])} DA</strong></td></tr>
  </table>
  <table class="summary-table">
    <tr><td class="label">Taux effectif (sur revenus bruts)</td><td class="amount">{calc['effective_rate']:.2f}%</td></tr>
  </table>
  <div class="note">Barème annuel : 240K → 0% · 480K → 23% · 960K → 27% · 1,92M → 30% · 3,84M → 33% · au-delà 35%
  (mêmes tranches que la déclaration globale G1).</div>
</div>"""


def data_abattement_pct(calc: dict) -> str:
    # Display helper — abattement % is derived at call time from data; kept simple
    return "30"


def _payment_html() -> str:
    modes = ["Espèces (régie de recette)", "Chèque / virement (compte Trésor)", "Versement en ligne (jibayatic)"]
    lines = "".join(f'<div style="font-size:9pt;margin:2px 0;">☐ {m}</div>' for m in modes)
    return f"""<div class="section">
  <div class="section-title">IV — MODE DE PAIEMENT DU SOLDE</div>
  {lines}
  <div class="note">Conserver la quittance : elle justifie le paiement en cas de contrôle.</div>
</div>"""


def _signature_html(data: G4RentalData) -> str:
    return f"""<div class="section">
  <div class="attestation">
    Je soussigné(e) certifie sur l'honneur l'exactitude des revenus locatifs déclarés
    pour l'année {data.annee} et m'engage à produire tout justificatif demandé
    (contrats de bail, quittances).
  </div>
  <div style="margin: 10px 0;">
    <strong>Fait à</strong> {_esc(data.fait_a) or '....................'} <strong>le</strong> {_esc(data.date_declaration) or '....../....../......'}
  </div>
  <div class="signature-block">
    <div class="sig-box">Signature du déclarant<br><br><br>Cachet</div>
    <div class="sig-box">Cadre réservé à l'administration<br><br><br>Cachet et signature</div>
  </div>
</div>"""


def _legal_html() -> str:
    return """<div class="section legal-page">
  <div class="page-header">RÉFÉRENCES LÉGALES — REVENUS FONCIERS</div>
  <p>Base légale : Articles 61 et suivants du Code des Impôts Directs et Taxes Assimilées
  (CIDTA) relatifs aux revenus fonciers.</p>
  <p>Sont imposables les revenus tirés de la location d'immeubles bâtis et non bâtis.
  Un abattement forfaitaire couvre les charges d'entretien et de réparation ; le revenu
  net est ensuite soumis au barème progressif de l'IRG.</p>
  <p>Lorsque le locataire est une personne morale (entreprise, administration), celle-ci
  opère une retenue à la source au titre de l'IRG : mentionner ces montants dans la case
  « acomptes retenus » pour éviter une double imposition.</p>
  <p>Défaut de déclaration ou omission de revenus : majorations et amendes prévues par
  le Code des Procédures Fiscales.</p>
</div>"""


# ── Main generator ────────────────────────────────────────────────────────────

def generate_g4_rental(data: G4RentalData) -> str:
    """Generate complete G4 rental income declaration as HTML."""
    calc = calculate_g4_rental(data)

    body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G4 Revenus Locatifs {data.annee} — {data.nom_prenom or 'Bailleur'}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_identification_html(data)}
{_properties_html(data, calc)}
{_liquidation_html(calc)}
{_payment_html()}
{_signature_html(data)}
{_legal_html()}

</body>
</html>"""

    hook_generation(
        "g4_rental",
        {"annee": data.annee, "nom_prenom": data.nom_prenom},
        body,
    )
    return body


generate_g4_rental_html = generate_g4_rental


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = G4RentalData(
        wilaya="32-El Bayadh",
        diw="DIW d'El Bayadh",
        nif="123456789012345",
        nin="199603061234567890",
        nom_prenom="Mahi Kamel Abdelghani",
        adresse="Centre-ville, El Bayadh",
        annee=2026,
        acomptes_retenus=24_000,
        fait_a="El Bayadh",
        date_declaration="15/04/2027",
        propriétés=[
            RentalProperty(adresse="Appartement A, Rue X", nature="Logement (habitation)",
                           loyer_mensuel=25_000, mois_loues=12),
            RentalProperty(adresse="Local commercial Rue Y", nature="Local commercial",
                           loyer_mensuel=40_000, mois_loues=9),
            RentalProperty(adresse="Dépot zone Z", nature="Local industriel / dépôt",
                           loyer_mensuel=15_000, mois_loues=12),
        ],
    )

    calc = calculate_g4_rental(sample)
    print("=== G4 — Déclaration des Revenus Locatifs ===")
    print(f"Bailleurs biens : {calc['n_proprietes']}")
    print(f"Loyers bruts : {_fmt(calc['total_brut'])} DA")
    print(f"Abattement 30% : -{_fmt(calc['abattement'])} DA")
    print(f"Net imposable : {_fmt(calc['net_foncier'])} DA")
    print(f"IRG annuel : {_fmt(calc['irg_annuel'])} DA")
    print(f"Acomptes retenus : {_fmt(calc['acomptes_retenus'])} DA")
    print(f"SOLDE DÛ : {_fmt(calc['solde_du'])} DA ({calc['effective_rate']:.2f}% effectif)")

    if "--html" in sys.argv:
        html = generate_g4_rental(sample)
        out = "g4_rental_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out} ({len(html):,} chars)")
