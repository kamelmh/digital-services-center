import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from cover_letter_generator import CoverLetterGenerator, TEMPLATES


def cover_letter_page():
    _sidebar()
    app.title("Cover Letter Generator")
    app.text("إنشاء رسالة تعريفية احترافية")

    template_keys = list(TEMPLATES.keys())

    # Separate states for error and success — passed directly to widgets
    error_msg = app.session_state("", key="cl_error")
    success_msg = app.session_state("", key="cl_success")

    with app.expander("1️⃣ Your Info"):
        c1, c2 = app.columns(2)
        sender_name = c1.text_input("Full Name", "")
        sender_phone = c2.text_input("Phone", "")
        sender_email = c1.text_input("Email", "")
        sender_city = c2.text_input("City", "El Bayadh")

    with app.expander("2️⃣ Job Info"):
        c1, c2 = app.columns(2)
        recipient_name = c1.text_input("Recipient / Company", "")
        subject = c2.text_input("Subject", "")

    with app.expander("3️⃣ Content"):
        body = app.text_area("Main paragraph (what you want to say)", "", height=120)

    with app.expander("⚙️ Settings"):
        c1, c2 = app.columns(2)
        template_key = c1.selectbox("Template", template_keys)
        lang = c2.selectbox("Language", ["fr", "ar"])

    def on_generate():
        try:
            tpl = TEMPLATES.get(template_key.value, TEMPLATES["spontaneous_fr"])
            data = {
                "sender_name": sender_name.value or tpl["sender_name"],
                "sender_address": [f"{sender_city.value}" if sender_city.value else "El Bayadh, Algérie"],
                "date": "",
                "recipient_name": recipient_name.value or "À l'attention du Directeur",
                "recipient_address": [],
                "subject": subject.value or tpl["subject"],
                "greeting": tpl["greeting"],
                "body": [body.value] if body.value else tpl["body"],
                "closing": tpl["closing"],
            }
            gen = CoverLetterGenerator()
            filepath = gen.generate(data, lang.value)
            error_msg.value = ""
            success_msg.value = f"PDF saved: {filepath}"
            _save_output("cover_letter", sender_name.value or "cover", "Cover letter generated", f"{lang.value}.pdf")
        except Exception as e:
            success_msg.value = ""
            error_msg.value = f"Error: {e}"

    app.button("📄 Generate Cover Letter", type="primary", use_container_width=True, on_click=on_generate)

    # Pass State objects directly — widgets resolve inside their builders
    app.error(error_msg)
    app.success(success_msg)
