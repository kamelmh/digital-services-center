import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar


def home_page():
    _sidebar()
    app.html("""
    <div style="text-align:center;padding:25px 0;">
        <h1 style="color:#0A1628;margin-bottom:5px;">Digital Services Center</h1>
        <p style="color:#D4AF37;font-size:1.1em;margin-top:0;">مركز الخدمات الرقمية — الجزائر</p>
        <p style="color:#888;font-size:0.9em;margin-top:5px;">28 Tools • 28 Pages • One-Click Dossier Pipeline</p>
    </div>
    """)

    categories = [
        ("📊 Studies & Feasibility", "#0A1628", [
            ("Feasibility", "دراسات جدوى 10k-60k"),
            ("Business Plan", "خطط عمل 25k-40k"),
            ("Market Research", "أبحاث سوق 10k-20k"),
            ("Financials", "توقعات مالية 15k-25k"),
            ("Complete Dossier", "ملف كامل NESDA"),
            ("BMC Canvas", "نموذج أعمال 9 محاور"),
        ]),
        ("🎯 NESDA Tools", "#D4AF37", [
            ("NESDA Calc", "حساب تمويل ثلاثي"),
            ("NESDA Catalog", "51 نشاط مدعوم"),
            ("Eligibility", "تحقق من الأهلية"),
        ]),
        ("💰 Pricing & Quotes", "#28a745", [
            ("Pricing", "حاسبة أسعار + واتساب"),
            ("Invoice/Quote", "فواتير وعروض سعر"),
            ("G12 IFU", "تصريح G12"),
            ("G50 Monthly", "تصريح G50"),
            ("Tax Guides", "تصريحات ضريبية"),
        ]),
        ("📣 Marketing", "#e83e8c", [
            ("Marketing Plan", "خطط تسويقية"),
            ("Social Media", "محتوى شبكات اجتماعية"),
            ("LinkedIn", "إنشاء محتوى تلقائي"),
        ]),
        ("📄 Documents", "#6f42c1", [
            ("CV Generator", "سيرة ذاتية PDF"),
            ("Cover Letter", "رسالة تعريفية"),
            ("Gov Paperwork", "مساعدة إدارية"),
        ]),
        ("🛠️ Operations", "#17a2b8", [
            ("Calculators", "حسابات مالية VAN/TRI"),
            ("AAPI Scorer", "نقاط AAPI /1500"),
            ("Batch Process", "إدارة العملاء"),
        ]),
    ]

    for cat_title, color, tools in categories:
        app.html(f"""<div style="margin:15px 0 8px;padding:8px 12px;background:{color}10;border-radius:8px;border-left:4px solid {color};">
            <strong style="color:{color};">{cat_title}</strong>
        </div>""")
        cols = app.columns(min(3, len(tools)))
        for i, (tool, desc) in enumerate(tools):
            with cols[i % len(cols)]:
                app.html(f"""<div style="padding:10px;background:white;border-radius:6px;margin:3px 0;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <strong style="font-size:0.9em;">{tool}</strong>
                    <div style="font-size:0.78em;color:#888;">{desc}</div>
                </div>""")

    app.html("""<div style="text-align:center;padding:20px;margin-top:15px;background:#f8f9fa;border-radius:8px;">
        <div style="display:flex;justify-content:center;gap:30px;">
            <div><strong style="font-size:1.5em;color:#0A1628;">28</strong><div style="font-size:0.8em;color:#888;">Generators</div></div>
            <div><strong style="font-size:1.5em;color:#D4AF37;">51</strong><div style="font-size:0.8em;color:#888;">NESDA Activities</div></div>
            <div><strong style="font-size:1.5em;color:#28a745;">20</strong><div style="font-size:0.8em;color:#888;">Services</div></div>
            <div><strong style="font-size:1.5em;color:#e83e8c;">4</strong><div style="font-size:0.8em;color:#888;">Packages</div></div>
        </div>
    </div>""")
