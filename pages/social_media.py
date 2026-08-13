import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _provider_select, _wilaya_select, _save_output
from feasibility_generator import BUSINESS_TEMPLATES
from social_media_generator import SocialMediaGenerator


def social_media_page():
    _sidebar()
    app.title("Social Media Content Generator")
    app.text("إنشاء محتوى احترافي للشبكات الاجتماعية")

    business_type = app.selectbox("Business Type", options=list(BUSINESS_TEMPLATES.keys()), index=0)
    template = BUSINESS_TEMPLATES[business_type.value]
    app.html(f"<h3 style='margin-bottom:2px;'>{template['name_ar']}</h3><p style='margin-top:0;color:#666;'>{template['name_en']}</p>")

    location = app.text_input("City / Location")
    wilaya = _wilaya_select()
    business_name = app.text_input("Business Name (Arabic)")
    provider = _provider_select()

    if app.button("Generate Social Media Content"):
        if not business_name.value:
            app.toast("Please enter a business name", variant="error")
            return
        app.toast("Generating social media content...", variant="info")
        try:
            gen = SocialMediaGenerator(provider=provider.value)
            result = gen.generate(business_type.value, business_name.value, location.value, wilaya.value)
            app.markdown("### Social Media Content")
            app.html(f"<div style='background:#f8f9fa;padding:15px;border-radius:8px;white-space:pre-wrap;font-family:serif;line-height:1.8;'>{result['content']}</div>")
            _save_output("social_media", business_name.value, result["content"])
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
