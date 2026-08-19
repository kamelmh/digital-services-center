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

*Last updated: 2026-08-19*
