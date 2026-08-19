# DSC — Digital Services Center Skill

## Identity
You are helping users generate professional Arabic/French bilingual documents for Algerian businesses using the DSC generator suite.

## Capabilities
All generators are in `C:\Users\Admin\projects\active\apps\digital-services-center\`. Import directly from these files.

### Document Generators (16 total)

| Generator | File | Class/Function | Purpose |
|-----------|------|----------------|---------|
| **Feasibility Study** | `feasibility_generator.py` | `FeasibilityGenerator.generate_full_study()` | 10-section Arabic PDF feasibility study (Decree 26-154) |
| **NESDA Dossier** | `nesda_dossier_generator.py` | `NESDADossierGenerator().generate()` | 9-part NESDA financing application dossier |
| **Business Plan** | `business_plan_generator.py` | `BusinessPlanGenerator().generate()` | Full business plan (5/7 years) |
| **BMC** | `bmc_generator.py` | `BMCGenerator().generate()` | Business Model Canvas (9 blocks) |
| **Market Research** | `market_research_generator.py` | `MarketResearchGenerator().generate()` | Market analysis report |
| **Marketing Plan** | `marketing_plan_generator.py` | `MarketingPlanGenerator().generate()` | Marketing strategy document |
| **Financial Projections** | `financial_projections_generator.py` | `FinancialProjectionsGenerator().generate()` | 5-year financial projections |
| **Invoice** | `invoice_generator.py` | `InvoiceGenerator.generate_invoice()` | Proforma invoices |
| **CV** | `cv_generator.py` | `CVGenerator().generate()` | Professional CV/resume |
| **Cover Letter** | `cover_letter_generator.py` | `CoverLetterGenerator().generate()` | Cover letter |
| **Social Media** | `social_media_generator.py` | `SocialMediaGenerator().generate()` | Social media content |
| **Tax Declaration** | `tax_declaration_generator.py` | `TaxDeclarationGenerator().generate()` | Tax declaration forms |

### Tax Form Generators (6 official DGI forms)

| Form | File | Class/Function | Purpose |
|------|------|----------------|---------|
| **G1 GGR** | `g1_ggr_generator.py` | `G1Data` + `generate_g1()` | Annual revenue declaration (IRG progressive barème) |
| **G4 IBS** | `g4_ibs_generator.py` | `G4Data` + `generate_g4()` | Corporate tax declaration |
| **G8** | `g8_existence_generator.py` | `G8Data` + `generate_g8()` | Business existence declaration |
| **G11 BIC** | `g11_bic_generator.py` | `G11Data` + `generate_g11()` | Industrial/commercial profits declaration |
| **G12** | `g12_generator.py` | `G12Data` + `generate_g12()` | IFU forecast declaration |
| **G29 IRG** | `g29_irg_salaires_generator.py` | `G29Data` + `generate_g29()` | Salary IRG annual declaration |
| **G50** | `g50_generator.py` | `G50Data` + `generate_g50()` | Monthly multi-tax declaration |

### Financial Calculators

| Calculator | File | Function | Purpose |
|-----------|------|----------|---------|
| **VAN (NPV)** | `financial_calculators.py` | `FinancialCalculators.van()` | Net Present Value at 12% |
| **TRI (IRR)** | `financial_calculators.py` | `FinancialCalculators.tri()` | Internal Rate of Return |
| **Break-even (units)** | `financial_calculators.py` | `FinancialCalculators.seuil_rentabilite()` | Break-even in units |
| **Break-even (DZD)** | `financial_calculators.py` | `FinancialCalculators.seuil_rentabilite_valeur()` | Break-even in DZD |
| **NESDA Financing** | `nesda_calculator.py` | `calculate_nesda_financing()` | NESDA loan terms (2%/12y/1.5y) |

### Verification

| Tool | File | Purpose |
|------|------|---------|
| **Rate Checker** | `verify_rates.py` | 30 automated rate verification checks |
| **Tests** | `tests/test_generators.py` | 47 generator tests |

## Usage Patterns

### Generate a Feasibility Study
```python
from feasibility_generator import FeasibilityGenerator
gen = FeasibilityGenerator()
result = gen.generate_full_study(params)  # Returns dict with sections
```

### Generate a NESDA Dossier
```python
from nesda_dossier_generator import NESDADossierGenerator
gen = NESDADossierGenerator()
result = gen.generate({
    'activity_key': 'restauration',
    'business_type': 'restaurant',
    'wilaya': 'Alger',
    'investment': 8_000_000,
    'client_name': 'Mohamed B.',
    'client_status': 'unemployed',
})
```

### Calculate VAN
```python
from financial_calculators import FinancialCalculators
cash_flows = [-5_000_000, 1_200_000, 1_200_000, 1_200_000, 1_200_000, 1_200_000]
van = FinancialCalculators.van(cash_flows)  # Returns float in DZD
```

### Generate G29 Salary IRG Form
```python
from g29_irg_salaires_generator import G29Data, generate_g29
data = G29Data(
    annee_imposition=2026,
    raison_sociale="SARL Example",
    employees=[{"nom": "Ben Ali", "salaire_brut": 80_000, "parts": 1}],
)
html = generate_g29(data)
```

## Critical Rate Constants (2026 verified)

```python
# NESDA Financing
NESDA_INTEREST_RATE = 0.02      # 2% (was 3%)
NESDA_REPAYMENT_YEARS = 12      # (was 10)
NESDA_GRACE_YEARS = 1.5         # (was 1)

# IRG G1 Revenue (annual, per part)
IRG_BAREME = [
    (120_000, 0.00),   # ≤120K: 0%
    (360_000, 0.20),   # 120K-360K: 20%
    (1_440_000, 0.30), # 360K-1.44M: 30%
    (float("inf"), 0.35),  # >1.44M: 35%
]

# IRG G29 Salary (monthly, per employee)
IRG_BAREME_MONTHLY = [
    (30_000, 0.00),    # ≤30K: 0% (exonéré)
    (120_000, 0.23),   # 30K-120K: 23%
    (360_000, 0.27),   # 120K-360K: 27%
    (float("inf"), 0.30),  # >360K: 30%
]

# SNMG (Salaire Minimum National Garanti)
SNMG_MONTHLY = 24_000  # DZD/month

# Tax Rates
TVA_NORMAL = 0.19      # 19%
TVA_REDUCED = 0.09     # 9%
IBS_INDUSTRY = 0.19    # 19%
IBS_SERVICES = 0.23    # 23%
CNAS_EMPLOYER = 0.255  # 25.5%
```

## Verification
```bash
python verify_rates.py          # 30 rate checks
python -m pytest tests/ -v     # 47 generator tests
```

## Compliance Notes
- All rates verified against 2026 Algerian law (mfdgi.gov.dz, CIDTA, LF 2026)
- VAN/TRI use single source of truth: `FinancialCalculators` class
- NESDA dossiers use 12% discount rate (was 10% — fixed 2026-08-19)
- Arabic PDFs require: ReportLab + Tahoma font + arabic_reshaper + python-bidi
