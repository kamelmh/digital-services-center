import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from nesda_calculator import calculate_nesda_financing, format_nesda_report
from dsc_utils import success_box, error_box, info_box, stat_card, export_page_to_pdf, save_dossier


def nesda_calc_page():
    _sidebar()
    app.title("NESDA Triple Financing Calculator")
    app.text("حاسبة التمويل الثلاثي — NESDA 2026")

    app.html("""
    <div style="background:linear-gradient(135deg,#1b5e20,#2e7d32);color:white;padding:15px;border-radius:10px;margin-bottom:15px;">
        <strong>🏛️ NESDA 2026 — Zero Interest Financing</strong><br>
        <span style="opacity:0.9;">Personal contribution: 5% | NESDA grant: 25% | Bank loan: 70% @ <strong>0% interest</strong> | Repayment: 7 years</span>
    </div>
    """)

    # Input section
    cols = app.columns(2)
    name = cols[0].text_input("Project Name", placeholder="مؤسسة...")
    total = cols[1].number_input("Total Investment (DZD)", 500000, 10000000, 2500000, 100000)

    col2a, col2b = app.columns(2)
    model = col2a.selectbox("Financing Model", ["triangular", "mixed", "self"], index=0,
                             help="triangular = standard NESDA, self = self-financed")
    profile = col2b.selectbox("Applicant Profile", ["unemployed", "employed", "graduate"], index=0)

    monthly_rev = app.number_input("Expected Monthly Revenue (DZD)", min_value=0, value=400000, step=50000)

    if app.button("📊 Calculate NESDA Financing", key="calc_nesda"):
        try:
            result = calculate_nesda_financing(total.value, model.value, profile.value, monthly_rev)

            # Header with key figures
            app.html(success_box("NESDA Financing Calculated",
                f"Monthly payment: {result.monthly_payment:,.0f} DZD | Interest: {result.interest_rate*100:.0f}% | Payback: {result.payback_months} months"))

            # Main metrics
            c1, c2, c3, c4 = app.columns(4)
            c1.metric("Bank Loan", f"{result.bank_loan:,.0f} DZD")
            c2.metric("Monthly Payment", f"{result.monthly_payment:,.0f} DZD")
            c3.metric("Total Interest", f"{result.total_interest:,.0f} DZD")
            c4.metric("ROI", f"{result.roi_annual:.1f}%")

            # Detailed breakdown
            with app.expander("📋 Detailed Breakdown", expanded=True):
                app.html(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;">
                    <div style="background:#f8f9fa;padding:15px;border-radius:8px;">
                        <h4 style="margin:0 0 10px;">💰 Financing Structure</h4>
                        <div>Personal (5%): <strong>{result.personal_amount:,.0f} DZD</strong></div>
                        <div>NESDA Grant (25%): <strong>{result.nesda_grant:,.0f} DZD</strong></div>
                        <div>Bank Loan (70%): <strong>{result.bank_loan:,.0f} DZD</strong></div>
                        <div>Interest Rate: <strong>{result.interest_rate*100:.0f}%</strong></div>
                        <div>Repayment: <strong>{result.repayment_years} years</strong></div>
                        <div>Grace Period: <strong>{result.grace_years} years</strong></div>
                    </div>
                    <div style="background:#f8f9fa;padding:15px;border-radius:8px;">
                        <h4 style="margin:0 0 10px;">📈 Profitability</h4>
                        <div>Monthly Revenue: <strong>{result.monthly_revenue:,.0f} DZD</strong></div>
                        <div>Monthly Costs: <strong>{result.monthly_costs:,.0f} DZD</strong></div>
                        <div>Monthly Profit: <strong>{result.monthly_profit:,.0f} DZD</strong></div>
                        <div>Payback Period: <strong>{result.payback_months} months</strong></div>
                        <div>Annual ROI: <strong>{result.roi_annual:.1f}%</strong></div>
                    </div>
                </div>
                """)

            # Amortization table
            if hasattr(result, 'amortization') and result.amortization:
                with app.expander("📊 Amortization Schedule"):
                    app.html("<table style='width:100%;border-collapse:collapse;'>")
                    app.html("<tr style='background:#0A1628;color:white;'><th style='padding:8px;'>Year</th><th>Balance</th><th>Payment</th><th>Interest</th><th>Principal</th></tr>")
                    for row in result.amortization:
                        app.html(f"<tr style='border-bottom:1px solid #eee;'><td style='padding:8px;'>{row['year']}</td><td>{row['balance']:,.0f}</td><td>{row['payment']:,.0f}</td><td>{row['interest']:,.0f}</td><td>{row['principal']:,.0f}</td></tr>")
                    app.html("</table>")

            # Export options
            app.html("<h3>📥 Export Options</h3>")
            col1, col2, col3 = app.columns(3)
            with col1:
                if app.button("📄 Export PDF Report", key="export_nesda_pdf"):
                    try:
                        report = format_nesda_report(result, name.value or "NESDA Project")
                        pdf_path = export_page_to_pdf(report, "nesda_report", app)
                        app.html(success_box("PDF Exported", f"Saved: {pdf_path.name}"))
                    except Exception as e:
                        app.html(error_box("Export Failed", str(e)))
            with col2:
                if app.button("💾 Save to Database", key="save_nesda"):
                    dossier_id = save_dossier(
                        project_name=name.value or "NESDA Project",
                        total_cost=total.value,
                        monthly_revenue=monthly_rev,
                        monthly_profit=result.monthly_profit,
                        content=format_nesda_report(result, name.value or "NESDA Project"),
                        status='draft',
                    )
                    app.html(success_box("Saved", f"Dossier #{dossier_id} saved to database"))
            with col3:
                if app.button("📊 Compare 3 Scenarios", key="compare_nesda"):
                    app.html("<h4>Scenario Comparison</h4>")
                    for scenario, mult in [("Optimistic (+20%)", 1.2), ("Base", 1.0), ("Pessimistic (-20%)", 0.8)]:
                        rev = int(monthly_rev * mult)
                        r = calculate_nesda_financing(total.value, model.value, profile.value, rev)
                        color = "#4CAF50" if mult > 1 else ("#f44336" if mult < 1 else "#2196F3")
                        app.html(f"""
                        <div style="background:white;padding:10px;border-radius:8px;margin:5px 0;border-left:4px solid {color};">
                            <strong>{scenario}</strong> — Revenue: {rev:,} DZD<br>
                            Monthly profit: {r.monthly_profit:,.0f} | ROI: {r.roi_annual:.1f}% | Payback: {r.payback_months} months
                        </div>
                        """)

        except Exception as e:
            app.html(error_box("Calculation Error", str(e)))

    # Info section
    app.html(info_box("NESDA 2026 Key Facts",
        "✅ 0% interest (100% bonified by state) | ✅ 7 years repayment | ✅ 1.5 years grace period | ✅ Max 10,000,000 DZD"))

    app.markdown("---")
    app.markdown("#### NESDA Business Types (51 Activities)")
    app.text("See NESDA Catalog page for full list of supported activities")
