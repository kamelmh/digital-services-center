"""BMC (Business Model Canvas) Generator — Osterwalder 9-block canvas.

Generates a visual Business Model Canvas as HTML for any Algerian business.
Each block is pre-filled based on business_defaults and activity data.
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from business_defaults import get_defaults, BUSINESS_DEFAULTS
except ImportError:
    BUSINESS_DEFAULTS = {}
    def get_defaults(key):
        return {"name_fr": key, "name_ar": key, "cogs_pct": 0.65, "monthly_revenue_estimate": 500_000, "staff_range": [2, 5]}


# ── BMC Data ─────────────────────────────────────────────────────────────────

BMC_TEMPLATES = {
    "quincaillerie": {
        "customer_segments": ["Comptoirs de matériaux", "Artisans locaux", "Particuliers (rénovation)", "Entreprises BTP"],
        "value_propositions": ["Large gamme de matériaux", "Prix compétitifs", "Livraison locale", "Conseil technique"],
        "channels": ["Vente en magasin", "Livraison sur chantier", "Réseaux sociaux", " bouche-à-oreille"],
        "customer_relationships": ["Conseil personnalisé", "Programme fidélité", "Service après-vente"],
        "revenue_streams": ["Vente de matériaux", "Livraison", "Conseil technique", "Services de découpe"],
        "key_resources": ["Stock initial", "Local commercial", "Fournisseurs", "Connaissance du marché"],
        "key_activities": ["Approvisionnement", "Gestion de stock", "Vente", "Marketing local"],
        "key_partnerships": ["Grossistes nationaux", "Transporteurs", "Fournisseurs locaux"],
        "cost_structure": ["Achat de marchandises (70%)", "Loyer (8%)", "Salaires (10%)", "Transport (5%)", "Marketing (3%)"],
    },
    "restaurant": {
        "customer_segments": ["Familles", "Jeunes", "Employés (midi)", "Étudiants"],
        "value_propositions": ["Cuisine traditionnelle", "Prix abordables", "Ambiance conviviale", "Service rapide"],
        "channels": ["Sur place", "À emporter", "Livraison (Jumia Food)", "Réseaux sociaux"],
        "customer_relationships": ["Service chaleureux", "Programme fidélité", "Événements spéciaux"],
        "revenue_streams": ["Vente de repas", "Boissons", "Livraison", "Événements privés"],
        "key_resources": ["Cuisine équipée", "Chef cuisinier", "Local bien situé", "Recettes traditionnelles"],
        "key_activities": ["Préparation des repas", "Service", "Gestion des stocks", "Marketing"],
        "key_partnerships": ["Fournisseurs alimentaires", "Livreurs", "Organisateurs d'événements"],
        "cost_structure": ["Nourriture (35%)", "Salaires (25%)", "Loyer (12%)", "Énergie (5%)", "Marketing (3%)"],
    },
    "cybercafe": {
        "customer_segments": ["Étudiants", "Jeunes 18-35 ans", "Professionnels", "Gaming community"],
        "value_propositions": ["Internet haut débit", "Impression/scanner", "Climatisation", "Espace gaming"],
        "channels": ["Sur place", "Réseaux sociaux", "Bouche-à-oreille", "Affichage local"],
        "customer_relationships": ["Ambiance amicale", "Tarifs horaires clairs", "Abonnements mensuels"],
        "revenue_streams": ["Accès internet (horaire)", "Impression/scanner", "Jeux vidéo", "Boissons", "Dépôt Argaz"],
        "key_resources": ["PC performants", "Connexion fibre", "Local climatisé", "Imprimantes"],
        "key_activities": ["Gestion des postes", "Maintenance", "Vente de consommables", "Animation gaming"],
        "key_partnerships": ["Fournisseur internet", "Fournisseur PC", "Dépositaire Argaz"],
        "cost_structure": ["Internet (15%)", "Électricité (12%)", "Loyer (15%)", "Personnel (15%)", "Maintenance PC (5%)"],
    },
    "boulangerie": {
        "customer_segments": ["Familles quotidiennes", "Commerces de proximité", "Restaurants", "Écoles"],
        "value_propositions": ["Pain frais quotidien", "Horaires stables", "Qualité constante", "Prix populaire"],
        "channels": ["Vente directe", "Commandes restaurants", "Livraison matinale", "Stands marché"],
        "customer_relationships": ["Habitude quotidienne", "Service fiable", "Qualité garantie"],
        "revenue_streams": ["Vente pain", "Viennoiseries", "Pâtisseries", "Commandes spéciales"],
        "key_resources": ["Four professionnel", "Local/atelier", "Recettes", "Fournisseur farine"],
        "key_activities": ["Pétrissage", "Cuisson", "Vente", "Gestion des commandes"],
        "key_partnerships": ["Minoteries", "Fournisseurs matières premières", "Dépositaires"],
        "cost_structure": ["Farine (40%)", "Énergie (12%)", "Salaires (18%)", "Loyer (10%)", "Emballage (3%)"],
    },
    "coiffure": {
        "customer_segments": ["Hommes (coiffure)", "Femmes (coiffure/teinture)", "Jeunes", "Événements (mariages)"],
        "value_propositions": ["Tendances actuelles", "Service rapide", "Prix abordables", "Ambiance moderne"],
        "channels": ["Sur place", "Réservation WhatsApp", "Instagram", "Google Maps"],
        "customer_relationships": ["Personnalisé", "Réservation facile", "Avant/après photos"],
        "revenue_streams": ["Coupe", "Teinture", "Défrisage", "Soins", "Événements mariages"],
        "key_resources": ["Salon équipé", "Coiffeur qualifié", "Produits capillaires", "Localisation"],
        "key_activities": ["Coiffure", "Conseil", "Marketing Instagram", "Formation"],
        "key_partnerships": ["Fournisseurs cosmétiques", "Photographe (mariages)", "Influenceurs locaux"],
        "cost_structure": ["Produits (15%)", "Loyer (18%)", "Salaires (25%)", "Marketing (5%)", "Énergie (5%)"],
    },
    "formation_informatique": {
        "customer_segments": ["Étudiants", "Jeunes diplômés", "Professionnels", "Entreprises"],
        "value_propositions": ["Certificats reconnus", "Formateurs qualifiés", "Ordinateurs modernes", "Horaires flexibles"],
        "channels": ["Centre de formation", "En ligne (Zoom)", "Réseaux sociaux", "Partenariats universités"],
        "customer_relationships": ["Suivi personnalisé", "Assistance emploi", "Communauté alumni"],
        "revenue_streams": ["Frais de formation", "Certifications", "Formation entreprise", "Ateliers"],
        "key_resources": ["Salle de formation", "Ordinateurs", "Formateurs certifiés", "Programmes"],
        "key_activities": ["Formation", "Évaluation", "Placement emploi", "Développement programmes"],
        "key_partnerships": ["Microsoft", "Google", "Universités", "Entreprises recruteuses"],
        "cost_structure": ["Salaires formateurs (35%)", "Loyer (15%)", "Équipement (10%)", "Marketing (8%)", "Licences (5%)"],
    },
}

# Generic fallback
BMC_GENERIC = {
    "customer_segments": ["Particuliers", "Entreprises locales", "Administration"],
    "value_propositions": ["Service de qualité", "Prix compétitif", "Proximité", "Réactivité"],
    "channels": ["Vente directe", "Réseaux sociaux", "Bouche-à-oreille", "Site web"],
    "customer_relationships": ["Personnalisé", "Suivi client", "Garantie"],
    "revenue_streams": ["Vente de services/produits", "Abonnements", "Conseil"],
    "key_resources": ["Local", "Équipement", "Compétences", "Fournisseurs"],
    "key_activities": ["Production", "Vente", "Marketing", "Gestion"],
    "key_partnerships": ["Fournisseurs", "Distributeurs", "Institutions"],
    "cost_structure": ["Achats (65%)", "Loyer (10%)", "Salaires (12%)", "Marketing (5%)", "Autres (8%)"],
}


# ── BMC Generator ────────────────────────────────────────────────────────────

class BMCGenerator:
    """Generates a Business Model Canvas."""

    def generate(self, business_type: str, params: dict = None) -> dict:
        """Generate BMC data structure."""
        params = params or {}
        template = BMC_TEMPLATES.get(business_type, BMC_GENERIC)
        defaults = {}
        try:
            defaults = get_defaults(business_type)
        except Exception:
            pass

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="bmc",
                input_params={"business_type": business_type, "custom_params": bool(params)},
                output_content=json.dumps({"meta": {"business_type": business_type}, "blocks": blocks}, ensure_ascii=False),
                metadata={"custom_overrides": list(params.keys()) if params else []},
            )
        except Exception:
            pass

        return {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "generator": "DSC BMC Generator v1.0",
                "business_type": business_type,
                "business_name_fr": defaults.get("name_fr", business_type),
                "business_name_ar": defaults.get("name_ar", business_type),
            },
            "blocks": {
                "customer_segments": params.get("customer_segments", template["customer_segments"]),
                "value_propositions": params.get("value_propositions", template["value_propositions"]),
                "channels": params.get("channels", template["channels"]),
                "customer_relationships": params.get("customer_relationships", template["customer_relationships"]),
                "revenue_streams": params.get("revenue_streams", template["revenue_streams"]),
                "key_resources": params.get("key_resources", template["key_resources"]),
                "key_activities": params.get("key_activities", template["key_activities"]),
                "key_partnerships": params.get("key_partnerships", template["key_partnerships"]),
                "cost_structure": params.get("cost_structure", template["cost_structure"]),
            },
        }

    def to_html(self, bmc: dict) -> str:
        """Generate visual BMC as HTML."""
        blocks = bmc["blocks"]
        meta = bmc["meta"]
        now = datetime.now().strftime("%d/%m/%Y")

        def render_block(title_ar, title_fr, items, color):
            li = "\n".join(f"            <li>{item}</li>" for item in items)
            return f"""        <div class="block" style="border-top: 3px solid {color};">
            <div class="block-title">
                <span class="ar">{title_ar}</span>
                <span class="fr">{title_fr}</span>
            </div>
            <ul>
{li}
            </ul>
        </div>"""

        segments = render_block("الشرائح ?", "Customer Segments", blocks["customer_segments"], "#2196F3")
        value = render_block("القيمة ?", "Value Propositions", blocks["value_propositions"], "#E91E63")
        channels = render_block("القنوات", "Channels", blocks["channels"], "#4CAF50")
        relationships = render_block("العلاقات", "Customer Relationships", blocks["customer_relationships"], "#9C27B0")
        revenue = render_block("الإيرادات", "Revenue Streams", blocks["revenue_streams"], "#FF9800")
        resources = render_block("الموارد ?", "Key Resources", blocks["key_resources"], "#00BCD4")
        activities = render_block("الأنشطة", "Key Activities", blocks["key_activities"], "#795548")
        partnerships = render_block("الشراكات ?", "Key Partnerships", blocks["key_partnerships"], "#607D8B")
        costs = render_block("التكاليف ?", "Cost Structure", blocks["cost_structure"], "#F44336")

        return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BMC — {meta['business_name_ar']} | DSC</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f0; color: #1a1a1a; }}
.header {{ background: #0A1628; color: white; padding: 20px; text-align: center; }}
.header h1 {{ font-size: 1.5em; }}
.header .subtitle {{ color: #D4AF37; margin-top: 5px; font-size: 1.1em; }}
.header .meta {{ color: #aaa; font-size: 0.85em; margin-top: 8px; }}
.bmc {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1fr; grid-template-rows: auto auto; gap: 8px; padding: 15px; max-width: 1400px; margin: 0 auto; }}
.block {{ background: white; border-radius: 8px; padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); min-height: 180px; }}
.block-title {{ margin-bottom: 8px; padding-bottom: 5px; border-bottom: 1px solid #eee; }}
.block-title .ar {{ display: block; font-weight: bold; font-size: 1em; color: #0A1628; }}
.block-title .fr {{ display: block; font-size: 0.75em; color: #888; }}
ul {{ list-style: none; padding: 0; }}
li {{ padding: 3px 0; font-size: 0.82em; border-bottom: 1px solid #f5f5f5; }}
li:before {{ content: "\\25CF"; color: #D4AF37; margin-left: 5px; font-size: 0.7em; }}
.segments {{ grid-column: 1; grid-row: 1 / 3; }}
.value {{ grid-column: 2; grid-row: 1 / 3; }}
.channels {{ grid-column: 3; grid-row: 1; }}
.relationships {{ grid-column: 3; grid-row: 2; }}
.revenue {{ grid-column: 4 / 6; grid-row: 1; }}
.resources {{ grid-column: 4; grid-row: 2; }}
.activities {{ grid-column: 5; grid-row: 2; }}
 partnerships {{ grid-column: 1; grid-row: 3; }}
.costs {{ grid-column: 2 / 6; grid-row: 3; }}
.footer {{ text-align: center; padding: 15px; color: #999; font-size: 0.8em; }}
@media (max-width: 900px) {{
    .bmc {{ grid-template-columns: 1fr 1fr; }}
    .segments, .value, .channels, .relationships, .revenue, .resources, .activities, .partnerships, .costs {{ grid-column: auto; grid-row: auto; }}
}}
</style>
</head>
<body>
<div class="header">
    <h1>نموذج أعمال — Business Model Canvas</h1>
    <div class="subtitle">{meta['business_name_ar']} — {meta['business_name_fr']}</div>
    <div class="meta">DSC Digital Services Center — {now}</div>
</div>
<div class="bmc">
    {segments}
    {value}
    {channels}
    {relationships}
    {revenue}
    {resources}
    {activities}
    {partnerships}
    {costs}
</div>
<div class="footer">
    DSC Digital Services Center — Business Model Canvas — contact@dsc-dz.com
</div>
</body>
</html>"""

    def to_markdown(self, bmc: dict) -> str:
        """Generate BMC as markdown."""
        blocks = bmc["blocks"]
        meta = bmc["meta"]

        def render_block(title, items):
            li = "\n".join(f"- {item}" for item in items)
            return f"### {title}\n{li}"

        return f"""# نموذج أعمال — Business Model Canvas

**المشروع:** {meta['business_name_ar']} — {meta['business_name_fr']}
**التاريخ:** {meta['generated_at']}

---

{render_block('شرائح العملاء (?) — Customer Segments', blocks['customer_segments'])}

{render_block('القيمة المضافة (?) — Value Propositions', blocks['value_propositions'])}

{render_block('قنوات التوزيع (?) — Channels', blocks['channels'])}

{render_block('علاقات العملاء (?) — Customer Relationships', blocks['customer_relationships'])}

{render_block('مصادر الإيرادات (?) — Revenue Streams', blocks['revenue_streams'])}

{render_block('الموارد الرئيسية (?) — Key Resources', blocks['key_resources'])}

{render_block('الأنشطة الرئيسية (?) — Key Activities', blocks['key_activities'])}

{render_block('الشراكات الرئيسية (?) — Key Partnerships', blocks['key_partnerships'])}

{render_block('هيكل التكاليف (?) — Cost Structure', blocks['cost_structure'])}
"""


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BMC Generator")
    parser.add_argument("--business", default="quincaillerie", help="Business type")
    parser.add_argument("--output", default=None, help="Output file (.html or .md)")
    args = parser.parse_args()

    gen = BMCGenerator()
    bmc = gen.generate(args.business)

    if args.output and args.output.endswith(".html"):
        html = gen.to_html(bmc)
        Path(args.output).write_text(html, encoding="utf-8")
        print(f"Saved: {args.output}")
    elif args.output and args.output.endswith(".md"):
        md = gen.to_markdown(bmc)
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"Saved: {args.output}")
    else:
        print(gen.to_markdown(bmc))
