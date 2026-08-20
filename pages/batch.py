import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from batch_processor import BatchManager


def batch_page():
    _sidebar()
    app.title("Client Batch Manager")
    app.text("إدارة مجموعة العملاء — batch 5-10 clients")

    manager = BatchManager()

    with app.expander("➕ Add New Client"):
        c1, c2, c3 = app.columns(3)
        new_name = c1.text_input("Business Name", placeholder="مؤسسة...")
        new_phone = c2.text_input("Phone", placeholder="0555555555")
        new_type = c3.selectbox("Business Type", ["digital_services", "manufacturing", "retail", "education", "agriculture", "services"], key="new_type")
        c4, c5 = app.columns(2)
        new_wilaya = c4.text_input("Wilaya", value="Alger", key="new_wil")
        new_inv = c5.number_input("Investment (DZD)", min_value=0, value=1_000_000, step=100_000, key="new_inv")
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
                    app.success(f"Added: {new_name.value} (ID: {client.id})")
                except Exception as e:
                    app.error(str(e))
            else:
                app.warning("Please enter Business Name and Phone")

    status_filter = app.selectbox("Filter by Status", ["all", "lead", "contacted", "proposal", "won", "delivered"], key="status_filter")
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
        app.info("No clients yet. Add a client above.")

    summary = manager.get_batch_summary()
    app.markdown("### Summary")
    app.text(f"Total clients: {summary.get('total', 0)}")
    app.text(f"By status: {summary.get('by_status', {})}")

    if app.button("📥 Export CSV", key="export_csv"):
        try:
            csv_content = manager.export_csv()
            _save_output("batch_report", "batch_report", csv_content, "clients.csv")
            app.success("CSV exported!")
        except Exception as e:
            app.error(str(e))
