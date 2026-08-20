import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES


def orchestrated_dossier_page():
    _sidebar()
    app.title("One-Click Dossier (Orchestrated)")
    app.text("ملف كامل — جودة عالية مع تقييم AAPI")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")
    app.text(f"Category: {template['category']} | Products: {template['products']}")
    app.text(f"Investment: {template['investment'][0]:,} – {template['investment'][1]:,} DZD | Staff: {template['staff'][0]}-{template['staff'][1]}")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    location = app.text_input("City / Location")
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()
    skip_quality = app.checkbox("Skip Quality Checks (faster)")

    if app.button("Generate One-Click Dossier", type="primary"):
        if not business_name.value or not location.value:
            app.toast("Please fill all fields", variant="error")
            return

        progress = app.progress(0, text="Starting orchestrator...")

        try:
            from service_orchestrator import ServiceOrchestrator

            orchestrator = ServiceOrchestrator(provider=provider.value)

            def on_progress(stage, msg, pct):
                progress.progress(int(pct), text=f"{stage}: {msg}")

            orchestrator.on_progress(on_progress)

            results = orchestrator.generate_dossier(
                business_type=business_type.value,
                location=location.value,
                wilaya=wilaya.value,
                investment=investment.value,
                client_name=business_name.value,
                skip_quality=skip_quality.value,
            )

            progress.progress(100, text="Complete!")

            # Display results
            app.markdown("### Dossier Results")

            # AAPI Score
            aapi = results.get("aapi", {})
            if "total" in aapi:
                app.html(f"""
                <div style='background:#d4edda;padding:15px;border-radius:8px;margin:10px 0;'>
                    <strong>AAPI Score:</strong> {aapi['total']}/1500 ({aapi.get('rating', 'N/A')})<br>
                    <strong>Percentage:</strong> {aapi.get('percentage', 0):.1f}%
                </div>
                """)

            # Quality Grades
            quality = results.get("quality", {})
            if quality:
                grades = {k: v.grade for k, v in quality.items() if hasattr(v, 'grade')}
                app.html(f"""
                <div style='background:#fff3cd;padding:15px;border-radius:8px;margin:10px 0;'>
                    <strong>Quality Grades:</strong> {grades}
                </div>
                """)

            # Financial Summary
            financials = results.get("financials", {})
            if "projections" in financials:
                proj = financials["projections"]
                app.html(f"""
                <div style='background:#d1ecf1;padding:15px;border-radius:8px;margin:10px 0;'>
                    <strong>VAN:</strong> {proj.get('van', 0):,.0f} DZD<br>
                    <strong>TRI:</strong> {proj.get('tri', 0):.1%}<br>
                    <strong>Payback:</strong> {proj.get('payback_years', 0)} years
                </div>
                """)

            # Feasibility Sections
            feasibility = results.get("feasibility", {})
            sections = feasibility.get("sections", {})
            if sections:
                with app.expander("Feasibility Study"):
                    for title, content in sections.items():
                        app.markdown(f"#### {title}")
                        app.text(content[:500] + "..." if len(str(content)) > 500 else str(content))

            # PDF Path
            pdf_path = results.get("pdf_path")
            if pdf_path:
                app.success(f"PDF saved: {pdf_path}")
            else:
                app.warning("PDF generation failed")

            # Metadata
            metadata = results.get("metadata", {})
            app.text(f"Generation time: {metadata.get('elapsed_seconds', 0):.1f}s")

            # Save output
            full_content = "\n\n---\n\n".join([
                f"## {k}\n\n{v}" for k, v in sections.items()
            ])
            if full_content:
                _save_output("orchestrated_dossier", business_name.value, full_content)

            app.toast("Dossier generated with quality gates!", variant="success")

        except Exception as e:
            progress.progress(100, text=f"Error: {e}")
            app.toast(f"Error: {e}", variant="error")
