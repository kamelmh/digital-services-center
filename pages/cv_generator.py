import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from cv_generator import CVGenerator, TEMPLATES


def cv_generator_page():
    _sidebar()
    app.title("Professional CV Generator")
    app.text("إنشاء سيرة ذاتية احترافية")

    # Separate states for error and success — passed directly to widgets
    error_msg = app.session_state("", key="cv_error")
    success_msg = app.session_state("", key="cv_success")

    with app.expander("⭐ Template", expanded=True):
        c1, c2 = app.columns(2)
        template_key = c1.selectbox("Template", ["student", "employee", "freelancer", "cv_ar"], index=0)
        lang = c2.selectbox("Language", ["fr", "ar"], index=0)

    with app.expander("1️⃣ Personal Info"):
        c1, c2 = app.columns(2)
        full_name = c1.text_input("Full Name", "")
        title_en = c2.text_input("Title (EN)", "")
        title_ar = c1.text_input("Title (AR)", "")
        email = c2.text_input("Email", "")
        phone = c1.text_input("Phone", "")
        address = c2.text_input("Address", "")

    with app.expander("2️⃣ Objective"):
        objective_en = app.text_area("Objective (EN)", "", height=100)
        objective_ar = app.text_area("Objective (AR)", "", height=100)

    with app.expander("3️⃣ Skills"):
        skills_en = app.text_area("Skills (comma-separated)", "", height=100)

    with app.expander("4️⃣ Experience"):
        c1, c2 = app.columns(2)
        exp1_role = c1.text_input("Position 1", "")
        exp1_company = c2.text_input("Company 1", "")
        exp1_period = c1.text_input("Period 1", "")
        exp1_details = c2.text_area("Responsibilities 1", "", height=80)

    with app.expander("5️⃣ Education"):
        c1, c2 = app.columns(2)
        edu1_degree = c1.text_input("Degree 1", "")
        edu1_institution = c2.text_input("Institution 1", "")
        edu1_year = c1.text_input("Year 1", "")

    with app.expander("6️⃣ Languages & Certs"):
        languages = app.text_area("Languages", "", height=80)
        certifications = app.text_area("Certifications", "", height=80)

    def on_generate():
        name_val = full_name.value
        if not name_val:
            success_msg.value = ""
            error_msg.value = "Please enter your full name."
            return
        try:
            tpl = TEMPLATES.get(template_key.value, TEMPLATES["student"])
            data = {
                "name": name_val or tpl["name"],
                "title": title_en.value or title_ar.value or tpl["title"],
                "phone": phone.value,
                "email": email.value,
                "location": address.value,
                "summary": objective_en.value or objective_ar.value or tpl["summary"],
                "experience": [
                    {
                        "role": exp1_role.value,
                        "company": exp1_company.value,
                        "period": exp1_period.value,
                        "details": exp1_details.value,
                    }
                ] if exp1_role.value else tpl["experience"],
                "education": [
                    {
                        "degree": edu1_degree.value,
                        "institution": edu1_institution.value,
                        "period": edu1_year.value,
                    }
                ] if edu1_degree.value else tpl["education"],
                "skills": [s.strip() for s in skills_en.value.split(",") if s.strip()] if skills_en.value else tpl["skills"],
            }
            gen = CVGenerator()
            filepath = gen.generate(data, lang.value)
            error_msg.value = ""
            success_msg.value = f"CV saved: {filepath}"
            _save_output("cv", name_val, f"CV generated for {name_val}", f"{lang.value}.pdf")
        except Exception as e:
            success_msg.value = ""
            error_msg.value = f"Error: {e}"

    app.button("📄 Generate CV (PDF)", type="primary", use_container_width=True, on_click=on_generate)

    # Pass State objects directly — widgets resolve inside their builders where rendering_ctx is set
    app.error(error_msg)
    app.success(success_msg)
