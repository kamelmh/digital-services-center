"""Generate sample dossier gallery — 3 redacted dossiers as browsable HTML."""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from projections_engine import ProjectionsEngine
from business_defaults import get_defaults, estimate_profitability
from aapi_optimizer import AAAPIOptimizer
from quality_scorer import QualityScorer

SAMPLES = [
    {
        "key": "quincaillerie_elbayadh",
        "title": "Étude de Faisabilité — Quincaillerie",
        "title_ar": "دراسة جدوى — متجر مواد البناء والعتاد",
        "business_type": "quincaillerie",
        "location": "Centre-ville",
        "wilaya": "El Bayadh",
        "investment": 4_600_000,
        "client": "Client Confidentiel",
    },
    {
        "key": "restaurant_oran",
        "title": "Étude de Faisabilité — Restaurant",
        "title_ar": "دراسة جدوى — مطعم",
        "business_type": "restaurant",
        "location": "Bir El Djir",
        "wilaya": "Oran",
        "investment": 8_000_000,
        "client": "Client Confidentiel",
    },
    {
        "key": "cybercafe_alger",
        "title": "Étude de Faisabilité — Cybercafé",
        "title_ar": "دراسة جدوى — مقهى إنترنت",
        "business_type": "cybercafe",
        "location": "Bab Ezzouar",
        "wilaya": "Alger",
        "investment": 4_000_000,
        "client": "Client Confidentiel",
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — DSC</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f5f5f0; color: #1a1a1a; }}
.header {{ background: #0A1628; color: white; padding: 20px 0; }}
.header-inner {{ max-width: 900px; margin: 0 auto; padding: 0 20px; }}
.header h1 {{ font-size: 1.8em; margin-bottom: 5px; }}
.header .subtitle {{ color: #D4AF37; font-size: 1.1em; }}
.header .meta {{ color: #aaa; font-size: 0.9em; margin-top: 10px; }}
.container {{ max-width: 900px; margin: 0 auto; padding: 30px 20px; }}
.section {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.section h2 {{ color: #0A1628; font-size: 1.3em; margin-bottom: 15px; border-bottom: 2px solid #D4AF37; padding-bottom: 8px; }}
.section h3 {{ color: #0A1628; font-size: 1.1em; margin: 15px 0 10px; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
th {{ background: #0A1628; color: white; padding: 10px; text-align: center; font-size: 0.9em; }}
td {{ padding: 8px 10px; border-bottom: 1px solid #e8e8e8; text-align: center; font-size: 0.9em; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.kpi-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }}
.kpi {{ background: #f8f9fa; border-radius: 8px; padding: 15px; text-align: center; }}
.kpi .value {{ font-size: 1.4em; font-weight: bold; color: #0A1628; }}
.kpi .label {{ font-size: 0.85em; color: #666; margin-top: 5px; }}
.kpi.good .value {{ color: #28a745; }}
.kpi.warn .value {{ color: #ffc107; }}
.kpi.bad .value {{ color: #dc3545; }}
.bar {{ height: 8px; background: #e8e8e8; border-radius: 4px; margin: 5px 0; }}
.bar-fill {{ height: 100%; border-radius: 4px; }}
.footer {{ text-align: center; padding: 30px; color: #999; font-size: 0.85em; }}
.badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
.badge-green {{ background: #d4edda; color: #155724; }}
.badge-yellow {{ background: #fff3cd; color: #856404; }}
.badge-red {{ background: #f8d7da; color: #721c24; }}
</style>
</head>
<body>
<div class="header">
<div class="header-inner">
<h1>{title}</h1>
<div class="subtitle">{title_ar}</div>
<div class="meta">{wilaya} — {location} — Investissement: {investment:,} DZD — {date}</div>
</div>
</div>
<div class="container">
{content}
</div>
<div class="footer">
DSC Digital Services Center — Étude de faisabilité (échantillon anonymisé)<br>
contact@dsc-dz.com — {date}
</div>
</body>
</html>"""


def generate_dossier_html(sample: dict) -> str:
    """Generate one dossier HTML page with real financial data."""
    defaults = get_defaults(sample["business_type"])
    investment = sample["investment"]

    # Projections
    engine = ProjectionsEngine(
        business_type=sample["business_type"],
        wilaya=sample["wilaya"],
        investment=investment,
    )
    proj = engine.generate(years=5)
    profitability = estimate_profitability(sample["business_type"], investment)

    # AAPI
    optimizer = AAAPIOptimizer()
    aapi_params = {
        "activity_priority": defaults["aapi_priority"],
        "investment_amount": investment,
        "employees": (defaults["staff_range"][0] + defaults["staff_range"][1]) // 2,
        "equity_ratio": 0.65, "local_integration": 50,
        "cdd_ratio": 0.10, "has_extension": False, "export_ratio": 0,
    }
    score = optimizer.score_project(aapi_params)
    suggestions = optimizer.optimize(score, aapi_params)

    # Quality
    scorer = QualityScorer()
    feas_text = f"""# وصف المشروع
متجر {defaults['name_ar']} في {sample['location']}، ولاية {sample['wilaya']}.
الاستثمار: {investment:,} دج. عدد العمال: {defaults['staff_range'][0]}-{defaults['staff_range'][1]}.

## دراسة السوق
السوق المحلية تشهد طلبا متزايدا على {defaults['name_ar']}. عدد سكان الولاية:(population data).
المنافسة: 3-5 متاجر مشابهة في المنطقة. ميزة الموقع: وسط المدينة.

## الدراسة الفنية
مساحة المحل: 120-200 م2. ساعات العمل: 8 صباحا - 6 مساء.
المعدات: رفوف عرض، نظام كمبيوتر، خزينة أمان.

## الدراسة المالية
الاستثمار: {investment:,} دج. الإيراد الشهري المتوقع: {profitability['monthly_revenue']:,} دج.
هامش الربح الصافي: {profitability['net_margin']:.1%}. الدخل السنوي: {profitability['annual_revenue']:,} دج.

## تحليل المخاطر
مخاطر السوق: متوسطة. مخاطر المنافسة: متوسطة. مخافر التمويل: منخفضة.

## جدوى المشروع
المشروع مجدٍ اقتصادياً باسترداد خلال {profitability['payback_years']:.1f} سنوات.
ROI السنوي: {profitability['roi_annual']:.1%}.

## الخطة التسويقية
التسويق عبر الشبكات الاجتماعية والشارع المحلي. خصومات الافتتاح.

## الخطة التشغيلية
ساعات العمل: 8 صباحا - 6 مساء. أيام العمل: 6 أيام/أسبوع.

## خطة التنمية
توسيع النشاط خلال 3 سنوات. إضافة خدمات جديدة."""

    report = scorer.score("feasibility", feas_text)

    # Build HTML
    profit_color = "good" if profitability["net_margin"] > 0.10 else "warn" if profitability["net_margin"] > 0.05 else "bad"
    van_color = "good" if proj.van > 0 else "bad"
    aapi_color = "good" if score.percentage >= 60 else "warn" if score.percentage >= 40 else "bad"

    criteria_map = {
        "activity_type": ("Nature activité", 420),
        "investment_amount": ("Investissement", 360),
        "employment": ("Emploi", 300),
        "equity_contribution": ("Fonds propres", 200),
        "local_content": ("Contenu local", 60),
        "employment_permanence": ("Pérennité", 60),
        "investment_extension": ("Extension", 70),
        "export_diversification": ("Export", 30),
    }

    aapi_rows = ""
    for key, (label, max_pts) in criteria_map.items():
        val = getattr(score, key, 0)
        pct = (val / max_pts * 100) if max_pts else 0
        color = "#28a745" if pct >= 70 else "#ffc107" if pct >= 40 else "#dc3545"
        aapi_rows += f"""<tr><td>{label}</td><td>{val}/{max_pts}</td>
        <td><div class="bar"><div class="bar-fill" style="width:{pct}%;background:{color};"></div></div></td>
        <td>{pct:.0f}%</td></tr>"""

    fin_rows = ""
    for y in proj.years:
        fin_rows += f"""<tr><td>{y.year}</td><td>{y.revenue:,.0f}</td><td>{y.cogs:,.0f}</td>
        <td>{y.gross_profit:,.0f}</td><td>{y.net_income:,.0f}</td>
        <td>{y.net_margin:.1%}</td><td>{y.cash_flow:,.0f}</td><td>{y.cumulative_cash:,.0f}</td></tr>"""

    suggestions_html = "".join(
        f"<li><strong>{s['criterion']}</strong>: +{s['gap']} pts — {s['advice']}</li>"
        for s in suggestions
    )

    content = f"""
<div class="section">
<h2>1. Résumé Exécutif</h2>
<p>Étude de faisabilité pour un établissement de type <strong>{defaults['name_fr']}</strong> ({defaults['name_ar']}) situé à {sample['location']}, wilaya de {sample['wilaya']}.</p>
<p>Investissement total: <strong>{investment:,} DZD</strong> — dont {defaults['staff_range'][0]}-{defaults['staff_range'][1]} emplois créés.</p>
<div class="kpi-grid">
<div class="kpi {profit_color}"><div class="value">{profitability['net_margin']:.1%}</div><div class="label">Marge Nette</div></div>
<div class="kpi {van_color}"><div class="value">{proj.van:,.0f}</div><div class="label">VAN (5 ans)</div></div>
<div class="kpi"><div class="value">{proj.payback_year}</div><div class="label">Année Récupération</div></div>
</div>
</div>

<div class="section">
<h2>2. Étude de Marché</h2>
<p>Analyse du marché local pour <strong>{defaults['name_fr']}</strong> dans la wilaya de {sample['wilaya']}.</p>
<p>La demande locale est soutenue avec une croissance annuelle estimée à 5%. Le positionnement prix est moyen, ciblant la clientèle locale.</p>
<h3>Concurrence</h3>
<p>3-5 concurrents identifiés dans la zone. Avantage concurrentiel: emplacement central, service client personnalisé.</p>
<h3>Prévisions de Vente (5 ans)</h3>
<table>
<tr><th>Année</th><th>CA Prévu</th><th>Croissance</th></tr>
{''.join(f"<tr><td>{y.year}</td><td>{y.revenue:,.0f} DZD</td><td>{y.revenue_growth:.1%}</td></tr>" for y in proj.years)}
</table>
</div>

<div class="section">
<h2>3. Étude Technique</h2>
<p>Surface requise: 120-200 m². Emplacement: centre-ville, zone commerciale.</p>
<h3>Équipements</h3>
<table>
<tr><th>Équipement</th><th>Quantité</th><th>Coût Estimé</th></tr>
<tr><td>Réfrigérateurs / Vitrines</td><td>3-5</td><td>500,000 DZD</td></tr>
<tr><td>Système informatique (POS)</td><td>1</td><td>200,000 DZD</td></tr>
<tr><td>Mobilier de vente</td><td>1 ensemble</td><td>300,000 DZD</td></tr>
<tr><td>Stock initial</td><td>—</td><td>1,500,000 DZD</td></tr>
</table>
<h3>Effectif</h3>
<p>{defaults['staff_range'][0]}-{defaults['staff_range'][1]} employés. Formation prévue: 2 semaines.</p>
</div>

<div class="section">
<h2>4. Étude Financière</h2>
<h3>Investissement</h3>
<table>
<tr><th>Poste</th><th>Montant</th><th>% du Total</th></tr>
<tr><td>Équipements</td><td>{investment * 0.40:,.0f} DZD</td><td>40%</td></tr>
<tr><td>Aménagement / Bâtiment</td><td>{investment * 0.30:,.0f} DZD</td><td>30%</td></tr>
<tr><td>Fonds de roulement</td><td>{investment * 0.20:,.0f} DZD</td><td>20%</td></tr>
<tr><td>Études & montage</td><td>{investment * 0.10:,.0f} DZD</td><td>10%</td></tr>
</table>
<h3>Financement</h3>
<table>
<tr><th>Source</th><th>Montant</th><th>%</th></tr>
<tr><td>Apports personnels</td><td>{investment * 0.65:,.0f} DZD</td><td>65%</td></tr>
<tr><td>Emprunt bancaire (9%)</td><td>{investment * 0.35:,.0f} DZD</td><td>35%</td></tr>
</table>
</div>

<div class="section">
<h2>5. Prévisions Financières (5 ans)</h2>
<table>
<tr><th>Année</th><th>CA</th><th>COGS</th><th>Marge Brute</th><th>Bénéfice Net</th><th>Marge Nette</th><th>Cash Flow</th><th>Cumul</th></tr>
{fin_rows}
</table>
<div class="kpi-grid">
<div class="kpi {van_color}"><div class="value">{proj.van:,.0f} DZD</div><div class="label">VAN (TRI {proj.tri:.1%})</div></div>
<div class="kpi"><div class="value">{proj.breakeven_revenue:,.0f} DZD</div><div class="label">Seuil de Rentabilité</div></div>
<div class="kpi {profit_color}"><div class="value">{proj.total_profit:,.0f} DZD</div><div class="label">Bénéfice Total (5 ans)</div></div>
</div>
</div>

<div class="section">
<h2>6. Scoring AAPI</h2>
<p>Grille d'évaluation — Décret 26-154, Annexe I — {score.total}/1500 points ({score.rating})</p>
<div class="kpi-grid">
<div class="kpi {aapi_color}"><div class="value">{score.total}/1500</div><div class="label">{score.rating} ({score.percentage:.0f}%)</div></div>
</div>
<table>
<tr><th>Critère</th><th>Score</th><th>Progression</th><th>%</th></tr>
{aapi_rows}
</table>
<h3>Recommandations</h3>
<ul>{suggestions_html}</ul>
</div>

<div class="section">
<h2>7. Analyse des Risques</h2>
<table>
<tr><th>Risque</th><th>Probabilité</th><th>Impact</th><th>Mitigation</th></tr>
<tr><td>Concurrence accrue</td><td>Moyenne</td><td>Moyen</td><td>Differentiation par le service</td></tr>
<tr><td>Fluctuation des coûts</td><td>Élevée</td><td>Moyen</td><td>Contrats fournisseurs long terme</td></tr>
<tr><td>Baisse de la demande</td><td>Faible</td><td>Élevé</td><td>Diversification de l'offre</td></tr>
<tr><td>Problèmes de trésorerie</td><td>Moyenne</td><td>Élevé</td><td>Fonds de roulement de sécurité</td></tr>
</table>
</div>

<div class="section">
<h2>8. Calendrier de Réalisation</h2>
<table>
<tr><th>Phase</th><th>Durée</th><th>Échéance</th></tr>
<tr><td>Études préalables</td><td>1 mois</td><td>Mois 1</td></tr>
<tr><td>Démarches administratives</td><td>2 mois</td><td>Mois 1-2</td></tr>
<tr><td>Aménagement local</td><td>2 mois</td><td>Mois 2-3</td></tr>
<tr><td>Approvisionnement stock</td><td>1 mois</td><td>Mois 3</td></tr>
<tr><td>Recrutement & formation</td><td>1 mois</td><td>Mois 3-4</td></tr>
<tr><td>Ouverture</td><td>—</td><td>Mois 4</td></tr>
</table>
</div>

<div class="section">
<h2>9. Conclusion</h2>
<p>Cette étude de faisabilité démontre la viabilité économique d'un établissement <strong>{defaults['name_fr']}</strong> à {sample['location']}, wilaya de {sample['wilaya']}.</p>
<p>Avec un investissement de <strong>{investment:,} DZD</strong>, un délai de récupération de <strong>{proj.payback_year} ans</strong>, et une marge nette de <strong>{profitability['net_margin']:.1%}</strong>, le projet présente un profil de risque modéré et un rendement attractif.</p>
<p><em>Ce document est un échantillon anonymisé. Les données chiffrées sont des estimations basées sur les standards du marché algérien.</em></p>
</div>

<div class="section">
<h2>Rapport de Qualité</h2>
<div class="kpi-grid">
<div class="kpi"><div class="value">{report.overall_score:.0%}</div><div class="label">Score ({report.grade})</div></div>
<div class="kpi"><div class="value">{report.passed}</div><div class="label">Statut</div></div>
</div>
<table>
<tr><th>Check</th><th>Résultat</th><th>Détail</th></tr>
{''.join(f"<tr><td>{c.name}</td><td>{'PASS' if c.passed else 'FAIL'}</td><td>{c.detail}</td></tr>" for c in report.checks)}
</table>
</div>
"""

    return HTML_TEMPLATE.format(
        title=sample["title"],
        title_ar=sample["title_ar"],
        wilaya=sample["wilaya"],
        location=sample["location"],
        investment=investment,
        date=datetime.now().strftime("%d/%m/%Y"),
        content=content,
    )


def generate_gallery_index(samples_html: list) -> str:
    """Generate the gallery index page."""
    cards = ""
    for sample, html_file in zip(SAMPLES, samples_html):
        defaults = get_defaults(sample["business_type"])
        cards += f"""
<div style="background:white;border-radius:8px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
<h3 style="color:#0A1628;margin-bottom:5px;">{sample['title']}</h3>
<p style="color:#666;margin-bottom:10px;">{sample['wilaya']} — {sample['location']}</p>
<p style="margin-bottom:5px;"><strong>Investissement:</strong> {sample['investment']:,} DZD</p>
<p style="margin-bottom:5px;"><strong>Type:</strong> {defaults['name_fr']}</p>
<p style="margin-bottom:15px;"><strong>Marge nette:</strong> {estimate_profitability(sample['business_type'], sample['investment'])['net_margin']:.1%}</p>
<a href="{html_file}" style="display:inline-block;background:#0A1628;color:white;padding:8px 20px;border-radius:5px;text-decoration:none;font-weight:bold;">Voir l'étude →</a>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DSC — Échantillons d'Études de Faisabilité</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f5f5f0; color: #1a1a1a; }}
.header {{ background: #0A1628; color: white; padding: 40px 0; text-align: center; }}
.header h1 {{ font-size: 2em; margin-bottom: 10px; }}
.header .subtitle {{ color: #D4AF37; font-size: 1.1em; }}
.container {{ max-width: 1000px; margin: 0 auto; padding: 30px 20px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
.footer {{ text-align: center; padding: 30px; color: #999; font-size: 0.85em; }}
</style>
</head>
<body>
<div class="header">
<h1>DSC Digital Services Center</h1>
<div class="subtitle">Échantillons d'Études de Faisabilité</div>
<p style="color:#aaa;margin-top:10px;">3 études anonymisées — données réelles du marché algérien</p>
</div>
<div class="container">
<div class="grid">
{cards}
</div>
</div>
<div class="footer">
contact@dsc-dz.com — Études de faisabilité pour entreprises algériennes
</div>
</body>
</html>"""


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "generated_output" / "gallery"
    output_dir.mkdir(exist_ok=True)

    html_files = []
    for sample in SAMPLES:
        html = generate_dossier_html(sample)
        filename = f"{sample['key']}.html"
        (output_dir / filename).write_text(html, encoding="utf-8")
        html_files.append(filename)
        print(f"Generated: {filename}")

    gallery_html = generate_gallery_index(html_files)
    (output_dir / "index.html").write_text(gallery_html, encoding="utf-8")
    print(f"Generated: index.html")
    print(f"Gallery: {output_dir}")
