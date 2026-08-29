"""Financial Calculators — VAN, TRI, Seuil de Rentabilité, Scenarios.

Real mathematical calculations for Algerian business feasibility studies.
No LLM guessing — pure Python math.
"""

import math
from dataclasses import dataclass, field

from policy_constants import DEFAULT_BANK_LOAN_RATE, IBS_PRODUCTION_RATE, VAN_DISCOUNT_RATE


@dataclass
class CashFlow:
    year: int
    revenue: float
    cogs: float  # Cost of Goods Sold
    operating_costs: float  # Salaries, rent, energy, maintenance
    depreciation: float  # Annual depreciation
    tax_rate: float = IBS_PRODUCTION_RATE  # Corporate tax 19% in Algeria

    @property
    def gross_margin(self) -> float:
        return self.revenue - self.cogs

    @property
    def ebitda(self) -> float:
        return self.gross_margin - self.operating_costs

    @property
    def ebit(self) -> float:
        return self.ebitda - self.depreciation

    @property
    def tax(self) -> float:
        return max(0, self.ebit * self.tax_rate)

    @property
    def net_income(self) -> float:
        return self.ebit - self.tax

    @property
    def operating_cash_flow(self) -> float:
        return self.net_income + self.depreciation


@dataclass
class InvestmentPlan:
    equipment: float
    buildings: float
    engineering: float  # Study, permits, setup
    working_capital: float
    land: float = 0  # If purchasing

    @property
    def total_initial(self) -> float:
        return self.equipment + self.buildings + self.engineering + self.working_capital + self.land

    @property
    def depreciable(self) -> float:
        return self.equipment + self.buildings

    def annual_depreciation(self, years: int = 5) -> float:
        return self.depreciable / years if years > 0 else 0


@dataclass
class FinancingPlan:
    equity: float  # Apports en fonds propres
    bank_loan: float = 0
    loan_rate: float = DEFAULT_BANK_LOAN_RATE  # 9% Algeria default
    loan_years: int = 7

    @property
    def total_financing(self) -> float:
        return self.equity + self.bank_loan

    @property
    def equity_ratio(self) -> float:
        total = self.total_financing
        return self.equity / total if total > 0 else 0

    def annual_payment(self) -> float:
        if self.bank_loan <= 0 or self.loan_years <= 0:
            return 0
        r = self.loan_rate
        n = self.loan_years
        return self.bank_loan * (r * (1 + r)**n) / ((1 + r)**n - 1)

    def annual_interest(self, remaining: float) -> float:
        return remaining * self.loan_rate


class FinancialCalculators:
    """Real financial calculators for Algerian business studies."""

    @staticmethod
    def van(cash_flows: list[float], discount_rate: float = VAN_DISCOUNT_RATE) -> float:
        """Valeur Actuelle Nette / Net Present Value.
        
        VAN = -Investment + Σ(CF_t / (1+r)^t)
        Discount rate: 12% default (Algerian market rate).
        """
        if not cash_flows:
            return 0
        investment = cash_flows[0]  # Year 0 = initial investment (negative)
        npv = investment
        for t, cf in enumerate(cash_flows[1:], start=1):
            npv += cf / (1 + discount_rate) ** t
        return npv

    @staticmethod
    def tri(cash_flows: list[float], tolerance: float = 1e-6, max_iter: int = 1000) -> float:
        """Taux de Rentabilité Interne / Internal Rate of Return.
        
        Finds rate r where VAN = 0 using Newton-Raphson.
        Returns as percentage (e.g., 15.3 for 15.3%).
        """
        if not cash_flows or len(cash_flows) < 2:
            return 0

        def npv_at(r):
            return sum(cf / (1 + r) ** t for t, cf in enumerate(cash_flows))

        def npv_derivative(r):
            return sum(-t * cf / (1 + r) ** (t + 1) for t, cf in enumerate(cash_flows))

        # Bisection fallback if Newton fails
        r = 0.1  # Initial guess
        for _ in range(max_iter):
            f = npv_at(r)
            if abs(f) < tolerance:
                return r * 100
            df = npv_derivative(r)
            if abs(df) < 1e-12:
                break
            r -= f / df
            r = max(-0.99, min(r, 10))  # Clamp

        # Bisection fallback
        low, high = -0.5, 5.0
        for _ in range(max_iter):
            mid = (low + high) / 2
            f_mid = npv_at(mid)
            if abs(f_mid) < tolerance:
                return mid * 100
            if npv_at(low) * f_mid < 0:
                high = mid
            else:
                low = mid
        return r * 100

    @staticmethod
    def seuil_rentabilite(fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> float:
        """Seuil de Rentabilité / Break-Even Point (in units).
        
        Seuil = Costs fixes / (Prix unitaire - Coût variable unitaire)
        """
        contribution = price_per_unit - variable_cost_per_unit
        if contribution <= 0:
            return float('inf')
        return fixed_costs / contribution

    @staticmethod
    def seuil_rentabilite_valeur(fixed_costs: float, contribution_margin_rate: float) -> float:
        """Seuil de rentabilité en valeur (DZD).
        
        Seuil = Costs fixes / Taux de marge sur coûts variables
        """
        if contribution_margin_rate <= 0:
            return float('inf')
        return fixed_costs / contribution_margin_rate

    @staticmethod
    def taux_marge(revenue: float, cogs: float) -> float:
        """Taux de marge / Gross margin rate.
        
        Taux = (Chiffre d'affaires - Coût d'achat) / CA × 100
        """
        if revenue <= 0:
            return 0
        return ((revenue - cogs) / revenue) * 100

    @staticmethod
    def delai_recuperation(investment: float, annual_cash_flows: list[float]) -> float:
        """Délai de récupération / Payback Period (in years).
        
        First year where cumulative cash flows >= initial investment.
        """
        cumulative = 0
        for i, cf in enumerate(annual_cash_flows):
            cumulative += cf
            if cumulative >= investment:
                # Linear interpolation within the year
                prev = cumulative - cf
                if cf > 0:
                    fraction = (investment - prev) / cf
                    return i + fraction
                return i + 1
        return len(annual_cash_flows) + 1  # Never pays back

    @staticmethod
    def tresorerie_annuelle(
        revenue: float,
        cogs: float,
        operating_costs: float,
        loan_payment: float,
        tax: float,
    ) -> float:
        """Trésorerie nette annuelle / Annual net cash flow."""
        return revenue - cogs - operating_costs - loan_payment - tax

    @staticmethod
    def plan_tresorerie(
        cash_flows: list[CashFlow],
        loan_payment: float,
    ) -> list[dict]:
        """Génère un tableau de trésorerie sur N ans."""
        result = []
        cumulative = 0
        for cf in cash_flows:
            net = cf.operating_cash_flow - loan_payment
            cumulative += net
            result.append({
                "year": cf.year,
                "revenue": cf.revenue,
                "cogs": cf.cogs,
                "operating": cf.operating_costs,
                "depreciation": cf.depreciation,
                "ebitda": cf.ebitda,
                "ebit": cf.ebit,
                "tax": cf.tax,
                "net_income": cf.net_income,
                "operating_cf": cf.operating_cash_flow,
                "loan_payment": loan_payment,
                "net_cash_flow": net,
                "cumulative_cash_flow": cumulative,
            })
        return result

    @staticmethod
    def compte_resultat_previsionnel(cash_flows: list[CashFlow]) -> list[dict]:
        """Compte de résultat prévisionnel (3-5 ans)."""
        result = []
        for cf in cash_flows:
            result.append({
                "year": cf.year,
                "revenue": cf.revenue,
                "cogs": cf.cogs,
                "gross_margin": cf.gross_margin,
                "gross_margin_pct": (cf.gross_margin / cf.revenue * 100) if cf.revenue > 0 else 0,
                "operating_costs": cf.operating_costs,
                "ebitda": cf.ebitda,
                "ebitda_pct": (cf.ebitda / cf.revenue * 100) if cf.revenue > 0 else 0,
                "depreciation": cf.depreciation,
                "ebit": cf.ebit,
                "tax": cf.tax,
                "net_income": cf.net_income,
                "net_margin_pct": (cf.net_income / cf.revenue * 100) if cf.revenue > 0 else 0,
            })
        return result

    @staticmethod
    def bilan_previsionnel(
        investment: InvestmentPlan,
        cash_flows: list[CashFlow],
        financing: FinancingPlan,
    ) -> list[dict]:
        """Bilan prévisionnel (3-5 ans)."""
        result = []
        total_depreciation = 0
        remaining_loan = financing.bank_loan

        for cf in cash_flows:
            total_depreciation += cf.depreciation
            net_assets = investment.depreciable - total_depreciation
            cash_balance = sum(c.operating_cash_flow for c in cash_flows[:cf.year])
            remaining_loan = max(0, remaining_loan - (financing.annual_payment() - financing.annual_interest(remaining_loan)))

            result.append({
                "year": cf.year,
                "fixed_assets": net_assets,
                "current_assets": investment.working_capital + cash_balance,
                "total_assets": net_assets + investment.working_capital + cash_balance,
                "equity": financing.equity + cf.net_income * cf.year,
                "debt": remaining_loan,
                "total_liabilities": financing.equity + cf.net_income * cf.year + remaining_loan,
            })
        return result


def generate_3_scenarios(
    base_revenue: float,
    base_cogs_rate: float,
    base_operating_rate: float,
    investment: InvestmentPlan,
    financing: FinancingPlan,
    years: int = 5,
) -> dict:
    """Generate 3 scenarios: prudent, reference, défavorable.
    
    Varies: revenue (-20%/+0%/+15%), COGS (+5%/+0%/-5%),
    operating costs (+10%/+0%/-5%).
    """
    scenarios = {}
    calc = FinancialCalculators()

    params = {
        "prudent": {"rev_mult": 0.80, "cogs_mult": 1.05, "op_mult": 1.10, "label": "Hypothèse prudente"},
        "reference": {"rev_mult": 1.00, "cogs_mult": 1.00, "op_mult": 1.00, "label": "Hypothèse de référence"},
        "favorable": {"rev_mult": 1.15, "cogs_mult": 0.95, "op_mult": 0.95, "label": "Hypothèse favorable"},
    }

    for name, p in params.items():
        revenue = base_revenue * p["rev_mult"]
        cogs = revenue * base_cogs_rate * p["cogs_mult"]
        operating = revenue * base_operating_rate * p["op_mult"]
        depreciation = investment.annual_depreciation(years)
        loan_payment = financing.annual_payment()

        cash_flows_list = []
        for yr in range(1, years + 1):
            cf = CashFlow(
                year=yr,
                revenue=revenue * (1.03) ** (yr - 1),  # 3% growth
                cogs=cogs * (1.03) ** (yr - 1),
                operating_costs=operating * (1.03) ** (yr - 1),
                depreciation=depreciation,
            )
            cash_flows_list.append(cf)

        # Year 0 = negative investment
        all_cfs = [-investment.total_initial] + [cf.operating_cash_flow - loan_payment for cf in cash_flows_list]

        van = calc.van(all_cfs)
        tri = calc.tri(all_cfs)
        seuil = calc.seuil_rentabilite(
            fixed_costs=operating + depreciation,
            price_per_unit=revenue / 1000,  # Assume 1000 units
            variable_cost_per_unit=cogs / 1000,
        )
        taux_marge = calc.taux_marge(revenue, cogs)
        delai = calc.delai_recuperation(investment.total_initial, [cf.operating_cash_flow - loan_payment for cf in cash_flows_list])

        compte = calc.compte_resultat_previsionnel(cash_flows_list)
        tresorerie = calc.plan_tresorerie(cash_flows_list, loan_payment)
        bilan = calc.bilan_previsionnel(investment, cash_flows_list, financing)

        scenarios[name] = {
            "label": p["label"],
            "params": p,
            "annual_revenue": revenue,
            "van": van,
            "tri": tri,
            "seuil_rentabilite": seuil,
            "taux_marge": taux_marge,
            "delai_recuperation": delai,
            "compte_resultat": compte,
            "tresorerie": tresorerie,
            "bilan": bilan,
            "loan_payment": loan_payment,
        }

    return scenarios


def format_dzd(amount: float) -> str:
    """Format amount in DZD with thousand separators."""
    if amount >= 1_000_000:
        return f"{amount/1_000_000:,.1f} M DZD"
    elif amount >= 1_000:
        return f"{amount/1_000:,.0f} k DZD"
    return f"{amount:,.0f} DZD"


def format_pct(value: float) -> str:
    """Format percentage."""
    return f"{value:.1f}%"


if __name__ == "__main__":
    # Example: Quincaillerie in El Bayadh
    investment = InvestmentPlan(
        equipment=2_000_000,
        buildings=1_500_000,
        engineering=300_000,
        working_capital=800_000,
    )
    financing = FinancingPlan(
        equity=3_000_000,
        bank_loan=1_600_000,
        loan_rate=DEFAULT_BANK_LOAN_RATE,
        loan_years=7,
    )

    print(f"Total Investment: {format_dzd(investment.total_initial)}")
    print(f"Equity: {format_dzd(financing.equity)} ({financing.equity_ratio*100:.0f}%)")
    print(f"Loan: {format_dzd(financing.bank_loan)}")
    print(f"Annual Payment: {format_dzd(financing.annual_payment())}")
    print()

    scenarios = generate_3_scenarios(
        base_revenue=6_000_000,
        base_cogs_rate=0.65,
        base_operating_rate=0.15,
        investment=investment,
        financing=financing,
    )

    for name, s in scenarios.items():
        print(f"=== {s['label']} ===")
        print(f"  Revenue: {format_dzd(s['annual_revenue'])}")
        print(f"  VAN: {format_dzd(s['van'])}")
        print(f"  TRI: {format_pct(s['tri'])}")
        print(f"  Seuil: {format_dzd(s['seuil_rentabilite'])} units")
        print(f"  Taux marge: {format_pct(s['taux_marge'])}")
        print(f"  Délai récupération: {s['delai_recuperation']:.1f} ans")
        print()
