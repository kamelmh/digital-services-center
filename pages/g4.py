import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g4_ibs_generator import G4Data, generate_g4


def g4_page():
    _sidebar()
    app.title("G4 — Annual Income Declaration")
    app.text("تصريح G4 — الإقرار السنوي للضريبة على الدخل")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)

    wilaya = app.selectbox("Wilaya", options=list(ALGERIA_DATA["wilayas"].keys()), index=0)
    nif = app.text_input("NIF")
    raison_sociale = app.text_input("Raison Sociale")
    activite = app.text_input("Activité principale")

    resultat_comptable = app.number_input("Résultat comptable (DZD)", value=500_000, step=10_000)
    reintegrations = app.number_input("Réintégrations (DZD)", value=0, step=5_000)
    deductions = app.number_input("Déductions (DZD)", value=0, step=5_000)

    if app.button("Generate G4"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G4 declaration...", variant="info")
        try:
            data = G4Data(
                wilaya=wilaya.value,
                nif=nif.value or "0000000000",
                raison_sociale=raison_sociale.value or business_name.value,
                activite_principale=activite.value or BUSINESS_TEMPLATES[business_type.value]["name_en"],
                resultat_comptable=resultat_comptable.value,
                reintegrations_montant=reintegrations.value,
                deductions_montant=deductions.value,
            )
            result = generate_g4(data)
            app.markdown("### G4 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result}</div>")
            _save_output("g4", business_name.value, result)
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
