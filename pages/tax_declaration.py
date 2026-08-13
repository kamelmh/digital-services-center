import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from tax_declaration_generator import TaxDeclarationGenerator


def tax_declaration_page():
    _sidebar()
    app.title("Tax Declaration Guide")
    app.text("دليل إعداد التصريحات الضريبية")

    tax_type = app.selectbox("Tax Type", options=["TVA", "IR", "BIC", "IFU", "TSL", "fiscal_calendar"], index=0)
    annual_revenue = app.number_input("Annual Revenue (DZD)", min_value=0, value=2_400_000, step=100_000)
    num_employees = app.number_input("Number of Employees", min_value=0, value=3, step=1)
    has_vehicle = app.checkbox("Company Vehicle")
    provider = _provider_select()

    if app.button("Generate Declaration Guide"):
        app.toast("Generating tax guide...", variant="info")
        try:
            gen = TaxDeclarationGenerator(provider=provider.value)
            result = gen.generate(tax_type.value, annual_revenue.value, num_employees.value, has_vehicle)
            app.markdown(f"### {tax_type.value} Declaration Guide")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("tax_declaration", tax_type.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
