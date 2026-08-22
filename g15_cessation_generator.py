"""G15 Generator — Déclaration de Cessation d'Activité (DGI).

Generates the business-closure declaration filed with the DGI when a
taxpayer stops a professional/commercial activity.

Who must file:
- Any business or individual ceasing commercial/professional activity
- Deadline: within 30 days of cessation (Art. 296 bis CIDTA practice)
- Triggers: final tax settlement, inventory valuation, NIF deactivation

Usage:
    from g15_cessation_generator import G15Data, calculate_g15, generate_g15

Reference: knowledge_base/forms/catalog.md (G15)
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

RAISONS_CESSATION = [
    "Cessation volontaire de l'activité",
    "Retraite du titulaire",
    "Décès du titulaire",
    "Vente du fonds de commerce",
    "Faillite / liquidation judiciaire",
    "Fusion ou absorption",
    "Changement de statut juridique (poursuite sous autre forme)",
    "Autre motif",
]

REGIMES_FISCAUX = ["Régime réel", "Régime réel simplifié", "Régime forfaitaire", "IFU / Auto-entrepreneur"]


@dataclass
class G15Data:
    """Data for the G15 cessation declaration."""
    # DGI hierarchy
    wilaya: str = ""
    diw: str = ""
    inspection: str = ""

    # Taxpayer identification
    nif: str = ""
    nis: str = ""
    rc: str = ""                       # Registre du Commerce (blank for BNC/auto-entrepreneur)
    nom_raison_sociale: str = ""
    forme_juridique: str = ""          # SARL, personne physique, ...
    activite: str = ""
    adresse_activite: str = ""

    # Regime & accounting
    regime_fiscal: str = "Régime réel"
    date_debut_activite: str = ""
    date_cessation: str = ""           # JJ/MM/AAAA — the effective closure date
    raison: str = RAISONS_CESSATION[0]
    motif_detail: str = ""             # free-text detail when raison == "Autre"

    # Successor / transfert (optional)
    reprise_par_tiers: bool = False
    successeur_nom: str = ""

    # Metadata
    fait_a: str = ""
    date_declaration: str = ""


# ── Calculation ───────────────────────────────────────────────────────────────

def calculate_g15(data: G15Data) -> dict:
    """Validate dates and compute derived flags.

    Returns dict with: duree_annees, duree_label, deadline_declaration,
    is_late, obligations checklist keys.
    """
    def _parse(d: str):
        try:
            return datetime.strptime(d.strip(), "%d/%m/%Y")
        except Exception:
            return None

    debut = _parse(data.date_debut_activite)
    fin = _parse(data.date_cessation)

    duree_annees = None
    if debut and fin and fin >= debut:
        duree_annees = round((fin - debut).days / 365.25, 1)

    # Legal deadline: declaration within 30 days of cessation
    deadline_declaration = None
    is_late = False
    if fin:
        from datetime import timedelta
        deadline_declaration = (fin + timedelta(days=30)).strftime("%d/%m/%Y")
        declared = _parse(data.date_declaration)
        if declared:
            is_late = declared > fin + timedelta(days=30)

    return {
        "duree_annees": duree_annees,
        "duree_label": f"{duree_annees} an(s)" if duree_annees is not None else "",
        "deadline_declaration": deadline_declaration or "....../....../......",
        "is_late": is_late,
        "needs_successeur": data.reprise_par_tiers,
        "final_settlement_required": data.regime_fiscal.startswith("Régime réel"),
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
  .summary-table { width: 100%; border-collapse: collapse; margin: 5px 0; }
  .summary-table td { padding: 4px 8px; font-size: 9pt; border: 1px solid #000; }
  .summary-table .label { font-weight: bold; width: 55%; }
  .summary-table .amount { font-family: 'Courier New', monospace; text-align: right; width: 45%; }
  .summary-table .warn { background: #fff3cd; font-weight: bold; }
  .checkbox-line { font-size: 9pt; margin: 3px 0; }
  .note { font-size: 8pt; color: #666; font-style: italic; margin-top: 3px; }
  .signature-block { display: flex; justify-content: space-between; margin: 15px 0; }
  .sig-box { width: 45%; text-align: center; font-size: 9pt; border-top: 1px solid #000; padding-top: 5px; }
  .attestation { font-size: 9pt; font-style: italic; margin: 10px 0; padding: 5px; border: 1px solid #ccc; }
  .legal-page p { font-size: 8.5pt; text-align: justify; margin: 5px 0; line-height: 1.5; }
  @media print { body { padding: 0; } .no-print { display: none; } }
</style>"""


# ── HTML section builders ─────────────────────────────────────────────────────

def _header_html(data: G15Data) -> str:
    return f"""<div class="header">
  <div class="republique">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>
  <div class="dgi">DIRECTION GÉNÉRALE DES IMPÔTS</div>
  <h1>Série G N°15 — DÉCLARATION DE CESSATION D'ACTIVITÉ</h1>
  <div class="subtitle">إقرار بتوقف النشاط</div>
  <div class="deadline">À déposer dans les 30 jours suivant la date de cessation</div>
</div>"""


def _identification_html(data: G15Data) -> str:
    return f"""<div class="section">
  <div class="section-title">I — IDENTIFICATION DU CONTRIBUABLE</div>
  <table class="fields-table">
    <tr><td class="field-label">Nom / Raison sociale :</td><td class="field-value">{_esc(data.nom_raison_sociale) or _blank()}</td></tr>
    <tr><td class="field-label">Forme juridique :</td><td class="field-value">{_esc(data.forme_juridique) or _blank(20)}</td></tr>
    <tr><td class="field-label">NIF :</td><td class="field-value">{_esc(data.nif) or _blank()}</td></tr>
    <tr><td class="field-label">NIS :</td><td class="field-value">{_esc(data.nis) or _blank()}</td></tr>
    <tr><td class="field-label">N° Registre de Commerce :</td><td class="field-value">{_esc(data.rc) or _blank(20)}</td></tr>
    <tr><td class="field-label">Activité exercée :</td><td class="field-value">{_esc(data.activite) or _blank()}</td></tr>
    <tr><td class="field-label">Adresse de l'activité :</td><td class="field-value">{_esc(data.adresse_activite) or _blank()}</td></tr>
    <tr><td class="field-label">Régime fiscal :</td><td class="field-value">{_esc(data.regime_fiscal)}</td></tr>
  </table>
</div>"""


def _cessation_html(data: G15Data, calc: dict) -> str:
    raisons = "".join(
        f'<div class="checkbox-line">{_checkbox(data.raison, r)} {r}</div>'
        for r in RAISONS_CESSATION
    )
    late_warn = (
        '<div class="note" style="color:#b00;">⚠ Déclaration hors délai légal de 30 jours '
        '(majorations possibles).</div>' if calc["is_late"] else ""
    )
    detail_line = (
        f'<table class="fields-table"><tr><td class="field-label">Précision du motif :</td>'
        f'<td class="field-value">{_esc(data.motif_detail) or _blank()}</td></tr></table>'
        if data.raison == "Autre motif" else ""
    )
    return f"""<div class="section">
  <div class="section-title">II — RENSEIGNEMENTS SUR LA CESSATION</div>
  <table class="fields-table">
    <tr><td class="field-label">Date de début d'activité :</td><td class="field-value">{_esc(data.date_debut_activite) or '....../....../......'}</td></tr>
    <tr><td class="field-label"><strong>Date de cessation :</strong></td><td class="field-value"><strong>{_esc(data.date_cessation) or '....../....../......'}</strong></td></tr>
    <tr><td class="field-label">Durée d'exercice :</td><td class="field-value">{calc['duree_label'] or _blank(15)}</td></tr>
    <tr><td class="field-label">Déclaration à déposer au plus tard le :</td><td class="field-value">{calc['deadline_declaration']}</td></tr>
  </table>
  <p style="font-weight:bold;font-size:9pt;">Motif de la cessation :</p>
  {raisons}
  {detail_line}
  {late_warn}
</div>"""


def _succession_html(data: G15Data) -> str:
    reprise_lines = (
        '<div class="checkbox-line">☑ Oui — l\'activité est reprise par un tiers</div>'
        '<div class="checkbox-line">☐ Non</div>' if data.reprise_par_tiers
        else '<div class="checkbox-line">☐ Oui — l\'activité est reprise par un tiers</div>'
             '<div class="checkbox-line">☑ Non</div>'
    )
    successeur = (
        f'<table class="fields-table"><tr><td class="field-label">Nom du repreneur :</td>'
        f'<td class="field-value">{_esc(data.successeur_nom) or _blank()}</td></tr></table>'
        if data.reprise_par_tiers else ""
    )
    return f"""<div class="section">
  <div class="section-title">III — REPRISE PAR UN TIERS</div>
  {reprise_lines}
  {successeur}
  <div class="note">En cas de vente ou transmission du fonds, joindre l'acte et les références
  d'enregistrement. Le repreneur doit souscrire une déclaration d'existence (G8).</div>
</div>"""


def _obligations_html(data: G15Data, calc: dict) -> str:
    items = [
        ("Dépôt des déclarations de résultats (exercice en cours)", True),
        ("Paiement du solde d'impôt exigible", True),
        ("Inventaire et évaluation des stocks au jour de la cessation", calc["final_settlement_required"]),
        ("Régularisation de la TVA sur stocks et immobilisations", calc["final_settlement_required"]),
        ("Dépôt des déclarations de salaires (G29/G30) si employeur", True),
        ("Déclaration des cessions d'immobilisations", True),
        ("Restitution des carnets à souches et documents fiscaux", True),
    ]
    rows = "".join(
        f'<div class="checkbox-line">☐ {label}</div>'
        if required else ""
        for label, required in items
    )
    return f"""<div class="section">
  <div class="section-title">IV — OBLIGATIONS FISCALES FINALES (checklist)</div>
  {rows}
  <div class="note">Cochez les obligations déjà accomplies. Le défaut de dépôt expose à des
  taxes d'office et majorations.</div>
</div>"""


def _signature_html(data: G15Data) -> str:
    return f"""<div class="section">
  <div class="attestation">
    Je soussigné(e) certifie avoir cessé toute activité à la date indiquée ci-dessus
    et m'engage à régler le solde de mes impositions.
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
  <div class="page-header">RÉFÉRENCES LÉGALES — CESSATION D'ACTIVITÉ</div>
  <p>Base légale : Articles 296 bis et suivants du Code des Impôts Directs et Taxes
  Assimilées (CIDTA), relatifs à la taxation des bénéfices en cas de cessation.</p>
  <p>En cas de cessation, l'exercice est réputé clos à la date d'arrêté ; les bénéfices
  et stocks sont immédiatement imposés. Les plus-values réalisées ou constatées sur
  éléments d'actif sont taxables au titre de cet exercice particulier.</p>
  <p>La déclaration de cessation doit être déposée auprès du centre des impôts
  compétent dans un délai de trente (30) jours. Le défaut de déclaration entraîne
  taxation d'office conformément au Code des Procédures Fiscales.</p>
</div>"""


# ── Main generator ────────────────────────────────────────────────────────────

def generate_g15(data: G15Data) -> str:
    """Generate complete G15 cessation declaration as HTML."""
    calc = calculate_g15(data)

    body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<title>G15 — Cessation d'Activité {data.nom_raison_sociale or ''}</title>
{_css()}
</head>
<body>

{_header_html(data)}
{_identification_html(data)}
{_cessation_html(data, calc)}
{_succession_html(data)}
{_obligations_html(data, calc)}
{_signature_html(data)}
{_legal_html()}

</body>
</html>"""

    hook_generation(
        "g15_cessation",
        {"nom_raison_sociale": data.nom_raison_sociale, "date_cessation": data.date_cessation},
        body,
    )
    return body


generate_g15_html = generate_g15


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sample = G15Data(
        wilaya="32-El Bayadh",
        diw="DIW d'El Bayadh",
        inspection="Inspection des Impôts d'El Bayadh Centre",
        nif="123456789012345",
        nis="0998161234567",
        rc="32/00-7654321B18",
        nom_raison_sociale="Entreprise Mahi Travaux",
        forme_juridique="Personne physique",
        activite="Travaux de plomberie générale",
        adresse_activite="Centre-ville, El Bayadh",
        regime_fiscal="Régime réel simplifié",
        date_debut_activite="01/06/2018",
        date_cessation="31/12/2026",
        raison=RAISONS_CESSATION[1],  # Retraite
        fait_a="El Bayadh",
        date_declaration="10/01/2027",
    )

    calc = calculate_g15(sample)
    print("=== G15 — Déclaration de Cessation d'Activité ===")
    print(f"Contribuable : {sample.nom_raison_sociale}")
    print(f"Durée d'exercice : {calc['duree_label']}")
    print(f"Dépôt au plus tard le : {calc['deadline_declaration']}")
    print(f"Hors délai : {calc['is_late']}")
    print(f"Régularisation TVA requise : {calc['final_settlement_required']}")

    if "--html" in sys.argv:
        html = generate_g15(sample)
        out = "g15_sample.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML written to {out} ({len(html):,} chars)")
