"""Financial Projections Engine — Mathematical (no LLM).

Generates precise 5-year financial projections from business defaults.
Uses real formulas: CMUP, break-even, cash flow, VAN, TRI.
The LLM only adds narrative text around the numbers.
"""

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class YearProjection:
    year: int
    revenue: int
    cogs: int
    gross_profit: int
    operating_costs: int
    depreciation: int
    ebit: int  # Earnings Before Interest & Taxes
    interest: int
    ebt: int  # Earnings Before Tax
    tax: int
    net_income: int
    cash_flow: int
    cumulative_cash: int
    revenue_growth: float = 0.0
    net_margin: float = 0.0


@dataclass
class FinancialProjections:
    business_type: str
    wilaya: str
    investment: int
    equity: int
    loan: int
    loan_rate: float
    loan_years: int
    depreciation_years: int
    monthly_revenue_y1: int
    annual_revenue_growth: float
    cogs_pct: float
    operating_pct: float
    tax_rate: float
    years: list[YearProjection] = field(default_factory=list)
    van: float = 0.0
    tri: float = 0.0
    breakeven_revenue: int = 0
    breakeven_units: int = 0
    payback_year: int = 0
    total_profit: int = 0
    avg_roi: float = 0.0

    def to_dict(self) -> dict:
        return {
            "business_type": self.business_type,
            "wilaya": self.wilaya,
            "investment": self.investment,
            "equity": self.equity,
            "loan": self.loan,
            "years": [
                {
                    "year": y.year,
                    "revenue": y.revenue,
                    "cogs": y.cogs,
                    "gross_profit": y.gross_profit,
                    "operating_costs": y.operating_costs,
                    "depreciation": y.depreciation,
                    "ebit": y.ebit,
                    "interest": y.interest,
                    "ebt": y.ebt,
                    "tax": y.tax,
                    "net_income": y.net_income,
                    "cash_flow": y.cash_flow,
                    "cumulative_cash": y.cumulative_cash,
                    "revenue_growth": y.revenue_growth,
                    "net_margin": y.net_margin,
                }
                for y in self.years
            ],
            "van": self.van,
            "tri": self.tri,
            "breakeven_revenue": self.breakeven_revenue,
            "payback_year": self.payback_year,
            "total_profit": self.total_profit,
            "avg_roi": self.avg_roi,
        }


class ProjectionsEngine:
    """Generate financial projections mathematically from business defaults."""

    def __init__(
        self,
        business_type: str,
        wilaya: str,
        investment: int,
        monthly_revenue_y1: int = None,
        equity_pct: float = 0.65,
        loan_rate: float = 0.09,
        loan_years: int = 5,
        depreciation_years: int = 10,
        annual_revenue_growth: float = 0.05,
        tax_rate: float = 0.19,
    ):
        from business_defaults import get_defaults, estimate_monthly_revenue
        defaults = get_defaults(business_type)

        self.business_type = business_type
        self.wilaya = wilaya
        self.investment = investment
        self.cogs_pct = defaults["cogs_pct"]
        self.operating_pct = defaults["operating_pct"]
        self.equity = int(investment * equity_pct)
        self.loan = investment - self.equity
        self.loan_rate = loan_rate
        self.loan_years = loan_years
        self.depreciation_years = depreciation_years
        self.annual_revenue_growth = annual_revenue_growth
        self.tax_rate = tax_rate

        if monthly_revenue_y1:
            self.monthly_revenue_y1 = monthly_revenue_y1
        else:
            self.monthly_revenue_y1 = estimate_monthly_revenue(business_type, investment)

    def generate(self, years: int = 5) -> FinancialProjections:
        """Generate complete projections."""
        proj = FinancialProjections(
            business_type=self.business_type,
            wilaya=self.wilaya,
            investment=self.investment,
            equity=self.equity,
            loan=self.loan,
            loan_rate=self.loan_rate,
            loan_years=self.loan_years,
            depreciation_years=self.depreciation_years,
            monthly_revenue_y1=self.monthly_revenue_y1,
            annual_revenue_growth=self.annual_revenue_growth,
            cogs_pct=self.cogs_pct,
            operating_pct=self.operating_pct,
            tax_rate=self.tax_rate,
        )

        # Annual depreciation (straight-line)
        annual_depreciation = self.investment // self.depreciation_years

        # Annual loan payment (annuity)
        annual_loan_payment = self._annuity(self.loan, self.loan_rate, self.loan_years) if self.loan > 0 else 0

        cumulative_cash = -self.equity
        payback_found = False

        for year in range(1, years + 1):
            # Revenue grows annually
            if year == 1:
                revenue = self.monthly_revenue_y1 * 12
            else:
                revenue = int(proj.years[-1].revenue * (1 + self.annual_revenue_growth))

            cogs = int(revenue * self.cogs_pct)
            gross_profit = revenue - cogs
            operating = int(revenue * self.operating_pct)

            # Fixed operating costs (don't scale linearly with revenue)
            # Rent, insurance, etc. are mostly fixed
            fixed_ops = int(operating * 0.6)
            variable_ops = int(operating * 0.4 * (1 + self.annual_revenue_growth * 0.5))
            total_operating = fixed_ops + variable_ops

            ebit = gross_profit - total_operating - annual_depreciation

            # Interest (decreasing as loan is paid)
            remaining_loan = max(0, self.loan - (year - 1) * (self.loan // self.loan_years))
            interest = int(remaining_loan * self.loan_rate)

            ebt = ebit - interest
            tax = max(0, int(ebt * self.tax_rate))
            net_income = ebt - tax

            # Cash flow: net income + depreciation - principal repayment
            principal = annual_loan_payment - interest if year <= self.loan_years else 0
            cash_flow = net_income + annual_depreciation - principal
            cumulative_cash += cash_flow

            growth = (revenue / proj.years[-1].revenue - 1) if proj.years else 0
            net_margin = net_income / revenue if revenue else 0

            proj.years.append(YearProjection(
                year=year,
                revenue=revenue,
                cogs=cogs,
                gross_profit=gross_profit,
                operating_costs=total_operating,
                depreciation=annual_depreciation,
                ebit=ebit,
                interest=interest,
                ebt=ebt,
                tax=tax,
                net_income=net_income,
                cash_flow=cash_flow,
                cumulative_cash=cumulative_cash,
                revenue_growth=growth,
                net_margin=net_margin,
            ))

            # Payback year
            if not payback_found and cumulative_cash >= 0:
                proj.payback_year = year
                payback_found = True

        # Break-even
        annual_fixed = int(self.monthly_revenue_y1 * 12 * self.operating_pct * 0.6) + annual_depreciation
        contribution_margin = 1 - self.cogs_pct - (self.operating_pct * 0.4)
        proj.breakeven_revenue = int(annual_fixed / contribution_margin) if contribution_margin > 0 else 0

        # VAN (NPV at 10% discount rate)
        discount_rate = 0.10
        cash_flows = [-self.equity] + [y.cash_flow for y in proj.years]
        proj.van = sum(cf / (1 + discount_rate) ** t for t, cf in enumerate(cash_flows))

        # TRI (IRR via Newton-Raphson)
        proj.tri = self._irr(cash_flows)

        # Summary
        proj.total_profit = sum(y.net_income for y in proj.years)
        proj.avg_roi = proj.total_profit / self.investment / years if self.investment else 0

        return proj

    @staticmethod
    def _annuity(principal: int, rate: float, years: int) -> int:
        """Calculate annual loan payment (annuity)."""
        if principal <= 0 or rate <= 0:
            return principal // years if years > 0 else 0
        r = rate
        n = years
        payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return int(payment)

    @staticmethod
    def _irr(cash_flows: list, max_iter: int = 100, tol: float = 1e-6) -> float:
        """Calculate IRR using Newton-Raphson."""
        if not cash_flows or cash_flows[0] >= 0:
            return 0.0

        # Initial guess
        rate = 0.10

        for _ in range(max_iter):
            npv = sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
            dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cash_flows))

            if abs(dnpv) < 1e-12:
                break

            rate -= npv / dnpv
            if abs(npv) < tol:
                break

        return rate


def format_projections(proj: FinancialProjections) -> str:
    """Format projections as readable markdown."""
    lines = [
        f"# Prévisions Financières — {proj.business_type}",
        f"**Wilaya:** {proj.wilaya}",
        f"**Investissement:** {proj.investment:,.0f} DZD",
        f"**Financement:** {proj.equity:,.0f} DZD equity + {proj.loan:,.0f} DZD emprunt",
        "",
        "## Tableau Récapitulatif (5 ans)",
        "",
        "| Année | CA | COGS | Marge Brute | Charges | EBIT | Intérêts | Bénéfice Net | Marge Nette | Cash Flow | Cumul |",
        "|-------|-----|------|-------------|---------|------|----------|--------------|-------------|-----------|-------|",
    ]

    for y in proj.years:
        lines.append(
            f"| {y.year} | {y.revenue:,.0f} | {y.cogs:,.0f} | {y.gross_profit:,.0f} | "
            f"{y.operating_costs:,.0f} | {y.ebit:,.0f} | {y.interest:,.0f} | "
            f"{y.net_income:,.0f} | {y.net_margin:.1%} | {y.cash_flow:,.0f} | {y.cumulative_cash:,.0f} |"
        )

    lines.extend([
        "",
        "## Indicateurs Clés",
        f"- **VAN (TRI {proj.tri:.1%}):** {proj.van:,.0f} DZD",
        f"- **Seuil de rentabilité:** {proj.breakeven_revenue:,.0f} DZD/an",
        f"- **Délai de récupération:** Année {proj.payback_year}" if proj.payback_year else "- **Délai de récupération:** > 5 ans",
        f"- **Bénéfice total (5 ans):** {proj.total_profit:,.0f} DZD",
        f"- **ROI moyen annuel:** {proj.avg_roi:.1%}",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    engine = ProjectionsEngine(
        business_type="quincaillerie",
        wilaya="El Bayadh",
        investment=4_600_000,
    )
    proj = engine.generate(years=5)
    print(format_projections(proj))
    print(f"\n--- JSON ---")
    import json
    print(json.dumps(proj.to_dict(), indent=2, ensure_ascii=False))
