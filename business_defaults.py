"""Business Defaults — Pre-filled operational data for all 13 Algerian business types.

Used by the service orchestrator to auto-fill financial assumptions when generating
dossiers. Values are estimates based on Algerian market data and industry benchmarks.

Each template provides:
- cogs_pct: Cost of goods sold as % of revenue
- operating_pct: Operating expenses as % of revenue (rent, utilities, salaries excl. COGS)
- monthly_revenue_estimate: Typical monthly revenue in DZD
- staff_range: (min, max) employees
- investment_range: (min, max) investment in DZD
- aapi_priority: Recommended AAPI priority level (1=industry, 2=services, 3=commerce)
- profit_margin_target: Expected net profit margin after all costs
- working_capital_months: Months of operating costs to hold as working capital
- seasonal_factor: Revenue multiplier for peak vs average month (1.0 = no seasonality)
"""

BUSINESS_DEFAULTS = {
    "quincaillerie": {
        "name_fr": "Quincaillerie / Ferraillerie",
        "name_ar": "متجر مواد البناء والعتاد",
        "cogs_pct": 0.70,
        "operating_pct": 0.12,
        "monthly_revenue_estimate": 500_000,
        "staff_range": (2, 5),
        "investment_range": (3_000_000, 8_000_000),
        "aapi_priority": 3,
        "profit_margin_target": 0.10,
        "working_capital_months": 2,
        "seasonal_factor": 1.15,
    },
    "supermarche": {
        "name_fr": "Supermarché / Épicerie",
        "name_ar": "سوبر ماركت / دكان كبير",
        "cogs_pct": 0.75,
        "operating_pct": 0.10,
        "monthly_revenue_estimate": 800_000,
        "staff_range": (3, 8),
        "investment_range": (4_000_000, 15_000_000),
        "aapi_priority": 3,
        "profit_margin_target": 0.08,
        "working_capital_months": 1.5,
        "seasonal_factor": 1.20,
    },
    "restaurant": {
        "name_fr": "Restaurant / Snack",
        "name_ar": "مطعم / سناك",
        "cogs_pct": 0.35,
        "operating_pct": 0.30,
        "monthly_revenue_estimate": 600_000,
        "staff_range": (4, 12),
        "investment_range": (3_000_000, 12_000_000),
        "aapi_priority": 3,
        "profit_margin_target": 0.12,
        "working_capital_months": 1,
        "seasonal_factor": 1.30,
    },
    "atelier_ferro": {
        "name_fr": "Atelier de Ferraillement",
        "name_ar": "ورشة حدادة",
        "cogs_pct": 0.55,
        "operating_pct": 0.15,
        "monthly_revenue_estimate": 400_000,
        "staff_range": (2, 6),
        "investment_range": (2_000_000, 7_000_000),
        "aapi_priority": 1,
        "profit_margin_target": 0.18,
        "working_capital_months": 1.5,
        "seasonal_factor": 1.10,
    },
    "pharmacie": {
        "name_fr": "Pharmacie",
        "name_ar": "صيدلية",
        "cogs_pct": 0.65,
        "operating_pct": 0.15,
        "monthly_revenue_estimate": 1_200_000,
        "staff_range": (2, 5),
        "investment_range": (5_000_000, 15_000_000),
        "aapi_priority": 2,
        "profit_margin_target": 0.12,
        "working_capital_months": 2,
        "seasonal_factor": 1.10,
    },
    "cafe_patisserie": {
        "name_fr": "Café-Pâtisserie",
        "name_ar": "مقهى ومحل حلويات",
        "cogs_pct": 0.30,
        "operating_pct": 0.35,
        "monthly_revenue_estimate": 450_000,
        "staff_range": (3, 8),
        "investment_range": (2_000_000, 8_000_000),
        "aapi_priority": 3,
        "profit_margin_target": 0.15,
        "working_capital_months": 1,
        "seasonal_factor": 1.25,
    },
    "boulangerie": {
        "name_fr": "Boulangerie",
        "name_ar": "مخبزة",
        "cogs_pct": 0.40,
        "operating_pct": 0.25,
        "monthly_revenue_estimate": 350_000,
        "staff_range": (2, 5),
        "investment_range": (2_000_000, 6_000_000),
        "aapi_priority": 3,
        "profit_margin_target": 0.15,
        "working_capital_months": 1,
        "seasonal_factor": 1.05,
    },
    "epicerie": {
        "name_fr": "Épicerie / Dagaguer",
        "name_ar": "دكاكير / بقالة",
        "cogs_pct": 0.72,
        "operating_pct": 0.08,
        "monthly_revenue_estimate": 250_000,
        "staff_range": (1, 2),
        "investment_range": (1_000_000, 3_000_000),
        "aapi_priority": 3,
        "profit_margin_target": 0.10,
        "working_capital_months": 1.5,
        "seasonal_factor": 1.10,
    },
    "garage": {
        "name_fr": "Garage Auto / Mécanique",
        "name_ar": "ورشة سيارات",
        "cogs_pct": 0.40,
        "operating_pct": 0.20,
        "monthly_revenue_estimate": 500_000,
        "staff_range": (2, 6),
        "investment_range": (3_000_000, 10_000_000),
        "aapi_priority": 2,
        "profit_margin_target": 0.18,
        "working_capital_months": 1.5,
        "seasonal_factor": 1.05,
    },
    "salon_coiffure": {
        "name_fr": "Salon de Coiffure",
        "name_ar": " صالون حلاقة وتصفيف الشعر",
        "cogs_pct": 0.15,
        "operating_pct": 0.40,
        "monthly_revenue_estimate": 300_000,
        "staff_range": (2, 5),
        "investment_range": (1_500_000, 5_000_000),
        "aapi_priority": 3,
        "profit_margin_target": 0.20,
        "working_capital_months": 0.5,
        "seasonal_factor": 1.20,
    },
    "cybercafe": {
        "name_fr": "Cybercafé / Gaming Center",
        "name_ar": " مقهى إنترنت / صالة ألعاب",
        "cogs_pct": 0.10,
        "operating_pct": 0.45,
        "monthly_revenue_estimate": 250_000,
        "staff_range": (1, 3),
        "investment_range": (2_000_000, 7_000_000),
        "aapi_priority": 2,
        "profit_margin_target": 0.18,
        "working_capital_months": 1,
        "seasonal_factor": 1.15,
    },
    "plombier": {
        "name_fr": "Plombier / Installateur Sanitaire",
        "name_ar": "سباك / مouldi",
        "cogs_pct": 0.35,
        "operating_pct": 0.15,
        "monthly_revenue_estimate": 350_000,
        "staff_range": (1, 4),
        "investment_range": (1_000_000, 4_000_000),
        "aapi_priority": 2,
        "profit_margin_target": 0.25,
        "working_capital_months": 1,
        "seasonal_factor": 1.10,
    },
    "centre_services_num": {
        "name_fr": "Centre de Services Numériques",
        "name_ar": "مركز خدمات رقمية",
        "cogs_pct": 0.20,
        "operating_pct": 0.35,
        "monthly_revenue_estimate": 400_000,
        "staff_range": (2, 6),
        "investment_range": (2_000_000, 8_000_000),
        "aapi_priority": 2,
        "profit_margin_target": 0.20,
        "working_capital_months": 1,
        "seasonal_factor": 1.05,
    },
}


def get_defaults(business_type: str) -> dict:
    """Get pre-filled defaults for a business type. Raises KeyError if not found."""
    if business_type not in BUSINESS_DEFAULTS:
        available = ", ".join(BUSINESS_DEFAULTS.keys())
        raise KeyError(f"Unknown business type: {business_type}. Available: {available}")
    return BUSINESS_DEFAULTS[business_type]


def list_types() -> list[dict]:
    """List all available business types with key defaults."""
    return [
        {
            "key": k,
            "name_fr": v["name_fr"],
            "name_ar": v["name_ar"],
            "investment_range": v["investment_range"],
            "monthly_revenue": v["monthly_revenue_estimate"],
            "aapi_priority": v["aapi_priority"],
        }
        for k, v in BUSINESS_DEFAULTS.items()
    ]


def estimate_monthly_revenue(business_type: str, investment: int = None) -> int:
    """Estimate monthly revenue based on business type and investment level."""
    defaults = get_defaults(business_type)
    base = defaults["monthly_revenue_estimate"]
    if investment:
        min_inv, max_inv = defaults["investment_range"]
        if investment < min_inv:
            ratio = investment / min_inv
            base = int(base * ratio * 0.8)
        elif investment > max_inv:
            ratio = investment / max_inv
            base = int(base * ratio * 1.1)
    return base


def estimate_profitability(business_type: str, investment: int, monthly_revenue: int = None) -> dict:
    """Estimate key profitability metrics."""
    defaults = get_defaults(business_type)
    if monthly_revenue is None:
        monthly_revenue = estimate_monthly_revenue(business_type, investment)

    annual_revenue = monthly_revenue * 12
    cogs = int(annual_revenue * defaults["cogs_pct"])
    operating = int(annual_revenue * defaults["operating_pct"])
    gross_profit = annual_revenue - cogs
    net_profit_before_tax = gross_profit - operating
    net_profit_after_tax = int(net_profit_before_tax * 0.81)  # 19% corporate tax
    annual_margin = net_profit_after_tax / annual_revenue if annual_revenue else 0

    return {
        "annual_revenue": annual_revenue,
        "monthly_revenue": monthly_revenue,
        "annual_cogs": cogs,
        "annual_operating": operating,
        "gross_profit": gross_profit,
        "net_profit_before_tax": net_profit_before_tax,
        "net_profit_after_tax": net_profit_after_tax,
        "gross_margin": gross_profit / annual_revenue if annual_revenue else 0,
        "net_margin": annual_margin,
        "payback_years": investment / net_profit_after_tax if net_profit_after_tax > 0 else float("inf"),
        "roi_annual": net_profit_after_tax / investment if investment else 0,
    }
