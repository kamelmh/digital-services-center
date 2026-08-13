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
        c1,c2,c3 = app.columns(3)
        new_id = c1.text_input("Client ID", placeholder="C-001")
        new_name = c2.text_input("Business Name", placeholder="مؤسسة...")
        new_type = c3.selectbox("Business Type", ["digital_services","manufacturing","retail","education","agriculture","services"], key="new_type")
        c4,c5 = app.columns(2)
        new_wilaya = c4.text_input("Wilaya", value="Alger", key="new_wil")
        new_inv = c5.number_input("Investment (DZD)", min_value=0, value=1000000, step=100000, key="new_inv")
        if app.button("Add Client", key="add_client_btn"):
            if new_id.value and new_name.value:
                try:
                    manager.add_client(new_id.value, new_name.value, new_type.value, new_wilaya.value, new_inv.value)
                    app.success(f"Added: {new_name.value}")
                except Exception as e:
                    app.error(str(e))
            else:
                app.warning("Please enter Client ID and Name")

    try:
        clients = manager.list_clients() if hasattr(manager, 'list_clients') else []
        for client in clients:
            with app.expander(f"Client: {getattr(client, 'name', str(client))}"):
                app.text(str(client))
    except:
        app.info("No clients yet. Add a client above.")

    if app.button("📥 Export Report", key="export_batch"):
        try:
            report = manager.export_report() if hasattr(manager, 'export_report') else "No report available"
            _save_output("batch_report", "batch_report", str(report), "batch_report.pdf")
            app.success("Report exported!")
        except Exception as e:
            app.error(str(e))
