"""NESDA Financing Calculator — Triangular, Mixed, and Self-financing models.

Calculates personal contribution, NESDA grant (PNR), bank loan, repayment schedule,
and all financial indicators (VAN, TRI, seuil, DR) for NESDA projects.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class NESDAFinancingResult:
    """Result of NESDA financing calculation."""
    # Amounts
    total_cost: int
    personal_amount: int
    nesda_grant: int
    bank_loan: int
    # Percentages
    personal_pct: float
    nesda_pct: float
    bank_pct: float
    # Loan terms
    interest_rate: float
    repayment_years: int
    grace_years: float
    annual_payment: float
    monthly_payment: float
    total_interest: float
    total_repayment: float
    # Schedule
    schedule: List[dict]
    # Indicators
    monthly_revenue: int
    monthly_costs: int
    monthly_profit: int
    payback_months: int
    roi_annual: float


# ── Financing Models ──────────────────────────────────────────────────────────

MODELS = {
    "triangular": {
        "name_fr": "Financement Triangulaire",
        "name_ar": "التمويل الثلاثي",
        "description_fr": "Partenaire: Porteur (5-15%) + NESDA (15-25%) + Banque (70%)",
        "description_ar": "المساهمة: حامل المشروع (5-15%) + NESDA (15-25%) + البنك (70%)",
        "personal_range": (0.05, 0.15),
        "nesda_range": (0.15, 0.25),
        "bank_pct": 0.70,
    },
    "mixed": {
        "name_fr": "Financement Mixte",
        "name_ar": "التمويل المختلط",
        "description_fr": "Partenaire: Porteur (50%) + NESDA (50%)",
        "description_ar": "المساهمة: حامل المشروع (50%) + NESDA (50%)",
        "personal_range": (0.50, 0.50),
        "nesda_range": (0.50, 0.50),
        "bank_pct": 0.0,
    },
    "self": {
        "name_fr": "Auto-financement",
        "name_ar": "التمويل الذاتي",
        "description_fr": "Partenaire: Porteur (100%)",
        "description_ar": "المساهمة: حامل المشروع (100%)",
        "personal_range": (1.0, 1.0),
        "nesda_range": (0.0, 0.0),
        "bank_pct": 0.0,
    },
}


def calculate_nesda_financing(
    total_cost: int,
    model: str = "triangular",
    profile: str = "unemployed",
    monthly_revenue: int = 500_000,
    cogs_pct: float = 0.65,
    operating_pct: float = 0.15,
    interest_rate: float = 0.0,
    repayment_years: int = 7,
    grace_years: float = 1.5,
) -> NESDAFinancingResult:
    """Calculate NESDA financing breakdown."""

    m = MODELS.get(model, MODELS["triangular"])

    # Personal contribution
    if profile == "unemployed":
        personal_pct = m["personal_range"][0]
    elif profile == "employed":
        personal_pct = m["personal_range"][1]
    else:
        personal_pct = (m["personal_range"][0] + m["personal_range"][1]) / 2

    nesda_pct = m["nesda_range"][1] if profile == "unemployed" else m["nesda_range"][0]
    bank_pct = m["bank_pct"]

    personal_amount = int(total_cost * personal_pct)
    nesda_grant = int(total_cost * nesda_pct)
    bank_loan = int(total_cost * bank_pct)

    # Loan repayment — use annuity formula (same as FinancialCalculators.FinancingPlan)
    r = interest_rate
    n = repayment_years - grace_years  # actual repayment years (after grace)
    if r > 0 and n > 0 and bank_loan > 0:
        annual_payment = bank_loan * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    elif n > 0 and bank_loan > 0:
        annual_payment = bank_loan / n  # 0% interest: divide evenly over repayment period
    else:
        annual_payment = bank_loan / max(1, repayment_years)

    monthly_payment = annual_payment / 12
    total_interest = annual_payment * n - bank_loan
    total_repayment = bank_loan + total_interest

    # Schedule
    schedule = []
    balance = bank_loan
    for year in range(1, int(repayment_years) + 1):
        if year <= grace_years:
            interest = balance * interest_rate
            principal = 0
        else:
            interest = balance * interest_rate
            principal = annual_payment - interest
        balance = max(0, balance - principal)
        schedule.append({
            "year": year,
            "balance_start": int(balance + principal),
            "payment": int(annual_payment),
            "interest": int(interest),
            "principal": int(principal),
            "balance_end": int(balance),
        })

    # Profitability
    monthly_cogs = int(monthly_revenue * cogs_pct)
    monthly_operating = int(monthly_revenue * operating_pct)
    monthly_profit = monthly_revenue - monthly_cogs - monthly_operating - int(monthly_payment)

    payback_months = int(total_cost / max(1, monthly_profit)) if monthly_profit > 0 else 999
    roi_annual = (monthly_profit * 12 / total_cost * 100) if total_cost > 0 else 0

    return NESDAFinancingResult(
        total_cost=total_cost,
        personal_amount=personal_amount,
        nesda_grant=nesda_grant,
        bank_loan=bank_loan,
        personal_pct=personal_pct,
        nesda_pct=nesda_pct,
        bank_pct=bank_pct,
        interest_rate=interest_rate,
        repayment_years=repayment_years,
        grace_years=grace_years,
        annual_payment=annual_payment,
        monthly_payment=monthly_payment,
        total_interest=total_interest,
        total_repayment=total_repayment,
        schedule=schedule,
        monthly_revenue=monthly_revenue,
        monthly_costs=monthly_cogs + monthly_operating + int(monthly_payment),
        monthly_profit=monthly_profit,
        payback_months=payback_months,
        roi_annual=roi_annual,
    )


def format_nesda_report(result: NESDAFinancingResult, project_name: str = "") -> str:
    """Format NESDA financing report as markdown."""
    m = MODELS["triangular"]

    schedule_rows = ""
    for s in result.schedule:
        schedule_rows += f"| {s['year']} | {s['balance_start']:,.0f} | {s['payment']:,.0f} | {s['interest']:,.0f} | {s['principal']:,.0f} | {s['balance_end']:,.0f} |\n"

    return f"""# تقرير تمويل NESDA — NESDA Financing Report

**المشروع:** {project_name or '[Nom du projet]'}
**التكلفة الإجمالية:** {result.total_cost:,} دج
**نموذج التمويل:** {m['name_ar']} — {m['name_fr']}

---

## هيكل التمويل

| المصدر | النسبة | المبلغ (دج) |
|--------|--------|------------|
| **المساهمة الشخصية** | {result.personal_pct*100:.0f}% | {result.personal_amount:,} |
| **مساهمة NESDA (PNR)** | {result.nesda_pct*100:.0f}% | {result.nesda_grant:,} |
| **قرض بنكي** | {result.bank_pct*100:.0f}% | {result.bank_loan:,} |
| **المجموع** | 100% | {result.total_cost:,} |

## شروط القرض البنكي

| البند | القيمة |
|-------|--------|
| سعر الفائدة | {result.interest_rate*100:.1f}% |
| مدة السداد | {result.repayment_years} سنوات |
| فترة السماح | {result.grace_years} سنوات |
| القسط السنوي | {result.annual_payment:,.0f} دج |
| القسط الشهري | {result.monthly_payment:,.0f} دج |
| إجمالي الفائدة | {result.total_interest:,.0f} دج |
| الإجمالي المدفوع | {result.total_repayment:,.0f} دج |

## جدول السداد

| السنة | رصيد البداية | القسط | الفائدة | Principal | الرصيد النهاية |
|-------|-------------|-------|---------|-----------|---------------|
{schedule_rows}

## مؤشرات الجدوى

| المؤشر | القيمة | التقييم |
|--------|--------|---------|
| الإيرادات الشهرية | {result.monthly_revenue:,} دج | — |
| التكاليف الشهرية | {result.monthly_costs:,} دج | — |
| الربح الصافي الشهري | {result.monthly_profit:,} دج | {'جيد' if result.monthly_profit > 0 else 'خسارة'} |
| مدة الاسترداد | {result.payback_months} شهر | {'مقبول' if result.payback_months <= 36 else 'طويل'} |
| العائد السنوي (ROI) | {result.roi_annual:.1f}% | {'جيد' if result.roi_annual > 15 else 'متوسط'} |

## ملاحظات NESDA

- **فترة السماح:** لا سداد خلال الأشهر {result.grace_years} الأولى
- **القرض غير المربح (PNR):** يُسدد بعد القرض البنكي بالكامل
- **الشرط:** شهادة CDE إلزامية قبل تقديم الملف
- **العمر:** 18-55 سنة (إنشاء) / 20-58 سنة (توسعة)
"""


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NESDA Financing Calculator")
    parser.add_argument("--cost", type=int, default=3_000_000, help="Total project cost in DZD")
    parser.add_argument("--model", default="triangular", choices=["triangular", "mixed", "self"])
    parser.add_argument("--profile", default="unemployed", choices=["unemployed", "employed"])
    parser.add_argument("--revenue", type=int, default=500_000, help="Monthly revenue estimate")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    result = calculate_nesda_financing(
        total_cost=args.cost,
        model=args.model,
        profile=args.profile,
        monthly_revenue=args.revenue,
    )

    report = format_nesda_report(result)

    if args.output:
        from pathlib import Path
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Saved: {args.output}")
    else:
        print(report)
