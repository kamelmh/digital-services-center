import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g1_ggr_generator import G1Data, generate_g1


def g1_page():
    _sidebar()
    app.title("G1 — Employer Declaration")
    app.text("تصريح G1 — تصريح صاحب العمل")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)

    wilaya = app.selectbox("Wilaya", options=list(ALGERIA_DATA["wilayas"].keys()), index=0)
    nif = app.text_input("NIF")
    nom_prenoms = app.text_input("Nom et Prénoms")
    activite = app.text_input("Activité principale")
    adresse = app.text_input("Adresse")

    total_salaries = app.number_input("Total Salaries (DZD)", min_value=0, value=300_000, step=10_000)
    employees_count = app.number_input("Employees", min_value=0, value=3, step=1)
    employer_contribution = app.number_input("Employer CNAS Contribution (DZD)", min_value=0, value=100_000, step=5_000)

    if app.button("Generate G1"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G1 declaration...", variant="info")
        try:
            data = G1Data(
                wilaya=wilaya.value,
                nif=nif.value or "0000000000",
                nom_prenoms=nom_prenoms.value or business_name.value,
                activite_principale=activite.value or BUSINESS_TEMPLATES[business_type.value]["name_en"],
                adresse_domicile=adresse.value,
            )
            data.salaires.append(type('SalaireData', (), {
                'montant_brut': total_salaries.value,
                'cotisations_salariales': employer_contribution.value * 0.255,
                'impot_retenu': 0,
            })())
            result = generate_g1(data)
            app.markdown("### G1 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result}</div>")
            _save_output("g1", business_name.value, result)
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
