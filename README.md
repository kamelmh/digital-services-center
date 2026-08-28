# DSC — Digital Services Center

**مركز الخدمات الرقمية** — Professional feasibility studies, tax declarations, and business documents for Algerian entrepreneurs.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Violit app (30 pages)
cd violit-app && violit run main.py

# Generate a tax form (no API key needed)
python g50_generator.py --html

# Generate a PDF
python -c "
from g50_generator import G50Data, generate_g50_html
from tax_form_pdf_exporter import generate_tax_pdf
data = G50Data(nif='123', nom_prenom='Test', activite='Commerce', commune='El Bayadh', wilaya='32', month=6, year=2026)
pdf = generate_tax_pdf('g50', data)
open('test.pdf', 'wb').write(pdf)
print('PDF saved')
"
```

## What's Built

### Tax Form Generators (20 forms, template-based, no LLM)
| Form | Purpose | Price Range |
|------|---------|-------------|
| G1 | GGR (Personal Income, 6-tranche IRG) | 3,000–6,000 DA |
| G4 IBS | IBS Annual Corporate Tax | 8,000–15,000 DA |
| G4 Rental | Revenus Locatifs (rental income, 30% abattement) | 3,000–6,000 DA |
| G8 | Business Existence (NIF declaration) | 2,000–4,000 DA |
| G11 | BIC Régime Réel (6-tranche IRG) | 8,000–15,000 DA |
| G12 | IFU Declaration (Prévisionnelle) | 3,000–5,000 DA |
| G12 bis | IFU Final Declaration (Définitive) | 3,000–5,000 DA |
| G13 | IRG Professions Non Commerciales (BNC) | 5,000–10,000 DA |
| G15 | Cessation d'Activité (business closure) | 2,000–4,000 DA |
| G29/G30 | IRG Salary Declaration (monthly barème) | 5,000–10,000 DA |
| G50 | Monthly Multi-Tax (TVA/IRG/IBS/Timbre) | 5,000–8,000 DA |
| G51 | Attestation Fiscale (tax clearance) | 3,000–5,000 DA |
| CNRC F1 | Commercial Registration (companies) | 10,000–20,000 DA |
| CNRC F2 | Commercial Registration (individual traders) | 5,000–10,000 DA |
| DAS | CNAS Annual Salary Declaration | 5,000–10,000 DA |
| SECU 01 | CNAS Employer Affiliation | 3,000–5,000 DA |
| NIS | ONS Statistical Identification | 2,000–4,000 DA |
| ANAE | Auto-Entrepreneur Declaration | 3,000–5,000 DA |
| CASNOS Affil. | Self-Employed Social Security Enrollment | 3,000–5,000 DA |
| CASNOS CA | Self-Employed Annual Turnover Declaration | 2,000–4,000 DA |

### Business Document Generators
| Generator | Purpose | LLM Required? |
|-----------|---------|---------------|
| Feasibility Study | 9-part Decree 26-154 compliant | Yes (Groq) |
| Business Plan | Full business plan | Yes (Groq) |
| NESDA Dossier | NESDA financing application | Yes (Groq) |
| CV / Cover Letter | Professional documents | No |
| Invoice / Quote | Business documents | No |
| AAPI Optimizer | 1,500-point scoring | No |
| NESDA Eligibility | 5-check eligibility | No |
| NESDA Calculator | Triangular financing | No |

### Violit App (30 pages)
```bash
cd violit-app && violit run main.py
```
Full web interface for all generators with PDF export.

### GitHub Pages Site (5 pages)
```bash
# Deploy to GitHub Pages
# Push docs/ folder, enable Pages in repo settings
```
- Landing page, services catalog, tax forms guide, order form, contact

## Architecture

```
Input (User) → Generator (Python) → HTML/PDF Output
                    ↓
            Quality Scorer → Service Orchestrator → Unified PDF
                    ↓
            Training Data Collector (for future improvement)
```

**Key principle**: Tax form generators are 100% template-based (no API keys needed). Only feasibility/business plan/NESDA generators use LLM.

## File Structure

```
digital-services-center/
├── violit-app/main.py          # 30-page web interface
├── docs/                        # GitHub Pages marketing site (5 pages)
├── brand/                       # SVG logos, PNG exports, post graphics
│   ├── assets/                  # Logo variants (flat, hexagon)
│   ├── png-exports/             # All PNG exports (cover, profile, posts)
│   └── *.svg                    # SVG logo files
├── gallery/                     # Portfolio samples (3 HTML)
├── assets/print/                # Flyers, pricing board, business cards
├── feasibility/                 # Research & templates (12 files + 8 sectors)
├── tests/                       # Test suite
│
├── # Tax Form Generators (no LLM, template-based) — 20 forms
├── g1_ggr_generator.py          # G1 GGR Personal Income (6-tranche IRG)
├── g4_ibs_generator.py          # G4 IBS Annual Corporate Tax
├── g4_rental_generator.py       # G4 Rental Income (30% abattement)
├── g8_existence_generator.py    # G8 Business Existence (NIF)
├── g11_bic_generator.py         # G11 BIC Régime Réel
├── g12_official.py              # G12 IFU Prévisionnelle
├── g12_bis_generator.py         # G12 bis IFU Définitive
├── g13_bnc_generator.py         # G13 Professions Non Commerciales
├── g15_cessation_generator.py   # G15 Cessation d'Activité
├── g29_irg_salaires_generator.py # G29/G30 IRG Salaires (monthly barème)
├── g50_generator.py             # G50 Monthly Multi-Tax
├── g51_generator.py             # G51 Attestation Fiscale
├── cnrc_f1_generator.py         # CNRC F1 Commercial Registration (companies)
├── cnrc_f2_generator.py         # CNRC F2 Commercial Registration (traders)
├── das_cnas_generator.py        # DAS CNAS Annual Salary Declaration
├── secu01_generator.py          # SECU 01 CNAS Employer Affiliation
├── nis_generator.py             # NIS ONS Statistical ID
├── anae_generator.py            # ANAE Auto-Entrepreneur Declaration
├── casnos_affiliation_generator.py # CASNOS Self-Employed Enrollment
├── casnos_ca_generator.py       # CASNOS Annual Turnover Declaration
├── tax_form_pdf_exporter.py     # PDF export for all 20 forms
│
├── # Business Document Generators (some need LLM) — 12 generators
├── feasibility_generator.py     # 9-part feasibility study (Decree 26-154)
├── business_plan_generator.py   # Full business plan
├── nesda_dossier_generator.py   # NESDA financing dossier (9-part, 0%/7y/1.5y)
├── knowledge_base/              # Form catalog, gaps analysis, agency docs
├── financial_calculators.py     # VAN/TRI/Seuil (pure math, no LLM)
├── projections_engine.py        # Financial projections (math-based)
├── financial_projections_generator.py # Projections (LLM narrative)
├── aapi_optimizer.py            # AAPI 1,500-point scoring
├── quality_scorer.py            # Output validation
│
├── # Supporting Generators (no LLM)
├── cv_generator.py              # CV generator (PDF)
├── cover_letter_generator.py    # Cover letter generator (PDF)
├── invoice_generator.py         # Invoice/quote generator (PDF)
├── nesda_calculator.py          # NESDA financing calculator
├── nesda_eligibility.py         # NESDA eligibility checker
├── nesda_catalog.py             # 51 NESDA activities
├── business_defaults.py         # 13 business templates
├── pricing_calculator.py        # 30 services, 4 packages
├── government_paperwork_helper.py # CNAS/CASNOS/Carte Grise
├── bmc_generator.py             # Business Model Canvas
├── market_research_generator.py # Market research (LLM)
├── marketing_plan_generator.py  # Marketing plan (LLM)
├── social_media_generator.py    # Social media content
├── linkedin_automation.py       # LinkedIn content automation
├── linkedin_content.py          # LinkedIn content templates
├── sample_gallery.py            # Gallery HTML generator
│
├── # Infrastructure
├── service_orchestrator.py      # One-click dossier pipeline
├── business_pdf_exporter.py     # Business document PDF export
├── unified_dossier_pdf.py       # All-in-one dossier PDF
├── training_data_collector.py   # I/O collection for improvement
├── training_hook.py             # Auto-save generator I/O
├── batch_processor.py           # Batch processing for recurring clients
├── _html_escape.py              # XSS prevention utility
│
├── # Data & Config
├── generated_output/            # Generated files (gitignored)
├── training_data/               # Training records (gitignored)
├── batch_orders/                # Client tracking (gitignored)
├── feasibility/                 # Research & templates
│
├── requirements.txt             # Python dependencies
├── .env.example                 # API key template
├── FACEBOOK_PAGE_SETUP.md       # Facebook page setup guide
├── ALGERIAN_ADMIN_SERVICES.md   # Full form catalog research
├── BUSINESS_PLAN.md             # Business plan
├── STRATEGIC_ANALYSIS.md        # Competitive analysis & roadmap
└── README.md                    # This file
```

## API Keys

Only needed for LLM generators (feasibility, business plan, NESDA dossier):

```bash
# Get free Groq key (1,000 req/day): https://console.groq.com
export GROQ_API_KEY=gsk_xxxxx
```

All other generators work without any API keys.

## Legal

- IBS rates: 19% (industry/production), 23% (BTP/tourism), 26% (commerce/services) — verified 2026 per Art. 150 CIDTA
- IRG brackets: 0% ≤240K, 23% 240K-480K, 27% 480K-960K, 30% 960K-1.92M, 33% 1.92M-3.84M, 35% >3.84M — verified 2026-08-22 (LF 2026 Art.104 CIDTA, 6-tranche unified)
- TVA: 19% standard, 9% reduced (taux réduit) — verified 2026
- CNAS: 25.5% employer contribution (25% + 0.5% œuvres sociales) — verified 2026
- SMIG: 22,000 DZD/month | SNMG: 24,000 DZD/month (CNAS base) — verified 2026
- NESDA financing: 5-15% personal, 15-25% PNR grant, up to 70% bank (1-3% rate) — verified 2026
- IFU: 5% (biens), 12% (services), threshold 8M DZD — verified 2026 LF 2026
- Decree 26-154 (April 2026): Official 9-part feasibility study plan-type
- DGI forms: All sourced from mfdgi.gov.dz

## Contact

- WhatsApp: +213 676 773 892
- Email: contact@dsc-dz.com

---

**Built by MAHI Kamel Abdelghani** — DSC Digital Services Center © 2026
