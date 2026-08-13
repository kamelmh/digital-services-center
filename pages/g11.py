import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g_declaration_generator import GDeclarationGenerator


def g11_page():
    _sidebar()
    app.title("G11 — Professional Income Tax")
    app.text("تصريح G11 — ضريبة الدخل المهني")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]

    year = app.number_input("Fiscal Year", min_value=2020, max_value=2030, value=2025, step=1)
    professional_revenue = app.number_input("Professional Revenue (DZD)", min_value=0, value=1_200_000, step=100_000)
    business_expenses = app.number_input("Business Expenses (DZD)", min_value=0, value=600_000, step=50_000)
    provider = _provider_select()

    if app.button("Generate G11"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G11 declaration...", variant="info")
        try:
            gen = GDeclarationGenerator(provider=provider.value)
            result = gen.generate_g11(
                business_name.value, business_type.value, year.value,
                professional_revenue.value, business_expenses.value,
            )
            app.markdown("### G11 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("g11", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
