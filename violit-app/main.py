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
])

if __name__ == "__main__":
    app.run()
