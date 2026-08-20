import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar
from nesda_catalog import CATALOG, NESDAActivity, get_sector_stats, search_catalog


def nesda_catalog_page():
    _sidebar()
    app.title("NESDA Complete Catalog 2025")
    app.text("الدليل الكامل للأنشطة NESDA — 51 activity")

    app.html("""<div style="background:#d4edda;padding:12px;border-radius:8px;border-left:4px solid #28a745;margin-bottom:15px;">
        <strong>NESDA 2025:</strong> 51 supported activities — Subsidized up to 5M DZD (60% @ 2%, 20% micro, 20% leasing)
    </div>""")

    col1, col2, col3 = app.columns([2,1,1])
    with col1:
        q = str(app.text_input("🔍 Search", placeholder="Search activities...")).lower()
    with col2:
        sectors = list(set(a.sector for a in CATALOG.values())) if CATALOG else []
        cat_filter = app.selectbox("Category", ["All"] + sorted(sectors))
    with col3:
        sort_by = app.selectbox("Sort", ["id","name","sector"])

    activities = list(CATALOG.values()) if CATALOG else []
    if q:
        activities = [a for a in activities if q in a.name_fr.lower() or q in a.name_ar or q in str(a.key)]
    if cat_filter != "All":
        activities = [a for a in activities if a.sector == cat_filter]

    if sort_by == "id":
        activities.sort(key=lambda x: x.key)
    elif sort_by == "name":
        activities.sort(key=lambda x: x.name_fr)
    else:
        activities.sort(key=lambda x: x.sector)

    app.html(f"""<div style="background:#0A1628;color:white;padding:10px 15px;border-radius:8px;margin-bottom:10px;">
        <strong>{len(activities)}</strong> of {len(CATALOG)} activities shown
    </div>""")

    for a in activities:
        with app.expander(f"#{a.key} — {a.name_fr} [{a.sector}]"):
            app.html(f"""<div style="background:#f8f9fa;padding:12px;border-radius:8px;">
                <div><strong>Key:</strong> {a.key}</div>
                <div><strong>Name (FR):</strong> {a.name_fr}</div>
                <div><strong>Name (AR):</strong> {a.name_ar}</div>
                <div><strong>Sector:</strong> {a.sector}</div>
                <div><strong>Investment:</strong> {a.investment_min:,} — {a.investment_max:,} DZD</div>
                <div><strong>Margin:</strong> {a.profit_margin_pct}%</div>
                <div><strong>Difficulty:</strong> {a.difficulty}</div>
            </div>""")

    app.markdown("---")
    app.markdown("#### Sector Summary")
    seen_sectors = list(set(a.sector for a in CATALOG.values()))
    for sector in sorted(seen_sectors):
        sector_activities = [a for a in CATALOG.values() if a.sector == sector]
        app.text(f"{sector}: {len(sector_activities)} activities")
