"""DSC REST API — FastAPI layer for all generators, calculators, auth, and billing.

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
  /auth/register       — Create account (email + password)
  /auth/login          — Login, returns JWT
  /auth/me             — Current user (requires Bearer token)
  /billing/plans       — List plans (public)
  /billing/checkout    — Create checkout (requires auth)
  /billing/webhook     — Gateway webhook (mock or Chargily/Stripe)
  /billing/me          — My subscription (requires auth)
"""

from __future__ import annotations

import importlib
import os
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# ── Imports from existing modules ─────────────────────────────────────────────

from g50_generator import G50Data, generate_g50, generate_g50_html, calculate_g50
from g4_ibs_generator import G4Data, generate_g4, calculate_g4
from g8_existence_generator import G8Data, generate_g8, generate_g8_html
from g1_ggr_generator import G1Data, generate_g1
from g11_bic_generator import G11Data, generate_g11, generate_g11_html
from g29_irg_salaires_generator import G29Data, generate_g29
from g13_bnc_generator import G13Input, calculate_g13, generate_g13_html
from cnrc_f1_generator import F1Data, AssocieData, calculate_f1, generate_f1
from das_cnas_generator import DASData, DASEmployee, calculate_das, generate_das
from secu01_generator import Secu01Data, calculate_secu01, generate_secu01
from anae_generator import AnaeData, calculate_anae, generate_anae
from g15_cessation_generator import G15Data, calculate_g15, generate_g15
from nis_generator import NisData, calculate_nis, generate_nis
from cnrc_f2_generator import F2Data, calculate_f2, generate_f2
from g4_rental_generator import RentalProperty, G4RentalData, calculate_g4_rental, generate_g4_rental

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
from auth import (
    LoginRequest, RegisterRequest, TokenResponse, UserOut,
    authenticate, create_token, create_user, get_current_user,
    get_current_user_optional, get_user_by_id,
)

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="DSC Digital Services Center API",
    description="REST API for Algerian tax forms, feasibility studies, pricing, and financial calculators.",
    version="1.0.0",
)

# Rate limiting — 60/min for expensive endpoints (quality, finance, pricing)
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(status_code=429, content={"detail": f"Rate limit exceeded: {exc.detail}"}))
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Billing router (auth tables are created on auth import)
try:
    from billing import router as billing_router
    app.include_router(billing_router)
except Exception as _e:
    # Billing is optional for offline .exe
    pass


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
    interest_rate: float = Field(0.0, ge=0, le=1)
    repayment_years: int = Field(7, ge=1, le=30)
    grace_years: int = Field(2, ge=0, le=10)


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
@limiter.limit("60/minute")
def pricing_quote(request: Request, req: PricingRequest):
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
@limiter.limit("60/minute")
def finance_van(request: Request, req: VANRequest):
    """Calculate VAN (Net Present Value)."""
    result = FinancialCalculators.van(req.cash_flows, req.discount_rate)
    return {"van": round(result, 2), "discount_rate": req.discount_rate}


@app.post("/finance/tri")
@limiter.limit("60/minute")
def finance_tri(request: Request, req: TRIRequest):
    """Calculate TRI (Internal Rate of Return)."""
    result = FinancialCalculators.tri(req.cash_flows)
    return {"tri_pct": round(result, 2)}


@app.post("/finance/seuil")
@limiter.limit("60/minute")
def finance_seuil(request: Request, req: SeuilRequest):
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
@limiter.limit("60/minute")
def finance_scenarios(request: Request, req: ScenarioRequest):
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


# ── Tax Forms: New Generators (G13 BNC, CNRC F1, DAS CNAS, SECU 01, ANAE) ────

@app.post("/tax/g13")
def tax_g13(req: TaxFormRequest):
    """Generate G13 BNC declaration — IRG for liberal professions."""
    try:
        form_data = _build_dataclass(G13Input, req.data)
        calc = calculate_g13(
            annual_revenue=form_data.annual_revenue,
            rent_expenses=form_data.rent_expenses,
            equipment_expenses=form_data.equipment_expenses,
            insurance_expenses=form_data.insurance_expenses,
            other_expenses=form_data.other_expenses,
            depreciation=form_data.depreciation,
            cascnos_contribution=form_data.cascnos_contribution,
            advance_payments=form_data.advance_payments,
        )
        calc = {**calc, "total_deductible_expenses": (
            form_data.rent_expenses + form_data.equipment_expenses
            + form_data.insurance_expenses + form_data.other_expenses
            + form_data.depreciation
            + (form_data.cascnos_contribution or form_data.annual_revenue * 0.15)
        )}
        html = generate_g13_html(form_data, calc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G13", html=html, calculations=calc)


@app.post("/tax/cnrc_f1")
def tax_cnrc_f1(req: TaxFormRequest):
    """Generate CNRC F1 — commercial registration (personne morale)."""
    try:
        form_data = _build_dataclass(F1Data, req.data)
        # associes arrive as list of dicts — build AssocieData objects
        if isinstance(req.data.get("associes"), list) and req.data["associes"] and all(isinstance(a, dict) for a in form_data.associes):
            form_data.associes = [_build_dataclass(AssocieData, a) for a in form_data.associes]
        html = generate_f1(form_data)
        calc = calculate_f1(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="CNRC_F1", html=html, calculations=calc)


@app.post("/tax/das_cnas")
def tax_das_cnas(req: TaxFormRequest):
    """Generate CNAS DAS — annual salary declaration."""
    try:
        form_data = _build_dataclass(DASData, req.data)
        if isinstance(form_data.salaries, list) and form_data.salaries and all(isinstance(s, dict) for s in form_data.salaries):
            form_data.salaries = [_build_dataclass(DASEmployee, s) for s in form_data.salaries]
        html = generate_das(form_data)
        calc = calculate_das(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="DAS_CNAS", html=html, calculations=calc)


@app.post("/tax/secu01")
@limiter.limit("60/minute")
def tax_secu01(request: Request, req: TaxFormRequest):
    """Generate CNAS SECU 01 — employer affiliation request."""
    try:
        form_data = _build_dataclass(Secu01Data, req.data)
        html = generate_secu01(form_data)
        calc = calculate_secu01(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="SECU01", html=html, calculations=calc)


@app.post("/tax/anae")
def tax_anae(req: TaxFormRequest):
    """Generate ANAE auto-entrepreneur activity declaration."""
    try:
        form_data = _build_dataclass(AnaeData, req.data)
        html = generate_anae(form_data)
        calc = calculate_anae(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="ANAE", html=html, calculations=calc)


@app.post("/tax/g15")
def tax_g15(req: TaxFormRequest):
    """Generate G15 — cessation d'activité declaration."""
    try:
        form_data = _build_dataclass(G15Data, req.data)
        html = generate_g15(form_data)
        calc = calculate_g15(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G15", html=html, calculations=calc)


@app.post("/tax/nis")
def tax_nis(req: TaxFormRequest):
    """Generate ONS NIS request form."""
    try:
        form_data = _build_dataclass(NisData, req.data)
        html = generate_nis(form_data)
        calc = calculate_nis(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="NIS", html=html, calculations=calc)


@app.post("/tax/cnrc_f2")
def tax_cnrc_f2(req: TaxFormRequest):
    """Generate CNRC F2 — commercial registration (personne physique)."""
    try:
        form_data = _build_dataclass(F2Data, req.data)
        html = generate_f2(form_data)
        calc = calculate_f2(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="CNRC_F2", html=html, calculations=calc)


@app.post("/tax/g4_rental")
def tax_g4_rental(req: TaxFormRequest):
    """Generate G4 — rental income declaration (revenus fonciers)."""
    try:
        form_data = _build_dataclass(G4RentalData, req.data)
        if isinstance(form_data.propriétés, list) and form_data.propriétés and all(isinstance(p, dict) for p in form_data.propriétés):
            form_data.propriétés = [_build_dataclass(RentalProperty, p) for p in form_data.propriétés]
        html = generate_g4_rental(form_data)
        calc = calculate_g4_rental(form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaxFormResponse(form_type="G4_RENTAL", html=html, calculations=calc)


# ── Quality Scoring ───────────────────────────────────────────────────────────

@app.post("/quality/score", response_model=QualityResponse)
@limiter.limit("60/minute")
def quality_score(request: Request, req: QualityRequest):
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


# ── Auth ─────────────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=TokenResponse)
def auth_register(req: RegisterRequest):
    """Create account and return JWT."""
    user = create_user(req.email, req.password, req.name)
    token = create_token(user.id, user.email)
    return TokenResponse(access_token=token, user=user)


@app.post("/auth/login", response_model=TokenResponse)
def auth_login(req: LoginRequest):
    """Login and return JWT."""
    user = authenticate(req.email, req.password)
    token = create_token(user.id, user.email)
    return TokenResponse(access_token=token, user=user)


@app.get("/auth/me", response_model=UserOut)
def auth_me(user: UserOut = Depends(get_current_user)):
    """Current user (requires Authorization: Bearer <token>)."""
    return user


# ── HTML Preview ──────────────────────────────────────────────────────────────

@app.get("/tax/g12/preview", response_class=HTMLResponse)
def tax_g12_preview():
    """Preview G12 form with sample data — now parity with G50/G11/G8."""
    data = G12FormData(nif="1234567890", nom_prenoms="Ahmed Test", activite_exercee="Commerce de détail", adresse_activite="Oran")
    return generate_g12_previsionnelle(data)


@app.get("/tax/g50/preview", response_class=HTMLResponse)
def tax_g50_preview():
    """Preview G50 form with sample data."""
    data = G50Data(nif="1234567890", nom_prenom="Mohamed Test SARL", activite="Commerce")
    return generate_g50_html(data)


@app.get("/tax/g4/preview", response_class=HTMLResponse)
def tax_g4_preview():
    """Preview G4 form with sample data."""
    data = G4Data(nif="1234567890", raison_sociale="SARL Test", forme_juridique="SARL", resultat_comptable=500000)
    return generate_g4(data)


@app.get("/tax/g11/preview", response_class=HTMLResponse)
def tax_g11_preview():
    """Preview G11 form with sample data."""
    data = G11Data(nif="1234567890", nom_prenoms="Ahmed Test", code_activite="4711")
    return generate_g11_html(data)


@app.get("/tax/g29/preview", response_class=HTMLResponse)
def tax_g29_preview():
    """Preview G29 form with sample data."""
    data = G29Data(nif="1234567890", raison_sociale="SARL Test", annee_imposition=2026)
    return generate_g29(data)


@app.get("/tax/g1/preview", response_class=HTMLResponse)
def tax_g1_preview():
    """Preview G1 form with sample data."""
    data = G1Data(nif="1234567890", nom_prenoms="Karim Test", situation_familiale="celibataire")
    return generate_g1(data)


@app.get("/tax/g8/preview", response_class=HTMLResponse)
def tax_g8_preview():
    """Preview G8 form with sample data."""
    data = G8Data(nif="1234567890", nom="Benali", prenom="Karim")
    return generate_g8_html(data)


# ── Previews: New Generators ─────────────────────────────────────────────────

@app.get("/tax/g13/preview", response_class=HTMLResponse)
def tax_g13_preview():
    """Preview G13 BNC form with sample data — consultant with 2M DA revenue."""
    data = G13Input(
        nif="123456789012345",
        nin="199603061234567890",
        name="Benali Ahmed",
        profession="Consultant",
        address="El Bayadh Centre, Wilaya d'El Bayadh",
        wilaya="32",
        year=2026,
        annual_revenue=2_000_000,
        cascnos_contribution=300_000,
        rent_expenses=240_000,
        equipment_expenses=50_000,
        insurance_expenses=30_000,
        other_expenses=20_000,
        depreciation=15_000,
        advance_payments=100_000,
        fait_a="El Bayadh",
        date_declaration="30/04/2026",
    )
    calc = calculate_g13(
        annual_revenue=data.annual_revenue,
        rent_expenses=data.rent_expenses,
        equipment_expenses=data.equipment_expenses,
        insurance_expenses=data.insurance_expenses,
        other_expenses=data.other_expenses,
        depreciation=data.depreciation,
        cascnos_contribution=data.cascnos_contribution,
        advance_payments=data.advance_payments,
    )
    calc = {**calc, "total_deductible_expenses": (
        data.rent_expenses + data.equipment_expenses
        + data.insurance_expenses + data.other_expenses + data.depreciation
        + (data.cascnos_contribution or data.annual_revenue * 0.15)
    )}
    return generate_g13_html(data, calc)


@app.get("/tax/cnrc_f1/preview", response_class=HTMLResponse)
def tax_cnrc_f1_preview():
    """Preview CNRC F1 form with sample data — SARL with two partners."""
    data = F1Data(
        wilaya="16-Alger",
        denomination="SARL TECH SOLUTIONS",
        forme_juridique="SARL",
        sigle="TS",
        objet_social="Développement logiciel et services informatiques",
        capital_social=1_000_000,
        apports_numeraire=800_000,
        apports_nature=200_000,
        adresse_siege="123 Rue Didouche Mourad",
        commune="Alger Centre",
        wilaya_siege="16-Alger",
        associes=[
            AssocieData(nom_prenom="Benali Ahmed", nin="196030612345678901", parts_sociales=600, pourcentage=60.0, fonction="Gérant"),
            AssocieData(nom_prenom="Mebarki Fatima", nin="198507212345678902", parts_sociales=400, pourcentage=40.0, fonction="Associée"),
        ],
        gerant_nom="Benali Ahmed",
        fait_a="Alger",
        date_declaration="15/01/2026",
    )
    return generate_f1(data)


@app.get("/tax/das_cnas/preview", response_class=HTMLResponse)
def tax_das_cnas_preview():
    """Preview CNAS DAS with sample data — employer with 3 employees."""
    data = DASData(
        agence_cnas="Agence CNAS El Bayadh",
        wilaya="32-El Bayadh",
        annee=2026,
        nif="1234567890A",
        raison_sociale="SARL TECH SOLUTIONS",
        activite="Prestation de services informatiques",
        salaries=[
            DASEmployee(nom_prenom="Benali Ahmed", nss="9603061234", categorie="Cadre", salaire_brut_annuel=720_000),
            DASEmployee(nom_prenom="Mebarki Fatima", nss="8507212345", categorie="Non-cadre", salaire_brut_annuel=420_000),
            DASEmployee(nom_prenom="Khelifi Youcef", nss="9205153456", categorie="Non-cadre", salaire_brut_annuel=300_000),
        ],
    )
    return generate_das(data)


@app.get("/tax/secu01/preview", response_class=HTMLResponse)
def tax_secu01_preview():
    """Preview SECU 01 affiliation form with sample data."""
    data = Secu01Data(
        agence_cnas="Agence CNAS El Bayadh",
        wilaya="32-El Bayadh",
        nif="1234567890A",
        rc="16/00-1234567B21",
        raison_sociale="SARL TECH SOLUTIONS",
        forme_juridique="SARL",
        activite="Prestation de services informatiques",
        adresse="123 Rue Didouche Mourad",
        commune="El Bayadh",
        date_debut_activite="01/01/2026",
        date_premier_emploi="01/03/2026",
        effectif_prevu=3,
        salaire_mensuel_estime=60_000,
        representant_nom="Benali Ahmed",
        representant_qualite="Gérant",
        fait_a="El Bayadh",
        date_declaration="15/02/2026",
    )
    return generate_secu01(data)


@app.get("/tax/anae/preview", response_class=HTMLResponse)
def tax_anae_preview():
    """Preview ANAE auto-entrepreneur declaration with sample data."""
    data = AnaeData(
        antenne_anae="Antenne ANAE El Bayadh",
        wilaya="32-El Bayadh",
        nom_prenom="Mahi Kamel Abdelghani",
        nin="199603061234567890",
        type_activite="Services",
        secteur="Numérique (développement, design, marketing digital)",
        description_activite="Développement web et mobile, conseil en transformation numérique",
        ca_annuel_prevu=1_800_000,
        casnos_affiliation=True,
        fait_a="El Bayadh",
        date_declaration="15/01/2026",
    )
    return generate_anae(data)


# ── Previews: Batch 3 ────────────────────────────────────────────────────────

@app.get("/tax/g15/preview", response_class=HTMLResponse)
def tax_g15_preview():
    """Preview G15 cessation declaration with sample data."""
    data = G15Data(
        wilaya="32-El Bayadh",
        diw="DIW d'El Bayadh",
        inspection="Inspection des Impôts d'El Bayadh Centre",
        nif="123456789012345",
        rc="32/00-7654321B18",
        nom_raison_sociale="Entreprise Mahi Travaux",
        forme_juridique="Personne physique",
        activite="Travaux de plomberie générale",
        adresse_activite="Centre-ville, El Bayadh",
        regime_fiscal="Régime réel simplifié",
        date_debut_activite="01/06/2018",
        date_cessation="31/12/2026",
        fait_a="El Bayadh",
        date_declaration="10/01/2027",
    )
    return generate_g15(data)


@app.get("/tax/nis/preview", response_class=HTMLResponse)
def tax_nis_preview():
    """Preview ONS NIS request with sample data."""
    data = NisData(
        delegation_ons="Délégation ONS El Bayadh",
        wilaya="32-El Bayadh",
        nom_raison_sociale="Entreprise Mahi Travaux",
        forme_juridique="Personne physique",
        nif="123456789012345",
        rc="32/00-7654321B18",
        date_rc="15/06/2018",
        activite_principale="Travaux de plomberie générale",
        code_activite_detail="Installation sanitaires bâtiment",
        adresse="Centre-ville",
        commune="El Bayadh",
        phone="+213 661 23 45 67",
        email="contact@mahitravaux.dz",
        effectif_salarie=4,
        representant_nom="Mahi Kamel Abdelghani",
        representant_nin="199603061234567890",
        fait_a="El Bayadh",
        date_declaration="20/06/2018",
    )
    return generate_nis(data)


@app.get("/tax/cnrc_f2/preview", response_class=HTMLResponse)
def tax_cnrc_f2_preview():
    """Preview CNRC F2 individual merchant registration with sample data."""
    data = F2Data(
        wilaya="32-El Bayadh",
        centre_cnrc="CNRC — guichet El Bayadh",
        nom="Mahi",
        prenom="Kamel Abdelghani",
        nin="199603061234567890",
        date_naissance="06/03/1996",
        lieu_naissance="El Bayadh",
        situation_matrimoniale="Marié(e)",
        regime_matrimonial="Séparation de biens",
        nom_commercial="Épicerie El Baraka",
        activite="Commerce de détail alimentaire général",
        adresse_personnelle="Centre-ville, El Bayadh",
        adresse_commerce="Rue de la République, El Bayadh",
        commune_commerce="El Bayadh",
        nature_local="Local loué",
        duree_bail_annees=5,
        fait_a="El Bayadh",
        date_declaration="10/02/2026",
    )
    return generate_f2(data)


@app.get("/tax/g4_rental/preview", response_class=HTMLResponse)
def tax_g4_rental_preview():
    """Preview G4 rental income declaration with sample data — 3 properties."""
    data = G4RentalData(
        wilaya="32-El Bayadh",
        diw="DIW d'El Bayadh",
        nif="123456789012345",
        nin="199603061234567890",
        nom_prenom="Mahi Kamel Abdelghani",
        adresse="Centre-ville, El Bayadh",
        annee=2026,
        acomptes_retenus=24_000,
        fait_a="El Bayadh",
        date_declaration="15/04/2027",
        propriétés=[
            RentalProperty(adresse="Appartement A, Rue X", nature="Logement (habitation)", loyer_mensuel=25_000, mois_loues=12),
            RentalProperty(adresse="Local commercial Rue Y", nature="Local commercial", loyer_mensuel=40_000, mois_loues=9),
            RentalProperty(adresse="Dépôt zone Z", nature="Local industriel / dépôt", loyer_mensuel=15_000, mois_loues=12),
        ],
    )
    return generate_g4_rental(data)


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DSC_API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
