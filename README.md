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

### Tax Form Generators (7 forms, template-based, no LLM)
| Form | Purpose | Price Range |
|------|---------|-------------|
| G12 | IFU Declaration (Prévisionnelle + Définitive) | 3,000–5,000 DA |
| G50 | Monthly Multi-Tax (TVA/IRG/IBS/Timbre) | 5,000–8,000 DA |
| G4 | IBS Annual Corporate Tax | 8,000–15,000 DA |
| G11 | BIC Régime Réel | 8,000–15,000 DA |
| G29/G30 | IRG Salary Declaration | 5,000–10,000 DA |
| G1 | GGR (Personal Income) | 3,000–6,000 DA |
| G8 | Business Existence | 2,000–4,000 DA |

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
├── docs/                        # GitHub Pages marketing site
├── brand/                       # SVG logos, Canva exports
├── gallery/                     # Portfolio samples
├── assets/print/                # Flyers, pricing board
├── batch_orders/                # Client tracking
├── generated_output/            # Generated files (gitignored)
│
├── # Tax Form Generators (no LLM)
├── g12_official.py              # G12 IFU (Prévisionnelle + Définitive)
├── g50_generator.py             # G50 Monthly Multi-Tax
├── g4_ibs_generator.py          # G4 IBS Annual
├── g11_bic_generator.py         # G11 BIC Régime Réel
├── g29_irg_salaires_generator.py # G29/G30 IRG Salaires
├── g1_ggr_generator.py          # G1 GGR Personal Income
├── g8_existence_generator.py    # G8 Existence
├── tax_form_pdf_exporter.py     # PDF export for all 7 forms
│
├── # Business Document Generators (some need LLM)
├── feasibility_generator.py     # 9-part feasibility study
├── business_plan_generator.py   # Full business plan
├── nesda_dossier_generator.py   # NESDA financing dossier
├── financial_calculators.py     # VAN/TRI calculators
├── aapi_optimizer.py            # AAPI scoring optimizer
├── quality_scorer.py            # Output validation
│
├── # Supporting Generators (no LLM)
├── cv_generator.py              # CV generator
├── cover_letter_generator.py    # Cover letter generator
├── invoice_generator.py         # Invoice/quote generator
├── nesda_calculator.py          # NESDA financing calculator
├── nesda_eligibility.py         # NESDA eligibility checker
├── nesda_catalog.py             # 51 NESDA activities
├── business_defaults.py         # 13 business templates
├── pricing_calculator.py        # 30 services, 4 packages
├── government_paperwork_helper.py # CNAS/CASNOS/Carte Grise
│
├── # Infrastructure
├── service_orchestrator.py      # One-click dossier pipeline
├── business_pdf_exporter.py     # Business document PDF export
├── unified_dossier_pdf.py       # All-in-one dossier PDF
├── training_data_collector.py   # I/O collection for improvement
├── training_hook.py             # Auto-save generator I/O
│
├── requirements.txt             # Python dependencies
├── .env.example                 # API key template
└── ALGERIAN_ADMIN_SERVICES.md   # Full form catalog research
```

## API Keys

Only needed for LLM generators (feasibility, business plan, NESDA dossier):

```bash
# Get free Groq key (1,000 req/day): https://console.groq.com
export GROQ_API_KEY=gsk_xxxxx
```

All other generators work without any API keys.

## Legal

- IBS rates: 19% (production), 23% (BTP), 26% (commerce/services)
- IRG brackets: 0% ≤180K, 20% 180-360K, 30% 360-720K, 35% >720K
- TVA: 19% standard, 9% reduced
- CNAS: 26% employer contribution
- Decree 26-154 (April 2026): Official 9-part feasibility study plan-type
- DGI forms: All sourced from mfdgi.gov.dz

## Contact

- WhatsApp: +213 676 773 892
- Email: contact@dsc-dz.com

---

**Built by MAHI Kamel Abdelghani** — DSC Digital Services Center © 2026
