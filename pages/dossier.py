import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES
from dossier_generator import DossierGenerator


def dossier_page():
    _sidebar()
    app.title("NESDA Dossier Generator (25-Step)")
    app.text("إنشاء ملف NESDA الكامل — 25 خطوة")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")
    app.text(f"Products: {template['products']}")

    business_name = app.text_input("Business Name (Arabic)")
    business_name_en = app.text_input("Business Name (English)")
    wilaya = _wilaya_select()
    investment = app.number_input("Investment Amount (DZD)", min_value=0, value=1_500_000, step=100_000)
    monthly_revenue = app.number_input("Expected Monthly Revenue (DZD)", min_value=0, value=200_000, step=10_000)
    employees_count = app.number_input("Number of Employees", min_value=1, value=5, step=1)
    provider = _provider_select()

    if app.button("Generate Complete Dossier"):
        if not business_name.value or not business_name_en.value:
            app.toast("Please fill all fields", variant="error")
            return
        app.toast("Generating complete NESDA dossier (25 steps)... This may take a few minutes.", variant="info")
        try:
            gen = DossierGenerator(provider=provider.value)
            result = gen.generate_full_dossier(
                business_type.value, business_name.value, business_name_en.value,
                wilaya.value, investment.value, monthly_revenue.value, employees_count.value,
            )
            app.markdown("### Complete NESDA Dossier")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("dossier", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
