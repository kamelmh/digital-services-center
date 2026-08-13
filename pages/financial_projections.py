import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES
from financial_projections_generator import FinancialProjectionsGenerator


def financial_projections_page():
    _sidebar()
    app.title("Financial Projections Generator")
    app.text("إنشاء توقعات مالية تفصيلية")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")
    app.text(f"Profit margin: {template['margin'][0]*100:.0f}%-{template['margin'][1]*100:.0f}%")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    num_employees = app.number_input("Number of Employees", min_value=template["staff"][0], max_value=template["staff"][1], value=(template["staff"][0] + template["staff"][1]) // 2, step=1)
    monthly_revenue = app.number_input("Estimated Monthly Revenue (DZD) — leave 0 for auto", min_value=0, value=0, step=100_000)
    wilaya = _wilaya_select()
    location = app.text_input("City / Location")
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("Generate Financial Projections"):
        if not business_name.value or not location.value:
            app.toast("Please fill all fields", variant="error")
            return
        app.toast("Generating financial projections (5 sections)...", variant="info")
        try:
            gen = FinancialProjectionsGenerator(provider=provider.value)
            result = gen.generate(
                business_type.value, business_name.value, location.value, wilaya.value,
                investment.value, num_employees.value, monthly_revenue.value or None,
            )
            app.markdown("### Financial Projections")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("financial_projections", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
