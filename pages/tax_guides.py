import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from tax_declaration_generator import TaxDeclarationGenerator


def tax_guides_page():
    _sidebar()
    app.title("Tax Declaration Guides (DZ)")
    app.text("تصريحات الضرائب — Algeria")

    tab1, tab2, tab3, tab4, tab5, tab6 = app.tabs(["G12","G50","G4","G1","G29","G8"])

    with tab1:
        app.markdown("### G12 — Impot Forfait Unique")
        cols = app.columns(2)
        bname = cols[0].text_input("Business Name", key="g12_n")
        nif = cols[1].text_input("NIF", key="g12_nif")
        wilaya = app.selectbox("Wilaya", ["Adrar","Chlef","Laghouat","Alger","Oran","Constantine","Batna","Blida","Setif","Tizi Ouzou"], index=0, key="g12_wil")
        activity = app.text_input("Activity Description", key="g12_act")
        cols2 = app.columns(2)
        investment = cols2[0].number_input("Investment (DZD)", min_value=0, value=500000, step=50000, key="g12_inv")
        revenue = cols2[1].number_input("Annual Revenue (DZD)", min_value=0, value=5000000, step=100000, key="g12_rev")
        if app.button("Generate G12", key="g12_btn"):
            try:
                gen = TaxDeclarationGenerator()
                result = gen.generate("g12", bname.value or "غير محدد")
                _save_output("g12", bname.value or "g12", result, "g12_declaration.pdf")
                app.success("Generated G12!")
            except Exception as e:
                app.error(str(e))

    with tab2:
        app.markdown("### G50 — TVA Mensuelle")
        cols = app.columns(2)
        bname = cols[0].text_input("Business Name", key="g50_n")
        nif = cols[1].text_input("NIF", key="g50_nif")
        period = app.text_input("Period", value="Janvier 2026", key="g50_per")
        cols2 = app.columns(2)
        taxable = cols2[0].number_input("Taxable Turnover (DZD)", min_value=0, value=500000, step=10000, key="g50_tax")
        collected = cols2[1].number_input("VAT Collected (DZD)", min_value=0, value=90000, step=1000, key="g50_col")
        if app.button("Generate G50", key="g50_btn"):
            try:
                gen = TaxDeclarationGenerator()
                result = gen.generate("g50", bname.value or "غير محدد")
                _save_output("g50", bname.value or "g50", result, "g50_declaration.pdf")
                app.success("Generated G50!")
            except Exception as e:
                app.error(str(e))

    with tab3:
        app.markdown("### G4 — IR (Salaries)")
        cols = app.columns(2)
        bname = cols[0].text_input("Business Name", key="g4_n")
        nif = cols[1].text_input("NIF", key="g4_nif")
        period = app.text_input("Period (Year)", value="2026", key="g4_per")
        n_emp = app.number_input("Employees", min_value=1, max_value=50, value=1, key="g4_ne")
        employees = []
        for i in range(n_emp.value):
            c1,c2,c3,c4 = app.columns(4)
            name = c1.text_input(f"Name {i+1}", key=f"g4_en{i}")
            position = c2.text_input(f"Position", key=f"g4_ep{i}")
            gross = c3.number_input(f"Gross Annual", min_value=0, value=720000, step=10000, key=f"g4_eg{i}")
            cnss_empl = c4.number_input(f"CNSS Employee", min_value=0, value=10800, step=100, key=f"g4_ec{i}")
            employees.append({"name":name.value,"position":position.value,"gross_annual":gross.value,"cnss_employee":cnss_empl.value})
        if app.button("Generate G4", key="g4_btn"):
            try:
                gen = TaxDeclarationGenerator()
                result = gen.generate("g4", bname.value or "غير محدد")
                _save_output("g4", bname.value or "g4", result, "g4_declaration.pdf")
                app.success("Generated G4!")
            except Exception as e:
                app.error(str(e))

    with tab4:
        app.markdown("### G1 — IR BIC (Entreprise)")
        cols = app.columns(2)
        bname = cols[0].text_input("Business Name", key="g1_n")
        nif = cols[1].text_input("NIF", key="g1_nif")
        period = app.text_input("Period", value="2026", key="g1_per")
        cols2 = app.columns(3)
        revenue = cols2[0].number_input("Revenue", min_value=0, value=10000000, step=100000, key="g1_rev")
        cogs = cols2[1].number_input("COGS", min_value=0, value=4000000, step=100000, key="g1_cogs")
        operating = cols2[2].number_input("Operating Exp", min_value=0, value=2000000, step=100000, key="g1_op")
        if app.button("Generate G1", key="g1_btn"):
            try:
                gen = TaxDeclarationGenerator()
                result = gen.generate("g1", bname.value or "غير محدد")
                _save_output("g1", bname.value or "g1", result, "g1_declaration.pdf")
                app.success("Generated G1!")
            except Exception as e:
                app.error(str(e))

    with tab5:
        app.markdown("### G29 — IS Trimestriel")
        cols = app.columns(2)
        bname = cols[0].text_input("Business Name", key="g29_n")
        nif = cols[1].text_input("NIF", key="g29_nif")
        period = app.text_input("Period (Quarter)", value="T1 2026", key="g29_per")
        cols2 = app.columns(3)
        revenue = cols2[0].number_input("Revenue", min_value=0, value=5000000, step=100000, key="g29_rev")
        cogs = cols2[1].number_input("COGS", min_value=0, value=2000000, step=100000, key="g29_cogs")
        operating = cols2[2].number_input("Operating Exp", min_value=0, value=1000000, step=100000, key="g29_op")
        if app.button("Generate G29", key="g29_btn"):
            try:
                gen = TaxDeclarationGenerator()
                result = gen.generate("g29", bname.value or "غير محدد")
                _save_output("g29", bname.value or "g29", result, "g29_declaration.pdf")
                app.success("Generated G29!")
            except Exception as e:
                app.error(str(e))

    with tab6:
        app.markdown("### G8 — IS (Annual)")
        cols = app.columns(2)
        bname = cols[0].text_input("Business Name", key="g8_n")
        nif = cols[1].text_input("NIF", key="g8_nif")
        period = app.text_input("Period", value="2026", key="g8_per")
        cols2 = app.columns(3)
        revenue = cols2[0].number_input("Revenue", min_value=0, value=20000000, step=1000000, key="g8_rev")
        cogs = cols2[1].number_input("COGS", min_value=0, value=8000000, step=500000, key="g8_cogs")
        operating = cols2[2].number_input("Operating Exp", min_value=0, value=5000000, step=500000, key="g8_op")
        if app.button("Generate G8", key="g8_btn"):
            try:
                gen = TaxDeclarationGenerator()
                result = gen.generate("g8", bname.value or "غير محدد")
                _save_output("g8", bname.value or "g8", result, "g8_declaration.pdf")
                app.success("Generated G8!")
            except Exception as e:
                app.error(str(e))
