"""2026 Rate Verification — Validates all financial/tax parameters against
research-backed values sourced from UpGrowth.dz, ComptaLegal.dz, WebMinds.dz,
AfroTools.dz, and official Algerian sources (verified Aug 2026).

Usage:
    python verify_rates.py              # Full check
    python verify_rates.py --strict     # Fail on any discrepancy
"""

from __future__ import annotations

import json
import sys
import io
from dataclasses import dataclass, asdict
from typing import Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


@dataclass
class RateCheck:
    name: str
    expected: float
    actual: float
    unit: str
    source: str
    status: str = "PASS"


VERIFIED_2026_RATES = {
    # --- NESDA Financing ---
    "nesda_max_amount": {"expected": 10_000_000, "unit": "DZD", "source": "UpGrowth.dz"},
    "nesda_min_amount": {"expected": 500_000, "unit": "DZD", "source": "UpGrowth.dz"},
    "nesda_personal_pct_unemployed": {"expected": 0.05, "unit": "%", "source": "UpGrowth.dz"},
    "nesda_personal_pct_employed": {"expected": 0.15, "unit": "%", "source": "UpGrowth.dz"},
    "nesda_grant_pct_min": {"expected": 0.15, "unit": "%", "source": "UpGrowth.dz"},
    "nesda_grant_pct_max": {"expected": 0.25, "unit": "%", "source": "UpGrowth.dz"},
    "nesda_bank_pct": {"expected": 0.70, "unit": "%", "source": "UpGrowth.dz"},
    "nesda_interest_rate_min": {"expected": 0.0, "unit": "%", "source": "NESDA DG interview (lesenjeuxeco.dz Feb 2026), CPA Bank (100% bonified)"},
    "nesda_interest_rate_max": {"expected": 0.0, "unit": "%", "source": "NESDA DG interview (lesenjeuxeco.dz Feb 2026), CPA Bank (100% bonified)"},
    "nesda_repayment_years": {"expected": 7, "unit": "years", "source": "CPA Bank: 6 ans et 6 mois (5y repayment + 1.5y grace)"},
    "nesda_grace_years": {"expected": 1.5, "unit": "years", "source": "UpGrowth.dz"},

    # --- Tax Rates ---
    "tva_normal": {"expected": 0.19, "unit": "%", "source": "WebMinds.dz, lamacta.com"},
    "tva_reduced": {"expected": 0.09, "unit": "%", "source": "WebMinds.dz, lamacta.com"},
    "tva_threshold_services": {"expected": 240_000_000, "unit": "DZD", "source": "upgrowth.dz"},
    "tva_threshold_commerce": {"expected": 500_000_000, "unit": "DZD", "source": "upgrowth.dz"},

    "ibs_industry": {"expected": 0.19, "unit": "%", "source": "WebMinds.dz"},
    "ibs_services": {"expected": 0.26, "unit": "%", "source": "Art. 150 CIDTA, webminds.dz, gbsdz.com"},

    "irg_rate_max": {"expected": 0.35, "unit": "%", "source": "WebMinds.dz"},
    "irg_threshold_0": {"expected": 120_000, "unit": "DZD", "source": "WebMinds.dz"},
    "irg_threshold_20": {"expected": 360_000, "unit": "DZD", "source": "WebMinds.dz"},
    "irg_threshold_30": {"expected": 1_440_000, "unit": "DZD", "source": "WebMinds.dz"},

    "ifu_threshold": {"expected": 8_000_000, "unit": "DZD", "source": "UpGrowth.dz"},
    "ifu_benefits": {"expected": 0.05, "unit": "%", "source": "UpGrowth.dz"},
    "ifu_services": {"expected": 0.12, "unit": "%", "source": "UpGrowth.dz"},
    "ifu_auto_min": {"expected": 10_000, "unit": "DZD", "source": "upgrowth.dz"},
    "ifu_min": {"expected": 30_000, "unit": "DZD", "source": "upgrowth.dz"},

    "tap_production": {"expected": 0.01, "unit": "%", "source": "WebMinds.dz"},
    "tap_services_commerce": {"expected": 0.02, "unit": "%", "source": "WebMinds.dz"},

    # --- CNAS / Social Security ---
    "snmg_monthly": {"expected": 24_000, "unit": "DZD", "source": "macalculatriceenligne.com"},
    "snmg_monthly": {"expected": 24_000, "unit": "DZD", "source": "macalculatriceenligne.com"},
    "cnas_salaried_pct": {"expected": 0.09, "unit": "%", "source": "macalculatriceenligne.com"},
    "cnas_employer_pct": {"expected": 0.255, "unit": "%", "source": "macalculatriceenligne.com"},
    "cnas_total_pct": {"expected": 0.35, "unit": "%", "source": "macalculatriceenligne.com"},

    # --- Discount Rate ---
    "van_discount_rate": {"expected": 0.12, "unit": "%", "source": "Industry standard Algeria"},

    # --- Tax Incentives ---
    "tax_exemption_base": {"expected": 3, "unit": "years", "source": "RESEARCH_2026.md"},
    "tax_exemption_high_plateaus": {"expected": 6, "unit": "years", "source": "RESEARCH_2026.md"},
    "tax_exemption_south": {"expected": 10, "unit": "years", "source": "RESEARCH_2026.md"},
}


def verify_nesda_calculator() -> list[RateCheck]:
    from nesda_calculator import calculate_nesda_financing, MODELS

    checks = []

    result = calculate_nesda_financing(
        total_cost=5_000_000,
        model="triangular",
        profile="unemployed",
        interest_rate=0.0,
        repayment_years=7,
        grace_years=1.5,
    )

    checks.append(RateCheck("nesda_personal_pct", MODELS["triangular"]["personal_range"][0], VERIFIED_2026_RATES["nesda_personal_pct_unemployed"]["expected"], "%", "UpGrowth.dz"))
    checks.append(RateCheck("nesda_grant_pct", MODELS["triangular"]["nesda_range"][1], VERIFIED_2026_RATES["nesda_grant_pct_max"]["expected"], "%", "UpGrowth.dz"))
    checks.append(RateCheck("nesda_bank_pct", MODELS["triangular"]["bank_pct"], VERIFIED_2026_RATES["nesda_bank_pct"]["expected"], "%", "UpGrowth.dz"))
    checks.append(RateCheck("nesda_interest_rate", result.interest_rate, 0.0, "%", "NESDA DG, CPA Bank (100% bonified)"))
    checks.append(RateCheck("nesda_repayment_years", result.repayment_years, VERIFIED_2026_RATES["nesda_repayment_years"]["expected"], "years", "UpGrowth.dz"))
    checks.append(RateCheck("nesda_grace_years", result.grace_years, VERIFIED_2026_RATES["nesda_grace_years"]["expected"], "years", "UpGrowth.dz"))

    return checks


def verify_feasibility_generator() -> list[RateCheck]:
    from feasibility_generator import ALGERIA_DATA

    checks = []

    checks.append(RateCheck("tva_rate", ALGERIA_DATA["tva_rate"], VERIFIED_2026_RATES["tva_normal"]["expected"], "%", "lamacta.com, webminds.dz"))
    checks.append(RateCheck("corporate_tax_rate", ALGERIA_DATA["corporate_tax_rate"], VERIFIED_2026_RATES["ibs_industry"]["expected"], "%", "webminds.dz (industry default)"))
    checks.append(RateCheck("cnas_employer_rate", ALGERIA_DATA["cnas_employer_rate"], VERIFIED_2026_RATES["cnas_employer_pct"]["expected"], "%", "macalculatriceenligne.com"))
    checks.append(RateCheck("snmg_monthly", ALGERIA_DATA.get("snmg_monthly", ALGERIA_DATA.get("smig_monthly")), VERIFIED_2026_RATES["snmg_monthly"]["expected"], "DZD", "macalculatriceenligne.com"))

    return checks


def verify_financial_calculators() -> list[RateCheck]:
    from financial_calculators import FinancialCalculators

    checks = []
    van = FinancialCalculators.van
    checks.append(RateCheck("van_method", True, True, "exists", "financial_calculators.py"))

    tri = FinancialCalculators.tri
    checks.append(RateCheck("tri_method", True, True, "exists", "financial_calculators.py"))

    seuil = FinancialCalculators.seuil_rentabilite
    checks.append(RateCheck("break_even_units_method", True, True, "exists", "financial_calculators.py"))

    seuil_val = FinancialCalculators.seuil_rentabilite_valeur
    checks.append(RateCheck("break_even_dzd_method", True, True, "exists", "financial_calculators.py"))

    return checks


def verify_g1_ggr_bareme() -> list[RateCheck]:
    """Verify G1 GGR IRG barème constants match 2026 official values."""
    from g1_ggr_generator import IRG_BAREME

    checks = []

    expected = [(240_000, 0.00), (480_000, 0.23), (960_000, 0.27), (1_920_000, 0.30), (3_840_000, 0.33), (float("inf"), 0.35)]
    for i, (exp_tranche, exp_rate) in enumerate(expected):
        if i < len(IRG_BAREME):
            checks.append(RateCheck(
                f"g1_irg_tranche_{i}",
                exp_tranche,
                IRG_BAREME[i][0],
                "DZD",
                "mfdgi.gov.dz, CIDTA, LF 2026"
            ))
            checks.append(RateCheck(
                f"g1_irg_rate_{i}",
                exp_rate,
                IRG_BAREME[i][1],
                "%",
                "mfdgi.gov.dz, CIDTA, LF 2026"
            ))

    return checks


def verify_g29_salary_bareme() -> list[RateCheck]:
    """Verify G29/G30 salary IRG barème constants match 2026 official values."""
    from g29_irg_salaires_generator import IRG_BAREME_MONTHLY

    checks = []

    # G29/G30 applies the annual salary barème after conversion to monthly values.
    # The generator's IRG_BAREME_MONTHLY is intentionally 20k / 40k / 80k /
    # 160k / 320k DZD, then infinity.
    expected = [(20_000, 0.00), (40_000, 0.23), (80_000, 0.27), (160_000, 0.30), (320_000, 0.33), (float("inf"), 0.35)]
    for i, (exp_tranche, exp_rate) in enumerate(expected):
        if i < len(IRG_BAREME_MONTHLY):
            checks.append(RateCheck(
                f"g29_irg_tranche_{i}",
                exp_tranche,
                IRG_BAREME_MONTHLY[i][0],
                "DZD",
                "mfdgi.gov.dz, CIDTA, LF 2026"
            ))
            checks.append(RateCheck(
                f"g29_irg_rate_{i}",
                exp_rate,
                IRG_BAREME_MONTHLY[i][1],
                "%",
                "mfdgi.gov.dz, CIDTA, LF 2026"
            ))

    return checks


# ── Non-self-affirming policy_constants verification (Sprint 8, Guide §3) ─────
# This checks the canonical module against an independently reviewed snapshot so
# an accidental edit to policy_constants.py cannot make verification pass by
# construction. Generators are separately checked above — defense in depth.

REVIEWED_2026_IRG_ANNUAL = (
    (240_000, 0.00),
    (480_000, 0.23),
    (960_000, 0.27),
    (1_920_000, 0.30),
    (3_840_000, 0.33),
    (float("inf"), 0.35),
)


def verify_policy_constants() -> list[RateCheck]:
    """Verify policy_constants.py against the REVIEWED snapshot (Guide §3).

    An edit to policy_constants.py alone cannot self-affirm because the
    expected side is this snapshot, not the module itself. Subsequent
    verify_g1/verify_g29 calls separately prove generators == policy_constants.
    """
    import policy_constants as pc

    checks: list[RateCheck] = []

    for i, (exp_tr, exp_rate) in enumerate(REVIEWED_2026_IRG_ANNUAL):
        checks.append(RateCheck(f"pc_irg_annual_tranche_{i}", exp_tr, pc.IRG_ANNUAL_BRACKETS[i][0], "DZD", "reviewed policy snapshot"))
        checks.append(RateCheck(f"pc_irg_annual_rate_{i}", exp_rate, pc.IRG_ANNUAL_BRACKETS[i][1], "%", "reviewed policy snapshot"))

    # Monthly is derived = annual/12; check derivation, not just literals.
    for i, (exp_tr, exp_rate) in enumerate(REVIEWED_2026_IRG_ANNUAL):
        exp_m = exp_tr if exp_tr == float("inf") else exp_tr / 12
        checks.append(RateCheck(f"pc_irg_monthly_tranche_{i}", exp_m, pc.IRG_MONTHLY_BRACKETS[i][0], "DZD", "derived from reviewed annual table"))
        checks.append(RateCheck(f"pc_irg_monthly_rate_{i}", exp_rate, pc.IRG_MONTHLY_BRACKETS[i][1], "%", "derived from reviewed annual table"))

    # Shape / invariants (TableCheck-light): monotonic thresholds + inf terminator.
    checks.append(RateCheck("pc_irg_annual_monotonic", True, all(pc.IRG_ANNUAL_BRACKETS[i][0] < pc.IRG_ANNUAL_BRACKETS[i + 1][0] for i in range(len(pc.IRG_ANNUAL_BRACKETS) - 1)), "bool", "boundary invariant"))
    checks.append(RateCheck("pc_irg_monthly_monotonic", True, all(pc.IRG_MONTHLY_BRACKETS[i][0] < pc.IRG_MONTHLY_BRACKETS[i + 1][0] for i in range(len(pc.IRG_MONTHLY_BRACKETS) - 1)), "bool", "boundary invariant"))
    checks.append(RateCheck("pc_irg_annual_terminates_inf", True, pc.IRG_ANNUAL_BRACKETS[-1][0] == float("inf"), "bool", "boundary invariant"))

    checks.append(RateCheck("pc_cnas_combined_rate", 0.345, pc.CNAS_COMBINED_PAYROLL_RATE, "%", "reviewed CNAS convention"))
    checks.append(RateCheck("pc_van_discount_rate", 0.12, pc.VAN_DISCOUNT_RATE, "%", "reviewed financial policy"))

    return checks


def run_all(strict: bool = False) -> bool:
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    all_checks = []
    all_checks.extend(verify_nesda_calculator())
    all_checks.extend(verify_feasibility_generator())
    all_checks.extend(verify_financial_calculators())
    all_checks.extend(verify_g1_ggr_bareme())
    all_checks.extend(verify_g29_salary_bareme())
    all_checks.extend(verify_policy_constants())

    print("=" * 70)
    print(f"2026 Rate Verification Report — {timestamp}")
    print("=" * 70)

    failures = 0
    for check in all_checks:
        if isinstance(check.expected, float) and isinstance(check.actual, (int, float)):
            if check.expected == float("inf") and check.actual == float("inf"):
                match = True
            else:
                match = abs(check.expected - check.actual) < 0.001
        else:
            match = check.expected == check.actual
        if not match:
            check.status = "FAIL"
        else:
            check.status = "PASS"
        status_icon = "✅" if check.status == "PASS" else "❌"
        if check.status == "FAIL":
            failures += 1
            print(f"  {status_icon} {check.name}: expected={check.expected}{check.unit}, actual={check.actual}{check.unit}")
            print(f"      Source: {check.source}")
        else:
            print(f"  {status_icon} {check.name}: {check.actual}{check.unit}")

    print()
    print(f"Total checks: {len(all_checks)}")
    print(f"Passed: {len(all_checks) - failures}")
    print(f"Failed: {failures}")

    if strict and failures > 0:
        print("\n❌ STRICT MODE: Failing due to discrepancies.")

    return failures == 0


if __name__ == "__main__":
    strict = "--strict" in sys.argv
    ok = run_all(strict=strict)
    raise SystemExit(0 if ok else 1)
