import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar
from nesda_eligibility import check_eligibility, CATALOG


def eligibility_page():
    _sidebar()
    app.title("NESDA Eligibility Checker")
    app.text("التحقق من أهلية NESDA")

    app.html("""<div style="background:#f8f9fa;padding:12px;border-radius:8px;border-left:4px solid #0A1628;margin-bottom:15px;">
        <strong>Check your eligibility:</strong> Answer the questions below to see if you qualify for NESDA subsidized financing.
    </div>""")

    with app.expander("1️⃣ Basic Information", expanded=True):
        c1,c2 = app.columns(2)
        name = c1.text_input("Full Name")
        age = c2.number_input("Age", min_value=18, max_value=65, value=30)
        wilaya = c1.selectbox("Wilaya", ["Adrar","Chlef","Laghouat","Alger","Oran","Constantine","Batna","Blida","Setif","Tizi Ouzou"], index=0)
        has_nif = app.checkbox("I have a NIF")

    with app.expander("2️⃣ Project Details"):
        c1,c2 = app.columns(2)
        project_type = c1.selectbox("Project Type", list(CATALOG.keys()) if CATALOG else ["Digital Services","Manufacturing","Agriculture","Retail","Education"])
        investment = c2.number_input("Planned Investment (DZD)", min_value=0, value=1000000, step=100000)
        has_business_plan = app.checkbox("I have a business plan")

    with app.expander("3️⃣ Financial Readiness"):
        c1,c2 = app.columns(2)
        own_funds = c1.number_input("Own Funds Available (DZD)", 0, 5000000, 200000, 10000)
        credit_history = c1.selectbox("Credit History", ["Clean","Minor issues","No history"])

    with app.expander("4️⃣ NESDA-Specific"):
        c1,c2 = app.columns(2)
        is_first_project = c1.checkbox("This is my first business project")
        is_unemployed = c2.checkbox("I am currently unemployed")
        is_woman = c1.checkbox("I am a woman entrepreneur")
        is_youth = c2.checkbox("I am under 35")

    if app.button("🔍 Check Eligibility", type="primary"):
        answers = {
            "name":name.value,"age":age.value,"wilaya":wilaya.value,"has_nif":has_nif,
            "project_type":project_type.value,"investment":investment,"has_business_plan":has_business_plan,
            "own_funds":own_funds,"credit_history":credit_history,"is_first_project":is_first_project,
            "is_unemployed":is_unemployed,"is_woman":is_woman,"is_youth":is_youth,
        }
        try:
            result = check_eligibility(answers) if callable(check_eligibility) else {"eligible": False, "score": 0}
            c1,c2,c3 = app.columns(3)
            c1.metric("Score", f"{result.get('score', 0)}/{result.get('max_score', 1500)}")
            c2.metric("Status", "ELIGIBLE" if result.get('eligible', False) else "NOT ELIGIBLE")
            c3.metric("Percentage", f"{result.get('percentage', 0):.1f}%")
        except Exception as e:
            app.error(f"Error: {e}")
