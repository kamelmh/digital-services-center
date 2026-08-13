import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar
from feasibility_generator import BUSINESS_TEMPLATES


def social_analytics_page():
    _sidebar()
    app.title("Social Media Analytics")
    app.text("تحليل أداء وسائل التواصل الاجتماعي")

    app.html("""<div style="background:#f8f9fa;padding:12px;border-radius:8px;border-left:4px solid #e83e8c;margin-bottom:15px;">
        <strong>Analytics Dashboard:</strong> Track performance across all your social media platforms.
    </div>""")

    with app.expander("📊 Enter Metrics", expanded=True):
        c1,c2,c3 = app.columns(3)
        followers = c1.number_input("Total Followers", 0, 1000000, 5000, 100)
        engagement_rate = c2.number_input("Engagement Rate (%)", 0.0, 100.0, 3.5, 0.1)
        reach = c3.number_input("Monthly Reach", 0, 1000000, 50000, 1000)
        c4,c5,c6 = app.columns(3)
        impressions = c4.number_input("Impressions", 0, 5000000, 100000, 5000)
        clicks = c5.number_input("Link Clicks", 0, 50000, 2000, 100)
        conversions = c6.number_input("Conversions", 0, 5000, 50, 10)

    if app.button("📊 Analyze Performance", type="primary"):
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
        c1,c2,c3 = app.columns(3)
        c1.metric("Engagement Rate", f"{engagement_rate:.2f}%")
        c2.metric("Click-Through Rate", f"{ctr:.2f}%")
        c3.metric("Conversion Rate", f"{conversion_rate:.2f}%")
