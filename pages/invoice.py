import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from invoice_generator import InvoiceGenerator


def invoice_page():
    _sidebar()
    app.title("Invoice / Quote Generator (PDF)")
    app.text("إنشاء فاتورة أو عرض سعر بصيغة PDF")

    doc_type = app.radio("Document Type", ["invoice", "quote"])

    cols = app.columns(2)
    client_name_ar = cols[0].text_input("Client Name (Arabic)", placeholder="محمد أحمد")
    client_name_en = cols[1].text_input("Client Name (English)", placeholder="Mohamed Ahmed")
    client_addr = app.text_area("Client Address", placeholder="شارع الحرية، باب الوادي، الجزائر العاصمة")
    client_phone = app.text_input("Client Phone", placeholder="0555123456")

    cols2 = app.columns(2)
    project_desc = cols2[0].text_input("Project Description", placeholder="تصميم موقع إلكتروني")
    project_price = cols2[1].number_input("Price (DZD)", min_value=1_000, value=25_000, step=1_000)

    cols3 = app.columns(2)
    due_days = cols3[0].number_input("Payment Due (days)", min_value=1, value=30, step=1)
    notes = cols3[1].text_area("Notes", placeholder="Optional notes...")

    if app.button("Generate PDF", type="primary"):
        if not client_name_ar.value or not project_desc.value:
            app.toast("Please fill client name and project description", variant="error")
            return

        try:
            gen = InvoiceGenerator()
            if doc_type.value == "invoice":
                result = gen.generate_invoice(
                    client_name_ar=client_name_ar.value,
                    client_name_en=client_name_en.value,
                    client_address=client_addr.value,
                    client_phone=client_phone.value,
                    description=project_desc.value,
                    amount=project_price.value,
                    due_days=due_days.value,
                    notes=notes.value,
                )
            else:
                result = gen.generate_quote(
                    client_name_ar=client_name_ar.value,
                    client_name_en=client_name_en.value,
                    client_address=client_addr.value,
                    client_phone=client_phone.value,
                    description=project_desc.value,
                    amount=project_price.value,
                    due_days=due_days.value,
                    notes=notes.value,
                )
            _save_output(doc_type.value, client_name_ar.value or "client", result, f"{doc_type.value}.pdf")
            app.toast(f"Generated {doc_type.value}!", variant="success")
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
