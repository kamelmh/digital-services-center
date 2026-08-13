"""DSC REST API — FastAPI layer for all generators and calculators.

Endpoints:
  /health              — Health check
  /services            — List all service catalog entries
  /pricing/quote       — Generate instant pricing quote
  /nesda/calculate     — NESDA financing calculator
  /finance/van         — VAN (NPV) calculation
  /finance/tri         — TRI (IRR) calculation
  /finance/seuil       — Break-even point
  /finance/scenarios   — 3-scenario projection
  /tax/g12             — G12 IFU declaration
  /tax/g50             — G50 monthly declaration
  /tax/g4              — G4 IBS annual declaration
  /tax/g11             — G11 BIC declaration
  /tax/g29             — G29/G30 IRG salaries
  /tax/g1              — G1 general income declaration
  /tax/g8              — G8 existence declaration
  /quality/score       — Quality scoring for generated content
"""

from __future__ import annotations

import importlib
import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# ── Imports from existing modules ─────────────────────────────────────────────

from g50_generator import G50Data, generate_g50, generate_g50_html, calculate_g50
from g4_ibs_generator import G4Data, generate_g4, calculate_g4
from g8_existence_generator import G8Data, generate_g8, generate_g8_html
from g1_ggr_generator import G1Data, generate_g1
from g11_bic_generator import G11Data, generate_g11, generate_g11_html
from g29_irg_salaires_generator import G29Data, generate_g29

# g12 functions have Unicode names — import via getattr
_g12 = importlib.import_module("g12_official")
G12FormData = _g12.G12FormData
generate_g12_previsionnelle = getattr(_g12, "generate_g12_prévisionnelle")
generate_g12_definitive = getattr(_g12, "generate_g12_définitive")
calculate_g12 = _g12.calculate_g12
from pricing_calculator import SERVICES, PACKAGES, calculate_quote, PricingQuote
from nesda_calculator import calculate_nesda_financing, NESDAFinancingResult
from financial_calculators import (
    FinancialCalculators,
    CashFlow,
    InvestmentPlan,
    FinancingPlan,
    generate_3_scenarios,
)
from quality_scorer import QualityScorer, score_all, format_report

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="DSC Digital Services Center API",
    description="REST API for Algerian tax forms, feasibility studies, pricing, and financial calculators.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Schemas (request / response) ────────────────────────────────────

# Health
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    modules: list[str] = []


# Services catalog
class ServiceEntry(BaseModel):
    key: str
    name_fr: str
    name_ar: str
    price_min: int
    price_max: int
    delivery_days: int
    category: str
    includes: list[str]


class PackageEntry(BaseModel):
    key: str
    name_fr: str
    name_ar: str
    services: list[str]
    discount: int
    price_label: str


# Pricing
class PricingRequest(BaseModel):
    service_keys: list[str] = Field(..., description="List of service keys from catalog")
    custom_prices: dict[str, int] | None = Field(None, description="Override price per service key")
    discount_pct: float = Field(0, ge=0, le=100)
    deposit_pct: float = Field(50, ge=0, le=100)
    validity_days: int = Field(30, ge=1)
    client_name: str = ""
    client_phone: str = ""


class PricingResponse(BaseModel):
    services: list[dict]
    subtotal: int
    discount_pct: float
    discount_amount: int
    total: int
    deposit_pct: float
    deposit_amount: int
    balance: int
    validity_days: int
    estimated_delivery: str
    payment_terms: list[str]
    whatsapp_message: str
    whatsapp_url: str


# NESDA
class NESDARequest(BaseModel):
    total_cost: int = Field(..., gt=0, description="Total project cost in DZD")
    model: str = Field("triangular", description="triangular | mixed | self")
    profile: str = Field("unemployed", description="unemployed | employed")
    monthly_revenue: int = Field(500_000, gt=0)
    cogs_pct: float = Field(0.65, ge=0, le=1)
    operating_pct: float = Field(0.15, ge=0, le=1)
    interest_rate: float = Field(0.03, ge=0, le=1)
    repayment_years: int = Field(10, ge=1, le=30)
    grace_years: int = Field(1, ge=0, le=10)


class NESDAResponse(BaseModel):
    total_cost: int
    personal_amount: int
    nesda_grant: int
    bank_loan: int
    personal_pct: float
    nesda_pct: float
    bank_pct: float
    interest_rate: float
    repayment_years: int
    grace_years: int
    annual_payment: float
    monthly_payment: float
    total_interest: float
    total_repayment: float
    schedule: list[dict]
    monthly_revenue: int
    monthly_costs: int
    monthly_profit: int
    payback_months: int
    roi_annual: float


# Financial calculators
class VANRequest(BaseModel):
    cash_flows: list[float] = Field(..., min_length=2, description="Year 0 = investment (negative), then annual cash flows")
    discount_rate: float = Field(0.12, gt=0, description="Discount rate (default 12%)")


class TRIRequest(BaseModel):
    cash_flows: list[float] = Field(..., min_length=2)


class SeuilRequest(BaseModel):
    fixed_costs: float = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)
    variable_cost_per_unit: float = Field(..., ge=0)


class ScenarioRequest(BaseModel):
    base_revenue: float = Field(..., gt=0, description="Annual base revenue in DZD")
    base_cogs_rate: float = Field(0.40, ge=0, le=1, description="COGS as fraction of revenue")
    base_operating_rate: float = Field(0.15, ge=0, le=1, description="Operating costs as fraction of revenue")
    equipment: float = Field(0, ge=0)
    buildings: float = Field(0, ge=0)
    engineering: float = Field(0, ge=0)
    working_capital: float = Field(0, ge=0)
    land: float = Field(0, ge=0)
    equity: float = Field(0, ge=0)
    bank_loan: float = Field(0, ge=0)
    loan_rate: float = Field(0.09, ge=0, le=1)
    loan_years: int = Field(7, ge=1)
    years: int = Field(5, ge=1, le=20)


# Tax form schemas — using Dict[str, Any] for flexibility since
# the underlying dataclasses have many fields with defaults.
class TaxFormRequest(BaseModel):
    data: dict[str, Any] = Field(..., description="Form data as key-value pairs matching the generator dataclass fields")


class TaxFormResponse(BaseModel):
    form_type: str
    html: str
    calculations: dict[str, Any] | None = None


class QualityRequest(BaseModel):
    generator: str = Field(..., description="Generator name for scoring context")
    content: str = Field(..., description="HTML or text content to score")
    metadata: dict[str, Any] | None = None


class QualityCheckResult(BaseModel):
    name: str
    passed: bool
    score: float
    detail: str


class QualityResponse(BaseModel):
    generator: str
    overall_score: float
    grade: str
    passed: bool
    checks: list[QualityCheckResult]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health():
    """Health check with module availability."""
    modules = []
    for mod in ["g50_generator", "g12_official", "g4_ibs_generator",
                "g8_existence_generator", "g1_ggr_generator", "g11_bic_generator",
                "g29_irg_salaires_generator", "pricing_calculator", "nesda_calculator",
                "financial_calculators", "quality_scorer"]:
        try:
            __import__(mod)
            modules.append(mod)
        except ImportError:
            pass
    return HealthResponse(modules=modules)


@app.get("/services", response_model=dict[str, ServiceEntry])
def list_services():
    """List all available services from the pricing catalog."""
    return {
        k: ServiceEntry(
            key=k,
            name_fr=v["name_fr"],
            name_ar=v["name_ar"],
            price_min=v["price_min"],
            price_max=v["price_max"],
            delivery_days=v["delivery_days"],
            category=v["category"],
            includes=v["includes"],
        )
        for k, v in SERVICES.items()
    }


@app.get("/packages", response_model=dict[str, PackageEntry])
def list_packages():
    """List all available package deals."""
    return {
        k: PackageEntry(
            key=k,
            name_fr=v["name_fr"],
            name_ar=v["name_ar"],
            services=v["services"],
            discount=v["discount"],
            price_label=v["price_label"],
        )
        for k, v in PACKAGES.items()
    }


# ── Pricing ───────────────────────────────────────────────────────────────────

@app.post("/pricing/quote", response_model=PricingResponse)
def pricing_quote(req: PricingRequest):
    """Generate an instant pricing quote with WhatsApp message."""
    try:
        result = calculate_quote(
            service_keys=req.service_keys,
            custom_prices=req.custom_prices,
            discount_pct=req.discount_pct,
            deposit_pct=req.deposit_pct,
            validity_days=req.validity_days,
            client_name=req.client_name,
            client_phone=req.client_phone,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PricingResponse(
        services=result.services,
        subtotal=result.subtotal,
        discount_pct=result.discount_pct,
        discount_amount=result.discount_amount,
        total=result.total,
        deposit_pct=result.deposit_pct,
        deposit_amount=result.deposit_amount,
        balance=result.balance,
        validity_days=result.validity_days,
        estimated_delivery=result.estimated_delivery,
        payment_terms=result.payment_terms,
        whatsapp_message=result.whatsapp_message,
        whatsapp_url=result.whatsapp_url,
    )


# ── NESDA ─────────────────────────────────────────────────────────────────────

@app.post("/nesda/calculate", response_model=NESDAResponse)
def nesda_calculate(req: NESDARequest):
    """Calculate NESDA financing breakdown (triangular, mixed, self)."""
    try:
        result = calculate_nesda_financing(
            total_cost=req.total_cost,
            model=req.model,
            profile=req.profile,
            monthly_revenue=req.monthly_revenue,
            cogs_pct=req.cogs_pct,
            operating_pct=req.operating_pct,
            interest_rate=req.interest_rate,
            repayment_years=req.repayment_years,
            grace_years=req.grace_years,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return NESDAResponse(
        total_cost=result.total_cost,
        personal_amount=result.personal_amount,
        nesda_grant=result.nesda_grant,
        bank_loan=result.bank_loan,
        personal_pct=result.personal_pct,
        nesda_pct=result.nesda_pct,
        bank_pct=result.bank_pct,
        interest_rate=result.interest_rate,
        repayment_years=result.repayment_years,
        grace_years=result.grace_years,
        annual_payment=result.annual_payment,
        monthly_payment=result.monthly_payment,
        total_interest=result.total_interest,
        total_repayment=result.total_repayment,
        schedule=result.schedule,
        monthly_revenue=result.monthly_revenue,
        monthly_costs=result.monthly_costs,
        monthly_profit=result.monthly_profit,
        payback_months=result.payback_months,
        roi_annual=result.roi_annual,
    )


# ── Financial Calculators ─────────────────────────────────────────────────────

@app.post("/finance/van")
def finance_van(req: VANRequest):
    """Calculate VAN (Net Present Value)."""
    result = FinancialCalculators.van(req.cash_flows, req.discount_rate)
    return {"van": round(result, 2), "discount_rate": req.discount_rate}


@app.post("/finance/tri")
def finance_tri(req: TRIRequest):
    """Calculate TRI (Internal Rate of Return)."""
    result = FinancialCalculators.tri(req.cash_flows)
    return {"tri_pct": round(result, 2)}


@app.post("/finance/seuil")
def finance_seuil(req: SeuilRequest):
    """Calculate break-even point (units and DZD)."""
    units = FinancialCalculators.seuil_rentabilite(
        req.fixed_costs, req.price_per_unit, req.variable_cost_per_unit
    )
    contribution_margin = req.price_per_unit - req.variable_cost_per_unit
    dzd = FinancialCalculators.seuil_rentabilite_valeur(
        req.fixed_costs,
        contribution_margin / req.price_per_unit if req.price_per_unit > 0 else 0,
    )
    return {
        "units": round(units, 0) if units != float("inf") else None,
        "dzd": round(dzd, 0) if dzd != float("inf") else None,
        "contribution_margin": round(contribution_margin, 2),
    }


@app.post("/finance/scenarios")
def finance_scenarios(req: ScenarioRequest):
    """Generate prudent / reference / favorable scenario projections."""
    try:
        investment = InvestmentPlan(
            equipment=req.equipment,
            buildings=req.buildings,
            engineering=req.engineering,
            working_capital=req.working_capital,
            land=req.land,
        )
        financing = FinancingPlan(
            equity=req.equity,
            bank_loan=req.bank_loan,
            loan_rate=req.loan_rate,
            loan_years=req.loan_years,
        )
        result = generate_3_scenarios(
            base_revenue=req.base_revenue,
            base_cogs_rate=req.base_cogs_rate,
            base_operating_rate=req.base_operating_rate,
            investment=investment,
            financing=financing,
            years=req.years,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ── Tax Forms ─────────────────────────────────────────────────────────────────

def _build_dataclass(cls, data: dict[str, Any]):
    """Build a dataclass from a dict, ignoring unknown keys."""
    import dataclasses
    valid_fields = {f.name for f in dataclasses.fields(cls)}
    filtered = {k: v for k, v in data.items() if k in valid_fields}
    return cls(**filtered)


@app.post("/tax/g12")
def tax_g12(req: TaxFormRequest):
    """Generate G12 IFU declaration (prévisionnelle or définitive)."""
    is_definitive = req.data.pop("is_definitive", False)
    try:
        form_data = _build_dataclass(G12FormData, req.data)
        if is_definitive:
            html = generate_g12_definitive(form_data)
        else:
            html = generate_g12_previsionnelle(form_data)
        calc = calculate_g12(form_data, is_definitive=is_definitive)
        calc_dict = {k: v for k, v in calc.__dict__.items()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G12", html=html, calculations=calc_dict)


@app.post("/tax/g50")
def tax_g50(req: TaxFormRequest):
    """Generate G50 monthly declaration."""
    try:
        form_data = _build_dataclass(G50Data, req.data)
        html = generate_g50(form_data)
        result = calculate_g50(form_data)
        calc_dict = {k: v for k, v in result.__dict__.items()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G50", html=html, calculations=calc_dict)


@app.post("/tax/g4")
def tax_g4(req: TaxFormRequest):
    """Generate G4 IBS annual declaration."""
    try:
        form_data = _build_dataclass(G4Data, req.data)
        html = generate_g4(form_data)
        calc = calculate_g4(form_data)
        calc_dict = {k: v for k, v in calc.__dict__.items()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G4", html=html, calculations=calc_dict)


@app.post("/tax/g11")
def tax_g11(req: TaxFormRequest):
    """Generate G11 BIC declaration."""
    try:
        form_data = _build_dataclass(G11Data, req.data)
        html = generate_g11(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G11", html=html)


@app.post("/tax/g29")
def tax_g29(req: TaxFormRequest):
    """Generate G29/G30 IRG salaries declaration."""
    try:
        form_data = _build_dataclass(G29Data, req.data)
        html = generate_g29(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G29", html=html)


@app.post("/tax/g1")
def tax_g1(req: TaxFormRequest):
    """Generate G1 general income declaration."""
    try:
        form_data = _build_dataclass(G1Data, req.data)
        html = generate_g1(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G1", html=html)


@app.post("/tax/g8")
def tax_g8(req: TaxFormRequest):
    """Generate G8 existence declaration."""
    try:
        form_data = _build_dataclass(G8Data, req.data)
        html = generate_g8(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G8", html=html)


# ── Quality Scoring ───────────────────────────────────────────────────────────

@app.post("/quality/score", response_model=QualityResponse)
def quality_score(req: QualityRequest):
    """Score generated content for quality (word count, sections, specificity, language, structure)."""
    scorer = QualityScorer()
    report = scorer.score(req.generator, req.content, req.metadata)
    return QualityResponse(
        generator=report.generator,
        overall_score=round(report.overall_score, 3),
        grade=report.grade,
        passed=report.passed,
        checks=[
            QualityCheckResult(
                name=c.name, passed=c.passed, score=round(c.score, 3), detail=c.detail
            )
            for c in report.checks
        ],
    )


# ── HTML Preview ──────────────────────────────────────────────────────────────

@app.get("/tax/g50/preview", response_class=HTMLResponse)
def tax_g50_preview():
    """Preview G50 form with sample data."""
    data = G50Data(nif="1234567890", nom_prenom="Mohamed Test SARL", activite="Commerce")
    return generate_g50_html(data)


@app.get("/tax/g11/preview", response_class=HTMLResponse)
def tax_g11_preview():
    """Preview G11 form with sample data."""
    data = G11Data(nif="1234567890", nom_prenoms="Ahmed Test", code_activite="4711")
    return generate_g11_html(data)


@app.get("/tax/g8/preview", response_class=HTMLResponse)
def tax_g8_preview():
    """Preview G8 form with sample data."""
    data = G8Data(nif="1234567890", nom="Benali", prenom="Karim")
    return generate_g8_html(data)


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DSC_API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
