import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g8_existence_generator import G8Data, generate_g8


def g8_page():
    _sidebar()
    app.title("G8 — Monthly Payroll Summary")
    app.text("تصريح G8 — ملخص الرواتب الشهرية")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)

    wilaya = app.selectbox("Wilaya", options=list(ALGERIA_DATA["wilayas"].keys()), index=0)
    nif = app.text_input("NIF")
    nom = app.text_input("Nom")
    prenom = app.text_input("Prénom")
    activite = app.text_input("Activité principale")

    if app.button("Generate G8"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G8 declaration...", variant="info")
        try:
            data = G8Data(
                wilaya_dgi=wilaya.value,
                nif=nif.value or "0000000000",
                nom=nom.value or business_name.value,
                prenom=prenom.value,
                activite_principale=activite.value or BUSINESS_TEMPLATES[business_type.value]["name_en"],
            )
            result = generate_g8(data)
            app.markdown("### G8 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result}</div>")
            _save_output("g8", business_name.value, result)
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
