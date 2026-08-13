import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from government_paperwork_helper import GovernmentPaperworkHelper, PROCEDURES


def government_page():
    _sidebar()
    app.title("Government Paperwork Helper")
    app.text("مساعدة في الإجراءات الإدارية — Algeria")

    helper = GovernmentPaperworkHelper()

    doc_type = app.selectbox("Type of Procedure", list(PROCEDURES.keys()))

    with app.expander("📋 Procedure Details"):
        try:
            info = helper.get_procedure(doc_type.value)
            if info:
                app.text(str(info))
            else:
                app.info("Select a procedure type above")
        except Exception as e:
            app.info("Select a procedure type above")

    if app.button("📄 Download Checklist (PDF)", type="primary"):
        try:
            result = helper.generate_checklist(doc_type.value)
            _save_output("gov_paperwork", doc_type.value, str(result), f"{doc_type.value}_checklist.pdf")
            app.success("Generated!")
        except Exception as e:
            app.error(str(e))
