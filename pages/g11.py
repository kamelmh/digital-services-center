import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g11_bic_generator import G11Data, generate_g11


def g11_page():
    _sidebar()
    app.title("G11 — Professional Income Tax")
    app.text("تصريح G11 — ضريبة الدخل المهني")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)

    wilaya = app.selectbox("Wilaya", options=list(ALGERIA_DATA["wilayas"].keys()), index=0)
    nif = app.text_input("NIF")
    nom_prenoms = app.text_input("Nom et Prénoms")
    activite = app.text_input("Activité principale")
    registre_commerce = app.text_input("Registre de Commerce")

    resultat_comptable = app.number_input("Résultat comptable (DZD)", value=500_000, step=10_000)

    if app.button("Generate G11"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G11 declaration...", variant="info")
        try:
            data = G11Data(
                wilaya=wilaya.value,
                nif=nif.value or "0000000000",
                nom_prenoms=nom_prenoms.value or business_name.value,
                nature_activites=activite.value or BUSINESS_TEMPLATES[business_type.value]["name_en"],
                registre_commerce=registre_commerce.value,
            )
            result = generate_g11(data)
            app.markdown("### G11 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result}</div>")
            _save_output("g11", business_name.value, result)
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
