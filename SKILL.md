# DSC — Digital Services Center Skill

## Identity
You are helping users generate professional Arabic/French bilingual documents for Algerian businesses using the DSC generator suite.

## Capabilities
All generators are in `C:\Users\Admin\projects\active\apps\digital-services-center\`. Import directly from these files.

### Document Generators (12 total)

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

### Tax Form Generators (20 official DGI/CNAS/CASNOS/CNRC/ONS/ANAE forms)

| Form | File | Class/Function | Purpose |
|------|------|----------------|---------|
| **G1 GGR** | `g1_ggr_generator.py` | `G1Data` + `generate_g1()` | Annual revenue declaration (6-tranche IRG barème) |
| **G4 IBS** | `g4_ibs_generator.py` | `G4Data` + `generate_g4()` | Corporate tax declaration |
| **G4 Rental** | `g4_rental_generator.py` | `G4RentalData` + `generate_g4_rental()` | Rental income (30% abattement, 6-tranche IRG) |
| **G8** | `g8_existence_generator.py` | `G8Data` + `generate_g8()` | Business existence declaration |
| **G11 BIC** | `g11_bic_generator.py` | `G11Data` + `generate_g11()` | Industrial/commercial profits (regime reel, 6-tranche IRG) |
| **G12** | `g12_official.py` | `G12Data` + `generate_g12()` | IFU forecast declaration |
| **G12 bis** | `g12_bis_generator.py` | `G12BisData` + `generate_g12_bis()` | IFU final declaration |
| **G13 BNC** | `g13_bnc_generator.py` | `G13Data` + `generate_g13()` | Non-commercial professions IRG |
| **G15** | `g15_cessation_generator.py` | `G15Data` + `generate_g15()` | Business cessation declaration |
| **G29 IRG** | `g29_irg_salaires_generator.py` | `G29Data` + `generate_g29()` | Salary IRG annual declaration (monthly barème) |
| **G50** | `g50_generator.py` | `G50Data` + `generate_g50()` | Monthly multi-tax declaration |
| **G51** | `g51_generator.py` | `G51Data` + `generate_g51()` | Tax clearance certificate |
| **CNRC F1** | `cnrc_f1_generator.py` | `CNRCF1Data` + `generate_cnrc_f1()` | Commercial registration (companies) |
| **CNRC F2** | `cnrc_f2_generator.py` | `CNRCF2Data` + `generate_cnrc_f2()` | Commercial registration (individual traders) |
| **DAS** | `das_cnas_generator.py` | `DASData` + `generate_das()` | CNAS annual salary declaration |
| **SECU 01** | `secu01_generator.py` | `Secu01Data` + `generate_secu01()` | CNAS employer affiliation |
| **NIS** | `nis_generator.py` | `NISData` + `generate_nis()` | ONS statistical identification |
| **ANAE** | `anae_generator.py` | `ANAEData` + `generate_anae()` | Auto-entrepreneur declaration |
| **CASNOS Affil.** | `casnos_affiliation_generator.py` | `CASNOSAffilData` + `generate_casnoss_affiliation()` | Self-employed enrollment |
| **CASNOS CA** | `casnos_ca_generator.py` | `CASNOSCAData` + `generate_casnoss_ca()` | Annual turnover declaration |

### Financial Calculators

| Calculator | File | Function | Purpose |
|-----------|------|----------|---------|
| **VAN (NPV)** | `financial_calculators.py` | `FinancialCalculators.van()` | Net Present Value at 12% |
| **TRI (IRR)** | `financial_calculators.py` | `FinancialCalculators.tri()` | Internal Rate of Return |
| **Break-even (units)** | `financial_calculators.py` | `FinancialCalculators.seuil_rentabilite()` | Break-even in units |
| **Break-even (DZD)** | `financial_calculators.py` | `FinancialCalculators.seuil_rentabilite_valeur()` | Break-even in DZD |
| **NESDA Financing** | `nesda_calculator.py` | `calculate_nesda_financing()` | NESDA loan terms (0% bonified / 7y / 1.5y grace) |
| **Offline Engine** | `offline_templates.py` | `*_offline()` | 7 deterministic fallbacks — 100% offline sellable |

### Verification

| Tool | File | Purpose |
|------|------|---------|
| **Rate Checker** | `verify_rates.py` | 67 automated rate checks (non-self-affirming: `policy_constants` vs `REVIEWED_2026_IRG_ANNUAL` snapshot, Sprint 8) |
| **Tests** | `tests/test_generators.py` | 164 generator tests (+3 PG-only RLS, 1 skipped) |
| **Fonts** | `assets/fonts/Tahoma*.ttf` | Bundled for exe portability (no system dependency) |

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

## Critical Rate Constants (2026 verified — RESEARCH_2026.md, 11 sources)

```python
# NESDA Financing (bonified 100% — NESDA DG + CPA Bank, 2026-08-20)
NESDA_INTEREST_RATE = 0.00      # 0% (bonified, was 2%)
NESDA_REPAYMENT_YEARS = 7       # 7y (5y repayment + 1.5y grace via CPA)
NESDA_GRACE_YEARS = 1.5
NESDA_MAX = 10_000_000          # DZD max financing
# Offline: offline_templates.py uses these same values (deterministic)

# IRG — 6-tranche progressive (LF 2026, Art. 104 CIDTA — 2026-08-20)
IRG_BAREME = [  # annual, per part (G1 GGR)
    (240_000, 0.00),     # ≤240K: 0%
    (480_000, 0.23),     # 240K-480K: 23%
    (960_000, 0.27),     # 480K-960K: 27%
    (1_920_000, 0.30),   # 960K-1.92M: 30%
    (3_840_000, 0.33),   # 1.92M-3.84M: 33%
    (float("inf"), 0.35),# >3.84M: 35%
]
IRG_BAREME_MONTHLY = [  # monthly (G29/G30 IRG salaires)
    (20_000, 0.00),      # ≤20K: 0%
    (40_000, 0.23),      # 20K-40K: 23%
    (80_000, 0.27),      # 40K-80K: 27%
    (160_000, 0.30),     # 80K-160K: 30%
    (320_000, 0.33),     # 160K-320K: 33%
    (float("inf"), 0.35),# >320K: 35%
]

# SNMG / Wages
SNMG_MONTHLY = 24_000    # DZD/month (DP 26-01, Jan 2026)
# CNAS: salarié 9%, employeur 25.5% (+0.5% œuvres = 26% total patronal)

# Tax Rates (Art. 150 CIDTA, LF 2026)
TVA_NORMAL = 0.19        # 19% (taux normal)
TVA_REDUCED = 0.09       # 9%  (taux réduit)
IBS_PRODUCTION = 0.19    # 19% production
IBS_BTP_TOURISM = 0.23   # 23% BTP/tourisme
IBS_SERVICES = 0.26      # 26% commerce/services (was 23% — corrected 2026-08-20)
CNAS_EMPLOYER = 0.255    # 25.5% (26% with œuvres sociales)
# Discount rate for VAN: 12% (single source: FinancialCalculators.van)
```

## Verification
```bash
python verify_rates.py --strict # 67 rate checks (non-self-affirming: policy_constants vs reviewed snapshot, Sprint 8)
python -m pytest tests/ -v     # 164 generator tests
# new: python -c "from offline_templates import feasibility_offline; ..."
```

## Compliance Notes
- All rates verified against 2026 Algerian law (mfdgi.gov.dz, CIDTA, LF 2026)
- VAN/TRI use single source of truth: `FinancialCalculators` class
- NESDA dossiers use 12% discount rate (was 10% — fixed 2026-08-19)
- Arabic PDFs require: ReportLab + Tahoma font + arabic_reshaper + python-bidi
