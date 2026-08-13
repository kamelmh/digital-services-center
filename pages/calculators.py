import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar
from financial_calculators import FinancialCalculators


def calculators_page():
    _sidebar()
    app.title("Financial Calculators")
    app.text("Calculators financiers — VAN, TRI, Pricing")

    tabs = app.tabs(["VAN","TRI","Pricing"])

    with tabs[0]:
        app.markdown("**VAN** — Net Present Value")
        rate = app.number_input("Discount Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
        inv = app.number_input("Initial Investment (DZD)", min_value=0, value=1000000, step=100000)
        ncf = app.text_area("Net Cash Flows (one per line)", value="300000\n350000\n400000\n450000\n500000")
        if app.button("Calculate VAN", key="van_btn"):
            flows = [float(x.strip()) for x in ncf.value.split("\n") if x.strip()]
            try:
                calc = FinancialCalculators()
                result = calc.van(rate.value / 100, inv.value, flows)
                app.metric("VAN", f"{result:,.0f} DZD")
            except Exception as e:
                app.error(str(e))

    with tabs[1]:
        app.markdown("**TRI** — Internal Rate of Return")
        inv2 = app.number_input("Initial Investment (DZD)", min_value=0, value=1000000, step=100000, key="tri_inv")
        ncf2 = app.text_area("Net Cash Flows", value="300000\n350000\n400000\n450000\n500000", key="tri_ncf")
        if app.button("Calculate TRI", key="tri_btn"):
            flows = [float(x.strip()) for x in ncf2.value.split("\n") if x.strip()]
            try:
                calc = FinancialCalculators()
                result = calc.tri(inv2.value, flows)
                app.metric("TRI", f"{result:.2f}%")
            except Exception as e:
                app.error(str(e))

    with tabs[2]:
        app.markdown("**Pricing** — Cost+ and Monthly Pricing")
        cols = app.columns(3)
        fixed = cols[0].number_input("Fixed Costs (DZD)", min_value=0, value=150000, step=5000)
        var = cols[1].number_input("Variable Cost/unit", min_value=0, value=1500, step=100)
        units = cols[2].number_input("Units/month", min_value=1, value=30, step=1)
        margin = app.number_input("Desired Margin (%)", min_value=0.0, max_value=500.0, value=50.0, step=5.0)
        if app.button("Calculate Pricing", key="price_btn"):
            try:
                calc = FinancialCalculators()
                result = calc.cost_plus_pricing(fixed.value, var.value, units.value, margin.value / 100)
                c1,c2,c3 = app.columns(3)
                c1.metric("Unit Price", f"{result.get('unit_price', 0):,.0f}")
                c2.metric("Monthly Revenue", f"{result.get('monthly_revenue', 0):,.0f}")
                c3.metric("Monthly Profit", f"{result.get('monthly_profit', 0):,.0f}")
            except Exception as e:
                app.error(str(e))
