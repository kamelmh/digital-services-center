import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, FeasibilityGenerator
from business_plan_generator import BusinessPlanGenerator
from market_research_generator import MarketResearchGenerator
from financial_projections_generator import FinancialProjectionsGenerator
from marketing_plan_generator import MarketingPlanGenerator
from social_media_generator import SocialMediaGenerator


def complete_dossier_page():
    _sidebar()
    app.title("Complete NESDA Dossier")
    app.text("ملف NESDA كامل — جميع الأدوات في صفحة واحدة")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")
    app.text(f"Category: {template['category']} | Products: {template['products']}")
    app.text(f"Investment: {template['investment'][0]:,} – {template['investment'][1]:,} DZD | Staff: {template['staff'][0]}-{template['staff'][1]}")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    location = app.text_input("City / Location")
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("🚀 Generate COMPLETE NESDA Dossier", type="primary"):
        if not business_name.value or not location.value:
            app.toast("Please fill all fields", variant="error")
            return
        progress = app.progress(0, text="Starting generation...")

        try:
            all_content = []

            progress.progress(10, text="1/5 Generating Feasibility Study...")
            gen1 = FeasibilityGenerator(provider=provider.value)
            r1 = gen1.generate_full_study(business_type.value, business_name.value, wilaya.value, investment.value)
            all_content.append(r1["content"])

            progress.progress(30, text="2/5 Generating Market Research...")
            gen2 = MarketResearchGenerator(provider=provider.value)
            r2 = gen2.generate(business_type.value, location.value, wilaya.value, business_name.value)
            all_content.append(r2["content"])

            progress.progress(50, text="3/5 Generating Business Plan...")
            gen3 = BusinessPlanGenerator(provider=provider.value)
            r3 = gen3.generate(business_type.value, business_name.value, location.value, wilaya.value, investment.value)
            all_content.append(r3["content"])

            progress.progress(70, text="4/5 Generating Financial Projections...")
            gen4 = FinancialProjectionsGenerator(provider=provider.value)
            r4 = gen4.generate(business_type.value, business_name.value, location.value, wilaya.value, investment.value, (template["staff"][0] + template["staff"][1]) // 2)
            all_content.append(r4["content"])

            progress.progress(85, text="5/5 Generating Marketing & Social Media...")
            gen5 = MarketingPlanGenerator(provider=provider.value)
            r5 = gen5.generate(business_type.value, business_name.value, location.value, wilaya.value, investment.value)
            all_content.append(r5["content"])

            gen6 = SocialMediaGenerator(provider=provider.value)
            r6 = gen6.generate(business_type.value, business_name.value, location.value, wilaya.value)
            all_content.append(r6["content"])

            full_dossier = "\n\n---\n\n".join(all_content)
            progress.progress(100, text="✅ Complete!")

            app.markdown("### ✅ Complete NESDA Dossier")
            app.html(f"<div style='background:#d4edda;padding:15px;border-radius:8px;margin:10px 0;'><strong>Dossier Size:</strong> {len(full_dossier):,} characters | <strong>Sections:</strong> 6</div>")

            content_parts = full_dossier.split("\n\n---\n\n")
            for i, section in enumerate(["Feasibility Study", "Market Research", "Business Plan", "Financial Projections", "Marketing Plan", "Social Media Content"]):
                with app.expander(f"📄 {section}"):
                    if i < len(content_parts):
                        app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{content_parts[i]}</div>")

            _save_output("complete_dossier", business_name.value, full_dossier)
            app.toast("✅ Complete NESDA dossier generated!", variant="success")

        except Exception as e:
            progress.progress(100, text="❌ Error occurred")
            app.toast(f"Error: {e}", variant="error")
