import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g_declaration_generator import GDeclarationGenerator


def g29_page():
    _sidebar()
    app.title("G29 — Withholding Tax (Retenue à la Source)")
    app.text("تصريح G29 — الضريبة على الدخل المحتجز")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]

    month = app.selectbox("Month", options=["January", "February", "March", "April", "May", "June",
                                             "July", "August", "September", "October", "November", "December"], index=0)
    year = app.number_input("Year", min_value=2020, max_value=2030, value=2026, step=1)
    base_amount = app.number_input("Base Amount (DZD)", min_value=0, value=500_000, step=10_000)
    withholding_rate = app.number_input("Withholding Rate (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.5)
    provider = _provider_select()

    if app.button("Generate G29"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G29 declaration...", variant="info")
        try:
            gen = GDeclarationGenerator(provider=provider.value)
            result = gen.generate_g29(
                business_name.value, business_type.value, month.value, year.value,
                base_amount.value, withholding_rate.value,
            )
            app.markdown("### G29 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("g29", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
