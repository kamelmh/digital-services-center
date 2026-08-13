import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from linkedin_content import generate_post, POST_TEMPLATES


def linkedin_page():
    _sidebar()
    app.title("LinkedIn Auto-Content Generator")
    app.text("إنشاء محتوى LinkedIn تلقائي")

    with app.expander("1️⃣ Your Business"):
        c1,c2 = app.columns(2)
        niche = c1.text_input("Business Niche", placeholder="digital_services")
        audience = c2.text_input("Target Audience", placeholder="startups_algeria")

    with app.expander("2️⃣ Content Settings"):
        c1,c2 = app.columns(2)
        tone = c1.text_input("Tone of Voice", placeholder="professional")
        topic = c2.text_input("Post Topic", placeholder="NESDA financing guide")

    with app.expander("3️⃣ Templates"):
        if POST_TEMPLATES:
            template_key = app.selectbox("Template", list(POST_TEMPLATES.keys()))
        else:
            template_key = app.text_input("Template key", value="default")

    if app.button("🚀 Generate LinkedIn Post", type="primary"):
        if not niche.value or not topic.value:
            app.warning("Please fill Niche & Topic")
            return
        try:
            result = generate_post(niche.value, audience.value, tone.value, topic.value, template_key)
            app.markdown("### Generated Post")
            app.html(f"<div style='background:#f0f0f0;padding:15px;border-radius:8px;white-space:pre-wrap;'>{result}</div>")
            _save_output("linkedin", niche.value, result)
        except Exception as e:
            app.error(f"Error: {e}")

    with app.expander("📊 LinkedIn Best Practices"):
        app.markdown("""
        - Post 3-5 times per week
        - Best times: Tue-Thu, 8-10am / 12-2pm
        - Use carousel posts for 2x engagement
        - First 3 lines must hook
        - Hashtags: 3-5 relevant per post
        """)
