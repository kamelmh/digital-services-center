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
    wilaya = cols[0].selectbox("Wilaya", ["Adrar", "Chlef", "Laghouat", "Alger", "Oran", "Constantine", "Batna", "Blida", "Setif", "Tizi Ouzou"], index=3)
    commune = cols[1].text_input("Commune", value="Alger Centre")
    activite = cols[0].text_input("Activity Description", value="Creation de sites web")
    code_activite = cols[1].text_input("Activity Code", value="6201")
    month = cols[0].selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], index=0)
    year = cols[1].number_input("Year", min_value=2024, max_value=2030, value=2026)
    nb_salaries = cols[0].number_input("Nb. Employees", min_value=0, value=1, step=1)

    app.markdown("### Salary Fields")
    salaire = cols[1].number_input("Salaire de base (DZD)", min_value=0, value=60_000, step=5_000)
    prime = app.number_input("Prime (DZD)", min_value=0, value=0, step=1_000)

    if app.button("Generate G50", type="primary"):
        try:
            month_num = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"].index(month.value) + 1
            irg_salaires_revenus = salaire.value * nb_salaries.value * 12
            data = G50Data(
                wilaya=wilaya.value,
                inspection=f"Inspection {wilaya.value}",
                recette=f"Recette {wilaya.value}",
                mois=month.value,
                annee=str(int(year.value)),
                nif=nif.value or "0000000000",
                code_activite=code_activite.value,
                nom_prenom=nom.value or "Contribuable",
                activite=activite.value,
                adresse=commune.value,
                commune=commune.value,
                month=month_num,
                year=int(year.value),
                irg_salaires_revenus=irg_salaires_revenus,
            )
            result = calculate_g50(data)
            result_str = str(result)
            _save_output("g50", nom.value or "g50", result_str, "g50_declaration.pdf")
            app.success("Generated G50!")
        except Exception as e:
            app.error(f"Error: {e}")
