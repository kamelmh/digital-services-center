import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_instance import app, _sidebar, _provider_select, _save_output
from cv_generator import CVGenerator


def cv_page():
    _sidebar()
    app.title("CV Generator")
    app.text("إنشاء سيرة ذاتية احترافية PDF")

    full_name = app.text_input("Full Name")
    email = app.text_input("Email")
    phone = app.text_input("Phone Number")
    city = app.text_input("City")
    target_job = app.text_input("Target Job Title")
    experience = app.text_area("Work Experience (years, companies, roles)")
    skills = app.text_area("Skills (comma separated)")
    education = app.text_area("Education")
    languages = app.text_area("Languages (e.g., Arabic Native, English B2, French B1)")
    certifications = app.text_area("Certifications (optional)")
    template_style = app.selectbox("CV Style", options=["student", "employee", "freelancer", "cv_ar"], index=0)
    lang = app.selectbox("Language", options=["fr", "ar"], index=0)

    if app.button("Generate CV"):
        if not full_name.value or not target_job.value:
            app.toast("Please enter your name and target job", variant="error")
            return
        app.toast("Generating CV...", variant="info")
        try:
            from cv_generator import TEMPLATES
            template = TEMPLATES.get(template_style.value, TEMPLATES["student"])
            data = {
                "name": full_name.value or template["name"],
                "title": target_job.value or template["title"],
                "phone": phone.value,
                "email": email.value,
                "location": city.value,
                "summary": template["summary"],
                "experience": template["experience"],
                "education": template["education"],
                "skills": [s.strip() for s in skills.value.split(",") if s.strip()] if skills.value else template["skills"],
            }
            gen = CVGenerator()
            filepath = gen.generate(data, lang)
            app.markdown(f"### CV Generated")
            app.success(f"PDF saved: {filepath}")
            _save_output("cv", full_name.value, f"CV generated for {full_name.value} — {target_job.value}", f"{lang}.pdf")
        except Exception as e:
            app.toast(f"Error: {e}", variant="error")
