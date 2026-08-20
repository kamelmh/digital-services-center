import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from batch_processor import BatchManager
from dsc_utils import loading_spinner, progress_bar, success_box, error_box, save_dossier, get_dossiers

from nesda_calculator import calculate_nesda_financing


def batch_page():
    _sidebar()
    app.title("Client Batch Manager & Dossier Generator")
    app.text("إدارة مجموعة العملاء — generate 10 dossiers at once")

    manager = BatchManager()

    # ── Dashboard Stats ──────────────────────────────────────────────────
    stats = get_stats()
    c1, c2, c3, c4 = app.columns(4)
    c1.metric("Total Dossiers", stats["total_dossiers"])
    c2.metric("Final Dossiers", stats["final_dossiers"])
    c3.metric("Total Revenue", f"{stats['total_revenue']:,}")
    c4.metric("Total Profit", f"{stats['total_profit']:,}")

    # ── Add New Client ───────────────────────────────────────────────────
    with app.expander("➕ Add New Client"):
        c1, c2, c3 = app.columns(3)
        new_name = c1.text_input("Business Name", placeholder="مؤسسة...")
        new_name_ar = c2.text_input("Business Name (Arabic)", placeholder="...الاسم بالعربية")
        new_phone = c3.text_input("Phone", placeholder="0555555555")
        c4, c5, c6 = app.columns(3)
        new_type = c4.selectbox("Business Type",
            ["digital_services", "manufacturing", "retail", "education",
             "agriculture", "services", "restaurant", "coiffure", "boulangerie"],
            key="new_type")
        new_wilaya = c5.text_input("Wilaya", value="Alger", key="new_wil")
        new_inv = c6.number_input("Investment (DZD)", min_value=0, value=1_000_000,
                                   step=100_000, key="new_inv")
        c7, c8 = app.columns(2)
        new_revenue = c7.number_input("Monthly Revenue (DZD)", min_value=0, value=300_000,
                                       step=50_000, key="new_rev")
        new_profit = c8.number_input("Monthly Profit (DZD)", min_value=0, value=100_000,
                                      step=50_000, key="new_prof")

        if app.button("Add Client", key="add_client_btn"):
            if new_name.value and new_phone.value:
                try:
                    client = manager.add_client(
                        name=new_name.value,
                        phone=new_phone.value,
                        wilaya=new_wilaya.value,
                        business_type=new_type.value,
                        investment=new_inv.value,
                    )
                    # Also save to SQLite
                    dossier_id = save_dossier(
                        project_name=new_name.value,
                        beneficiary_name=new_name.value,
                        wilaya=new_wilaya.value,
                        activity_type=new_type.value,
                        total_cost=new_inv.value,
                        monthly_revenue=new_revenue.value,
                        monthly_profit=new_profit.value,
                    )
                    app.html(success_box("Client Added",
                        f"{new_name.value} (ID: {client.id}) — Dossier #{dossier_id} saved"))
                except Exception as e:
                    app.html(error_box("Error", str(e)))
            else:
                app.html(error_box("Missing Info", "Please enter Business Name and Phone"))

    # ── Batch NESDA Calculator ───────────────────────────────────────────
    with app.expander("📊 Batch NESDA Calculator (up to 10 projects)"):
        app.text("Enter multiple investment amounts to compare NESDA financing options")
        investments = []
        for i in range(10):
            inv = app.number_input(
                f"Project {i+1} Investment (DZD)",
                min_value=0, value=0, step=100_000,
                key=f"batch_inv_{i}"
            )
            if inv > 0:
                investments.append(inv)

        if investments and app.button("Calculate NESDA for All", key="batch_calc"):
            app.html(f"<h3>NESDA Financing Comparison — {len(investments)} Projects</h3>")
            for i, inv in enumerate(investments, 1):
                r = calculate_nesda_financing(inv, 'triangular', 'unemployed')
                app.html(f"""
                <div style="background:white;padding:12px;border-radius:8px;margin:8px 0;border:1px solid #e0e0e0;">
                    <strong>Project {i}: {r.total_cost:,} DZD</strong><br>
                    Personal: {r.personal_amount:,} | NESDA: {r.nesda_grant:,} | Bank: {r.bank_loan:,}<br>
                    Monthly payment: {r.monthly_payment:,.0f} DZD | Interest: {r.interest_rate*100:.0f}% |
                    Payback: {r.payback_months} months
                </div>
                """)

    # ── Client List ──────────────────────────────────────────────────────
    status_filter = app.selectbox("Filter by Status",
        ["all", "lead", "contacted", "proposal", "won", "delivered"],
        key="status_filter")

    if status_filter != "all":
        clients = manager.get_by_status(status_filter)
    else:
        clients = list(manager.clients.values())

    if clients:
        app.markdown(f"### {len(clients)} Client(s)")
        for client in clients:
            with app.expander(f"{client.name} — {client.status}"):
                app.text(f"ID: {client.id}")
                app.text(f"Phone: {client.phone}")
                app.text(f"Wilaya: {client.wilaya}")
                app.text(f"Type: {client.business_type}")
                app.text(f"Investment: {client.investment:,} DZD")
                app.text(f"Service: {client.service}")
                app.text(f"Notes: {client.notes}")
    else:
        app.html(info_box("No Clients", "Add a client above to get started."))

    # ── Saved Dossiers from SQLite ───────────────────────────────────────
    with app.expander("📁 Saved Dossiers (SQLite)"):
        saved = get_dossiers(limit=20)
        if saved:
            for d in saved:
                status_color = {"draft": "#ff9800", "final": "#4CAF50", "sent": "#2196F3", "paid": "#9C27B0"}
                color = status_color.get(d["status"], "#666")
                app.html(f"""
                <div style="padding:8px;border-bottom:1px solid #eee;">
                    <strong>{d['project_name']}</strong>
                    <span style="background:{color};color:white;padding:2px 8px;border-radius:10px;font-size:0.8em;margin-left:8px;">
                        {d['status']}
                    </span>
                    <span style="color:#999;font-size:0.85em;margin-left:8px;">
                        {d['created_at'][:10]} | {d['wilaya']} | {d['total_cost']:,} DZD
                    </span>
                </div>
                """)
        else:
            app.text("No saved dossiers yet.")

    # ── Summary & Export ─────────────────────────────────────────────────
    summary = manager.get_batch_summary()
    app.markdown("### CRM Summary")
    app.text(f"Total clients: {summary.get('total', 0)}")
    app.text(f"By status: {summary.get('by_status', {})}")

    if app.button("📥 Export CSV", key="export_csv"):
        try:
            csv_content = manager.export_csv()
            _save_output("batch_report", "batch_report", csv_content, "clients.csv")
            app.html(success_box("Export Complete", "CSV file exported successfully"))
        except Exception as e:
            app.html(error_box("Export Error", str(e)))
