import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import FeasibilityGenerator, BUSINESS_TEMPLATES, REGULATORY_CHECKLISTS


def feasibility_page():
    _sidebar()
    app.title("Feasibility Study Generator")
    app.text("إنشاء دراسة جدوى أولية احترافية")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")
    app.text(f"Category: {template['category']}")
    app.text(f"Products: {template['products']}")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    # Show regulatory checklist preview
    checklist_key = business_type.value if business_type.value in REGULATORY_CHECKLISTS else "default"
    checklist = REGULATORY_CHECKLISTS.get(checklist_key, REGULATORY_CHECKLISTS["default"])
    with app.expander("📋 Regulatory Requirements Preview", expanded=False):
        for item in checklist:
            app.markdown(f"- **{item['item']}** — {item['authority']} ({item['cost_range']})")

    if app.button("Generate Feasibility Study"):
        if not business_name.value:
            app.toast("Please enter a business name", variant="error")
            return
        app.toast("Generating...", variant="info")
        try:
            gen = FeasibilityGenerator(provider=provider.value)
            result = gen.generate_full_study(business_type.value, business_name.value, wilaya.value, investment.value)
            app.markdown("### Result")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("feasibility", business_name.value, result["content"])

            # Show real financial summary
            if "real_financials" in result:
                rf = result["real_financials"]
                with app.expander("📊 Real Financial Calculations (Computed)", expanded=False):
                    app.markdown(f"**VAN:** {rf['reference_van']:,.0f} DZD")
                    app.markdown(f"**TRI:** {rf['reference_tri']:.1f}%")
                    app.markdown(f"**Break-Even:** {rf['reference_seuil']:,.0f} units")
                    app.markdown(f"**Payback:** {rf['reference_delai']:.1f} years")
                    app.markdown(f"**Gross Margin:** {rf['reference_taux_marge']:.1f}%")
                    app.markdown(f"**Loan Payment:** {rf['loan_payment']:,.0f} DZD/year")

            # Export buttons
            col1, col2 = app.columns(2)
            with col1:
                if app.button("Export as PDF"):
                    try:
                        from business_pdf_exporter import BusinessDocumentPDF
                        exporter = BusinessDocumentPDF()
                        # Adapt result format for PDF exporter
                        pdf_data = {
                            "project_name": business_name.value,
                            "business_type": template['name_ar'],
                            "wilaya": wilaya.value,
                            "investment_amount": investment.value,
                            "sections": [{"title": "دراسة جدوى", "content": result["content"]}],
                        }
                        pdf_path = exporter.feasibility(pdf_data)
                        app.toast(f"PDF exported: {pdf_path}", variant="success")
                    except Exception as e:
                        app.toast(f"PDF export failed: {e}", variant="error")
            with col2:
                if app.button("Export NESDA Report"):
                    if "real_financials" in result and result["real_financials"].get("nesda_result"):
                        from nesda_calculator import format_nesda_report
                        nesda_report = format_nesda_report(result["real_financials"]["nesda_result"], business_name.value)
                        _save_output("nesda", business_name.value, nesda_report)
                        app.toast("NESDA report exported", variant="success")
                    else:
                        app.toast("NESDA not applicable for this investment level", variant="warning")

        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
