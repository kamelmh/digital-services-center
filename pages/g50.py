import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from g50_generator import G50Data, calculate_g50


def g50_page():
    _sidebar()
    app.title("G50 IFU — Monthly Declaration")
    app.text("تصريح شهري — G50 (IFU)")

    cols = app.columns(2)
    nom = cols[0].text_input("Full Name (Nom & Prénom)", placeholder="Kamel Mahi")
    nif = cols[1].text_input("NIF", placeholder="123456789")
    nni = cols[0].text_input("NNI (Dirigeant)", placeholder="1990010112345678")
    wilaya = cols[1].selectbox("Wilaya", ["Adrar","Chlef","Laghouat","Alger","Oran","Constantine","Batna","Blida","Setif","Tizi Ouzou"], index=3)
    commune = cols[0].text_input("Commune", value="Alger Centre")
    activite = cols[1].text_input("Activity Description", value="Creation de sites web")
    code_activite = cols[0].text_input("Activity Code", value="6201")
    month = cols[1].selectbox("Month", list(range(1, 13)), index=0, format_func=lambda m: ["January","February","March","April","May","June","July","August","September","October","November","December"][m-1])
    year = cols[0].number_input("Year", min_value=2024, max_value=2030, value=2026)
    nb_salaries = cols[1].number_input("Nb. Employees (CNAC)", min_value=0, value=1, step=1)

    app.markdown("### Salary Fields")
    stype = app.radio("Salary type", ["One employee","All identical","Custom per employee"])
    salaries, bonuses, advances = [], [], []

    if stype == "One employee":
        s = app.number_input("Salaire de base (DZD)", min_value=0, value=60000, step=5000)
        b = app.number_input("Bonus — Prime (DZD)", min_value=0, value=0, step=1000)
        a = app.number_input("Advance — Avance (DZD)", min_value=0, value=0, step=1000)
        salaries = [s] * nb_salaries.value; bonuses = [b] * nb_salaries.value; advances = [a] * nb_salaries.value
    elif stype == "All identical":
        s = app.number_input("Salaire de base (DZD)", min_value=0, value=60000, step=5000)
        b = app.number_input("Bonus (DZD)", min_value=0, value=0, step=1000)
        a = app.number_input("Advance (DZD)", min_value=0, value=0, step=1000)
        salaries = [s] * nb_salaries.value; bonuses = [b] * nb_salaries.value; advances = [a] * nb_salaries.value
    else:
        for i in range(nb_salaries.value):
            app.html(f"<strong>Employee {i+1}</strong>")
            c1, c2, c3 = app.columns(3)
            salaries.append(c1.number_input(f"Base_{i}", min_value=0, value=60000, step=5000, key=f"sal{i}"))
            bonuses.append(c2.number_input(f"Bonus_{i}", min_value=0, value=0, step=1000, key=f"bon{i}"))
            advances.append(c3.number_input(f"Advance_{i}", min_value=0, value=0, step=1000, key=f"adv{i}"))

    if app.button("Generate G50", type="primary"):
        try:
            data = G50Data(
                wilaya=wilaya.value, inspection=f"Inspection {wilaya.value}",
                recette=f"Recette {wilaya.value}", mois=str(month.value), annee=str(year.value),
                service_cdi="", nif=nif.value, code_activite=code_activite.value,
                article_imposition="", nom_prenom=nom.value, activite=activite.value,
                adresse=commune.value, commune=commune.value, month=month.value, year=year.value,
                tap_montant=0,
                tva_9_biens_total=0, tva_9_prestations_total=0, tva_9_immobilier_total=0,
            )
            result = calculate_g50(data)
            result_str = str(result)
            _save_output("g50", nom.value or "g50", result_str, "g50_declaration.pdf")
            app.success("Generated G50!")
        except Exception as e:
            app.error(f"Error: {e}")
