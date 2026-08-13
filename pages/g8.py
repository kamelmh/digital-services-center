import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g_declaration_generator import GDeclarationGenerator


def g8_page():
    _sidebar()
    app.title("G8 — Monthly Payroll Summary")
    app.text("تصريح G8 — ملخص الرواتب الشهرية")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]

    month = app.selectbox("Month", options=["January", "February", "March", "April", "May", "June",
                                             "July", "August", "September", "October", "November", "December"], index=0)
    year = app.number_input("Year", min_value=2020, max_value=2030, value=2026, step=1)
    employees_count = app.number_input("Employees", min_value=0, value=3, step=1)
    base_salaries = app.number_input("Base Salaries (DZD)", min_value=0, value=200_000, step=10_000)
    bonuses = app.number_input("Bonuses/Allowances (DZD)", min_value=0, value=30_000, step=5_000)
    provider = _provider_select()

    if app.button("Generate G8"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G8 declaration...", variant="info")
        try:
            gen = GDeclarationGenerator(provider=provider.value)
            result = gen.generate_g8(
                business_name.value, business_type.value, month.value, year.value,
                employees_count.value, base_salaries.value, bonuses.value,
            )
            app.markdown("### G8 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("g8", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
