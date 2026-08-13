import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar


def social_engagement_page():
    _sidebar()
    app.title("Social Media Engagement Manager")
    app.text("إدارة التفاعل — Social Media")

    with app.expander("💬 Comment Templates"):
        app.code("Thank you for your interest! DM us for details.", language=None)
        app.code("Great question! Here's what you need to know...", language=None)
        app.code("We'd love to help! Contact us at kamelmahi71@gmail.com", language=None)

    with app.expander("📊 Engagement Metrics"):
        c1,c2,c3 = app.columns(3)
        comments = c1.number_input("Comments", 0, 10000, 50, 10)
        replies = c2.number_input("Replies", 0, 10000, 20, 10)
        shares = c3.number_input("Shares", 0, 10000, 10, 10)
        if app.button("📊 Analyze Engagement", key="eng_analysis"):
            total = comments + replies + shares
            response_rate = (replies / comments * 100) if comments > 0 else 0
            c1,c2,c3 = app.columns(3)
            c1.metric("Total Interactions", f"{total:,}")
            c2.metric("Response Rate", f"{response_rate:.1f}%")
            c3.metric("Shares/Comments", f"{shares/comments:.2f}" if comments > 0 else "N/A")

    with app.expander("🔔 Notification Settings"):
        app.checkbox("Email notifications for new comments", value=True)
        app.checkbox("Desktop notifications", value=False)
        app.checkbox("Daily engagement summary", value=True)
