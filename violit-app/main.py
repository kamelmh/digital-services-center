import violit as vl
import os
import sys
import base64
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from feasibility_generator import FeasibilityGenerator, BUSINESS_TEMPLATES, ALGERIA_DATA
from business_plan_generator import BusinessPlanGenerator
from market_research_generator import MarketResearchGenerator
from financial_projections_generator import FinancialProjectionsGenerator
from marketing_plan_generator import MarketingPlanGenerator
from social_media_generator import SocialMediaGenerator, CONTENT_TYPES
from tax_declaration_generator import TaxDeclarationGenerator, DECLARATION_TYPES
from invoice_generator import InvoiceGenerator
from cv_generator import CVGenerator, TEMPLATES as CV_TEMPLATES
from cover_letter_generator import CoverLetterGenerator, TEMPLATES as COVER_TEMPLATES
from government_paperwork_helper import GovernmentPaperworkHelper, PROCEDURES
from financial_calculators import FinancialCalculators, InvestmentPlan, FinancingPlan, generate_3_scenarios, format_dzd, format_pct
from aapi_optimizer import AAAPIOptimizer, AAPIScore
from bmc_generator import BMCGenerator, BMC_TEMPLATES
from nesda_calculator import calculate_nesda_financing, format_nesda_report, MODELS as NESDA_MODELS
from nesda_catalog import search_catalog, recommend_activity, get_sector_stats, SECTORS, CATALOG
from nesda_eligibility import check_eligibility, format_eligibility_report
from linkedin_automation import LinkedInContentGenerator
from pricing_calculator import calculate_quote, SERVICES as PRICING_SERVICES, PACKAGES
from batch_processor import BatchManager
from training_data_collector import TrainingDataCollector
from g12_official import G12FormData, calculate_g12, generate_g12_prévisionnelle, generate_g12_définitive, WILAYAS as G12_WILAYAS
from g50_generator import G50Data, calculate_g50, generate_g50_html, generate_g50_text, MONTHS_FR, MONTHS_AR
from g4_ibs_generator import G4Data, calculate_g4, generate_g4_html
from g11_bic_generator import G11Data, calculate_g11, generate_g11_html
from g29_irg_salaires_generator import G29Data, EmployeeData, calculate_irg, generate_g29_html
from g1_ggr_generator import G1Data, calculate_g1, generate_g1_html
from g8_existence_generator import G8Data, generate_g8_html
from tax_form_pdf_exporter import generate_tax_pdf

app = vl.App(title="Digital Services Center", theme="ocean")


def _fmt(n):
    """Format number with thousand separators."""
    if n == int(n):
        return f"{int(n):,}".replace(",", " ")
    return f"{n:,.2f}".replace(",", " ")


def _sidebar():
    """Shared sidebar navigation."""
    with app.sidebar:
        app.html("""
        <div style="padding:10px 0;border-bottom:1px solid #ddd;margin-bottom:10px;">
            <h3 style="margin:0;color:#0A1628;">DSC</h3>
            <p style="margin:2px 0 0;font-size:0.85em;color:#666;">مركز الخدمات الرقمية</p>
        </div>
        """)
        app.markdown("### Navigation")


def home_page():
    _sidebar()
    app.html("""
    <div style="text-align:center;padding:25px 0;">
        <h1 style="color:#0A1628;margin-bottom:5px;">Digital Services Center</h1>
        <p style="color:#D4AF37;font-size:1.1em;margin-top:0;">مركز الخدمات الرقمية — الجزائر</p>
        <p style="color:#888;font-size:0.9em;margin-top:5px;">25 Tools • 25 Pages • One-Click Dossier Pipeline</p>
    </div>
    """)

    # Tool categories
    categories = [
        ("📊 Studies & Feasibility", "#0A1628", [
            ("Feasibility", "دراسات جدوى 10k-60k"),
            ("Business Plan", "خطط عمل 25k-40k"),
            ("Market Research", "أبحاث سوق 10k-20k"),
            ("Financials", "توقعات مالية 15k-25k"),
            ("Complete Dossier", "ملف كامل NESDA"),
            ("BMC Canvas", "نموذج أعمال 9 محاور"),
        ]),
        ("🎯 NESDA Tools", "#D4AF37", [
            ("NESDA Calc", "حساب تمويل ثلاثي"),
            ("NESDA Catalog", "51 نشاط مدعوم"),
            ("Eligibility", "تحقق من الأهلية"),
        ]),
        ("💰 Pricing & Quotes", "#28a745", [
            ("Pricing", "حاسبة أسعار + واتساب"),
            ("Invoice/Quote", "فواتير وعروض سعر"),
            ("G12 IFU", "تصريح G12"),
            ("G50 Monthly", "تصريح G50"),
            ("Tax Guides", "تصريحات ضريبية"),
        ]),
        ("📣 Marketing", "#e83e8c", [
            ("Marketing Plan", "خطط تسويقية"),
            ("Social Media", "محتوى شبكات اجتماعية"),
            ("LinkedIn", "إنشاء محتوى تلقائي"),
        ]),
        ("📄 Documents", "#6f42c1", [
            ("CV Generator", "سيرة ذاتية PDF"),
            ("Cover Letter", "رسالة تعريفية"),
            ("Gov Paperwork", "مساعدة إدارية"),
        ]),
        ("🛠️ Operations", "#17a2b8", [
            ("Calculators", "حسابات مالية VAN/TRI"),
            ("AAPI Scorer", "نقاط AAPI /1500"),
            ("Batch Process", "إدارة العملاء"),
        ]),
    ]

    for cat_title, color, tools in categories:
        app.html(f"""<div style="margin:15px 0 8px;padding:8px 12px;background:{color}10;border-radius:8px;border-left:4px solid {color};">
            <strong style="color:{color};">{cat_title}</strong>
        </div>""")
        cols = app.columns(min(3, len(tools)))
        for i, (tool, desc) in enumerate(tools):
            with cols[i % len(cols)]:
                app.html(f"""<div style="padding:10px;background:white;border-radius:6px;margin:3px 0;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <strong style="font-size:0.9em;">{tool}</strong>
                    <div style="font-size:0.78em;color:#888;">{desc}</div>
                </div>""")

    # Stats
    app.html("""<div style="text-align:center;padding:20px;margin-top:15px;background:#f8f9fa;border-radius:8px;">
        <div style="display:flex;justify-content:center;gap:30px;">
            <div><strong style="font-size:1.5em;color:#0A1628;">25</strong><div style="font-size:0.8em;color:#888;">Generator</div></div>
            <div><strong style="font-size:1.5em;color:#D4AF37;">51</strong><div style="font-size:0.8em;color:#888;">NESDA Activities</div></div>
            <div><strong style="font-size:1.5em;color:#28a745;">20</strong><div style="font-size:0.8em;color:#888;">Services</div></div>
            <div><strong style="font-size:1.5em;color:#e83e8c;">4</strong><div style="font-size:0.8em;color:#888;">Packages</div></div>
        </div>
    </div>""")


def _provider_select():
    """Shared provider selectbox."""
    return app.selectbox("AI Provider", options=["groq", "openrouter", "aihubmix"], index=0)


def _wilaya_select():
    """Shared wilaya selectbox."""
    return app.selectbox("Wilaya", options=list(ALGERIA_DATA["wilayas"].keys()), index=0)


def feasibility_page():
    _sidebar()
    app.title("Feasibility Study Generator")
    app.text("إنشاء دراسة جدوى أولية احترافية")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")
    app.text(f"Category: {template['category']}")
    app.text(f"Products: {template['products']}")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("Generate Feasibility Study"):
        if not business_name.value:
            app.toast("Please enter a business name", type="error")
            return
        app.toast("Generating...", type="info")
        try:
            gen = FeasibilityGenerator(provider=provider.value)
            result = gen.generate_full_study(business_type.value, business_name.value, wilaya.value, investment.value)
            app.markdown("### Result")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("feasibility", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def business_plan_page():
    _sidebar()
    app.title("Business Plan Generator")
    app.text("إنشاء خطة عمل احترافية")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    location = app.text_input("City / Location")
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("Generate Business Plan"):
        if not business_name.value or not location.value:
            app.toast("Please fill all fields", type="error")
            return
        app.toast("Generating business plan...", type="info")
        try:
            gen = BusinessPlanGenerator(provider=provider.value)
            result = gen.generate(business_type.value, business_name.value, location.value, wilaya.value, investment.value)
            app.markdown("### Business Plan")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("business_plan", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def market_research_page():
    _sidebar()
    app.title("Market Research Generator")
    app.text("إنشاء بحث سوق احترافي")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")

    location = app.text_input("City / Location")
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Optional)")
    provider = _provider_select()

    if app.button("Generate Market Research"):
        if not location.value:
            app.toast("Please enter a location", type="error")
            return
        app.toast("Generating market research...", type="info")
        try:
            gen = MarketResearchGenerator(provider=provider.value)
            result = gen.generate(business_type.value, location.value, wilaya.value, business_name.value)
            app.markdown("### Market Research Report")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("market_research", business_name.value or template["name_en"], result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def financial_projections_page():
    _sidebar()
    app.title("Financial Projections Generator")
    app.text("إنشاء توقعات مالية تفصيلية")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")
    app.text(f"Profit margin: {template['margin'][0]*100:.0f}%-{template['margin'][1]*100:.0f}%")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    num_employees = app.number_input("Number of Employees", min_value=template["staff"][0], max_value=template["staff"][1], value=(template["staff"][0] + template["staff"][1]) // 2, step=1)
    monthly_revenue = app.number_input("Estimated Monthly Revenue (DZD) — leave 0 for auto", min_value=0, value=0, step=100_000)
    wilaya = _wilaya_select()
    location = app.text_input("City / Location")
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("Generate Financial Projections"):
        if not business_name.value or not location.value:
            app.toast("Please fill all fields", type="error")
            return
        app.toast("Generating financial projections (5 sections)...", type="info")
        try:
            gen = FinancialProjectionsGenerator(provider=provider.value)
            result = gen.generate(
                business_type.value, business_name.value, location.value, wilaya.value,
                investment.value, num_employees.value, monthly_revenue.value or None,
            )
            app.markdown("### Financial Projections")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("financial_projections", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def marketing_plan_page():
    _sidebar()
    app.title("Marketing Plan Generator")
    app.text("إنشاء خطة تسويقية شاملة")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")

    inv_min, inv_max = template["investment"]
    investment = app.number_input("Investment Amount (DZD)", min_value=inv_min, max_value=inv_max, value=(inv_min + inv_max) // 2, step=100_000)
    monthly_budget = app.number_input("Monthly Marketing Budget (DZD) — leave 0 for auto", min_value=0, value=0, step=5_000)
    wilaya = _wilaya_select()
    location = app.text_input("City / Location")
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("Generate Marketing Plan"):
        if not business_name.value or not location.value:
            app.toast("Please fill all fields", type="error")
            return
        app.toast("Generating marketing plan...", type="info")
        try:
            gen = MarketingPlanGenerator(provider=provider.value)
            result = gen.generate(
                business_type.value, business_name.value, location.value, wilaya.value,
                investment.value, monthly_budget.value or None,
            )
            app.markdown("### Marketing Plan")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("marketing_plan", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def social_media_page():
    _sidebar()
    app.title("Social Media Content Generator")
    app.text("إنشاء محتوى جاهز للنشر على فيسبوك، إنستغرام، واتساب، تيك توك")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")

    content_type = app.selectbox("Content Type", options=list(CONTENT_TYPES.keys()), index=0)
    ct = CONTENT_TYPES[content_type.value]
    app.text(f"Generates: {ct['name_en']}")

    location = app.text_input("City / Location")
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("Generate Content"):
        if not business_name.value or not location.value:
            app.toast("Please fill all fields", type="error")
            return
        app.toast("Generating social media content...", type="info")
        try:
            gen = SocialMediaGenerator(provider=provider.value)
            result = gen.generate(content_type.value, business_type.value, business_name.value, location.value, wilaya.value)
            app.markdown("### Social Media Content")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("social_media", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def tax_declaration_page():
    _sidebar()
    app.title("Tax Declaration Helper")
    app.text("أدلة التصريات الضريبية — G12، G50، CNAS، CASNOS، IRG")

    decl_type = app.selectbox("Declaration Type", options=list(DECLARATION_TYPES.keys()), index=0)
    dt = DECLARATION_TYPES[decl_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{dt['name_ar']}</h3><p style='margin-top:0;color:#666;'>{dt['name_en']}</p>")

    business_name = app.text_input("Business / Person Name")
    provider = _provider_select()

    if app.button("Generate Guide"):
        app.toast("Generating tax declaration guide...", type="info")
        try:
            gen = TaxDeclarationGenerator(provider=provider.value)
            result = gen.generate(decl_type.value, business_name.value)
            app.markdown("### Tax Declaration Guide")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("tax_guide", dt["name_en"], result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def g12_page():
    """G12 Official Form — matches DGI printable forms exactly."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">G12 — Déclaration IFU (Formulaire Officiel)</h2>
        <p style="margin:3px 0 0;color:#888;">Série G N°12 — Impôt Forfaitaire Unique — conforme DGI</p>
    </div>
    """)

    # Form type
    form_type = app.selectbox("Type de déclaration", options=["Prévisionnelle (forecast)", "Définitive (final)"], index=0)
    is_definitive = "Définitive" in form_type.value

    # DGI hierarchy
    app.markdown("### Hierarchie DGI")
    col1, col2 = app.columns(2)
    with col1:
        diw = app.text_input("DIW DE", placeholder="DIW D'EL BAYADH")
        recette = app.text_input("Recette des Impôts de", placeholder="Recette des Impôts d'El Bayadh Centre")
    with col2:
        commune = app.text_input("Commune de", placeholder="El Bayadh Centre")
        structure = app.text_input("Structure", placeholder="...")

    # Section I — Identification
    app.markdown("### Section I — Identification")
    col1, col2 = app.columns(2)
    with col1:
        nom_prenoms = app.text_input("Nom, Prénoms / Raison sociale")
        activite_exercee = app.text_input("Activité(s) exercée(s)")
        date_debut = app.text_input("Date du début d'activité", placeholder="JJ/MM/AAAA")
        adresse_activite = app.text_input("Adresse du lieu d'exercice")
        wilaya_activite = app.selectbox("Wilaya activité", options=G12_WILAYAS, index=31)
    with col2:
        nif = app.text_input("NIF", placeholder="1234567890")
        nin = app.text_input("NIN", placeholder="199603061234567")
        article_imposition = app.text_input("Article d'imposition")
        telephone = app.text_input("Téléphone") if is_definitive else None
        nouveau = app.checkbox("Nouveau contribuable") if is_definitive else False

    exonere = app.checkbox("Activité exonérée")
    exoneration_type = ""
    if exonere:
        exoneration_type = app.selectbox("Type d'exonération", options=["anade", "cnac", "angem", "artisanale", "autre"], index=0)

    # Section II — CA
    app.markdown(f"### Section {'III' if is_definitive else 'II'} — Chiffre d'affaires")
    col1, col2 = app.columns(2)
    with col1:
        app.html("<strong>CA Prévisionnel (estimé pour l'année)</strong>")
        ca_prod_imp = app.number_input("Production/Vente imposable (DA)", min_value=0, value=0, step=100_000, key="ca_prod_prev")
        ca_prod_exo = app.number_input("Production/Vente exonéré (DA)", min_value=0, value=0, step=100_000, key="ca_prod_exo")
        ca_serv_imp = app.number_input("Services imposable (DA)", min_value=0, value=0, step=100_000, key="ca_serv_prev")
        ca_serv_exo = app.number_input("Services exonéré (DA)", min_value=0, value=0, step=100_000, key="ca_serv_exo")
        ca_auto_imp = app.number_input("Auto-entrepreneur imposable (DA)", min_value=0, value=0, step=100_000, key="ca_auto_prev")
        ca_auto_exo = app.number_input("Auto-entrepreneur exonéré (DA)", min_value=0, value=0, step=100_000, key="ca_auto_exo")

    ca_realise = (0, 0, 0, 0, 0, 0)
    if is_definitive:
        with col2:
            app.html("<strong>CA Réalisé (chiffres réels de l'année)</strong>")
            r_prod_imp = app.number_input("Prod/Vente réalisé imposable", min_value=0, value=0, step=100_000, key="r_prod_imp")
            r_prod_exo = app.number_input("Prod/Vente réalisé exonéré", min_value=0, value=0, step=100_000, key="r_prod_exo")
            r_serv_imp = app.number_input("Services réalisé imposable", min_value=0, value=0, step=100_000, key="r_serv_imp")
            r_serv_exo = app.number_input("Services réalisé exonéré", min_value=0, value=0, step=100_000, key="r_serv_exo")
            r_auto_imp = app.number_input("Auto-entrepreneur réalisé imposable", min_value=0, value=0, step=100_000, key="r_auto_imp")
            r_auto_exo = app.number_input("Auto-entrepreneur réalisé exonéré", min_value=0, value=0, step=100_000, key="r_auto_exo")
        ca_realise = (r_prod_imp.value, r_prod_exo.value, r_serv_imp.value, r_serv_exo.value, r_auto_imp.value, r_auto_exo.value)

    # Section — Salaires (Définitive only)
    nombre_salaries = 0
    salaires_brut = 0
    charges_sociales = 0
    irg_annuel = 0
    if is_definitive:
        app.markdown("### Section II — Salaires")
        col1, col2, col3, col4 = app.columns(4)
        with col1:
            nombre_salaries = app.number_input("Nombre de salariés", min_value=0, value=0)
        with col2:
            salaires_brut = app.number_input("Salaires bruts (DA)", min_value=0, value=0, step=10_000)
        with col3:
            charges_sociales = app.number_input("Charges sociales (DA)", min_value=0, value=0, step=10_000)
        with col4:
            irg_annuel = app.number_input("IRG annuel (DA)", min_value=0, value=0, step=10_000)

    # Payment
    app.markdown("### Paiement")
    mode_paiement = app.selectbox("Mode de paiement", options=["integral", "fractionne"], index=1)
    year = app.number_input("Année", min_value=2024, max_value=2030, value=2025)

    # Build data
    data = G12FormData(
        diw=diw.value, recette=recette.value, commune=commune.value, structure=structure.value,
        nom_prenoms=nom_prenoms.value, activite_exercee=activite_exercee.value,
        date_debut=date_debut.value, exonere=exonere, exoneration_type=exoneration_type,
        adresse_activite=adresse_activite.value, wilaya_activite=wilaya_activite.value,
        nif=nif.value, nin=nin.value, article_imposition=article_imposition.value,
        telephone=telephone.value if telephone else "",
        nouveau_contribuable=nouveau,
        ca_production_imposable=float(ca_prod_imp.value), ca_production_exonere=float(ca_prod_exo.value),
        ca_services_imposable=float(ca_serv_imp.value), ca_services_exonere=float(ca_serv_exo.value),
        ca_auto_entrepreneur_imposable=float(ca_auto_imp.value), ca_auto_entrepreneur_exonere=float(ca_auto_exo.value),
        ca_realise_production_imposable=float(ca_realise[0]), ca_realise_production_exonere=float(ca_realise[1]),
        ca_realise_services_imposable=float(ca_realise[2]), ca_realise_services_exonere=float(ca_realise[3]),
        ca_realise_auto_imposable=float(ca_realise[4]), ca_realise_auto_exonere=float(ca_realise[5]),
        nombre_salaries=int(nombre_salaries.value), salaires_brut=float(salaires_brut.value),
        charges_sociales=float(charges_sociales.value), irg_annuel=float(irg_annuel.value),
        mode_paiement=mode_paiement.value, year=int(year.value),
    )

    # Preview
    calc = calculate_g12(data, is_definitive=is_definitive)
    app.html(f"""<div style="padding:15px;background:#e8f5e9;border-radius:8px;margin:15px 0;">
        <div style="font-weight:bold;color:#2e7d32;margin-bottom:5px;">IFU Total: {_fmt(calc.ifu_total)} DA</div>
        <div style="font-size:0.85em;color:#555;">
            Production: {_fmt(calc.ifu_production)} DA | Services: {_fmt(calc.ifu_services)} DA | Auto: {_fmt(calc.ifu_auto)} DA<br>
            Minimum: {_fmt(calc.ifu_minimum)} DA
        </div>
    </div>""")

    if is_definitive and calc.ifu_complementaire > 0:
        app.html(f"""<div style="padding:10px;background:#fff3e0;border-radius:6px;margin:8px 0;font-size:0.85em;">
            <strong>IFU Complémentaire:</strong> {_fmt(calc.ifu_complementaire)} DA (réalisé > prévisionnel)
        </div>""")

    if mode_paiement.value == "fractionne":
        app.html(f"""<div style="padding:10px;background:#e3f2fd;border-radius:6px;margin:8px 0;font-size:0.85em;">
            <strong>Échéancier:</strong><br>
            1ère tranche (50%): {_fmt(calc.tranche_1)} DA — 30/06/{year.value}<br>
            2ème tranche (25%): {_fmt(calc.tranche_2)} DA — 15/09/{year.value}<br>
            3ème tranche (25%): {_fmt(calc.tranche_3)} DA — 15/12/{year.value}
        </div>""")

    # Generate
    if app.button("Generate G12 Form", primary=True):
        if not nif.value or not nom_prenoms.value:
            app.toast("NIF and Nom/Raison sociale required", type="error")
            return
        app.toast("Generating official G12 form...", type="info")
        if is_definitive:
            html = generate_g12_définitive(data)
            label = "G12_Définitive"
        else:
            html = generate_g12_prévisionnelle(data)
            label = "G12_Prévisionnelle"
        out = Path(__file__).parent.parent / "generated_output"
        out.mkdir(exist_ok=True)
        html_path = out / f"{label}_{nom_prenoms.value.replace(' ', '_') or 'client'}_{year.value}.html"
        html_path.write_text(html, encoding="utf-8")
        app.markdown(f"### {label} Generated")
        app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;max-height:500px;overflow-y:auto;'>{html}</div>")
        app.html(f"<p style='color:#28a745;'>Saved: {html_path}</p>")
        app.download_button("Download HTML", data=html.encode(), file_name=html_path.name, mime="text/html")
        try:
            pdf = generate_tax_pdf("g12", data, is_definitive=is_definitive)
            pdf_path = html_path.with_suffix(".pdf")
            pdf_path.write_bytes(pdf)
            app.download_button("Download PDF", data=pdf, file_name=pdf_path.name, mime="application/pdf")
        except Exception as e:
            app.html(f"<p style='color:#dc3545;'>PDF error: {e}</p>")


def g50_page():
    """G50 Multi-Tax Monthly Declaration — template-based (no LLM)."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">G50 — Déclaration Mensuelle</h2>
        <p style="margin:3px 0 0;color:#888;">Série G N°50 — TVA / IRG / IBS / Timbre</p>
    </div>
    """)

    # Company info
    app.markdown("### Identité")
    col1, col2 = app.columns(2)
    with col1:
        nif = app.text_input("NIF", placeholder="1234567890")
        nom_prenom = app.text_input("Nom et Prénom / Raison sociale")
        activite = app.text_input("Activité / Profession")
    with col2:
        adresse = app.text_input("Adresse")
        commune = app.text_input("Commune")
        wilaya = app.text_input("Wilaya", placeholder="32-El Bayadh")

    col1, col2 = app.columns(2)
    with col1:
        code_activite = app.text_input("Code Activité", placeholder="6201")
        article_imposition = app.text_input("Article d'imposition")
    with col2:
        month_idx = app.selectbox("Mois", options=list(range(1, 13)), format_func=lambda x: MONTHS_FR[x], index=5)
        year = app.number_input("Année", min_value=2024, max_value=2030, value=2026)

    # TVA
    app.markdown("### TVA — Chiffre d'affaires")
    col1, col2 = app.columns(2)
    with col1:
        tva_9_biens = app.number_input("CA TVA 9% — Biens, produits, denrées (DA)", min_value=0, value=0, step=1000)
        tva_9_prestations = app.number_input("CA TVA 9% — Prestations de services (DA)", min_value=0, value=0, step=1000)
        tva_19_production = app.number_input("CA TVA 19% — Production (DA)", min_value=0, value=0, step=1000)
        tva_19_revente = app.number_input("CA TVA 19% — Revente en l'état (DA)", min_value=0, value=0, step=1000)
    with col2:
        tva_19_liberales = app.number_input("CA TVA 19% — Professions libérales (DA)", min_value=0, value=0, step=1000)
        tva_19_telephone = app.number_input("CA TVA 19% — Téléphone (DA)", min_value=0, value=0, step=1000)
        tva_19_autres = app.number_input("CA TVA 19% — Autres prestations (DA)", min_value=0, value=0, step=1000)

    app.markdown("### TVA — Déductions")
    col1, col2 = app.columns(2)
    with col1:
        tva_achats_matieres = app.number_input("TVA achats matières et services (DA)", min_value=0, value=0, step=1000)
        tva_achats_amortissables = app.number_input("TVA achats biens amortissables (DA)", min_value=0, value=0, step=1000)
    with col2:
        tva_precompte = app.number_input("Précompte antérieur (DA)", min_value=0, value=0, step=1000)
        tva_autres_deductions = app.number_input("Autres déductions (DA)", min_value=0, value=0, step=1000)

    # IRG Salaires
    app.markdown("### IRG Salaires")
    col1, col2 = app.columns(2)
    with col1:
        irg_salaires_revenus = app.number_input("Revenus imposables salaires (DA)", min_value=0, value=0, step=10000)
    with col2:
        irg_salaires_irg = app.number_input("IRG retenu sur salaires (DA)", min_value=0, value=0, step=1000)

    # Retenues à la source
    app.markdown("### Retenues à la source")
    col1, col2, col3 = app.columns(3)
    with col1:
        irg_location_revenus = app.number_input("Loyers — Revenus (DA)", min_value=0, value=0, step=10000)
        irg_location_irg = app.number_input("Loyers — IRG retenu (DA)", min_value=0, value=0, step=1000)
    with col2:
        irg_autres_ras_revenus = app.number_input("Autres retenues — Revenus (DA)", min_value=0, value=0, step=10000)
        irg_autres_ras_irg = app.number_input("Autres retenues — IRG retenu (DA)", min_value=0, value=0, step=1000)
    with col3:
        ibs_prestations_revenus = app.number_input("IBS étrangères — Revenus (DA)", min_value=0, value=0, step=10000)
        ibs_prestations_irg = app.number_input("IBS étrangères — IBS retenu (DA)", min_value=0, value=0, step=1000)

    # Build G50Data
    data = G50Data(
        nif=nif.value, nom_prenom=nom_prenom.value, activite=activite.value,
        adresse=adresse.value, commune=commune.value, wilaya=wilaya.value,
        code_activite=code_activite.value, article_imposition=article_imposition.value,
        month=int(month_idx.value), year=int(year.value),
        tva_9_biens_total=float(tva_9_biens.value), tva_9_prestations_total=float(tva_9_prestations.value),
        tva_19_production_total=float(tva_19_production.value), tva_19_revente_total=float(tva_19_revente.value),
        tva_19_liberales_total=float(tva_19_liberales.value), tva_19_telephone_total=float(tva_19_telephone.value),
        tva_19_autres_serv_total=float(tva_19_autres.value),
        tva_precompte_anterieur=float(tva_precompte.value),
        tva_achats_matieres=float(tva_achats_matieres.value),
        tva_achats_amortissables=float(tva_achats_amortissables.value),
        tva_autres_deductions=float(tva_autres_deductions.value),
        irg_salaires_revenus=float(irg_salaires_revenus.value), irg_salaires_irg=float(irg_salaires_irg.value),
        irg_location_commerciale_revenus=float(irg_location_revenus.value),
        irg_location_commerciale_irg=float(irg_location_irg.value),
        irg_autres_ras_revenus=float(irg_autres_ras_revenus.value),
        irg_autres_ras_irg=float(irg_autres_ras_irg.value),
        ibs_prestations_revenus=float(ibs_prestations_revenus.value),
        ibs_prestations_irg=float(ibs_prestations_irg.value),
    )
    result = calculate_g50(data)

    app.html(f"""<div style="padding:15px;background:#e8f5e9;border-radius:8px;margin:15px 0;">
        <div style="font-weight:bold;color:#2e7d32;margin-bottom:5px;">Total à payer: {result.total_a_payer:,.0f} DA</div>
        <div style="font-size:0.85em;color:#555;">
            TVA: {result.tva_a_payer:,.0f} DA | IRG: {result.irg_salaires:,.0f} DA |
            Retenues: {result.total_retenues_source:,.0f} DA | Timbre: {result.total_table5:,.0f} DA
        </div>
    </div>""")

    # Generate
    if app.button("Generate G50 Form", primary=True):
        if not nif.value or not nom_prenom.value:
            app.toast("NIF and name required", type="error")
            return
        app.toast("Generating G50 form...", type="info")
        html = generate_g50_html(data)
        text = generate_g50_text(data)
        out = Path(__file__).parent.parent / "generated_output"
        out.mkdir(exist_ok=True)
        month_name = MONTHS_FR[int(month_idx.value)]
        html_path = out / f"G50_{nom_prenom.value.replace(' ', '_') or 'client'}_{month_name}_{year.value}.html"
        html_path.write_text(html, encoding="utf-8")
        app.markdown("### G50 Generated")
        app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;max-height:500px;overflow-y:auto;'>{html}</div>")
        app.html(f"<p style='color:#28a745;'>Saved: {html_path}</p>")
        app.download_button("Download HTML", data=html.encode(), file_name=html_path.name, mime="text/html")
        try:
            pdf = generate_tax_pdf("g50", data)
            pdf_path = html_path.with_suffix(".pdf")
            pdf_path.write_bytes(pdf)
            app.download_button("Download PDF", data=pdf, file_name=pdf_path.name, mime="application/pdf")
        except Exception as e:
            app.html(f"<p style='color:#dc3545;'>PDF error: {e}</p>")


def g4_page():
    """G4 IBS — Annual Corporate Tax Declaration."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">G4 — Déclaration IBS (Sociétés)</h2>
        <p style="margin:3px 0 0;color:#888;">Série G N°4 — Impôt sur les Bénéfices des Sociétés</p>
    </div>
    """)

    app.markdown("### Identité")
    col1, col2 = app.columns(2)
    with col1:
        nif = app.text_input("NIF", key="g4_nif")
        raison_sociale = app.text_input("Raison sociale")
        forme_juridique = app.selectbox("Forme juridique", options=["SARL", "EURL", "SPA", "SNC", "SAS", "EPE", "EPIC", "Coopérative", "Autre"], index=0)
        activite = app.text_input("Activité(s) exercée(s)")
        code_activite = app.text_input("Code Activité", key="g4_code")
    with col2:
        rc = app.text_input("N° Registre de Commerce")
        compte_bancaire = app.text_input("N° Compte bancaire/CCP")
        adresse = app.text_input("Adresse siège social")
        telephone = app.text_input("Téléphone / Email")
        wilaya = app.text_input("Wilaya", key="g4_wilaya")

    app.markdown("### Résultat fiscal")
    col1, col2 = app.columns(2)
    with col1:
        resultat_comptable = app.number_input("Résultat comptable (DA)", min_value=-1_000_000_000, value=0, step=100_000)
        reintegrations = app.number_input("Total réintégrations (DA)", min_value=0, value=0, step=10_000)
        deductions = app.number_input("Total déductions (DA)", min_value=0, value=0, step=10_000)
    with col2:
        benefices_exoneres = app.number_input("Bénéfices exonérés (DA)", min_value=0, value=0, step=100_000)
        benefices_reinvestis = app.number_input("Bénéfices réinvestis (DA)", min_value=0, value=0, step=100_000)
        taux_exoneration = app.number_input("Taux exonération (%)", min_value=0, max_value=100, value=0, step=5)

    app.markdown("### IBS — Calcul")
    col1, col2 = app.columns(2)
    with col1:
        ibs_19 = app.number_input("IBS 19% (production) (DA)", min_value=0, value=0, step=10_000)
        ibs_23 = app.number_input("IBS 23% (BTP/tourisme) (DA)", min_value=0, value=0, step=10_000)
        ibs_26 = app.number_input("IBS 26% (commerce/services) (DA)", min_value=0, value=0, step=10_000)
    with col2:
        ibs_minimum = app.number_input("Minimum d'impôt (DA)", min_value=0, value=0, step=10_000)
        credit_impot = app.number_input("Crédit d'impôt (DA)", min_value=0, value=0, step=10_000)
        acomptes_versement = app.number_input("Acomptes versés (DA)", min_value=0, value=0, step=10_000)

    annee = app.number_input("Année d'imposition", min_value=2024, max_value=2030, value=2026, key="g4_annee")

    data = G4Data(
        nif=nif.value, raison_sociale=raison_sociale.value, forme_juridique=forme_juridique.value,
        activite=activite.value, code_activite=code_activite.value, numero_rc=rc.value,
        compte_bancaire=compte_bancaire.value, adresse=adresse.value, telephone=telephone.value,
        wilaya=wilaya.value,
        resultat_comptable=float(resultat_comptable.value), reintegration_total=float(reintegrations.value),
        deduction_total=float(deductions.value), benefices_exoneres=float(benefices_exoneres.value),
        taux_exoneration=float(taux_exoneration.value), benefices_reinvestis=float(benefices_reinvestis.value),
        ibs_taux19=float(ibs_19.value), ibs_taux23=float(ibs_23.value), ibs_taux26=float(ibs_26.value),
        ibs_minimum=float(ibs_minimum.value), credit_impot=float(credit_impot.value),
        acomptes_verses=float(acomptes_versement.value),
        wilaya_nom=wilaya.value, diw="", inspection="", recette="", structure="",
        date_creation="", capital_social="", email="", telefax="",
        annee_imposition=int(annee.value), exercice_debut="", exercice_fin="",
    )

    calc = calculate_g4(data)
    app.html(f"""<div style="padding:15px;background:#e8f5e9;border-radius:8px;margin:15px 0;">
        <div style="font-weight:bold;color:#2e7d32;margin-bottom:5px;">Solde IBS à payer: {calc.solde_ibs:,.0f} DA</div>
        <div style="font-size:0.85em;color:#555;">
            IBS total: {calc.ibs_total:,.0f} DA | Minimum: {calc.minimum_impot:,.0f} DA | Crédit: {calc.credit_impot:,.0f} DA | Acomptes: {calc.acomptes_versement:,.0f} DA
        </div>
    </div>""")

    if app.button("Generate G4 Form", primary=True):
        if not nif.value or not raison_sociale.value:
            app.toast("NIF and Raison sociale required", type="error")
            return
        html = generate_g4_html(data)
        out = Path(__file__).parent.parent / "generated_output"
        out.mkdir(exist_ok=True)
        html_path = out / f"G4_{raison_sociale.value.replace(' ', '_') or 'client'}_{annee.value}.html"
        html_path.write_text(html, encoding="utf-8")
        app.markdown("### G4 Generated")
        app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;max-height:500px;overflow-y:auto;'>{html}</div>")
        app.download_button("Download HTML", data=html.encode(), file_name=html_path.name, mime="text/html")
        try:
            pdf = generate_tax_pdf("g4", data)
            pdf_path = html_path.with_suffix(".pdf")
            pdf_path.write_bytes(pdf)
            app.download_button("Download PDF", data=pdf, file_name=pdf_path.name, mime="application/pdf")
        except Exception as e:
            app.html(f"<p style='color:#dc3545;'>PDF error: {e}</p>")


def g11_page():
    """G11 BIC — Annual BIC Régime Réel Declaration."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">G11 — Déclaration BIC (Régime Réel)</h2>
        <p style="margin:3px 0 0;color:#888;">Série G N°11 — Bénéfices Industriels et Commerciaux</p>
    </div>
    """)

    app.markdown("### Identité")
    col1, col2 = app.columns(2)
    with col1:
        nif = app.text_input("NIF", key="g11_nif")
        nom = app.text_input("Nom, Prénom / Raison sociale")
        activite = app.text_input("Activité", key="g11_act")
        code = app.text_input("Code Activité", key="g11_code")
    with col2:
        rc = app.text_input("N° Registre de Commerce", key="g11_rc")
        adresse = app.text_input("Adresse", key="g11_addr")
        telephone = app.text_input("Téléphone / Email", key="g11_tel")

    app.markdown("### Résultat fiscal")
    col1, col2 = app.columns(2)
    with col1:
        resultat_comptable = app.number_input("Résultat comptable (DA)", min_value=-1_000_000_000, value=0, step=100_000, key="g11_rc_value")
        reintegration = app.number_input("Réintégrations (DA)", min_value=0, value=0, step=10_000, key="g11_reint")
    with col2:
        deduction = app.number_input("Déductions (DA)", min_value=0, value=0, step=10_000, key="g11_ded")
        benefices_exoneres = app.number_input("Bénéfices exonérés (DA)", min_value=0, value=0, step=100_000, key="g11_exo")

    app.markdown("### IRG — Calcul")
    col1, col2 = app.columns(2)
    with col1:
        irg_taux19 = app.number_input("IRG 19% (DA)", min_value=0, value=0, step=10_000, key="g11_irg19")
        irg_taux23 = app.number_input("IRG 23% (DA)", min_value=0, value=0, step=10_000, key="g11_irg23")
        irg_taux26 = app.number_input("IRG 26% (DA)", min_value=0, value=0, step=10_000, key="g11_irg26")
    with col2:
        acompte1 = app.number_input("1er acompte (DA)", min_value=0, value=0, step=10_000, key="g11_ac1")
        acompte2 = app.number_input("2ème acompte (DA)", min_value=0, value=0, step=10_000, key="g11_ac2")

    annee = app.number_input("Année", min_value=2024, max_value=2030, value=2026, key="g11_annee")

    data = G11Data(
        nif=nif.value, nom_raison_sociale=nom.value, activite=activite.value,
        code_activite=code.value, numero_rc=rc.value, adresse=adresse.value, telephone=telephone.value,
        resultat_comptable=float(resultat_comptable.value), reintegration=float(reintegration.value),
        deduction=float(deduction.value), benefices_exoneres=float(benefices_exoneres.value),
        irg_taux19=float(irg_taux19.value), irg_taux23=float(irg_taux23.value), irg_taux26=float(irg_taux26.value),
        acompte1=float(acompte1.value), acompte2=float(acompte2.value),
        wilaya="", diw="", inspection="", recette="", structure="",
        date_debut="", date_fin="", activite_code="",
        benefices_reinvestis=0.0, taux_exoneration=0.0,
    )

    calc = calculate_g11(data)
    app.html(f"""<div style="padding:15px;background:#e8f5e9;border-radius:8px;margin:15px 0;">
        <div style="font-weight:bold;color:#2e7d32;margin-bottom:5px;">Solde IRG à payer: {calc.solde_irg:,.0f} DA</div>
        <div style="font-size:0.85em;color:#555;">
            IRG dû: {calc.irg_total:,.0f} DA | Acomptes: {calc.acomptes_verses:,.0f} DA
        </div>
    </div>""")

    if app.button("Generate G11 Form", primary=True):
        if not nif.value or not nom.value:
            app.toast("NIF and Nom required", type="error")
            return
        html = generate_g11_html(data)
        out = Path(__file__).parent.parent / "generated_output"
        out.mkdir(exist_ok=True)
        html_path = out / f"G11_{nom.value.replace(' ', '_') or 'client'}_{annee.value}.html"
        html_path.write_text(html, encoding="utf-8")
        app.markdown("### G11 Generated")
        app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;max-height:500px;overflow-y:auto;'>{html}</div>")
        app.download_button("Download HTML", data=html.encode(), file_name=html_path.name, mime="text/html")
        try:
            pdf = generate_tax_pdf("g11", data)
            pdf_path = html_path.with_suffix(".pdf")
            pdf_path.write_bytes(pdf)
            app.download_button("Download PDF", data=pdf, file_name=pdf_path.name, mime="application/pdf")
        except Exception as e:
            app.html(f"<p style='color:#dc3545;'>PDF error: {e}</p>")


def g29_page():
    """G29/G30 — IRG Salaires Annual Declaration."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">G29 — Déclaration IRG Salaires</h2>
        <p style="margin:3px 0 0;color:#888;">Série G N°29 + G N°30 — État nominatif des salariés</p>
    </div>
    """)

    app.markdown("### Identité Employeur")
    col1, col2 = app.columns(2)
    with col1:
        nif = app.text_input("NIF", key="g29_nif")
        raison_sociale = app.text_input("Raison sociale")
    with col2:
        activite = app.text_input("Activité", key="g29_act")
        adresse = app.text_input("Adresse", key="g29_addr")

    # Employee input
    app.markdown("### Salariés")
    num_emp = app.number_input("Nombre de salariés", min_value=1, max_value=500, value=1, step=1)

    employees = []
    for i in range(int(num_emp.value)):
        app.html(f"<hr style='margin:10px 0;'><strong>Salarié {i+1}</strong>")
        c1, c2, c3 = app.columns(3)
        with c1:
            nom_emp = app.text_input(f"Nom complet", key=f"emp_nom_{i}")
            salaire_brut = app.number_input(f"Salaire brut (DA)", min_value=0, value=20000, step=1000, key=f"emp_brut_{i}")
            avantages = app.number_input(f"Avantages en nature", min_value=0, value=0, step=1000, key=f"emp_av_{i}")
        with c2:
            cotisations = app.number_input(f"Cotisations salariales", min_value=0, value=0, step=1000, key=f"emp_cot_{i}")
            nb_parts = app.number_input(f"Parts fiscales", min_value=0.5, value=1.0, step=0.5, key=f"emp_parts_{i}")
        with c3:
            indemnites = app.number_input(f"Indemnités", min_value=0, value=0, step=1000, key=f"emp_ind_{i}")
        if nom_emp.value:
            employees.append(EmployeeData(
                nom=nom_emp.value, salaire_brut=float(salaire_brut.value),
                avantages_en_nature=float(avantages.value), indemnites=float(indemnites.value),
                cotisations_salariales=float(cotisations.value), parts=float(nb_parts.value),
            ))

    annee = app.number_input("Année", min_value=2024, max_value=2030, value=2026, key="g29_annee")

    if employees:
        total_brut = sum(e.salaire_brut + e.avantages_en_nature + e.indemnites for e in employees)
        total_irg = sum(calculate_irg((e.salaire_brut + e.avantages_en_nature + e.indemnites - e.cotisations_salariales), e.parts) for e in employees)
        app.html(f"""<div style="padding:15px;background:#e8f5e9;border-radius:8px;margin:15px 0;">
            <div style="font-weight:bold;color:#2e7d32;margin-bottom:5px;">Masse salariale brute: {total_brut:,.0f} DA | IRG total: {total_irg:,.0f} DA</div>
            <div style="font-size:0.85em;color:#555;">{len(employees)} salarié(s) déclaré(s)</div>
        </div>""")

    if app.button("Generate G29 Form", primary=True):
        if not nif.value or not raison_sociale.value or not employees:
            app.toast("NIF, raison sociale, and at least 1 salarié required", type="error")
            return
        data = G29Data(
            nif=nif.value, raison_sociale=raison_sociale.value, activite=activite.value,
            adresse=adresse.value, nombre_salaries=len(employees), salaries=employees,
        )
        html = generate_g29_html(data)
        out = Path(__file__).parent.parent / "generated_output"
        out.mkdir(exist_ok=True)
        html_path = out / f"G29_{raison_sociale.value.replace(' ', '_') or 'client'}_{annee.value}.html"
        html_path.write_text(html, encoding="utf-8")
        app.markdown("### G29 Generated")
        app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;max-height:500px;overflow-y:auto;'>{html}</div>")
        app.download_button("Download HTML", data=html.encode(), file_name=html_path.name, mime="text/html")
        try:
            pdf = generate_tax_pdf("g29", data)
            pdf_path = html_path.with_suffix(".pdf")
            pdf_path.write_bytes(pdf)
            app.download_button("Download PDF", data=pdf, file_name=pdf_path.name, mime="application/pdf")
        except Exception as e:
            app.html(f"<p style='color:#dc3545;'>PDF error: {e}</p>")


def g1_page():
    """G1 — Déclaration Globale des Revenus."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">G1 — Déclaration Générale des Revenus</h2>
        <p style="margin:3px 0 0;color:#888;">Série G N°1 — IRG annuel des particuliers</p>
    </div>
    """)

    app.markdown("### Identité")
    col1, col2 = app.columns(2)
    with col1:
        nif = app.text_input("NIF", key="g1_nif")
        nom = app.text_input("Nom et Prénom")
        date_naissance = app.text_input("Date de naissance (JJ/MM/AAAA)")
    with col2:
        situation = app.selectbox("Situation familiale", options=["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"], index=0)
        nb_parts = app.number_input("Nombre de parts", min_value=0.5, value=1.0, step=0.5)
        activite = app.text_input("Activité principale", key="g1_act")
        adresse = app.text_input("Adresse domicile fiscal", key="g1_addr")

    app.markdown("### Revenus salariaux")
    col1, col2 = app.columns(2)
    with col1:
        salaire_brut = app.number_input("Salaire brut annuel (DA)", min_value=0, value=0, step=10_000, key="g1_sal_brut")
    with col2:
        cotisations = app.number_input("Cotisations salariales (DA)", min_value=0, value=0, step=1_000, key="g1_cot")
        irg_retenu = app.number_input("IRG retenu par employeur (DA)", min_value=0, value=0, step=1_000, key="g1_irg_ret")

    app.markdown("### Autres revenus")
    col1, col2, col3 = app.columns(3)
    with col1:
        revenus_fonciers = app.number_input("Revenus fonciers (DA)", min_value=0, value=0, step=10_000, key="g1_fonc")
    with col2:
        revenus_bic = app.number_input("BIC (DA)", min_value=0, value=0, step=10_000, key="g1_bic")
    with col3:
        revenus_bnc = app.number_input("BNC (DA)", min_value=0, value=0, step=10_000, key="g1_bnc")

    col1, col2, col3 = app.columns(3)
    with col1:
        revenus_capitaux = app.number_input("Revenus capitaux mobiliers (DA)", min_value=0, value=0, step=10_000, key="g1_cap")
    with col2:
        plus_values = app.number_input("Plus-values (DA)", min_value=0, value=0, step=10_000, key="g1_pv")
    with col3:
        revenus_agricoles = app.number_input("Revenus agricoles (DA)", min_value=0, value=0, step=10_000, key="g1_agr")

    charges = app.number_input("Charges déductibles (DA)", min_value=0, value=0, step=10_000, key="g1_charges")
    acomptes = app.number_input("Acomptes versés (DA)", min_value=0, value=0, step=10_000, key="g1_ac")
    annee = app.number_input("Année", min_value=2024, max_value=2030, value=2026, key="g1_annee")

    data = G1Data(
        nif=nif.value, nom=nom.value, date_naissance=date_naissance.value,
        situation_familiale=situation.value, nombre_parts=float(nb_parts.value),
        activite=activite.value, adresse=adresse.value,
        salaire_brut=float(salaire_brut.value), cotisations_salariales=float(cotisations.value),
        irg_retenu=float(irg_retenu.value),
        revenus_fonciers=float(revenus_fonciers.value),
        revenus_bic=float(revenus_bic.value),
        revenus_bnc=float(revenus_bnc.value),
        revenus_capitaux_mobiliers=float(revenus_capitaux.value),
        plus_values=float(plus_values.value),
        revenus_agricoles=float(revenus_agricoles.value),
        charges_deductibles=float(charges.value), acomptes_verses=float(acomptes.value),
    )

    calc = calculate_g1(data)
    app.html(f"""<div style="padding:15px;background:#e8f5e9;border-radius:8px;margin:15px 0;">
        <div style="font-weight:bold;color:#2e7d32;margin-bottom:5px;">Revenu net imposable: {calc.revenu_net_imposable:,.0f} DA | IRG: {calc.irg_total:,.0f} DA</div>
        <div style="font-size:0.85em;color:#555;">Solde: {calc.solde_irg:,.0f} DA ({'à payer' if calc.solde_irg > 0 else 'remboursement'})</div>
    </div>""")

    if app.button("Generate G1 Form", primary=True):
        if not nif.value or not nom.value:
            app.toast("NIF and Nom required", type="error")
            return
        html = generate_g1_html(data)
        out = Path(__file__).parent.parent / "generated_output"
        out.mkdir(exist_ok=True)
        html_path = out / f"G1_{nom.value.replace(' ', '_') or 'client'}_{annee.value}.html"
        html_path.write_text(html, encoding="utf-8")
        app.markdown("### G1 Generated")
        app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;max-height:500px;overflow-y:auto;'>{html}</div>")
        app.download_button("Download HTML", data=html.encode(), file_name=html_path.name, mime="text/html")
        try:
            pdf = generate_tax_pdf("g1", data)
            pdf_path = html_path.with_suffix(".pdf")
            pdf_path.write_bytes(pdf)
            app.download_button("Download PDF", data=pdf, file_name=pdf_path.name, mime="application/pdf")
        except Exception as e:
            app.html(f"<p style='color:#dc3545;'>PDF error: {e}</p>")


def g8_page():
    """G8 — Déclaration d'Existence."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">G8 — Déclaration d'Existence</h2>
        <p style="margin:3px 0 0;color:#888;">Série G N°8 — À souscrire dans les 30 jours</p>
    </div>
    """)

    app.markdown("### Identité")
    col1, col2 = app.columns(2)
    with col1:
        nif = app.text_input("NIF (si existant)", key="g8_nif")
        nouveau = app.checkbox("Nouveau contribuable", value=True)
        nom = app.text_input("Nom et Prénom")
        prenom = app.text_input("Prénom")
        date_naissance = app.text_input("Date de naissance (JJ/MM/AAAA)", key="g8_dn")
        lieu_naissance = app.text_input("Lieu de naissance")
    with col2:
        situation = app.selectbox("Situation familiale", options=["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"], index=0, key="g8_sit")
        activite = app.text_input("Activité principale", key="g8_act")
        code_activite = app.text_input("Code Activité", key="g8_code")
        date_debut = app.text_input("Date de commencement (JJ/MM/AAAA)")
        rc = app.text_input("N° Registre de Commerce")
        compte = app.text_input("N° Compte bancaire/CCP")

    app.markdown("### Adresse")
    col1, col2 = app.columns(2)
    with col1:
        adresse_siege = app.text_input("Adresse siège social", key="g8_addr")
        commune = app.text_input("Commune", key="g8_commune")
    with col2:
        wilaya = app.text_input("Wilaya", key="g8_wilaya")
        telephone = app.text_input("Téléphone / Email", key="g8_tel")

    app.markdown("### Activité")
    col1, col2 = app.columns(2)
    with col1:
        nature = app.selectbox("Nature de l'activité", options=["Commerciale", "Industrielle", "Libérale", "Agricole", "Autre"], index=0)
        forme_juridique = app.text_input("Forme juridique", key="g8_forme")
    with col2:
        capital_social = app.text_input("Capital social (DA)", key="g8_cap")
        nb_salaries = app.number_input("Nombre de salariés", min_value=0, value=0, key="g8_sal")

    data = G8Data(
        nif=nif.value if not nouveau else "",
        nom=nom.value, prenom=prenom.value,
        date_naissance=date_naissance.value, lieu_naissance=lieu_naissance.value,
        situation_familiale=situation.value, activite=activite.value,
        code_activite=code_activite.value, date_debut=date_debut.value,
        numero_rc=rc.value, compte_bancaire=compte.value,
        adresse_siege=adresse_siege.value, commune=commune.value,
        wilaya=wilaya.value, telephone=telephone.value,
        nature_activite=nature.value, forme_juridique=forme_juridique.value,
        capital_social=capital_social.value, nombre_salaries=int(nb_salaries.value),
        nouveau_contribuable=nouveau,
    )

    if app.button("Generate G8 Form", primary=True):
        if not nom.value or not prenom.value:
            app.toast("Nom and Prénom required", type="error")
            return
        html = generate_g8_html(data)
        out = Path(__file__).parent.parent / "generated_output"
        out.mkdir(exist_ok=True)
        full_name = f"{nom.value}_{prenom.value}".replace(' ', '_') if prenom.value else nom.value.replace(' ', '_')
        html_path = out / f"G8_{full_name or 'client'}.html"
        html_path.write_text(html, encoding="utf-8")
        app.markdown("### G8 Generated")
        app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;max-height:500px;overflow-y:auto;'>{html}</div>")
        app.download_button("Download HTML", data=html.encode(), file_name=html_path.name, mime="text/html")
        try:
            pdf = generate_tax_pdf("g8", data)
            pdf_path = html_path.with_suffix(".pdf")
            pdf_path.write_bytes(pdf)
            app.download_button("Download PDF", data=pdf, file_name=pdf_path.name, mime="application/pdf")
        except Exception as e:
            app.html(f"<p style='color:#dc3545;'>PDF error: {e}</p>")


def invoice_page():
    _sidebar()
    app.title("Invoice / Quote Generator")
    app.text("إنشاء فاتورة أو عرض سعر احترافي")

    doc_type = app.selectbox("Document Type", options=["Invoice (فاتورة)", "Quote (عرض سعر)"], index=0)
    is_invoice = doc_type.value.startswith("Invoice")

    business_name = app.text_input("Your Business Name")
    client_name = app.text_input("Client Name")

    app.markdown("### Items")
    num_items = app.number_input("Number of items", min_value=1, max_value=20, value=3, step=1)

    items = []
    for i in range(int(num_items.value)):
        cols = app.columns(3)
        with cols[0]:
            desc = app.text_input(f"Item {i+1} description", key=f"desc_{i}")
        with cols[1]:
            qty = app.number_input(f"Qty", min_value=1, value=1, key=f"qty_{i}")
        with cols[2]:
            price = app.number_input(f"Price (DZD)", min_value=0, value=0, step=100, key=f"price_{i}")
        if desc.value:
            items.append({"description": desc.value, "qty": int(qty.value), "price": int(price.value)})

    if is_invoice:
        discount = app.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0)
        payment_terms = app.text_input("Payment terms", value="30 jours")
        notes = app.text_input("Notes (optional)")
    else:
        validity = app.number_input("Quote validity (days)", min_value=7, max_value=90, value=30, step=7)
        notes = app.text_input("Notes (optional)")

    if app.button(f"Generate {doc_type.value.split(' ')[0]}"):
        if not business_name.value or not client_name.value or not items:
            app.toast("Please fill business name, client name, and at least 1 item", type="error")
            return
        app.toast("Generating document...", type="info")
        try:
            gen = InvoiceGenerator(provider=provider.value)
            if is_invoice:
                result = gen.generate_invoice(business_name.value, client_name.value, items, discount.value, notes.value, payment_terms.value)
            else:
                result = gen.generate_quote(business_name.value, client_name.value, items, validity.value, notes.value)
            doc_label = "Invoice" if is_invoice else "Quote"
            app.markdown(f"### {doc_label}")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output(doc_label.lower(), client_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def cv_page():
    _sidebar()
    app.title("CV Generator / مولّد السيرة الذاتية")
    app.text("إنشاء سيرة ذاتية احترافية بالعربية أو الفرنسية — PDF")

    lang = app.selectbox("Language / اللغة", options=["Français", "العربية"], index=0)
    template_key = app.selectbox("Template", options=list(CV_TEMPLATES.keys()), index=0)
    template = CV_TEMPLATES[template_key.value]

    name = app.text_input("Full Name / الاسم الكامل", value=template.get("name", ""))
    title = app.text_input("Job Title / المنصب", value=template.get("title", ""))
    phone = app.text_input("Phone / الهاتف")
    email = app.text_input("Email / البريد الإلكتروني")
    location = app.text_input("Location / الموقع")
    summary = app.text_area("Summary / الملخص", value=template.get("summary", ""), height=80)

    if app.button("Generate CV / إنشاء السيرة الذاتية"):
        if not name.value:
            app.toast("Please enter your name", type="error")
            return
        app.toast("Generating CV...", type="info")
        try:
            data = {
                "name": name.value, "title": title.value,
                "phone": phone.value, "email": email.value, "location": location.value,
                "summary": summary.value,
                "experience": template.get("experience", []),
                "education": template.get("education", []),
                "skills": template.get("skills", []),
            }
            gen = CVGenerator()
            lang_code = "ar" if "العربية" in lang.value else "fr"
            filepath = gen.generate(data, lang_code)
            app.markdown("### CV Generated ✅")
            app.html(f"<p style='color:#28a745;'>Saved: {filepath}</p>")
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    pdf_bytes = f.read()
                b64 = base64.b64encode(pdf_bytes).decode()
                app.html(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600px" style="border:1px solid #ddd;border-radius:8px;"></iframe>')
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def cover_letter_page():
    _sidebar()
    app.title("Cover Letter / رسالة التعريف")
    app.text("إنشاء رسالة تعريف احترافية —_FR أو AR — PDF")

    template_key = app.selectbox("Template", options=list(COVER_TEMPLATES.keys()), index=0)
    template = COVER_TEMPLATES[template_key.value]

    sender_name = app.text_input("Your Name / اسمك", value=template.get("sender_name", ""))
    date = app.text_input("Date / التاريخ", value="05/08/2026")
    recipient = app.text_input("Recipient /DESTINATAIRE", value="À l'attention du Directeur des Ressources Humaines")
    subject = app.text_input("Subject / الموضوع", value=template.get("subject", ""))

    if app.button("Generate Letter / إنشاء الرسالة"):
        if not sender_name.value:
            app.toast("Please enter your name", type="error")
            return
        app.toast("Generating cover letter...", type="info")
        try:
            data = dict(template)
            data["sender_name"] = sender_name.value
            data["date"] = date.value
            data["recipient_name"] = recipient.value
            data["recipient_address"] = [recipient.value]
            if subject.value:
                data["subject"] = subject.value
            gen = CoverLetterGenerator()
            lang_code = "ar" if "ar" in template_key.value else "fr"
            filepath = gen.generate(data, lang_code)
            app.markdown("### Cover Letter Generated ✅")
            app.html(f"<p style='color:#28a745;'>Saved: {filepath}</p>")
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    pdf_bytes = f.read()
                b64 = base64.b64encode(pdf_bytes).decode()
                app.html(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600px" style="border:1px solid #ddd;border-radius:8px;"></iframe>')
        except Exception as e:
            app.toast(f"Error: {e}", type="error")


def government_page():
    _sidebar()
    app.title("Government Paperwork / الإجراءات الإدارية")
    app.text("أدلة الإجراءات الحكومية — ANEM, CACI, CNAS, CASNOS, Carte Grise")

    categories = {
        "emploi": "Emploi / التشغيل",
        "creation": "Création d'entreprise / إنشاء مؤسسة",
        "social": "Sécurité sociale / الضمان الاجتماعي",
        "vehicule": "Véhicule / المركبات",
    }
    cat = app.selectbox("Category / الفئة", options=list(categories.keys()), index=0)
    helper = GovernmentPaperworkHelper()
    procs = helper.list_procedures(category=cat, lang="fr")

    proc_names = {p["key"]: p["name"] for p in procs}
    selected = app.selectbox("Procedure / الإجراء", options=list(proc_names.keys()), index=0)

    if selected.value:
        proc = PROCEDURES[selected.value]
        app.html(f"<h3 style='margin-bottom:2px;'>{proc['name_fr']}</h3><p style='margin-top:0;color:#666;'>{proc['name_ar']}</p>")
        app.text(f"⏱️ {proc['duration_fr']}")
        app.text(f"💰 {proc['cost_fr']}")

        app.markdown("### Documents requis")
        for doc in proc["documents_fr"]:
            app.html(f"<div style='padding:4px 0;border-bottom:1px dotted #eee;'>□ {doc}</div>")

        app.markdown("### Étapes")
        for step in proc["steps_fr"]:
            app.html(f"<div style='padding:4px 0;'>{step}</div>")

        app.markdown("### Notes")
        app.html(f"<div style='background:#f8f9fa;padding:12px;border-radius:8px;'>{proc['notes_fr']}</div>")

        if app.button("Save Checklist / حفظ القائمة"):
            filepath = helper.save_checklist(selected.value, "fr")
            app.toast(f"Saved: {filepath}", type="success")


def calculators_page():
    _sidebar()
    app.title("Financial Calculators / حاسبات مالية")
    app.text("VAN, TRI, Seuil de Rentabilité, Scénarios — calculs réels, pas de LLM")

    calc = FinancialCalculators()

    app.markdown("### 📊 Investissement & Financement")
    col1, col2 = app.columns(2)
    with col1:
        equipment = app.number_input("Équipements (DZD)", min_value=0, value=2_000_000, step=100_000)
        buildings = app.number_input("Bâtiments (DZD)", min_value=0, value=1_500_000, step=100_000)
        engineering = app.number_input("Études & montage (DZD)", min_value=0, value=300_000, step=50_000)
    with col2:
        working_capital = app.number_input("Fonds de roulement (DZD)", min_value=0, value=800_000, step=50_000)
        equity = app.number_input("Apports personnels (DZD)", min_value=0, value=3_000_000, step=100_000)
        loan = app.number_input("Emprunt bancaire (DZD)", min_value=0, value=1_600_000, step=100_000)

    investment = InvestmentPlan(
        equipment=equipment, buildings=buildings,
        engineering=engineering, working_capital=working_capital,
    )
    financing = FinancingPlan(equity=equity, bank_loan=loan)

    app.markdown("### 📈 Revenus & Coûts Annuels")
    annual_revenue = app.number_input("Chiffre d'affaires annuel (DZD)", min_value=0, value=6_000_000, step=500_000)
    cogs_rate = app.slider("Taux coût d'achat (%)", min_value=30, max_value=80, value=65) / 100
    operating_rate = app.slider("Taux charges opérationnelles (%)", min_value=5, max_value=40, value=15) / 100
    years = app.slider("Durée prévisionnelle (ans)", min_value=3, max_value=10, value=5)

    if app.button("Calculer VAN, TRI, Scénarios"):
        scenarios = generate_3_scenarios(
            base_revenue=annual_revenue,
            base_cogs_rate=cogs_rate,
            base_operating_rate=operating_rate,
            investment=investment,
            financing=financing,
            years=years,
        )

        for name, s in scenarios.items():
            color = "#28a745" if s["van"] > 0 else "#dc3545"
            app.html(f"""<div style="background:#f8f9fa;padding:15px;border-radius:8px;margin:10px 0;border-left:4px solid {color};">
                <h4 style="margin:0 0 8px;">{s['label']}</h4>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
                    <div><strong>VAN:</strong> <span style="color:{color};">{format_dzd(s['van'])}</span></div>
                    <div><strong>TRI:</strong> <span style="color:{color};">{format_pct(s['tri'])}</span></div>
                    <div><strong>Taux marge:</strong> {format_pct(s['taux_marge'])}</div>
                    <div><strong>Seuil rentabilité:</strong> {format_dzd(s['seuil_rentabilite'])} unités</div>
                    <div><strong>Délai récupération:</strong> {s['delai_recuperation']:.1f} ans</div>
                    <div><strong>Paiement emprunt:</strong> {format_dzd(s['loan_payment'])}/an</div>
                </div>
            </div>""")

        app.toast("Calculs terminés", type="success")


def aapi_page():
    _sidebar()
    app.title("AAPI Scorer / تقييم AAPI")
    app.text("Grille d'évaluation — Décret 26-154, Annexe I — 1500 points max")

    app.markdown("### Paramètres du Projet")
    col1, col2 = app.columns(2)
    with col1:
        activity_priority = app.selectbox("Priorité activité", options=["1 — Industrie/Agro/BTP", "2 — Services/Transport/Digital", "3 — Commerce/Restauration"], index=2)
        investment = app.number_input("Montant investissement (DZD)", min_value=0, value=4_600_000, step=100_000)
        employees = app.number_input("Nombre d'emplois créés", min_value=1, value=5, step=1)
    with col2:
        equity_pct = app.slider("Apport personnel (%)", min_value=10, max_value=100, value=65)
        local_pct = app.slider("Contenu local (%)", min_value=0, max_value=100, value=40)
        cdd_pct = app.slider("Part CDD (%)", min_value=0, max_value=100, value=10)

    has_extension = app.checkbox("Extension sur bien mitoyen")
    export_pct = app.slider("Part exportations (%)", min_value=0, max_value=100, value=0)

    priority_num = int(activity_priority[0])

    if app.button("Calculer Score AAPI"):
        params = {
            "activity_priority": priority_num,
            "investment_amount": investment,
            "employees": employees,
            "equity_ratio": equity_pct / 100,
            "local_integration": local_pct,
            "cdd_ratio": cdd_pct / 100,
            "has_extension": has_extension,
            "export_ratio": export_pct,
        }

        optimizer = AAAPIOptimizer()
        score = optimizer.score_project(params)
        suggestions = optimizer.optimize(score, params)

        color = "#28a745" if score.percentage >= 60 else "#ffc107" if score.percentage >= 40 else "#dc3545"
        app.html(f"""<div style="background:#f8f9fa;padding:20px;border-radius:8px;margin:15px 0;border:2px solid {color};text-align:center;">
            <h2 style="margin:0;color:{color};">{score.total}/1500</h2>
            <p style="margin:5px 0;font-size:1.1em;">{score.percentage:.0f}% — {score.rating}</p>
        </div>""")

        app.markdown("### Détail par Critère")
        for key, criterion in [
            ("activity_type", "Nature de l'activité", 420),
            ("investment_amount", "Montant investissement", 360),
            ("employment", "Emploi", 300),
            ("equity_contribution", "Apports fonds propres", 200),
            ("local_content", "Contenu local", 60),
            ("employment_permanence", "Pérennité emploi", 60),
            ("investment_extension", "Extension investissement", 70),
            ("export_diversification", "Exportations", 30),
        ]:
            val = getattr(score, key)
            pct = (val / max_val * 100) if (max_val := criterion[2] if isinstance(criterion[2], int) else 100) else 0
            bar_len = int(pct / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            app.html(f"<div style='padding:3px 0;font-size:0.9em;'><strong>{criterion[1]}</strong>: {val}/{criterion[2]} <code>{bar}</code> {pct:.0f}%</div>")

        if suggestions:
            app.markdown("### 💡 Recommandations")
            for s in suggestions[:-1]:
                app.html(f"<div style='padding:4px 0;'>• <strong>{s['criterion']}</strong>: +{s['gap']} pts — {s['advice']}</div>")


def dossier_page():
    _sidebar()
    app.title("Complete Dossier / dossier complet")
    app.text("One-click pipeline: Feasibility + Financials + AAPI + Quality + PDF")

    app.markdown("### Client Information")
    col1, col2 = app.columns(2)
    with col1:
        client_name = app.text_input("Client Name", value="Nouveau Client")
        biz_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    with col2:
        location = app.text_input("City/Location", value="El Bayadh")
        wilaya = app.selectbox("Wilaya", options=list(ALGERIA_DATA["wilayas"].keys()), index=0)
        investment = app.number_input("Investment (DZD)", min_value=100_000, value=4_600_000, step=100_000)

    from business_defaults import get_defaults, estimate_profitability, estimate_monthly_revenue
    defaults = get_defaults(biz_type)
    est_revenue = estimate_monthly_revenue(biz_type, investment)
    est_profit = estimate_profitability(biz_type, investment, est_revenue)

    app.markdown("### Auto-Estimated Values")
    col1, col2, col3 = app.columns(3)
    with col1:
        app.html(f"<div style='text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;'><strong>Monthly Revenue</strong><br><span style='font-size:1.2em;color:#D4AF37;'>{est_revenue:,.0f} DZD</span></div>")
    with col2:
        app.html(f"<div style='text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;'><strong>Net Margin</strong><br><span style='font-size:1.2em;color:#28a745;'>{est_profit['net_margin']:.1%}</span></div>")
    with col3:
        app.html(f"<div style='text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;'><strong>Payback</strong><br><span style='font-size:1.2em;color:#0A1628;'>{est_profit['payback_years']:.1f} years</span></div>")

    monthly_revenue = app.number_input("Monthly Revenue (override if needed)", min_value=0, value=est_revenue, step=50_000)
    skip_quality = app.checkbox("Skip quality checks", value=False)

    if app.button("Generate Complete Dossier", type="primary"):
        from service_orchestrator import ServiceOrchestrator
        orch = ServiceOrchestrator()
        stage_text = app.text("Starting...")

        def progress_cb(stage, msg, pct):
            stage_text.value = f"[{pct:.0f}%] {stage}: {msg}"
        orch.on_progress(progress_cb)

        with app.spinner("Generating dossier... 30-60s"):
            results = orch.generate_dossier(
                business_type=biz_type, location=location, wilaya=wilaya,
                investment=investment, client_name=client_name,
                monthly_revenue=monthly_revenue, skip_quality=skip_quality,
            )

        if results.get("pdf_path"):
            app.success(f"PDF: {os.path.basename(results['pdf_path'])}")
            if os.path.exists(results["pdf_path"]):
                with open(results["pdf_path"], "rb") as f:
                    app.download_button("Download PDF", data=f.read(), file_name=os.path.basename(results["pdf_path"]), mime="application/pdf")

        aapi = results.get("aapi", {})
        if "total" in aapi:
            color = "#28a745" if aapi.get("percentage", 0) >= 60 else "#ffc107"
            app.html(f"<div style='padding:15px;border-radius:8px;border:2px solid {color};margin:10px 0;'><strong>AAPI:</strong> <span style='color:{color};font-size:1.2em;'>{aapi['total']}/1500 ({aapi.get('rating', '')})</span></div>")

        quality = results.get("quality", {})
        if quality:
            app.markdown("### Quality Report")
            for gen, report in quality.items():
                gc = "#28a745" if report.grade in ("A", "B") else "#ffc107" if report.grade == "C" else "#dc3545"
                app.html(f"<div style='padding:5px 10px;margin:3px 0;background:#f8f9fa;border-radius:4px;'><strong>{gen}</strong>: <span style='color:{gc};'>{report.overall_score:.0%} ({report.grade})</span></div>")

        app.html(f"<div style='padding:10px;margin-top:10px;color:#666;'>Time: {results.get('metadata', {}).get('elapsed_seconds', 0):.1f}s</div>")


def _save_output(doc_type: str, name: str, content: str):
    """Save generated content to output directory."""
    output_dir = Path(__file__).parent.parent / "generated_output"
    output_dir.mkdir(exist_ok=True)
    filename = f"{doc_type}_{name.replace(' ', '_')}.md"
    (output_dir / filename).write_text(content, encoding="utf-8")
    app.toast(f"Saved: {filename}", type="success")


def bmc_page():
    """Business Model Canvas — Osterwalder 9-block canvas."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">Business Model Canvas</h2>
        <p style="margin:3px 0 0;color:#888;">نموذج أعمال — Osterwalder 9-block</p>
    </div>
    """)
    btypes = list(BMC_TEMPLATES.keys())
    biz_type = app.selectbox("Business Type", options=btypes, index=0)
    btn = app.button("Generate BMC", primary=True)

    if btn:
        gen = BMCGenerator()
        bmc = gen.generate(biz_type)
        html = gen.to_html(bmc)
        app.html(html)

        md = gen.to_markdown(bmc)
        if app.button("Save HTML + Markdown"):
            out = Path(__file__).parent.parent / "generated_output"
            out.mkdir(exist_ok=True)
            (out / f"bmc_{biz_type}.html").write_text(html, encoding="utf-8")
            (out / f"bmc_{biz_type}.md").write_text(md, encoding="utf-8")
            app.toast(f"Saved: bmc_{biz_type}.html + .md", type="success")


def nesda_calc_page():
    """NESDA Financing Calculator — triangular, mixed, self models."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">Calculateur NESDA</h2>
        <p style="margin:3px 0 0;color:#888;">حساب تمويل NESDA — النموذج الثلاثي والمختلط</p>
    </div>
    """)

    col1, col2 = app.columns(2)
    with col1:
        total_cost = app.number_input("التكلفة الإجمالية (DZD)", min_value=500_000, max_value=50_000_000, value=3_000_000, step=100_000)
        model_key = app.selectbox("نموذج التمويل", options=list(NESDA_MODELS.keys()), index=0)
    with col2:
        profile = app.selectbox("الوضع", options=["unemployed", "employed"], index=0)
        monthly_rev = app.number_input("الإيرادات الشهرية (DZD)", min_value=50_000, max_value=10_000_000, value=500_000, step=50_000)

    btn = app.button("Calculate NESDA Financing", primary=True)

    if btn:
        result = calculate_nesda_financing(
            total_cost=total_cost,
            model=model_key,
            profile=profile,
            monthly_revenue=monthly_rev,
        )

        # Summary cards
        col1, col2, col3 = app.columns(3)
        with col1:
            app.html(f"""<div style="text-align:center;padding:20px;background:#e3f2fd;border-radius:8px;">
                <div style="font-size:0.85em;color:#666;">المساهمة الشخصية</div>
                <div style="font-size:1.5em;font-weight:bold;color:#1565c0;">{result.personal_amount:,} دج</div>
                <div style="color:#888;">{result.personal_pct*100:.0f}%</div>
            </div>""")
        with col2:
            app.html(f"""<div style="text-align:center;padding:20px;background:#e8f5e9;border-radius:8px;">
                <div style="font-size:0.85em;color:#666;">مساهمة NESDA (PNR)</div>
                <div style="font-size:1.5em;font-weight:bold;color:#2e7d32;">{result.nesda_grant:,} دج</div>
                <div style="color:#888;">{result.nesda_pct*100:.0f}%</div>
            </div>""")
        with col3:
            app.html(f"""<div style="text-align:center;padding:20px;background:#fff3e0;border-radius:8px;">
                <div style="font-size:0.85em;color:#666;">القرض البنكي</div>
                <div style="font-size:1.5em;font-weight:bold;color:#e65100;">{result.bank_loan:,} دج</div>
                <div style="color:#888;">{result.bank_pct*100:.0f}%</div>
            </div>""")

        # Key metrics
        app.markdown("### مؤشرات الجدوى")
        col1, col2, col3, col4 = app.columns(4)
        with col1:
            app.metric("القسط الشهري", f"{result.monthly_payment:,.0f} دج")
        with col2:
            app.metric("الربح الشهري", f"{result.monthly_profit:,} دج")
        with col3:
            app.metric("مدة الاسترداد", f"{result.payback_months} شهر")
        with col4:
            app.metric("ROI السنوي", f"{result.roi_annual:.1f}%")

        # Amortization schedule
        app.markdown("### جدول السداد")
        schedule_data = []
        for s in result.schedule:
            schedule_data.append({
                "السنة": s["year"],
                "الرصيد البداية": f"{s['balance_start']:,}",
                "القسط": f"{s['payment']:,}",
                "الفائدة": f"{s['interest']:,}",
                "Principal": f"{s['principal']:,}",
                "الرصيد النهاية": f"{s['balance_end']:,}",
            })
        app.table(schedule_data)

        # Full report
        report = format_nesda_report(result)
        if app.button("Save Full Report"):
            out = Path(__file__).parent.parent / "generated_output"
            out.mkdir(exist_ok=True)
            (out / f"nesda_calc_{model_key}.md").write_text(report, encoding="utf-8")
            app.toast(f"Saved: nesda_calc_{model_key}.md", type="success")


def nesda_catalog_page():
    """NESDA Activity Catalog — searchable database of 47 eligible activities."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">NESDA Activity Catalog</h2>
        <p style="margin:3px 0 0;color:#888;">قائمة الأنشطة المدعومة من NESDA — 47 نشاط عبر 5 قطاعات</p>
    </div>
    """)

    # Filters
    col1, col2, col3 = app.columns(3)
    with col1:
        query = app.text_input("Search (FR/AR)", placeholder="boulangerie, مخبزة...")
    with col2:
        sector_filter = app.selectbox("Sector", options=["all"] + list(SECTORS.keys()), index=0)
    with col3:
        budget = app.number_input("Budget (DZD)", min_value=100_000, max_value=50_000_000, value=3_000_000, step=500_000)

    # Sector overview
    app.markdown("### Sector Overview")
    cols = app.columns(len(SECTORS))
    for i, (key, s) in enumerate(SECTORS.items()):
        stats = get_sector_stats(key)
        with cols[i]:
            app.html(f"""<div style="text-align:center;padding:12px;background:#f8f9fa;border-radius:8px;border-top:3px solid {s['color']};">
                <div style="font-weight:bold;font-size:0.9em;">{s['ar']}</div>
                <div style="font-size:0.75em;color:#888;">{s['fr']}</div>
                <div style="font-size:1.3em;font-weight:bold;color:{s['color']};margin:5px 0;">{stats['count']}</div>
                <div style="font-size:0.75em;color:#666;">avg {stats['avg_investment']:,} DZD</div>
                <div style="font-size:0.75em;color:#666;">margin {stats['avg_margin']:.0f}%</div>
            </div>""")

    # Search results
    if query or sector_filter != "all":
        results = search_catalog(query, sector_filter if sector_filter != "all" else None)
    else:
        results = list(CATALOG.values())

    app.markdown(f"### Results ({len(results)} activities)")
    for a in results:
        color = "#28a745" if a.profit_margin_pct >= 40 else "#ffc107" if a.profit_margin_pct >= 25 else "#dc3545"
        app.html(f"""<div style="padding:12px;margin:6px 0;background:white;border-radius:8px;border-left:4px solid {SECTORS.get(a.sector, {}).get('color', '#666')};box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <strong style="font-size:0.95em;">{a.name_fr}</strong>
                    <span style="color:#888;font-size:0.85em;margin-left:8px;">{a.name_ar}</span>
                </div>
                <div style="text-align:right;">
                    <span style="background:{SECTORS.get(a.sector, {}).get('color', '#666')};color:white;padding:2px 8px;border-radius:4px;font-size:0.75em;">{a.sector}</span>
                    <span style="background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:4px;font-size:0.75em;margin-left:4px;">priority {a.aapi_priority}</span>
                </div>
            </div>
            <div style="margin-top:6px;font-size:0.82em;color:#555;">
                💰 {a.investment_min:,} - {a.investment_max:,} DZD (ideal: {a.investment_ideal:,})
                &nbsp;|&nbsp; 📈 margin: <span style="color:{color};font-weight:bold;">{a.profit_margin_pct:.0f}%</span>
                &nbsp;|&nbsp; 👥 {a.staff_range[0]}-{a.staff_range[1]} staff
                &nbsp;|&nbsp; ⏱️ {a.time_to_launch}
            </div>
            {f'<div style="margin-top:4px;font-size:0.8em;color:#888;">📝 {a.notes_fr}</div>' if a.notes_fr else ''}
        </div>""")

    # Recommendations
    if app.button("Get Recommendations for My Budget", primary=True):
        recs = recommend_activity(budget)
        app.markdown(f"### Top 5 for {budget:,} DZD")
        for i, a in enumerate(recs, 1):
            app.html(f"""<div style="padding:10px;margin:4px 0;background:#e8f5e9;border-radius:6px;">
                <strong>{i}. {a.name_fr}</strong> ({a.name_ar}) — {a.investment_ideal:,} DZD, margin {a.profit_margin_pct:.0f}%, priority {a.aapi_priority}
            </div>""")


def linkedin_page():
    """LinkedIn Content Automation — auto-generate posts from generator outputs."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">LinkedIn Content Generator</h2>
        <p style="margin:3px 0 0;color:#888;">إنشاء محتوى لينكدإن تلقائي — عربي / فرنسي / إنجليزي</p>
    </div>
    """)

    gen = LinkedInContentGenerator()

    post_type = app.selectbox("Post Type", options=["case_study", "data_insight", "myth_busting", "listicle", "arabic_hook", "generator_showcase"])
    sector = app.selectbox("Market Sector", options=list(MARKET_DATA.keys()) if 'MARKET_DATA' in dir() else ["retail", "food", "digital", "construction", "services"])

    if post_type == "case_study":
        biz = app.text_input("Business Type", value="quincaillerie")
        inv = app.number_input("Investment (DZD)", value=3_000_000)
        wil = app.text_input("Wilaya", value="El Bayadh")
        if app.button("Generate Post"):
            post = gen.generate_from_feasibility({"business_type": biz, "investment": inv, "wilaya": wil})
            for lang, content in post.items():
                app.html(f"""<div style="padding:15px;margin:8px 0;background:white;border-radius:8px;border-left:3px solid #0A1628;">
                    <div style="font-weight:bold;color:#0A1628;margin-bottom:5px;">{lang.upper()}</div>
                    <pre style="white-space:pre-wrap;font-size:0.9em;">{content}</pre>
                </div>""")
    elif post_type == "data_insight":
        if app.button("Generate Insight"):
            for lang in ["ar", "fr", "en"]:
                post = gen.generate_market_insight(sector, lang)
                app.html(f"""<div style="padding:15px;margin:8px 0;background:white;border-radius:8px;border-left:3px solid #D4AF37;">
                    <div style="font-weight:bold;color:#D4AF37;margin-bottom:5px;">{lang.upper()}</div>
                    <pre style="white-space:pre-wrap;font-size:0.9em;">{post}</pre>
                </div>""")
    elif post_type == "generator_showcase":
        tool = app.text_input("Tool Name", value="NESDA Dossier Generator")
        desc = app.text_input("Description", value="Generate NESDA-compatible feasibility studies")
        result = app.text_input("Result", value="Complete 9-part dossier in 30 seconds")
        if app.button("Generate Post"):
            post = gen.generate_tool_showcase(tool, desc, result)
            for lang, content in post.items():
                app.html(f"""<div style="padding:15px;margin:8px 0;background:white;border-radius:8px;border-left:3px solid #28a745;">
                    <div style="font-weight:bold;color:#28a745;margin-bottom:5px;">{lang.upper()}</div>
                    <pre style="white-space:pre-wrap;font-size:0.9em;">{content}</pre>
                </div>""")
    else:
        if app.button("Generate Post"):
            post = gen.generate_market_insight(sector, "ar")
            app.html(f"""<div style="padding:15px;margin:8px 0;background:white;border-radius:8px;">
                <pre style="white-space:pre-wrap;font-size:0.9em;">{post}</pre>
            </div>""")

    # Content Calendar
    app.markdown("### 30-Day Content Calendar")
    if app.button("Generate Calendar"):
        calendar = gen.generate_content_calendar()
        cal_data = [{"Date": c["date"], "Day": c["day"], "Topic": c["topic"], "Time": c["time"]} for c in calendar[:15]]
        app.table(cal_data)
        gen.save_calendar(calendar)
        app.toast("Calendar saved to generated_output/", type="success")


def batch_page():
    """Batch Processing — client management, pipeline, referrals, revenue."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">Batch Clients</h2>
        <p style="margin:3px 0 0;color:#888;">إدارة العملاء والدفعات — Pipeline, CRM, الإيرادات</p>
    </div>
    """)

    manager = BatchManager()
    summary = manager.get_batch_summary()

    # ── Pipeline Dashboard ──
    app.markdown("### Pipeline Dashboard")
    status_cols = app.columns(5)
    statuses = [
        ("new", "New", "#007bff"),
        ("quoted", "Quoted", "#ffc107"),
        ("in_progress", "In Progress", "#17a2b8"),
        ("delivered", "Delivered", "#28a745"),
        ("paid", "Paid", "#6f42c1"),
    ]
    for i, (s, label, color) in enumerate(statuses):
        with status_cols[i]:
            count = summary["by_status"].get(s, 0)
            app.html(f"""<div style="text-align:center;padding:12px;background:{color}10;border-radius:8px;border:2px solid {color};">
                <div style="font-size:1.5em;font-weight:bold;color:{color};">{count}</div>
                <div style="font-size:0.85em;color:#666;">{label}</div>
            </div>""")

    col1, col2, col3 = app.columns(3)
    with col1:
        app.metric("Total Clients", summary["total_clients"])
    with col2:
        app.metric("Active Pipeline", summary["active_pipeline"])
    with col3:
        app.metric("Total Value", f"{summary['total_investment_value']:,} DZD")

    # ── Add New Client ──
    app.markdown("### Add New Client")
    with app.form("new_client"):
        col1, col2 = app.columns(2)
        with col1:
            name = app.text_input("Client Name")
            phone = app.text_input("Phone (+213)")
            email = app.text_input("Email")
        with col2:
            wilaya = app.selectbox("Wilaya", options=[""] + ["Adrar", "Chlef", "Laghouat", "Oum El Bouaghi", "Batna", "Béjaïa", "Biskra", "Béchar", "Blida", "Bouira", "Tamanrasset", "Tébessa", "Tlemcen", "Tiaret", "Tizi Ouzou", "Alger", "Djelfa", "Jijel", "Sétif", "Saïda", "Skikda", "Sidi Bel Abbès", "Annaba", "Guelma", "Constantine", "Médéa", "Mostaganem", "M'Sila", "Mascara", "Ouargla", "Oran", "El Bayadh", "Illizi", "Bordj Bou Arréridj", "Boumerdès", "El Tarf", "Tindouf", "Tissemsilt", "El Oued", "Khenchela", "Souk Ahras", "Tipaza", "Mila", "Aïn Defla", "Naâma", "Aïn Témouchent", "Ghardaïa", "Relizane"], index=0)
            biz = app.selectbox("Business Type", options=[""] + list(CATALOG.keys()), index=0)
            inv = app.number_input("Investment (DZD)", value=0, step=100_000)
            svc = app.selectbox("Service", options=["feasibility", "business_plan", "market_research", "financials", "marketing", "full_dossier"])
            notes = app.text_area("Notes")

        submitted = app.form_submit_button("Add Client")
        if submitted and name and phone:
            client = manager.add_client(name, phone, wilaya, biz, inv, svc, email, notes)
            app.toast(f"Added: {client.name} ({client.id})", type="success")

    # ── Client List (filterable) ──
    app.markdown("### Client List")
    clients = list(manager.clients.values())
    if clients:
        col1, col2 = app.columns(2)
        with col1:
            filter_status = app.selectbox("Filter by Status", options=["all"] + [s[0] for s in statuses], index=0)
        with col2:
            all_wilayas = sorted(set(c.wilaya for c in clients if c.wilaya))
            filter_wilaya = app.selectbox("Filter by Wilaya", options=["all"] + all_wilayas, index=0)

        filtered = clients
        if filter_status != "all":
            filtered = [c for c in filtered if c.status == filter_status]
        if filter_wilaya != "all":
            filtered = [c for c in filtered if c.wilaya == filter_wilaya]

        app.html(f"<p style='color:#888;font-size:0.9em;'>Showing {len(filtered)} of {len(clients)} clients</p>")

        client_data = []
        for c in filtered:
            client_data.append({
                "ID": c.id,
                "Name": c.name,
                "Phone": c.phone,
                "Wilaya": c.wilaya,
                "Business": c.business_type,
                "Service": c.service,
                "Status": c.status,
                "Investment": f"{c.investment:,}" if c.investment else "-",
                "Created": c.created_at[:10] if c.created_at else "-",
            })
        app.table(client_data)

        # ── Status Update ──
        app.markdown("### Update Client Status")
        client_ids = [c.id for c in clients]
        sel_client = app.selectbox("Select Client", options=client_ids, index=0)
        new_status = app.selectbox("New Status", options=["new", "quoted", "in_progress", "delivered", "paid"], index=0)
        status_notes = app.text_input("Notes (optional)")
        if app.button("Update Status"):
            manager.update_status(sel_client, new_status, notes=status_notes)
            app.toast(f"Updated {sel_client} → {new_status}", type="success")

        # ── Referral Network ──
        referrals = manager.get_referral_network()
        if referrals:
            app.markdown("### Referral Network")
            for wilaya_name, refs in referrals.items():
                if refs:
                    app.html(f"""<div style="padding:10px;margin:5px 0;background:#e8f5e9;border-radius:6px;">
                        <strong>{wilaya_name}:</strong> {len(refs)} referral connections
                    </div>""")
    else:
        app.info("No clients yet. Add your first client above.")

    # ── Revenue Summary ──
    app.markdown("### Revenue Summary")
    revenue = manager.get_revenue_report()
    if revenue.get("total_revenue", 0) > 0:
        col1, col2 = app.columns(2)
        with col1:
            app.html(f"""<div style="text-align:center;padding:20px;background:#e8f5e9;border-radius:8px;">
                <div style="font-size:0.85em;color:#666;">Total Revenue</div>
                <div style="font-size:1.5em;font-weight:bold;color:#2e7d32;">{revenue['total_revenue']:,} DZD</div>
            </div>""")
        with col2:
            app.html(f"""<div style="text-align:center;padding:20px;background:#e3f2fd;border-radius:8px;">
                <div style="font-size:0.85em;color:#666;">Transactions</div>
                <div style="font-size:1.5em;font-weight:bold;color:#1565c0;">{revenue.get('transaction_count', 0)}</div>
            </div>""")

        if revenue.get("by_service"):
            app.markdown("#### By Service")
            svc_data = [{"Service": s, "Revenue": f"{r:,} DZD"} for s, r in revenue["by_service"].items()]
            app.table(svc_data)

        if revenue.get("by_month"):
            app.markdown("#### By Month")
            month_data = [{"Month": m, "Revenue": f"{r:,} DZD"} for m, r in sorted(revenue["by_month"].items())]
            app.table(month_data)
    else:
        app.html("""<div style="text-align:center;padding:20px;background:#f8f9fa;border-radius:8px;color:#888;">
            No revenue recorded yet. Use the Pricing page to generate quotes and track payments.
        </div>""")


def eligibility_page():
    """NESDA Eligibility Checker — verify project eligibility for financing."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">NESDA Eligibility Checker</h2>
        <p style="margin:3px 0 0;color:#888;">تحقق من أهليتك لتمويل NESDA</p>
    </div>
    """)

    col1, col2 = app.columns(2)
    with col1:
        age = app.number_input("العمر / Âge", min_value=18, max_value=65, value=28)
        activity = app.selectbox("النشاط / Activité", options=list(CATALOG.keys()), index=0)
    with col2:
        investment = app.number_input("المبلغ (DZD)", min_value=100_000, max_value=50_000_000, value=3_000_000, step=100_000)
        profile = app.selectbox("الوضع / Profil", options=["unemployed", "employed", "student"], index=0)

    # Document checklist
    app.markdown("### المستندات / Documents")
    col1, col2 = app.columns(2)
    with col1:
        has_cde = app.checkbox("شهادة CDE")
        has_anem = app.checkbox("تسجيل ANEM")
    with col2:
        has_bp = app.checkbox("خطة العمل")
        has_feas = app.checkbox("دراسة الجدوى")

    if app.button("Check Eligibility", primary=True):
        result = check_eligibility(
            age=age, activity_key=activity, investment=investment,
            wilaya="El Bayadh", profile=profile,
            has_cde_training=has_cde, has_anem_registration=has_anem,
            has_business_plan=has_bp, has_feasibility_study=has_feas,
        )

        # Score display
        color = "#28a745" if result.eligible else "#dc3545"
        app.html(f"""<div style="text-align:center;padding:25px;background:{color}10;border-radius:12px;border:2px solid {color};margin:15px 0;">
            <div style="font-size:3em;font-weight:bold;color:{color};">{result.score}/{result.max_score}</div>
            <div style="font-size:1.2em;color:{color};">{'مؤهل ✓' if result.eligible else 'غير مؤهل ✗'}</div>
        </div>""")

        # Individual checks
        app.markdown("### نتائج الفحص")
        for c in result.checks:
            icon = "✅" if c["status"] == "pass" else "⚠️" if c["status"] == "warning" else "❌" if c["status"] == "fail" else "ℹ️"
            app.html(f"""<div style="padding:8px 12px;margin:4px 0;background:white;border-radius:6px;border-left:3px solid {'#28a745' if c['status']=='pass' else '#ffc107' if c['status']=='warning' else '#dc3545'};">
                <strong>{icon} {c['name']}</strong>: {c['detail']}
            </div>""")

        # Financing estimate
        app.markdown("### هيكل التمويل")
        fe = result.financing_estimate
        col1, col2, col3 = app.columns(3)
        with col1:
            app.html(f"""<div style="text-align:center;padding:15px;background:#e3f2fd;border-radius:8px;">
                <div style="font-size:0.85em;color:#666;">المساهمة الشخصية</div>
                <div style="font-size:1.3em;font-weight:bold;color:#1565c0;">{fe['personal']:,} دج</div>
            </div>""")
        with col2:
            app.html(f"""<div style="text-align:center;padding:15px;background:#e8f5e9;border-radius:8px;">
                <div style="font-size:0.85em;color:#666;">مساهمة NESDA</div>
                <div style="font-size:1.3em;font-weight:bold;color:#2e7d32;">{fe['nesda_grant']:,} دج</div>
            </div>""")
        with col3:
            app.html(f"""<div style="text-align:center;padding:15px;background:#fff3e0;border-radius:8px;">
                <div style="font-size:0.85em;color:#666;">القرض البنكي</div>
                <div style="font-size:1.3em;font-weight:bold;color:#e65100;">{fe['bank_loan']:,} دج</div>
            </div>""")

        # Next steps
        app.markdown("### الخطوات التالية")
        for step in result.next_steps:
            app.html(f"<div style='padding:6px 12px;margin:3px 0;background:#f8f9fa;border-radius:4px;'>{step}</div>")


def pricing_page():
    """DSC Pricing Calculator — instant quotes with WhatsApp."""
    _sidebar()
    app.html("""
    <div style="padding:15px 0;border-bottom:1px solid #ddd;margin-bottom:15px;">
        <h2 style="margin:0;color:#0A1628;">Pricing Calculator</h2>
        <p style="margin:3px 0 0;color:#888;">حاسبة الأسعار — عروض فورية مع واتساب</p>
    </div>
    """)

    # Package presets
    app.markdown("### Quick Packages")
    pkg_cols = app.columns(4)
    for i, (key, pkg) in enumerate(PACKAGES.items()):
        with pkg_cols[i]:
            if app.button(f"{pkg['name_ar']}\n{pkg['price_label']}", key=f"pkg_{key}"):
                app.session_state.selected_services = pkg["services"]
                app.session_state.pkg_discount = pkg["discount"]

    app.markdown("### Select Services")
    selected = []
    for key, svc in PRICING_SERVICES.items():
        if app.checkbox(f"{svc['name_fr']} — {svc['name_ar']} ({svc['price_min']:,}-{svc['price_max']:,} DZD)", key=f"svc_{key}"):
            selected.append(key)

    discount = app.number_input("Discount %", min_value=0, max_value=50, value=0)
    client_name = app.text_input("Client Name")
    client_phone = app.text_input("Phone (+213)")

    if app.button("Generate Quote", primary=True) and selected:
        quote = calculate_quote(selected, discount_pct=discount, client_name=client_name, client_phone=client_phone)

        # Summary
        app.markdown("### Quote Summary")
        for s in quote.services:
            app.html(f"""<div style="padding:8px 12px;margin:4px 0;background:white;border-radius:6px;">
                <strong>{s['name_fr']}</strong> ({s['name_ar']}) — <strong>{s['price']:,} دج</strong>
                <span style="color:#888;font-size:0.85em;"> | {s['delivery_days']} أيام</span>
            </div>""")

        # Total
        color = "#D4AF37"
        app.html(f"""<div style="text-align:center;padding:20px;background:{color}10;border-radius:12px;border:2px solid {color};margin:15px 0;">
            <div style="font-size:1.5em;font-weight:bold;color:{color};">الإجمالي: {quote.total:,} دج</div>
            <div style="color:#666;">العربون: {quote.deposit_amount:,} دج | المتبقي: {quote.balance:,} دج</div>
            <div style="color:#888;font-size:0.9em;margin-top:5px;">التسليم: {quote.estimated_delivery}</div>
        </div>""")

        # WhatsApp
        if client_phone:
            app.html(f"""<div style="padding:15px;background:#25D36610;border-radius:8px;border:2px solid #25D366;margin:10px 0;">
                <div style="font-weight:bold;color:#25D366;">📱 WhatsApp Quote Ready</div>
                <div style="font-size:0.85em;color:#555;margin-top:5px;white-space:pre-wrap;">{quote.whatsapp_message[:200]}...</div>
            </div>""")

        # Save
        if app.button("Save Quote"):
            out = Path(__file__).parent.parent / "generated_output"
            out.mkdir(exist_ok=True)
            from pricing_calculator import format_quote_markdown
            md = format_quote_markdown(quote, client_name)
            (out / f"quote_{client_name.replace(' ', '_') or 'client'}.md").write_text(md, encoding="utf-8")
            app.toast("Quote saved!", type="success")


app.navigation([
    vl.Page(home_page, title="Home", icon="house"),
    vl.Page(dossier_page, title="Complete Dossier", icon="package"),
    vl.Page(feasibility_page, title="Feasibility", icon="file-text"),
    vl.Page(business_plan_page, title="Business Plan", icon="briefcase"),
    vl.Page(market_research_page, title="Market Research", icon="bar-chart"),
    vl.Page(financial_projections_page, title="Financials", icon="trending-up"),
    vl.Page(bmc_page, title="BMC Canvas", icon="layout"),
    vl.Page(nesda_calc_page, title="NESDA Calc", icon="calculator"),
    vl.Page(nesda_catalog_page, title="NESDA Catalog", icon="search"),
    vl.Page(eligibility_page, title="Eligibility", icon="check-circle"),
    vl.Page(pricing_page, title="Pricing", icon="dollar-sign"),
    vl.Page(marketing_plan_page, title="Marketing Plan", icon="megaphone"),
    vl.Page(social_media_page, title="Social Media", icon="share-2"),
    vl.Page(g12_page, title="G12 IFU", icon="file-text"),
    vl.Page(g50_page, title="G50 Monthly", icon="file"),
    vl.Page(g4_page, title="G4 IBS", icon="briefcase"),
    vl.Page(g11_page, title="G11 BIC", icon="file-text"),
    vl.Page(g29_page, title="G29 IRG", icon="users"),
    vl.Page(g1_page, title="G1 GGR", icon="file"),
    vl.Page(g8_page, title="G8 Existence", icon="check-circle"),
    vl.Page(tax_declaration_page, title="Tax Guides", icon="book"),
    vl.Page(invoice_page, title="Invoice/Quote", icon="file"),
    vl.Page(cv_page, title="CV Generator", icon="user"),
    vl.Page(cover_letter_page, title="Cover Letter", icon="mail"),
    vl.Page(government_page, title="Gov Paperwork", icon="building"),
    vl.Page(calculators_page, title="Calculators", icon="calculator"),
    vl.Page(aapi_page, title="AAPI Scorer", icon="award"),
    vl.Page(linkedin_page, title="LinkedIn", icon="linkedin"),
    vl.Page(batch_page, title="Batch Process", icon="layers"),
])

if __name__ == "__main__":
    app.run()
