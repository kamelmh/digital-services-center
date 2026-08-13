import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES
from marketing_plan_generator import MarketingPlanGenerator


def marketing_plan_page():
    _sidebar()
    app.title("Marketing Plan Generator")
    app.text("إنشاء خطة تسويقية شاملة")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    monthly_budget = app.number_input("Monthly Marketing Budget (DZD) — leave 0 for auto", min_value=0, value=0, step=5_000)
    wilaya = _wilaya_select()
    location = app.text_input("City / Location")
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("Generate Marketing Plan"):
        if not business_name.value or not location.value:
            app.toast("Please fill all fields", variant="error")
            return
        app.toast("Generating marketing plan...", variant="info")
        try:
            gen = MarketingPlanGenerator(provider=provider.value)
            result = gen.generate(
                business_type.value, business_name.value, location.value, wilaya.value,
                investment.value, monthly_budget.value or None,
            )
            app.markdown("### Marketing Plan")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("marketing_plan", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
