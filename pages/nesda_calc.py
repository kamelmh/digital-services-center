import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from nesda_calculator import calculate_nesda_financing


def nesda_calc_page():
    _sidebar()
    app.title("NESDA Triple Financing Calculator")
    app.text("حاسبة التمويل الثلاثي — NESDA 2025")

    app.html("""<div style="background:#fff3cd;padding:12px;border-radius:8px;border-left:4px solid #ffc107;margin-bottom:15px;">
        <strong>NESDA 2025:</strong> Subsidized (60% @ 2%), Micro (20% @ 9%), Leasing (20% @ 9%) — Total cap: 5M DZD
    </div>""")

    cols = app.columns(2)
    name = cols[0].text_input("Project Name", placeholder="مؤسسة...")
    total = cols[1].number_input("Total Financing (DZD)", 500000, 5000000, 2000000, 100000)

    if app.button("📊 Calculate Triple Financing"):
        try:
            result = calculate_nesda_financing(total.value)
            if hasattr(result, 'subsidized_amount'):
                c1,c2,c3 = app.columns(3)
                c1.metric("Subsidized", f"{result.subsidized_amount:,.0f}", "2%")
                c2.metric("Micro", f"{result.micro_amount:,.0f}", "9%")
                c3.metric("Leasing", f"{result.leasing_amount:,.0f}", "9%")
            else:
                app.json(result)
        except Exception as e:
            app.error(f"Error: {e}")

    app.markdown("---")
    app.markdown("#### NESDA Business Types (51 Activities)")
    app.text("See NESDA Catalog page for full list")
