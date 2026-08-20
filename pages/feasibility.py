import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import FeasibilityGenerator, BUSINESS_TEMPLATES, REGULATORY_CHECKLISTS
from dsc_utils import loading_spinner, success_box, error_box, info_box, export_page_to_pdf, save_dossier


def feasibility_page():
    _sidebar()
    app.title("Feasibility Study Generator")
    app.text("إنشاء دراسة جدوى أولية احترافية")
    app.html("""
    <div style="background:linear-gradient(135deg,#0A1628,#1a237e);color:white;padding:15px;border-radius:10px;margin-bottom:15px;">
        <strong>📊 Professional Feasibility Study</strong><br>
        <span style="opacity:0.8;">Generate complete feasibility studies with real financial calculations, regulatory checklists, and NESDA financing options.</span>
    </div>
    """)

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]

    # Show template info in a nice card
    app.html(f"""
    <div style="background:#f8f9fa;padding:15px;border-radius:10px;border-left:4px solid #2196F3;">
        <h3 style="margin:0 0 5px;">{template['name_ar']}</h3>
        <p style="margin:0;color:#666;">{template['name_en']}</p>
        <div style="margin-top:8px;">
            <span style="background:#e3f2fd;padding:3px 10px;border-radius:15px;font-size:0.85em;">📁 {template['category']}</span>
            <span style="background:#e8f5e9;padding:3px 10px;border-radius:15px;font-size:0.85em;margin-left:5px;">📦 {template['products']}</span>
        </div>
    </div>
    """)

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max,
                                   value=(inv_min + inv_max) // 2, step=100_000)
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    # Show regulatory checklist preview
    checklist_key = business_type.value if business_type.value in REGULATORY_CHECKLISTS else "default"
    checklist = REGULATORY_CHECKLISTS.get(checklist_key, REGULATORY_CHECKLISTS["default"])
    with app.expander("📋 Regulatory Requirements Preview", expanded=False):
        for item in checklist:
            app.markdown(f"- **{item['item']}** — {item['authority']} ({item['cost_range']})")

    if app.button("🚀 Generate Feasibility Study", key="gen_feasibility"):
        if not business_name.value:
            app.html(error_box("Missing Info", "Please enter a business name"))
            return
        app.html(loading_spinner("Generating feasibility study..."))
        try:
            gen = FeasibilityGenerator(provider=provider.value)
            result = gen.generate_full_study(business_type.value, business_name.value,
                                              wilaya.value, investment.value)

            app.html(success_box("Feasibility Study Generated",
                f"Project: {business_name.value} | Investment: {investment.value:,} DZD | Wilaya: {wilaya.value}"))

            # Show result in styled container
            app.html(f"""
            <div style="background:#f8f9fa;padding:20px;border-radius:10px;border:1px solid #e0e0e0;white-space:pre-wrap;font-family:serif;line-height:1.8;">
                {result['content']}
            </div>
            """)

            # Save to database
            dossier_id = save_dossier(
                project_name=business_name.value,
                beneficiary_name=business_name.value,
                wilaya=wilaya.value,
                activity_type=business_type.value,
                total_cost=investment.value,
                content=result['content'],
                status='draft',
            )

            _save_output("feasibility", business_name.value, result["content"])

            # Show real financial summary
            if "real_financials" in result:
                rf = result["real_financials"]
                app.html("<h3>📊 Financial Summary</h3>")
                c1, c2, c3, c4 = app.columns(4)
                c1.metric("VAN", f"{rf['reference_van']:,.0f} DZD")
                c2.metric("TRI", f"{rf['reference_tri']:.1f}%")
                c3.metric("Break-Even", f"{rf['reference_seuil']:,.0f} units")
                c4.metric("Payback", f"{rf['reference_delai']:.1f} years")

                with app.expander("📈 Detailed Financials", expanded=False):
                    app.text(f"Gross Margin: {rf['reference_taux_marge']:.1f}%")
                    app.text(f"Loan Payment: {rf['loan_payment']:,.0f} DZD/year")

            # Export buttons
            app.html("<h3>📥 Export Options</h3>")
            col1, col2, col3 = app.columns(3)
            with col1:
                if app.button("📄 Export as PDF", key="export_pdf_feas"):
                    try:
                        pdf_path = export_page_to_pdf(result['content'], "feasibility", app)
                        app.html(success_box("PDF Exported", f"Saved: {pdf_path.name}"))
                    except Exception as e:
                        app.html(error_box("PDF Export Failed", str(e)))
            with col2:
                if app.button("📊 Export NESDA Report", key="export_nesda_feas"):
                    if "real_financials" in result and result["real_financials"].get("nesda_result"):
                        from nesda_calculator import format_nesda_report
                        nesda_report = format_nesda_report(
                            result["real_financials"]["nesda_result"], business_name.value)
                        _save_output("nesda", business_name.value, nesda_report)
                        app.html(success_box("NESDA Exported", "NESDA report saved"))
                    else:
                        app.html(info_box("NESDA", "NESDA not applicable for this investment level"))
            with col3:
                app.html(f"""
                <div style="background:#e3f2fd;padding:10px;border-radius:8px;text-align:center;">
                    <strong>Dossier #{dossier_id}</strong><br>
                    <span style="font-size:0.85em;color:#666;">Saved to database</span>
                </div>
                """)

        except Exception as e:
            app.html(error_box("Generation Failed", str(e)))
