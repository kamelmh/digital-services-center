# Project: Digital Services Center (DSC)
> Feasibility generator, Arabic PDF export, Algerian admin services

## How to Use
When starting a session in this project, read this file first.
When finishing work, append an entry below.

## Recent Changes

### 2026-08-08 — Arabic PDF Export Fixed
- **What:** PDF exporter now generates professional Arabic documents
- **Files:** `feasibility_generator.py`
- **Impact:** All feasibility reports now render correctly with Tahoma font, connected Arabic letters, proper RTL flow
- **Breaking changes:** None
- **Alerts for other projects:** If any project generates Arabic PDFs, it should use the same Tahoma font pattern from this project

### 2026-08-08 — Feasibility Generator Rewrite
- **What:** Expanded from 7 to 10 sections (official 9-part structure + risk analysis)
- **Files:** `feasibility_generator.py`
- **Impact:** NESDA/CNAC financing data, 5 tax incentives, Bank Regulation 14-03 context
- **Alerts for other projects:** None

## Pending Work
- [x] VAN/TRI calculation formulas — verified in `financial_calculators.py:96-149`
- [x] Break-even calculation templates — `seuil_rentabilite` (units) and `seuil_rentabilite_valeur` (DZD) in `financial_calculators.py:152-170`

## Recent Changes

### 2026-08-14 — VAN/TRI & Break-even Formulas Verified; Scenario Labeling Fixed; Training Hooks Added
- **What:** 
  - VAN (Net Present Value) and TRI (Internal Rate of Return) formulas confirmed correct in `financial_calculators.py`. Formula: VAN = Σ(CF_t / (1+r)^t), TRI via Newton-Raphson with bisection fallback.
  - Break-even templates verified: `seuil_rentabilite()` (units) and `seuil_rentabilite_valeur()` (DZD) in `financial_calculators.py:152-170`.
  - Fixed scenario labeling bug in `generate_3_scenarios()`: "defavorable" param (which had rev_mult=1.15, i.e. best case) was renamed to "favorable". Three scenarios now: prudent (pessimistic), reference (base), favorable (optimistic).
  - Fixed Section 8 break-even display in `feasibility_generator.py`: changed from `format_dzd()` on unit count (incorrect) to displaying raw unit count.
  - Added `training_hook` integration to `nesda_dossier_generator.py` and `bmc_generator.py` — all generators now capture I/O for training data.
- **Files:** `financial_calculators.py`, `feasibility_generator.py`, `nesda_dossier_generator.py`, `bmc_generator.py`
- **Impact:** Scenario labels now match their math. Training data capture expanded to all 12+ generators.
- **Breaking changes:** Scenario key changed from `'defavorable'` to `'favorable'` — any code referencing `scenarios['defavorable']` will need updating. All references found and updated in `feasibility_generator.py`.
- **Alerts for other projects:** Scenario key `'defavorable'` → `'favorable'` rename may affect any project consuming `generate_3_scenarios()` output.

---

### 2026-08-14 — 2026 IRG Salary Barème Corrected (G29/G30); G1 GGR Barème Thresholds Updated

- **What:** Corrected both IRG scales to their actual 2026 values:
  - G29/G30 (salary IRG): Replaced 5-tranche old scale (15K/30K/60K/120K: 0%/10%/20%/30%/40%) with correct 2026 scale (30K/120K/360K: 0%/23%/27%/30%, exonération ≤30K brût/mois)
  - G1 GGR (revenue IRG): Updated thresholds from old (180K/360K/720K: 0%/20%/30%/35%) to 2026 (120K/360K/1.44M: 0%/20%/30%/35%)
  - Fixed G29 barème reference HTML to match corrected 2026 salary scale
- **Files:** `g29_irg_salaires_generator.py`, `g1_ggr_generator.py`
- **Source:** mfdgi.gov.dz, CIDTA articles 1-92, Loi de Finances 2026, macalculatriceenligne.com, comptaLegal.dz
- **Impact:** G29/G30 salary IRG withholding now matches 2026 official barème. G1 revenue IRG uses correct 2026 thresholds.
- **Breaking changes:** None — old values were incorrect
- **Alerts for other projects:** If any project uses `IRG_BAREME` or `IRG_BAREME_MONTHLY` from these generators, results will change for salaries/revenue near threshold boundaries.

---

### 2026-08-15 — SNMG Rate Corrected (20K→24K); verify_rates.py Extended to 30 Checks

- **What:** 
  - Fixed `ALGERIA_DATA["smig_monthly"]` → `ALGERIA_DATA["snmg_monthly"]` in `feasibility_generator.py`: corrected minimum wage from 20,000 to 24,000 DZD (SNMG 2026, source: macalculatriceenligne.com)
  - Extended `verify_rates.py` from 14 to 30 checks: added G1 GGR IRG barème (4 tranches × 2 = 8 checks), G29 salary IRG barème (4 tranches × 2 = 8 checks), SNMG check, fixed inf comparison bug
  - G1/G29 IRG calculations validated manually against official DGI examples (comptaLegal.dz, macalculatriceenligne.com): 80K brut → IRG 3,146 DZD/month ✓
- **Files:** `feasibility_generator.py`, `verify_rates.py`
- **Impact:** All 30 rate verification checks now pass. Feasibility reports use correct 24,000 DZD SNMG.
- **Breaking changes:** `ALGERIA_DATA` key renamed from `smig_monthly` to `snmg_monthly`
- **Alerts for other projects:** If any project references `ALGERIA_DATA["smig_monthly"]`, update to `snmg_monthly`
- **Exports to LifeWorkspace:** `verify_rates.py`, `RESEARCH_2026.md`, `g1_ggr_generator.py`, `g29_irg_salaires_generator.py`

---

### 2026-08-19 — VAN/TRI Triplication Fixed — Single Source of Truth

- **What:** 
  - Fixed VAN/TRI triplication across three generators. All now use `FinancialCalculators.van()` and `FinancialCalculators.tri()` as single source of truth (12% Algerian market rate).
  - `nesda_dossier_generator.py`: Replaced inline VAN at 10% discount rate with `FinancialCalculators.van()` at 12%. This was the critical compliance fix — NESDA applicants were seeing artificially inflated VAN figures (10% vs 12%) on the exact document type a financing committee scrutinizes hardest.
  - `projections_engine.py`: Replaced inline VAN (12%) and IRR (Newton-Raphson) with `FinancialCalculators.van()` and `FinancialCalculators.tri()`. Rate agreed by coincidence, not shared source — now shares source.
  - Added `from financial_calculators import FinancialCalculators` to both files.
- **Files:** `nesda_dossier_generator.py`, `projections_engine.py`
- **Impact:** NESDA dossier VAN now uses correct 12% rate (was 10%). All VAN/TRI calculations use single audited implementation. 49.5% VAN reduction for NESDA applicants (more conservative, matches audited methodology).
- **Breaking changes:** NESDA VAN figures will be lower (more conservative) — committees see consistent 12% rate across all document types.
- **Alerts for other projects:** Any downstream consumer of NESDA dossier VAN/TRI figures should note the rate correction from 10% to 12%.
- **Exports to LifeWorkspace:** Updated `nesda_phase2_template.md` with VAN/TRI fix details

---

### 2026-08-19 — Claude Skill Created (SKILL.md)

- **What:** Created `SKILL.md` — comprehensive Claude skill file mapping all 16+ generators to Claude tool definitions. Includes:
  - Document generators (feasibility, NESDA dossier, business plan, BMC, market research, marketing plan, financial projections, invoice, CV, cover letter, social media, tax declaration)
  - Tax form generators (G1 GGR, G4 IBS, G8, G11 BIC, G12, G29 IRG, G50)
  - Financial calculators (VAN, TRI, break-even, NESDA financing)
  - Rate verification (30 checks)
  - Critical rate constants (2026 verified)
  - Usage patterns with code examples
  - Compliance notes
- **Files:** `SKILL.md` (new)
- **Impact:** Claude can now call generators directly as tools. VAN/TRI use single source of truth. All rates documented with 2026 verified values.
- **Breaking changes:** None
- **Alerts for other projects:** None
- **Exports to LifeWorkspace:** `SKILL.md` added to `04_Generators/`

---

### 2026-08-20 — Major Rate Corrections (NESDA, IBS, IRG)

- **What:**
  - **NESDA rates corrected:** Interest rate 2%→0% (100% bonified by state, per NESDA DG interview & CPA Bank). Repayment period 12y→7y (5y repayment + 1.5y grace, per CPA Bank). Grace period 1.5y unchanged.
  - **IBS services rate corrected:** 23%→26% (Art. 150 CIDTA, 3-tier structure: 19% production, 23% BTP/tourism, 26% commerce/services)
  - **IRG G1 barème expanded:** 4 tranches→6 tranches (new 33% bracket at 1.92M-3.84M). Updated thresholds: 240K/480K/960K/1.92M/3.84M with rates 0%/23%/27%/30%/33%/35%
  - **IRG G29 barème expanded:** Added 33% bracket (1.6M-3.2M) and 35% bracket (>3.2M). 6 tranches total.
  - **SMIG→SNMG in dossier:** Fixed hardcoded 20,000→24,000 in salary tables and Part 7
  - **G50 IRG brackets updated:** Old 4-tranche scale replaced with correct 2026 6-tranche scale
  - **Tests updated:** 2 tests fixed for new barème structure (45→47 pass)
  - **RESEARCH_2026.md updated:** All rates corrected, sources expanded to 11
- **Files:** `nesda_calculator.py`, `nesda_dossier_generator.py`, `g1_ggr_generator.py`, `g29_irg_salaires_generator.py`, `g50_generator.py`, `verify_rates.py`, `api.py`, `feasibility_generator.py`, `RESEARCH_2026.md`, `tests/test_generators.py`
- **Impact:** All financial outputs now use correct 2026 rates. NESDA dossiers show 0% interest (was 2%). IBS correctly shows 26% for services (was 23%). IRG calculations use full 6-tranche progressive scale.
- **Breaking changes:** NESDA financing figures will change significantly (0% interest = lower costs). IBS for services increases from 23% to 26%. IRG calculations more nuanced with 6 brackets.
- **Verification:** 38/38 rate checks pass, 47/47 tests pass

---

### 2026-08-20 — Offline Templates + PDF/Git Hardening (P0.1–P0.3)

- **What:**
  - **Offline lane (P0.1):** New `offline_templates.py` (399 lines) — 7 deterministic fallbacks for feasibility, business plan, market research, marketing plan, financial projections, social media, tax declaration. All use only local data (BUSINESS_TEMPLATES, ALGERIA_DATA, financial_calculators 12%, NESDA 0%/7y/1.5y, CNAS 25.5%, SNMG 24k). Same dict shape as LLM path (`content`, `sections`, `offline=True`) — zero UI change needed. 7 generators patched (`allow_offline=True` default) to delegate when `offline` or no `api_key`. `allow_offline=False` preserves hard-fail. Result: store sells offline — no internet, no key, no error.
  - **PDF fonts (P0.2):** `dsc_utils.generate_pdf()` now calls `_register_pdf_fonts()` — bundled `assets/fonts/Tahoma*.ttf` first, then `C:/Windows/Fonts` fallback, then Helvetica alias. Verified Arabic PDF 32K. Fonts tracked so exe works on any Windows. `dsc.spec` already bundles `assets/` recursively.
  - **Git hygiene (P0.3):** `.gitignore` adds `dsc_data.db` (+wal/shm), `nul`, `training_data/gen_*.json`. Untracked 17 previously-committed `gen_*.json` (stay on disk, now ignored; `index.jsonl` stays tracked).
  - **Docs lock (P0.4-0.5):** `SKILL.md` synced to 38 checks, 7 tax forms, 0%/7y/1.5y NESDA, 6-tranche IRG, 26% IBS. `requirements.txt` pinned from `pip freeze` (reportlab 4.5.1, violit 0.8.29 pinned alpha, arabic-reshaper 3.0.1, bidi 0.6.11, etc.).
  - **Desktop:** `.exe` rebuilt — 178 MB (was 176) includes offline templates + Tahoma.
- **Files:** `offline_templates.py` (new), `feasibility_generator.py`, `business_plan_generator.py`, `market_research_generator.py`, `marketing_plan_generator.py`, `financial_projections_generator.py`, `social_media_generator.py`, `tax_declaration_generator.py`, `dsc_utils.py`, `assets/fonts/Tahoma*.ttf`, `.gitignore`, `SKILL.md`, `requirements.txt`
- **Impact:** Product is now 100% offline sellable. Premium AI path stays via GROQ_API_KEY etc. No breaking change for online users — same call, richer text when key present.
- **Verification:** 47/47 pass, 7/7 offline generators >500 chars (VAN/TRI/DZD/NESDA present), PDF 32K, `allow_offline=False` raises correctly.
- **Alerts:** None — `offline=True` flag in output tells caller which path was used.

*Last updated: 2026-08-20*

## 2026-08-20 - Final evidence-based validation

### What changed
- Reconciled financial calculation pipeline: offline markdown now consumes  with canonical margin [0.2, 0.3] matching FinancialCalculators defaults
- Added Check #6 "financial_viability" to : detects negative VAN/TRI, assigns score=0.3 with detail "requires revised assumptions"; positive VAN/TRI gets score=1.0 with detail "Project financially viable"
- Margin override confirmed safe:  does not mutate original 
- All 47 tests pass, all 38 rate checks pass
- 9/9 financial figures agree between Markdown and PDF (revenue, VAN, TRI, payback, margin, NESDA terms)

### Files affected
- : margin override in  and 
- : added financial_viability check #6

### Breaking changes / alerts
- None — original artifacts untouched; new canonical markdown saved to new path; quality scorer improvement only

### Alerts for other projects
- No API changes, data format changes, or breaking changes that affect sibling projects
- Quality scoring now correctly flags financially unviable projects (negative VAN/TRI) instead of assigning A-grade

## 2026-08-20 - Final evidence-based validation

### What changed
- Reconciled financial calculation pipeline: offline markdown now consumes `calculate_real_financials()` with canonical margin [0.2, 0.3] matching FinancialCalculators defaults
- Added Check #6 "financial_viability" to `quality_scorer.py`: detects negative VAN/TRI, assigns score=0.3 with detail "requires revised assumptions"; positive VAN/TRI gets score=1.0 with detail "Project financially viable"
- Margin override confirmed safe: `business = dict(template); business['margin'] = [0.2, 0.3]` does not mutate original `BUSINESS_TEMPLATES`
- All 47 tests pass, all 38 rate checks pass
- 9/9 financial figures agree between Markdown and PDF (revenue, VAN, TRI, payback, margin, NESDA terms)

### Files affected
- `offline_templates.py`: margin override in `_real_financials_block` and `_real_fin_marge_line`
- `quality_scorer.py`: added financial_viability check #6

### Breaking changes / alerts
- None — original artifacts untouched; new canonical markdown saved to new path; quality scorer improvement only

### Alerts for other projects
- No API changes, data format changes, or breaking changes that affect sibling projects
- Quality scoring now correctly flags financially unviable projects (negative VAN/TRI) instead of assigning A-grade

## 2026-08-21 - Tax polish 2026 + preview parity

### What changed
- Updated `TAX_SYSTEM_PROMPT` in `tax_declaration_generator.py` from 2025 IRG 180k/360k/720k (20/30/35%) to 2026 6-tranche IRG 240k 0% / 480k 23% / 960k 27% / 1.92M 30% / 3.84M 33% / inf 35% (matches `g1_ggr_generator.py:36` IRG_BAREME and `verify_rates.py:38`). Also corrected TVA 19%/9%, IBS 19/23/26% (Art 150 CIDTA), IFU 5%/12% <8M, CNAS 25.5%+9% SNMG 24k, CASNOS 43.2k, NESDA 0%/7y/1.5y — now matches `ALGERIA_DATA` and `financial_calculators` single source.
- Fixed `DECLARATION_TYPES['irg_salaire']` prompt 2025 → 2026 6-tranche.
- Added 4 missing preview endpoints in `api.py` to achieve 7/7 parity: `GET /tax/g12/preview` (G12FormData activite_exercee), `GET /tax/g4/preview`, `GET /tax/g29/preview` (annee_imposition), `GET /tax/g1/preview` — now `g12/g50/g4/g11/g29/g1/g8` all return 200 HTML. Previously only g50/g11/g8 had preview.
- Fixed `g8_existence_generator.py:130` `html` → `_html_mod` (NameError) and `api.py:603` G12 field `activite` → `activite_exercee`.

### Files affected
- `tax_declaration_generator.py`: TAX_SYSTEM_PROMPT and DECLARATION_TYPES irg_salaire
- `api.py`: preview routes parity 3/7 → 7/7
- `g8_existence_generator.py`: _field html escape fix

### Breaking changes / alerts
- None — prompt only, no data format change. Tax guides now consistent with DGI 2026 barèmes and other generators.

### Alerts for other projects
- No cross-project impact — tax prompts and preview routes are isolated to DSC API.
