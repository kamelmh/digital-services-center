import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g_declaration_generator import GDeclarationGenerator


def g1_page():
    _sidebar()
    app.title("G1 — Employer Declaration")
    app.text("تصريح G1 — تصريح صاحب العمل")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]

    month = app.selectbox("Month", options=["January", "February", "March", "April", "May", "June",
                                             "July", "August", "September", "October", "November", "December"], index=0)
    year = app.number_input("Year", min_value=2020, max_value=2030, value=2026, step=1)
    total_salaries = app.number_input("Total Salaries (DZD)", min_value=0, value=300_000, step=10_000)
    employees_count = app.number_input("Employees", min_value=0, value=3, step=1)
    employer_contribution = app.number_input("Employer Contribution (DZD)", min_value=0, value=100_000, step=5_000)
    provider = _provider_select()

    if app.button("Generate G1"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G1 declaration...", variant="info")
        try:
            gen = GDeclarationGenerator(provider=provider.value)
            result = gen.generate_g1(
                business_name.value, business_type.value, month.value, year.value,
                total_salaries.value, employees_count.value, employer_contribution.value,
            )
            app.markdown("### G1 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("g1", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
