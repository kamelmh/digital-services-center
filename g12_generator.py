"""G12 IFU Declaration Generator — template-based, no LLM required.

Generates filled G12 (Série G N°12) forms for Algerian IFU taxpayers.
Calculates IFU automatically based on activity type and forecast CA.

Usage:
    from g12_generator import generate_g12
    html = generate_g12({
        "nif": "1234567890",
        "business_name": "SARL Exemple",
        "activity": "vente",
        "activity_label": "Commerce de détail",
        "ca_forecast": 3_000_000,
        "year": 2026,
        "payment_mode": "fractionne",
    })
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ── Constants ─────────────────────────────────────────────────────────────────

IFU_RATES = {
    "vente": {"label": "Commerce de vente (production/vente)", "rate": 0.05, "min": 30_000},
    "services": {"label": "Prestation de services", "rate": 0.12, "min": 30_000},
    "auto_entrepreneur": {"label": "Auto-entrepreneur (ANAE)", "rate": 0.005, "min": 10_000},
    "recyclage": {"label": "Recyclage papier/déchets", "rate": 0.05, "min": 30_000},
}

PAYMENT_MODES = {
    "integral": {"label": "Paiement intégral", "label_ar": "الدفع الكامل"},
    "fractionne": {"label": "Paiement fractionné (50% + 25% + 25%)", "label_ar": "الدفع المجزأ"},
}

TVA_RATE = 0.19


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class G12Data:
    """Input data for G12 generation."""
    nif: str
    business_name: str
    activity: str  # key in IFU_RATES
    activity_label: str = ""
    ca_forecast: float = 0
    year: int = datetime.now().year
    payment_mode: str = "integral"  # integral or fractionne
    # Optional extras
    address: str = ""
    commune: str = ""
    wilaya: str = ""
    activite_principale: str = ""  # code CNRC
    beneficiaire: str = ""  # name of person signing


@dataclass
class G12Result:
    """Calculated G12 results."""
    ca_forecast: float
    activity_rate: float
    activity_label: str
    ifu_amount: float
    ifu_minimum: float
    ifu_final: float
    # Fractionné breakdown
    tranche_1: float = 0
    tranche_2: float = 0
    tranche_3: float = 0
    tranche_1_date: str = ""
    tranche_2_date: str = ""
    tranche_3_date: str = ""
    # TVA estimate
    tva_estimate: float = 0
    # Payment mode
    payment_mode: str = "integral"


def calculate_ifu(data: G12Data) -> G12Result:
    """Calculate IFU from G12 input data."""
    activity_config = IFU_RATES.get(data.activity, IFU_RATES["vente"])
    rate = activity_config["rate"]
    minimum = activity_config["min"]
    label = data.activity_label or activity_config["label"]

    raw_ifu = data.ca_forecast * rate
    ifu_final = max(raw_ifu, minimum)

    # TVA estimate (for information only)
    tva_estimate = data.ca_forecast * TVA_RATE

    result = G12Result(
        ca_forecast=data.ca_forecast,
        activity_rate=rate,
        activity_label=label,
        ifu_amount=raw_ifu,
        ifu_minimum=minimum,
        ifu_final=ifu_final,
        tva_estimate=tva_estimate,
        payment_mode=data.payment_mode,
    )

    if data.payment_mode == "fractionne":
        year = data.year
        result.tranche_1 = int(ifu_final * 0.50)
        result.tranche_2 = int(ifu_final * 0.25)
        result.tranche_3 = int(ifu_final - result.tranche_1 - result.tranche_2)
        result.tranche_1_date = f"30/06/{year}"
        result.tranche_2_date = f"15/09/{year}"
        result.tranche_3_date = f"15/12/{year}"
    else:
        result.tranche_1 = int(ifu_final)
        result.tranche_2 = 0
        result.tranche_3 = 0
        result.tranche_1_date = f"30/06/{data.year}"
        result.tranche_2_date = "—"
        result.tranche_3_date = "—"

    return result


def _fmt(n: float) -> str:
    """Format number with thousand separators."""
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


# ── HTML Generator ────────────────────────────────────────────────────────────

def generate_g12_html(data: G12Data) -> str:
    """Generate filled G12 form as HTML."""
    result = calculate_ifu(data)
    now = datetime.now()
    year = data.year
    nif = data.nif or "________________"

    payment_cfg = PAYMENT_MODES.get(data.payment_mode, PAYMENT_MODES["integral"])

    return f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G12 — Déclaration Prévisionnelle IFU {year}</title>
<style>
  @page {{ size: A4; margin: 15mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Times New Roman', serif; font-size: 12pt; color: #1a1a1a; margin: 0; padding: 20px; }}
  .header {{ text-align: center; border: 2px solid #0A1628; padding: 10px; margin-bottom: 15px; }}
  .header h1 {{ font-size: 16pt; margin: 0; color: #0A1628; }}
  .header .subtitle {{ font-size: 11pt; color: #666; margin-top: 5px; }}
  .dsc-footer {{ text-align: center; font-size: 9pt; color: #D4AF37; margin-top: 20px; border-top: 1px solid #D4AF37; padding-top: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
  th, td {{ border: 1px solid #333; padding: 6px 10px; text-align: right; font-size: 11pt; }}
  th {{ background: #f0f0f0; font-weight: bold; }}
  td.label {{ text-align: right; font-weight: bold; width: 40%; background: #fafafa; }}
  td.value {{ text-align: center; width: 60%; }}
  .section {{ margin: 15px 0; }}
  .section-title {{ font-size: 13pt; font-weight: bold; color: #0A1628; border-bottom: 2px solid #0A1628; padding-bottom: 5px; margin-bottom: 10px; }}
  .highlight {{ background: #fffde7; font-weight: bold; }}
  .amount {{ font-family: 'Courier New', monospace; font-size: 13pt; font-weight: bold; }}
  .note {{ font-size: 10pt; color: #666; font-style: italic; margin-top: 5px; }}
  .fractions {{ background: #f5f5f0; padding: 10px; border-radius: 5px; margin: 10px 0; }}
  .signature {{ margin-top: 40px; display: flex; justify-content: space-between; }}
  .signature-box {{ width: 45%; text-align: center; border-top: 1px solid #333; padding-top: 5px; }}
  @media print {{
    body {{ padding: 0; }}
    .no-print {{ display: none; }}
  }}
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <h1>SÉRIE G N°12</h1>
  <div class="subtitle">DÉCLARATION PRÉVISIONNELLE DE L'IMPÔT FORFAITAIRE UNIQUE (IFU)</div>
  <div class="subtitle">Année {year}</div>
</div>

<!-- Business Info -->
<div class="section">
  <div class="section-title">I — IDENTIFICATION DU REDEVABLE</div>
  <table>
    <tr>
      <td class="label">NIF:</td>
      <td class="value">{nif}</td>
      <td class="label">Activité principale (code CNRC):</td>
      <td class="value">{data.activite_principale or '____'}</td>
    </tr>
    <tr>
      <td class="label">Raison sociale / Nom:</td>
      <td class="value" colspan="3">{data.business_name or '________________'}</td>
    </tr>
    <tr>
      <td class="label">Adresse:</td>
      <td class="value" colspan="3">{data.address or '________________'}</td>
    </tr>
    <tr>
      <td class="label">Commune:</td>
      <td class="value">{data.commune or '____'}</td>
      <td class="label">Wilaya:</td>
      <td class="value">{data.wilaya or '____'}</td>
    </tr>
  </table>
</div>

<!-- Exemption -->
<div class="section">
  <div class="section-title">II — EXONÉRATION</div>
  <table>
    <tr>
      <td class="label">Bénéficiez-vous d'une exonération ?</td>
      <td class="value">☐ Oui ☐ Non</td>
    </tr>
    <tr>
      <td class="label">Si oui, précisez le motif:</td>
      <td class="value">☐ ANADE/ANSEJ ☐ CNAC ☐ ANGEM ☐ Artisanal ☐ Autre</td>
    </tr>
  </table>
</div>

<!-- CA Forecast -->
<div class="section">
  <div class="section-title">III — CHIFFRE D'AFFAIRES PRÉVISIONNEL</div>
  <table>
    <tr>
      <th>Type d'activité</th>
      <th>Taux IFU</th>
      <th>CA Prévisionnel (DA)</th>
      <th>IFU Calculé (DA)</th>
    </tr>
    <tr>
      <td class="value">{result.activity_label}</td>
      <td class="value">{result.activity_rate * 100:.1f}%</td>
      <td class="value amount">{_fmt(result.ca_forecast)}</td>
      <td class="value amount">{_fmt(result.ifu_amount)}</td>
    </tr>
    <tr>
      <td class="label" colspan="3">IFU Minimum (seuil légal)</td>
      <td class="value amount">{_fmt(result.ifu_minimum)}</td>
    </tr>
    <tr class="highlight">
      <td class="label" colspan="3">IFU TOTAL (max du calcul et du seuil)</td>
      <td class="value amount" style="font-size: 14pt;">{_fmt(result.ifu_final)}</td>
    </tr>
  </table>
  <div class="note">Montant en chiffres: {_fmt(result.ifu_final)} DA — Montant en lettres: à compléter</div>
</div>

<!-- Payment Mode -->
<div class="section">
  <div class="section-title">IV — MODE DE PAIEMENT</div>
  <p><strong>{payment_cfg["label"]}</strong> ({payment_cfg["label_ar"]})</p>

  {"<div class='fractions'>" + f"""
  <table>
    <tr>
      <th>Tranche</th>
      <th>Montant (DA)</th>
      <th>Échéance</th>
      <th>% du total</th>
    </tr>
    <tr>
      <td class="value">1ère tranche (dépôt)</td>
      <td class="value amount">{_fmt(result.tranche_1)}</td>
      <td class="value">{result.tranche_1_date}</td>
      <td class="value">50%</td>
    </tr>
    <tr>
      <td class="value">2ème tranche</td>
      <td class="value amount">{_fmt(result.tranche_2)}</td>
      <td class="value">{result.tranche_2_date}</td>
      <td class="value">25%</td>
    </tr>
    <tr>
      <td class="value">3ème tranche</td>
      <td class="value amount">{_fmt(result.tranche_3)}</td>
      <td class="value">{result.tranche_3_date}</td>
      <td class="value">25%</td>
    </tr>
  </table>
  """ if data.payment_mode == "fractionne" else "<p>Paiement intégral à la date limite.</p>"}
</div>

<!-- TVA Info -->
<div class="section">
  <div class="section-title">V — TVA ESTIMÉE (à titre indicatif)</div>
  <table>
    <tr>
      <td class="label">CA prévisionnel HT:</td>
      <td class="value amount">{_fmt(result.ca_forecast)}</td>
      <td class="label">TVA (19%):</td>
      <td class="value amount">{_fmt(result.tva_estimate)}</td>
    </tr>
    <tr>
      <td class="label">CA TTC:</td>
      <td class="value amount">{_fmt(result.ca_forecast + result.tva_estimate)}</td>
      <td class="label"></td>
      <td class="value"></td>
    </tr>
  </table>
  <div class="note">La TVA n'est pas incluse dans l'IFU. Elle doit être déclarée séparément via G50.</div>
</div>

<!-- Signature -->
<div class="signature">
  <div class="signature-box">
    Le redevable<br>
    <br><br><br>
    {data.beneficiaire or data.business_name or '________________'}
  </div>
  <div class="signature-box">
    Le Receveur des Impôts<br>
    <br><br><br>
    Cachet et signature
  </div>
</div>

<!-- DSC Footer -->
<div class="dsc-footer">
  Document généré par DSC Digital Services Center — +213 676 773 892<br>
  Date de génération: {now.strftime("%d/%m/%Y à %H:%M")}
</div>

</body>
</html>"""


def generate_g12_text(data: G12Data) -> str:
    """Generate filled G12 as plain text (for printing)."""
    result = calculate_ifu(data)
    year = data.year
    nif = data.nif or "________________"

    lines = [
        "=" * 60,
        "SÉRIE G N°12",
        "DÉCLARATION PRÉVISIONNELLE DE L'IMPÔT FORFAITAIRE UNIQUE (IFU)",
        f"Année {year}",
        "=" * 60,
        "",
        "I — IDENTIFICATION DU REDEVABLE",
        "-" * 40,
        f"  NIF:                              {nif}",
        f"  Raison sociale / Nom:             {data.business_name or '________________'}",
        f"  Activité principale:              {data.activite_principale or '____'}",
        f"  Adresse:                          {data.address or '________________'}",
        f"  Commune:                          {data.commune or '____'}",
        f"  Wilaya:                           {data.wilaya or '____'}",
        "",
        "II — EXONÉRATION",
        "-" * 40,
        "  ☐ ANADE/ANSEJ   ☐ CNAC   ☐ ANGEM   ☐ Artisanal   ☐ Non",
        "",
        "III — CHIFFRE D'AFFAIRES PRÉVISIONNEL",
        "-" * 40,
        f"  Type d'activité:                  {result.activity_label}",
        f"  Taux IFU:                         {result.activity_rate * 100:.1f}%",
        f"  CA Prévisionnel:                  {_fmt(result.ca_forecast)} DA",
        f"  IFU Calculé:                      {_fmt(result.ifu_amount)} DA",
        f"  IFU Minimum (seuil):              {_fmt(result.ifu_minimum)} DA",
        f"  ─────────────────────────────────────────",
        f"  IFU TOTAL:                        {_fmt(result.ifu_final)} DA",
        "",
        "IV — MODE DE PAIEMENT",
        "-" * 40,
        f"  Mode: {PAYMENT_MODES.get(data.payment_mode, PAYMENT_MODES['integral']).label}",
    ]

    if data.payment_mode == "fractionne":
        lines.extend([
            f"  1ère tranche (50%):  {_fmt(result.tranche_1):>12} DA  —  {result.tranche_1_date}",
            f"  2ème tranche (25%):  {_fmt(result.tranche_2):>12} DA  —  {result.tranche_2_date}",
            f"  3ème tranche (25%):  {_fmt(result.tranche_3):>12} DA  —  {result.tranche_3_date}",
        ])
    else:
        lines.append(f"  Montant intégral: {_fmt(result.ifu_final)} DA — à verser avant le {result.tranche_1_date}")

    lines.extend([
        "",
        "V — TVA ESTIMÉE (à titre indicatif)",
        "-" * 40,
        f"  CA HT:          {_fmt(result.ca_forecast):>12} DA",
        f"  TVA (19%):      {_fmt(result.tva_estimate):>12} DA",
        f"  CA TTC:         {_fmt(result.ca_forecast + result.tva_estimate):>12} DA",
        "",
        "NOTE: La TVA n'est pas incluse dans l'IFU. Déclarer séparément via G50.",
        "",
        "=" * 60,
        f"  Le redevable:                       {data.beneficiaire or data.business_name or '________________'}",
        "",
        f"  Le Receveur des Impôts:",
        "  Cachet et signature",
        "",
        "=" * 60,
        f"  Document généré par DSC Digital Services Center",
        f"  +213 676 773 892 — kamelmahi71@gmail.com",
        f"  Date: {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
    ])

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys

    sample = G12Data(
        nif="1234567890",
        business_name="SARL Tech Solutions",
        activity="services",
        activity_label="Prestation de services informatiques",
        ca_forecast=4_800_000,
        year=2026,
        payment_mode="fractionne",
        address="123 Rue Didouche Mourad",
        commune="El Bayadh Centre",
        wilaya="32",
        beneficiaire="Ahmed Benali",
    )

    result = calculate_ifu(sample)
    print(f"IFU: {_fmt(result.ifu_final)} DA")
    print(f"Mode: {result.payment_mode}")
    if result.payment_mode == "fractionne":
        print(f"  1ère: {_fmt(result.tranche_1)} DA ({result.tranche_1_date})")
        print(f"  2ème: {_fmt(result.tranche_2)} DA ({result.tranche_2_date})")
        print(f"  3ème: {_fmt(result.tranche_3)} DA ({result.tranche_3_date})")

    if "--html" in sys.argv:
        html = generate_g12_html(sample)
        out = "g12_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out}")
    else:
        print()
        print(generate_g12_text(sample))
