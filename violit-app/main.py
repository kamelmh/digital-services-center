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


def _save_output(doc_type: str, name: str, content: str):
    """Save generated content to output directory."""
    output_dir = Path(__file__).parent.parent / "generated_output"
    output_dir.mkdir(exist_ok=True)
    filename = f"{doc_type}_{name.replace(' ', '_')}.md"
    (output_dir / filename).write_text(content, encoding="utf-8")
    app.toast(f"Saved: {filename}", type="success")


app.navigation([
    vl.Page(home_page, title="Home", icon="house"),
    vl.Page(feasibility_page, title="Feasibility", icon="file-text"),
    vl.Page(business_plan_page, title="Business Plan", icon="briefcase"),
    vl.Page(market_research_page, title="Market Research", icon="bar-chart"),
    vl.Page(financial_projections_page, title="Financials", icon="trending-up"),
    vl.Page(marketing_plan_page, title="Marketing Plan", icon="megaphone"),
    vl.Page(social_media_page, title="Social Media", icon="share-2"),
    vl.Page(tax_declaration_page, title="Tax Helper", icon="receipt"),
    vl.Page(invoice_page, title="Invoice / Quote", icon="file-plus"),
    vl.Page(cv_page, title="CV Generator", icon="user"),
    vl.Page(cover_letter_page, title="Cover Letter", icon="mail"),
    vl.Page(government_page, title="Gov Paperwork", icon="building"),
])

if __name__ == "__main__":
    app.run()
