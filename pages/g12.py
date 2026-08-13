import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from g12_official import G12FormData, G12Calculations, calculate_g12


def g12_page():
    _sidebar()
    app.title("G12 IFU — Declaration Initiale")
    app.text("تصريح البداية — G12 (IFU)")

    cols = app.columns(2)
    business_name = cols[0].text_input("Business Name (Arabic)", placeholder="مؤسسة")
    nif = cols[1].text_input("NIF", placeholder="123456789")
    activity_code = cols[0].text_input("Activity Code", placeholder="6201")
    legal_form = cols[1].selectbox("Legal Form", [" entreprise individuelle", "SARL", "SAS"])
    wilaya = app.selectbox("Wilaya", ["Adrar","Chlef","Laghouat","Alger","Oran","Constantine","Batna","Blida","Setif","Tizi Ouzou"], index=0)
    commune = app.text_input("Commune", placeholder="Alger Centre")
    address = app.text_area("Full Address", placeholder="Rue Didouche Mourad, Alger")
    phone = app.text_input("Phone")
    email = app.text_input("Email")
    investment = app.number_input("Investment (DZD)", min_value=0, value=500000, step=50000)
    activity_desc = app.text_area("Activity Description", placeholder="Creation de sites web...")
    start_date = app.date_input("Start Date")
    source = app.selectbox("Funding Source", ["Fonds propres", "Credit bancaire", "Baded + Credit"])

    if app.button("Generate G12", type="primary"):
        try:
            form_data = G12FormData(
                business_name=business_name.value, nif=nif.value, activity_code=activity_code.value,
                legal_form=legal_form.value, wilaya=wilaya.value, commune=commune.value,
                address=address.value, phone=phone.value, email=email.value,
                investment=investment.value, activity_desc=activity_desc.value,
                start_date=start_date.value.isoformat(), source=source.value,
            )
            calculations = calculate_g12(form_data)
            result = f"G12 Declaration for {business_name.value}\nInvestment: {investment.value:,} DZD\n{calculations}"
            _save_output("g12", business_name.value or "entrepreneur", result, "g12_declaration.pdf")
            app.success("Generated G12!")
        except Exception as e:
            app.error(f"Error: {e}")
