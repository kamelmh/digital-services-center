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
from training_data_collector import TrainingDataCollector

app = vl.App(title="Digital Services Center", theme="ocean")


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
    <div style="text-align:center;padding:30px 0;">
        <h1 style="color:#0A1628;margin-bottom:5px;">Digital Services Center</h1>
        <p style="color:#D4AF37;font-size:1.1em;margin-top:0;">مركز الخدمات الرقمية — الجزائر</p>
    </div>
    """)
    app.markdown("### Services")
    col1, col2 = app.columns(2)
    with col1:
        app.html("""<div style="padding:15px;background:#f8f9fa;border-radius:8px;border-left:3px solid #D4AF37;">
            <h4 style="margin:0 0 8px;">📄 Feasibility Studies</h4>
            <p style="margin:0;font-size:0.9em;color:#555;">دراسات جدوى أولية احترافية — 3k to 20k DZD</p>
        </div>""")
        app.html("""<div style="padding:15px;background:#f8f9fa;border-radius:8px;border-left:3px solid #28a745;margin-top:10px;">
            <h4 style="margin:0 0 8px;">📊 Market Research</h4>
            <p style="margin:0;font-size:0.9em;color:#555;">أبحاث سوق وتحليل المنافسين — 5k DZD</p>
        </div>""")
        app.html("""<div style="padding:15px;background:#f8f9fa;border-radius:8px;border-left:3px solid #6f42c1;margin-top:10px;">
            <h4 style="margin:0 0 8px;">📈 Financial Projections</h4>
            <p style="margin:0;font-size:0.9em;color:#555;">توقعات مالية وتحليل حساسية — 7k DZD</p>
        </div>""")
    with col2:
        app.html("""<div style="padding:15px;background:#f8f9fa;border-radius:8px;border-left:3px solid #0A1628;">
            <h4 style="margin:0 0 8px;">📋 Business Plans</h4>
            <p style="margin:0;font-size:0.9em;color:#555;">خطط عمل مفصلة — 15k to 25k DZD</p>
        </div>""")
        app.html("""<div style="padding:15px;background:#f8f9fa;border-radius:8px;border-left:3px solid #e83e8c;margin-top:10px;">
            <h4 style="margin:0 0 8px;">📣 Marketing Plans</h4>
            <p style="margin:0;font-size:0.9em;color:#555;">خطط تسويقية + محتوى — 5k to 10k DZD</p>
        </div>""")
        app.html("""<div style="padding:15px;background:#D4AF3710;border-radius:8px;border:2px solid #D4AF37;margin-top:10px;">
            <h4 style="margin:0 0 8px;color:#D4AF37;">⭐ Full Package</h4>
            <p style="margin:0;font-size:0.9em;color:#333;font-weight:bold;">30k DZD — All 5 services</p>
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


app.navigation([
    vl.Page(home_page, title="Home", icon="house"),
    vl.Page(dossier_page, title="Complete Dossier", icon="package"),
    vl.Page(feasibility_page, title="Feasibility", icon="file-text"),
    vl.Page(business_plan_page, title="Business Plan", icon="briefcase"),
    vl.Page(market_research_page, title="Market Research", icon="bar-chart"),
    vl.Page(financial_projections_page, title="Financials", icon="trending-up"),
    vl.Page(bmc_page, title="BMC Canvas", icon="layout"),
    vl.Page(nesda_calc_page, title="NESDA Calc", icon="calculator"),
    vl.Page(marketing_plan_page, title="Marketing Plan", icon="megaphone"),
    vl.Page(social_media_page, title="Social Media", icon="share-2"),
    vl.Page(tax_helper_page, title="Tax Helper", icon="calculator"),
    vl.Page(invoice_quote_page, title="Invoice/Quote", icon="file"),
    vl.Page(cv_page, title="CV Generator", icon="user"),
    vl.Page(cover_letter_page, title="Cover Letter", icon="mail"),
    vl.Page(gov_paperwork_page, title="Gov Paperwork", icon="building"),
    vl.Page(calculators_page, title="Calculators", icon="calculator"),
    vl.Page(aapi_page, title="AAPI Scorer", icon="award"),
])

if __name__ == "__main__":
    app.run()
