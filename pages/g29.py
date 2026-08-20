import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES, ALGERIA_DATA
from g29_irg_salaires_generator import G29Data, EmployeeData, generate_g29


def g29_page():
    _sidebar()
    app.title("G29 — Withholding Tax (Retenue à la Source)")
    app.text("تصريح G29 — الضريبة على الدخل المحتجز")

    business_name = app.text_input("Business Name (Arabic)")
    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)

    wilaya = app.selectbox("Wilaya", options=list(ALGERIA_DATA["wilayas"].keys()), index=0)
    nif = app.text_input("NIF")
    raison_sociale = app.text_input("Raison Sociale")
    activite = app.text_input("Activité principale")

    employees_count = app.number_input("Number of Employees", min_value=1, value=3, step=1)
    total_salaries = app.number_input("Total Monthly Salaries (DZD)", min_value=0, value=300_000, step=10_000)

    if app.button("Generate G29"):
        if not business_name.value:
            app.toast("Please enter business name", variant="error")
            return
        app.toast("Generating G29 declaration...", variant="info")
        try:
            avg_salary = total_salaries.value / max(employees_count.value, 1)
            salaries = [
                EmployeeData(
                    nom_prenoms=f"Employé {i+1}",
                    salaire_brut=avg_salary,
                    nombre_parts=1.0,
                )
                for i in range(employees_count.value)
            ]
            data = G29Data(
                wilaya=wilaya.value,
                nif=nif.value or "0000000000",
                raison_sociale=raison_sociale.value or business_name.value,
                activite=activite.value or BUSINESS_TEMPLATES[business_type.value]["name_en"],
                nombre_salaries=employees_count.value,
                salaries=salaries,
            )
            result = generate_g29(data)
            app.markdown("### G29 Declaration")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result}</div>")
            _save_output("g29", business_name.value, result)
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
