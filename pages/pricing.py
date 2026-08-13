import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar, _save_output
from pricing_calculator import SERVICES, PACKAGES, calculate_quote, format_quote_markdown


def pricing_page():
    _sidebar()
    app.title("Service Pricing & WhatsApp Export")
    app.text("حساب الأسعار وتصدير رسائل واتساب")

    app.markdown("### Select Services")
    selected_services = []
    for key, svc in SERVICES.items():
        if app.checkbox(f"{svc['name_ar']} ({svc['name_fr']}) — {svc['price_min']:,}-{svc['price_max']:,} DZD", key=f"svc_{key}"):
            selected_services.append(key)

    if not selected_services:
        app.info("Select at least one service above.")
        return

    cols = app.columns(2)
    discount = cols[0].number_input("Discount (%)", 0, 50, 0, 5)
    client_name = cols[1].text_input("Client Name (Arabic)")
    client_phone = cols[0].text_input("Client Phone", placeholder="+213...")
    deposit_pct = cols[1].number_input("Deposit (%)", 0, 100, 50, 10)

    if app.button("Calculate & Prepare Messages", type="primary"):
        result = calculate_quote(
            selected_services, discount_pct=discount,
            deposit_pct=deposit_pct, client_name=client_name.value,
            client_phone=client_phone.value,
        )

        _save_output("pricing", client_name.value or "client", result.whatsapp_message)

        app.html(f"""
        <div style="background:#d4edda;padding:20px;border-radius:10px;margin:15px 0;">
            <h3 style="margin:0;color:#155724;">Total: {result.total:,} DZD</h3>
            <p style="margin:5px 0 0;">Deposit: {result.deposit_amount:,} DZD | Balance: {result.balance:,} DZD</p>
            <p style="margin:5px 0 0;">Delivery: {result.estimated_delivery}</p>
        </div>""")

        app.markdown("### WhatsApp Message")
        app.code(result.whatsapp_message, language=None)

        if result.whatsapp_url:
            app.markdown(f"[Open WhatsApp]({result.whatsapp_url})")

        app.markdown("### Full Quote (Markdown)")
        full_quote = format_quote_markdown(result, client_name.value)
        app.html(f"<div style='background:#f0f0f0;padding:15px;border-radius:8px;white-space:pre-wrap;font-size:0.85em;'>{full_quote}</div>")
