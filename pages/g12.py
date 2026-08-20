import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from g12_official import G12FormData, calculate_g12


def g12_page():
    _sidebar()
    app.title("G12 IFU — Declaration Initiale")
    app.text("تصريح البداية — G12 (IFU)")

    cols = app.columns(2)
    business_name = cols[0].text_input("Business Name (Arabic)", placeholder="مؤسسة")
    nif = cols[1].text_input("NIF", placeholder="123456789")
    activity_code = cols[0].text_input("Activity Code", placeholder="6201")
    legal_form = cols[1].selectbox("Legal Form", ["Entreprise individuelle", "SARL", "SAS"])
    wilaya = app.selectbox("Wilaya", ["Adrar", "Chlef", "Laghouat", "Alger", "Oran", "Constantine", "Batna", "Blida", "Setif", "Tizi Ouzou"], index=3)
    commune = app.text_input("Commune", placeholder="Alger Centre")
    address = app.text_input("Full Address", placeholder="Rue Didouche Mourad, Alger")
    phone = app.text_input("Phone")
    investment = app.number_input("Investment (DZD)", min_value=0, value=500_000, step=50_000)
    activity_desc = app.text_input("Activity Description", placeholder="Creation de sites web...")

    if app.button("Generate G12", type="primary"):
        try:
            form_data = G12FormData(
                nom_prenoms=business_name.value or "Contribuable",
                nif=nif.value or "0000000000",
                activite_exercee=activity_desc.value or "Services numériques",
                date_debut="2026-01-01",
                adresse_activite=address.value or commune.value,
                wilaya_activite=wilaya.value,
                commune=commune.value,
                diw=f"DIW {wilaya.value}",
                recette=f"Recette {wilaya.value}",
                ca_production_imposable=investment.value,
                nouveau_contribuable=True,
            )
            calculations = calculate_g12(form_data)
            result = f"G12 Declaration for {business_name.value}\nInvestment: {investment.value:,} DZD\n{calculations}"
            _save_output("g12", business_name.value or "entrepreneur", result, "g12_declaration.pdf")
            app.success("Generated G12!")
        except Exception as e:
            app.error(f"Error: {e}")
