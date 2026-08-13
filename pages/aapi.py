import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from aapi_optimizer import AAAPIOptimizer, AAPI_CRITERIA


def aapi_page():
    _sidebar()
    app.title("AAPI Scorer — Auto-Entrepreneur Eligibility")
    app.text("Pointage AAPI /1500 — Eligibilite auto-entrepreneur")

    app.html("""<div style="background:#fff3cd;padding:12px;border-radius:8px;border-left:4px solid #ffc107;margin-bottom:15px;">
        <strong>AAPI Scoring:</strong> Score >= 800/1500 = Eligible for Badik & 3asri funding. Score >= 1100 = Strong candidacy.
    </div>""")

    # Separate states for error and each success metric
    error_msg = app.session_state("", key="aapi_error")
    total_score = app.session_state(0, key="aapi_total")
    status = app.session_state("", key="aapi_status")
    pct_score = app.session_state(0.0, key="aapi_pct")
    rating = app.session_state("", key="aapi_rating")

    with app.expander("📋 Enter AAPI Criteria", expanded=True):
        inputs = {}
        for key, criteria in AAPI_CRITERIA.items():
            if isinstance(criteria, dict):
                max_val = criteria.get("max_score", 100)
                label = criteria.get("name_fr", key)
                if max_val <= 70:
                    inputs[key] = app.checkbox(label, False, key=f"a_{key}")
                else:
                    inputs[key] = app.number_input(label, 0, max_val, 0, key=f"a_{key}")

    def on_score():
        try:
            optimizer = AAAPIOptimizer()
            params = {
                "activity_priority": 3,
                "investment_amount": inputs.get("investment_amount", 0).value * 1_000_000 if hasattr(inputs.get("investment_amount", 0), "value") else 0,
                "employees": inputs.get("employment", 0).value if hasattr(inputs.get("employment", 0), "value") else 0,
                "equity_ratio": inputs.get("equity_contribution", 30).value / 100 if hasattr(inputs.get("equity_contribution", 30), "value") else 0.3,
                "local_integration": inputs.get("local_content", 0).value if hasattr(inputs.get("local_content", 0), "value") else 0,
                "cdd_ratio": 0.1,
                "has_extension": bool(inputs.get("investment_extension", False).value if hasattr(inputs.get("investment_extension", False), "value") else False),
                "export_ratio": inputs.get("export_diversification", 0).value if hasattr(inputs.get("export_diversification", 0), "value") else 0,
            }
            score = optimizer.score_project(params)
            error_msg.value = ""
            total_score.value = score.total
            status.value = "ELIGIBLE" if score.total >= 800 else "NOT ELIGIBLE"
            pct_score.value = score.percentage
            rating.value = score.rating
        except Exception as e:
            error_msg.value = f"Error: {e}"

    app.button("📊 Calculate AAPI Score", type="primary", on_click=on_score)

    # Pass State objects directly — widgets resolve inside their builders
    app.error(error_msg)

    c1, c2, c3 = app.columns(3)
    c1.metric("Total", total_score)
    c2.metric("Status", status)
    c3.metric("Score %", pct_score)
    app.markdown(rating)
