import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES
from market_research_generator import MarketResearchGenerator


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
            app.toast("Please enter a location", variant="error")
            return
        app.toast("Generating market research...", variant="info")
        try:
            gen = MarketResearchGenerator(provider=provider.value)
            result = gen.generate(business_type.value, location.value, wilaya.value, business_name.value)
            app.markdown("### Market Research Report")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("market_research", business_name.value or template["name_en"], result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
