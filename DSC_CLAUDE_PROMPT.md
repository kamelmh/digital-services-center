# DSC System Analysis Prompt — Copy & Paste into Claude Desktop

## Prompt (copy everything below the line)

---

I need you to do a deep analysis of my Digital Services Center (DSC) project. This is a productized AI-powered business document generation system for Algerian entrepreneurs. I'll give you the repo, then I need you to:

1. **Read the entire codebase** — every .py file, every .html file, every .md file
2. **Understand the architecture** — how all 23 generators connect, the data flow, the business logic
3. **Find what's missing** — gaps in the system, broken connections, unused code, incomplete features
4. **Give me strategic insights** — what I should build next, what's redundant, what could be 10x'd
5. **Identify revenue opportunities** — what's missing from a commercial standpoint

## Repository

**GitHub:** https://github.com/kamelmh/digital-services-center
**Branch:** master
**Clone path:** C:\Users\Admin\Projects\active\digital-services-center\

## What the System Does

DSC is an AI-powered SaaS platform (deployed as Python CLI + Violit web app) that generates professional business documents for Algerian entrepreneurs. It serves two markets:

1. **Direct clients** — entrepreneurs who need feasibility studies, business plans, CVs, tax declarations
2. **NESDA applicants** — people applying for NESDA government financing (Decree 26-154) who need compliant feasibility studies

## Architecture

```
Python Generators (23 modules) → JSON/Markdown/PDF output → Violit Web App (23 pages) → Client delivery
```

**Key files to read first:**
- `violit-app/main.py` — Web app with 23 pages (the frontend)
- `service_orchestrator.py` — One-click pipeline (feasibility → projections → AAPI → PDF)
- `business_defaults.py` — 13 business templates with pre-filled data
- `nesda_dossier_generator.py` — NESDA 9-part dossier (Decree 26-154 compliant)
- `nesda_catalog.py` — 51 NESDA-eligible activities with investment ranges
- `pricing_calculator.py` — 20 services, 4 packages, WhatsApp quote generator
- `aapi_optimizer.py` — AAPI scoring system (1500 points max)
- `projections_engine.py` — Mathematical financial projections (no LLM)
- `training_data_collector.py` — Collects I/O for future fine-tuning

## The 23 Generators

| # | Generator | What It Does |
|---|-----------|--------------|
| 1 | feasibility_generator.py | 9-part feasibility study (Decree 26-154) |
| 2 | business_plan_generator.py | 9-section business plan |
| 3 | market_research_generator.py | 7-section market research |
| 4 | financial_projections_generator.py | LLM-based financial projections |
| 5 | projections_engine.py | Mathematical projections (VAN/TRI/break-even) |
| 6 | marketing_plan_generator.py | 9-section marketing plan |
| 7 | social_media_generator.py | 6 content types (posts, campaigns, TikTok) |
| 8 | nesda_dossier_generator.py | NESDA 9-part dossier with financing model |
| 9 | bmc_generator.py | Osterwalder 9-block Business Model Canvas |
| 10 | nesda_calculator.py | NESDA triangular financing calculator |
| 11 | nesda_catalog.py | 51 NESDA activities, search, recommendations |
| 12 | nesda_eligibility.py | 5-check eligibility system (score 0-100) |
| 13 | aapi_optimizer.py | AAPI scoring (8 criteria, 1500 points) |
| 14 | tax_declaration_generator.py | 6 tax declarations (G12, G50, CNAS, etc.) |
| 15 | invoice_generator.py | Invoice + quote (devis) with TVA |
| 16 | cv_generator.py | 4 CV templates (PDF export) |
| 17 | cover_letter_generator.py | 4 cover letter templates (PDF) |
| 18 | government_paperwork_helper.py | 7 admin procedures |
| 19 | financial_calculators.py | VAN, TRI, 3-scenario, break-even |
| 20 | pricing_calculator.py | 20 services, 4 packages, WhatsApp quotes |
| 21 | linkedin_automation.py | LinkedIn post generator, 30-day calendar |
| 22 | business_pdf_exporter.py | Professional PDF export for all docs |
| 23 | unified_dossier_pdf.py | One PDF with cover, TOC, all sections |

## Business Model

**Pricing (DZD):**
- Feasibility Express: 10k-15k | Standard: 20k-30k | Complete: 40k-60k
- Business Plan: 25k-40k | Market Research: 10k-20k
- AAPI Optimized: 75k-150k
- CV: 2k-4k | Cover Letter: 1k-3k
- Tax Declaration: 3k-8k | Invoice/Quote: 1.5k-3k
- Logo: 8k-20k | Website: 25k-40k | E-commerce: 40k-60k

**Packages:**
- Starter (25k-35k): Express feasibility + CV
- Business (50k-70k): Standard feasibility + business plan + marketing
- Premium NESDA (80k-120k): Complete + business plan + marketing + social media + CV
- Enterprise (150k-250k): Complete + AAPI + website + logo

**Revenue targets:**
- Month 1-3: 5 clients/week × 25k avg = 125k DZD/week
- Month 4-6: 10 clients/week × 35k avg = 350k DZD/week
- Month 7-12: 15 clients/week × 45k avg = 675k DZD/week

## NESDA Context

NESDA is Algeria's national employment agency financing program. Key facts:
- Financing up to 10M DZD per project
- Triangular model: 5-15% personal + 15-25% NESDA grant + 70% bank loan
- Bank rate: 3% subsidized
- Repayment: 10 years (1.5yr grace + 5+5)
- Age: 18-55 (creation) / 20-58 (expansion)
- CDE training mandatory before application
- Decree 26-154 (April 2026) mandates 9-part feasibility study format

## What I Need From You

1. **Code quality audit** — What's duplicated? What's dead code? What could be refactored?
2. **Business logic gaps** — What calculations are wrong or missing?
3. **Missing features** — What would make this system 10x more valuable?
4. **Competitive analysis** — What are competitors doing that I'm not?
5. **Revenue optimization** — What pricing/tier changes would maximize revenue?
6. **Technical debt** — What needs fixing before this can scale?
7. **Integration opportunities** — What APIs/services should I connect to?
8. **Content strategy** — What should I post on LinkedIn to attract clients?
9. **NESDA-specific gaps** — Am I missing anything from the decree requirements?
10. **Automation potential** — What could be fully automated end-to-end?

Read the code, analyze it deeply, and give me your honest assessment. Be brutally honest about what's broken or missing.

---

## How to Use This Prompt

1. Open Claude Desktop
2. Paste everything above
3. Claude will need access to the GitHub repo — it can clone it or read files if you have the filesystem MCP connected
4. If Claude can't access the files directly, you can also paste the contents of key files in follow-up messages

## Alternative: If Claude Can Access Your Filesystem

If you have the filesystem MCP server connected in Claude Desktop, add this at the end:

```
The project is at C:\Users\Admin\Projects\active\digital-services-center\
Read all .py files in the root directory and violit-app/main.py to understand the full system.
Start with: service_orchestrator.py, business_defaults.py, nesda_dossier_generator.py, pricing_calculator.py
```

## Alternative: If Using Claude.ai (Web)

Since Claude.ai can't access your local files, you'll need to paste key files. Priority order:
1. `service_orchestrator.py` (the brain)
2. `business_defaults.py` (the data)
3. `pricing_calculator.py` (the monetization)
4. `nesda_dossier_generator.py` (the NESDA compliance)
5. `violit-app/main.py` (the frontend)
