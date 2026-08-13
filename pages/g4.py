import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g_declaration_generator import GDeclarationGenerator


def g4_page():
    _sidebar()
    app.title("G4 — Annual Income Declaration")
    app.text("تصريح G4 — الإقرار السنوي للضريبة على الدخل")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]

    year = app.number_input("Fiscal Year", min_value=2020, max_value=2030, value=2025, step=1)
    annual_revenue = app.number_input("Annual Revenue (DZD)", min_value=0, value=2_400_000, step=100_000)
    annual_expenses = app.number_input("Annual Expenses (DZD)", min_value=0, value=1_500_000, step=100_000)
    depreciation = app.number_input("Depreciation (DZD)", min_value=0, value=200_000, step=10_000)
    employees_count = app.number_input("Employees", min_value=0, value=5, step=1)
    has_vehicle = app.checkbox("Company Vehicle")
    provider = _provider_select()

    if app.button("Generate G4"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G4 declaration...", variant="info")
        try:
            gen = GDeclarationGenerator(provider=provider.value)
            result = gen.generate_g4(
                business_name.value, business_type.value, year.value,
                annual_revenue.value, annual_expenses.value, depreciation.value,
                employees_count.value, has_vehicle,
            )
            app.markdown("### G4 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("g4", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
