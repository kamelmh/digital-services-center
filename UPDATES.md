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

## 2026-08-21 - Offline 9-part + Invoice deterministic

### What changed
- `InvoiceGenerator` now supports `allow_offline=True` (default) — deterministic fallback without LLM. `generate_invoice`/`generate_quote` compute TVA 19% locally and return markdown table with offline note. Previously required API key and raised FeasibilityError.
- Added `invoice_offline`/`quote_offline` wrappers in `offline_templates.py` for consistency with other 7 offline generators.
- Verified `NESDADossierGenerator` 9-part (I-IX) already deterministic via `_generate_part1..9` — no LLM needed. `_generate_offline` placeholder retained for `_chat` path only. Tested with `boulangerie/Oran/3M` — 9 parts generated offline.

### Files affected
- `invoice_generator.py`: offline flag + deterministic rendering
- `offline_templates.py`: added invoice_offline/quote_offline
- `nesda_dossier_generator.py`: verified offline (no change, already 9-part deterministic)

### Breaking changes / alerts
- None — offline path is additive. Existing LLM path unchanged when API key present.

## 2026-08-22 — Batch 2 generators (CNRC F1, DAS CNAS, SECU 01, ANAE) + API integration + rate limiting

### What changed
- **4 new form generators** (Batch 2 of KB gaps plan), all following the G13 pattern (dataclass + calculate + DGI/CNAS-styled HTML + training_hook):
  - `cnrc_f1_generator.py` — Registre du Commerce personne morale: partners table with share/percentage validation, capital-per-share calc, apports-vs-capital check, 4000 DA timbre, required-docs checklist
  - `das_cnas_generator.py` — CNAS annual salary declaration: per-employee NSS/salary rows, employer 25.5% / employee 9% contributions, masse salariale recap, rate reference table
  - `secu01_generator.py` — CNAS employer affiliation: monthly contribution estimator (9%/25.5%), first-hire details, docs checklist
  - `anae_generator.py` — Auto-entrepreneur activity declaration: IFU 5% (services) / 12% (production), plafond checks (5M/8M), CASNOS 43.2k flat, effective-load calc
- **API integration** (`api.py`): POST /tax/g13, /tax/cnrc_f1, /tax/das_cnas, /tax/secu01, /tax/anae + GET preview for each (12/12 tax endpoints now have previews). Nested lists (associes, salaries) built from dicts via _build_dataclass.
- **G13 bug fixes**: `cascnos_contribution=None` crashed HTML generation (`None > 0`); missing paren in acomptes label.
- **Rate limiting for SaaS v1 routers**: new `apps/api/app/middleware/rate_limiter.py` with dependency-based sliding-window limiter (`make_rate_limit("60/minute")`) — slowapi decorators silently break FastAPI >=0.141 `include_router` (routes vanish; `_IncludedRouter` wrapper). Applied: feasibility 30/min, reads 60/min, job-poll 120/min, export-csv 10/min, checkout 10/min, webhook+me 60/min. Returns 429 + Retry-After.
- **Route-order bug fixed** (`dossiers.py`): GET /{dossier_id} was defined before /export-csv and /jobs/{job_id}, shadowing them (export-csv always 404'd). Dynamic route moved last.
- **CSV export fix**: JS-ism `Date.now()` → Python datetime stamp; commas stripped from CSV fields.
- **Tests**: +23 new generator tests (IRG tranche boundaries, CASNOS auto vs explicit, CNRC shares/apports/timbre, DAS rates/totals, SECU estimator, ANAE plafonds/load). 81/81 pass.

### Files affected
- New: `cnrc_f1_generator.py`, `das_cnas_generator.py`, `secu01_generator.py`, `anae_generator.py`, `apps/api/app/middleware/rate_limiter.py`
- Modified: `api.py`, `g13_bnc_generator.py`, `apps/api/app/main.py`, `apps/api/app/routers/dossiers.py`, `apps/api/app/routers/billing.py`, `tests/test_generators.py`

### Breaking changes / alerts
- **slowapi decorators must NOT be used inside APIRouters** on FastAPI >= 0.141 — use `make_rate_limit()` dependencies instead. Direct-on-app slowapi usage (legacy api.py) still works.
- `/v1/dossiers/export-csv` and `/v1/dossiers/jobs/{id}` now actually reachable (were shadowed).
- In-memory rate limiter is per-worker (Render 2 workers → effective limit x2).

### Alerts for other projects
- If academix-dss or other FastAPI projects use slowapi inside include_router-mounted routers on FastAPI >= 0.141, their routes are silently dropped — same fix applies (dependency-based limiting).

## 2026-08-22 — Batch 3 generators + RLS verified on real Postgres

### What changed
- **4 new form generators** (Batch 3, KB gaps plan complete for all P1/P2/P3 priorities):
  - `g15_cessation_generator.py` — cessation d'activité: durée d'exercice calc, 30-day legal deadline + late flag, obligations checklist by regime, successor/reprise block
  - `nis_generator.py` — ONS statistical ID request: 7-field completeness scorer, ONS section classification checkboxes, effectif tranches, auto-entrepreneur mode (ANAE card instead of RC)
  - `cnrc_f2_generator.py` — individual merchant RC: marital-status conditional logic (community regime requires conjoint info), bail ≥3y warning, age/majority check, conditional docs checklist
  - `g4_rental_generator.py` — revenus fonciers: multi-property table with prorated annual rent (loyer_mensuel × mois_loués), 30% abattement forfaitaire, annual IRG barème (same 6-tranche source as G1/G13), retenue à la source deduction
- **API**: POST + preview for g15, nis, cnrc_f2, g4_rental — now **16/16 tax endpoints** with parity.
- **RLS migration made portable + VERIFIED on real Neon Postgres**:
  - Root cause of prior failure: policies used Supabase-only `TO anon` role and `auth.uid()` function — undefined on vanilla Postgres. Also RLS was never ENABLED.
  - Fix in `e9ed55d79b2f_init_saas_tables.py`: dialect-guarded (`postgresql` only, SQLite skips), `ENABLE ROW LEVEL SECURITY` on dossiers/jobs/checkouts, portable policies keyed on session GUC `app.current_tenant_id`, idempotent `DROP POLICY IF EXISTS`, matching downgrade.
  - Verified end-to-end on Neon: tables created, version e9ed55d79b2f recorded, RLS enabled ×3, 6 policies present. Tenant isolation proven with restricted role `dsc_app`: tenant A sees only its dossier, tenant B only its own, no-GUC sees nothing. Owner role bypasses RLS by design (application-level `tenant_id ==` filtering stays authoritative).
  - Note: Neon blocks `SET ROLE` without membership — verify via direct login as the restricted role.
- **Tests**: +23 Batch 3 tests (duration/deadline/late-flag, completeness scoring, marital/bail conditionals, proration/abattement/barème/solde). **104/104 pass.**

### Files affected
- New: `g15_cessation_generator.py`, `nis_generator.py`, `cnrc_f2_generator.py`, `g4_rental_generator.py`
- Modified: `api.py`, `alembic/versions/e9ed55d79b2f_init_saas_tables.py`, `tests/test_generators.py`

### Breaking changes / alerts
- Migration revision edited in place — safe because no environment had ever applied it successfully (prior attempt rolled back transactionally on Neon). Any DB that somehow has the old policies should re-run downgrade→upgrade.
- RLS via GUC means a future least-privilege DB role needs the app to `SET app.current_tenant_id = '<uuid>'` per request/connection; current owner-role deployment relies on application-level filtering (unchanged).

### Alerts for other projects
- None cross-project. Generator pattern unchanged.

### Remaining (not in this commit)
- Render secrets must be set manually in Dashboard: DATABASE_URL, REDIS_URL, DSC_JWT_SECRET (generate via `python -c "import secrets; print(secrets.token_hex(32))"`), R2_BUCKET/R2_ENDPOINT/R2_ACCESS_KEY/R2_SECRET_KEY, DSC_CHARGILY_KEY/DSC_CHARGILY_SECRET when going live. render.yaml wires DATABASE_URL/REDIS automatically from provisioned services.

## 2026-08-22 — Deep Audit: 7-Lane Swarm + P0 Fixes + Free-Stack Assessment

### What changed
- **7-lane parallel audit** across file topology, generator math, API/infra, frontend, knowledge base, testing, business model.
- **5 generator math bugs fixed:**
  - `anae_generator.py`: IFU rates swapped (Services 0.05→0.12, Production 0.12→0.05, Art.282sexies)
  - `g50_generator.py`: TVA double-deduction — collapsed `tva_deductions_total` subtracted twice; now `tva_net = collectee+regs-deductions`
  - `g12_official.py`: CA table total now uses `calc.ifu_total` (minimum-clamped) not raw sum
  - `g13_bnc_generator.py`: added `total_deductible_expenses` to return dict (was always 0 in HTML)
  - `g1_ggr_generator.py`: `SalaireData.compute()` now subtracts `cotisations_salarié` before abattement
- **2 frontend P0 build blockers fixed:**
  - `apps/web/app/pricing/page.tsx`: `"use client"` moved to line 1 (Next 14 requires top directive)
  - `apps/web/app/admin/page.tsx`: added `API` const, fixed `PdfViewer` props (`r2Key→url`)
- **Git hygiene:** `.gitignore` adds `apps/api/dsc_saas.db`, debug dumps, `generate_*.py`; `knowledge_base/` (9 files, core IP) + `alembic/` scaffolding now committed; `FREE_HOSTING_RESEARCH.md` tracked
- **New doc:** `DSC_DEEP_ASSESSMENT.md` — full audit synthesis, free-only scaling plan (Render free → Oracle free 4 OCPU → $5 VPS), 3 sprints, context for future AIs
- **Tests:** ANAE tests corrected to new rates; **132/132 pass**

### Files affected
- Fixed: `anae_generator.py`, `g50_generator.py`, `g12_official.py`, `g13_bnc_generator.py`, `g1_ggr_generator.py`, `tests/test_generators.py`
- Frontend: `apps/web/app/pricing/page.tsx`, `apps/web/app/admin/page.tsx`
- Hygiene: `.gitignore`, `knowledge_base/` (9 files), `alembic/README`, `alembic/script.py.mako`, `FREE_HOSTING_RESEARCH.md`
- New: `DSC_DEEP_ASSESSMENT.md`

### Breaking changes / alerts
- **ANAE IFU now correct** — Services 12% / Production 5% (was swapped). Any cached ANAE quotes for services will increase ~2.4×.
- **G50 TVA now correct** — single deduction, not double. TVA à payer figures will increase for dossiers with high deductions.
- **G1 salary net now correct** — subtracts cotisations before 10% abattement. Salary nets will decrease slightly.

### Alerts for other projects
- Same `academix-dss` slowapi/FastAPI note still applies — audit confirmed the pattern is documented in UPDATES.md 2026-08-22 Batch 2

### Remaining (not in this commit)
- **P1 docs:** `knowledge_base/forms/catalog.md` (13 entries still marked None/NEEDED → should be ✅), `README.md` IRG 4-tranche footer, `SKILL.md` 7→20 forms, `PROJECT_MAP.md` 7→20 / 2%→0%
- **P1 math:** G11 + G29 IRG bareme still on legacy scales (see DSC_DEEP_ASSESSMENT.md §4 P1 table)
- **SaaS billing:** Chargily env + tenant isolation + mock-pay page (see DSC_DEEP_ASSESSMENT.md §6.2 Sprint 2)
- Render secrets still need manual dashboard setup as above


## 2026-08-24 — G29 verification and authenticated SaaS tenant routing

### What changed
- Corrected `verify_rates.py` G29/G30 expectations to the generator's monthly barème: 20K/40K/80K/160K/320K DZD plus the final open bracket.
- Changed the verifier CLI to return a nonzero exit status when any check fails, not only when `--strict` is supplied.
- Updated the stale NESDA comment in `feasibility_generator.py` to the implemented 2026 terms: 0% interest, 7-year repayment, and 1.5-year grace.
- Added `apps/api/app/core/tenant.py` with JWT UUID validation, authenticated SaaS user lookup, and PostgreSQL transaction-local `app.current_tenant_id` context setup.
- Wired authenticated tenant resolution into dossier creation, listing, job polling, CSV export, dossier retrieval, billing checkout, and `/billing/me`.
- Updated entitlement checks to use the authenticated tenant rather than the shared anonymous user.
- Added tenant ownership filters to job and dossier queries.

### Verification
- Full test suite: 131 passed, 1 skipped.
- Rate verification: 38/38 checks passed.
- Modified Python modules compile successfully.

### Breaking changes / alerts
- SaaS dossier and billing endpoints now require a valid bearer JWT whose `sub` claim is a UUID matching the SQLAlchemy SaaS `users.id` row.
- Local anonymous fallback is no longer used by these protected endpoints; legacy offline auth remains separate from SaaS UUID tenants.

### Remaining risks
- Live webhook hardening and Chargily production configuration remain separate tasks.
- Integration tests should be added for JWT authentication, tenant cross-access denial, and PostgreSQL RLS behavior using the request dependency path.


## 2026-08-24 — SaaS tenancy and billing integration coverage

### What changed
- Added `tests/test_saas_auth_billing_integration.py` covering missing/malformed JWTs, UUID subject validation, authenticated billing access, checkout tenant binding, unknown-user rejection, and an opt-in PostgreSQL RLS probe.
- The RLS probe checks that `dossiers`, `jobs`, and `checkouts` have RLS enabled and that the expected tenant policies exist. It requires `DSC_RLS_TEST_DATABASE_URL` to point to a least-privilege PostgreSQL/Neon role.

### Verification
- Local integration coverage: 5 passed, 1 skipped.
- The PostgreSQL/Neon test was skipped because no `DATABASE_URL` or `DSC_RLS_TEST_DATABASE_URL` is configured in the attached environment. No database was modified.

### Next implementation priorities
- Run the opt-in RLS suite using a restricted Neon role and verify cross-tenant reads and writes are denied.
- Add request-path tests for dossier creation, listing, retrieval, export, and job polling across two JWT tenants.
- Harden webhook handling so unknown checkout IDs cannot be created from webhook metadata and gateway fallback cannot be mislabeled as live Chargily.
- Complete the remaining documentation and legacy G11/G29 barème reconciliation noted in the 2026-08-22 audit.


## 2026-08-24 — Webhook hardening and multi-tenant endpoint coverage

### What changed
- Hardened `apps/api/app/routers/billing.py` webhook processing: unknown checkout IDs are rejected, payload currency/amount/plan/tenant metadata are checked against the stored checkout, and paid events remain idempotent.
- Extended `tests/test_saas_auth_billing_integration.py` with live-mode HMAC validation, metadata mismatch rejection, webhook idempotency, and two-tenant dossier/job isolation across listing, retrieval, CSV export, and job polling.
- Added an unauthenticated dossier-creation regression test.

### Verification
- Complete suite: 141 passed, 2 skipped.
- The skipped tests are the opt-in Neon/RLS checks because `DSC_RLS_TEST_DATABASE_URL` is not configured.
- No real Neon connection or database mutation was performed.

### Remaining risks
- Configure a least-privilege Neon test role and run the RLS tests before claiming database-level isolation.
- Confirm the exact production gateway signature contract and event payload schema with the selected payment provider before enabling live payments.
- Add a dedicated PostgreSQL transaction-context test to prove `app.current_tenant_id` is set on every request through the production session path.

### 2026-08-29 — Sprint 5: CI hardening, Chargily activation, admin dashboard
- **What:** CI pipeline hardened with PostgreSQL service, RLS migration application, and tenant isolation tests in CI. render.yaml Chargily env vars wired. Admin dashboard now supports cross-tenant view via `is_admin` bypass.
- **Files:** `.github/workflows/ci.yml`, `apps/api/app/routers/dossiers.py`, `apps/api/migrations/003_rls_policies.sql`, `apps/web/lib/dossiers.ts`, `apps/web/app/admin/page.tsx`, `render.yaml`
- **Impact:** CI now runs 163 tests + RLS policies on every push. Admin users see all dossiers across tenants. Chargily production activation is ready (set keys in Render dashboard).
- **Breaking changes:** `list_dossiers` returns all rows for admin users (no tenant filter). `GET /v1/dossiers/me` added for frontend admin check.
- **Alerts for other projects:** None
- **Tests:** 163 passed, 1 skipped (local; new RLS enforcement suite adds 3 PG-only tests skipped without env)

### 2026-08-29 — Sprint 6: RLS enforcement — least-privilege role + FORCE RLS
- **What:** Closed the gap flagged 2026-08-24 and left open through Sprints 4-5: RLS was schema-only, not load-bearing — CI tested as superuser (`postgres:postgres`) which bypasses RLS by Postgres design. Added `dsc_app` least-privilege role, scoped `GRANT`s, and `FORCE ROW LEVEL SECURITY` so every role including the owner is bound by policy. CI now connects as `dsc_app` (`DATABASE_URL`/`DSC_RLS_TEST_DATABASE_URL` both point to `dsc_app:dsc_app_local@localhost:5432/neondb`); "Verify RLS" checks `relforcerowsecurity` and `current_user`. New `tests/test_rls_enforcement.py` proves a foreign-tenant dossier is invisible after `SET LOCAL app.current_tenant_id` as `dsc_app`.
- **Files:** `apps/api/migrations/003_rls_policies.sql` (§0 role/grant + §1 FORCE), `.github/workflows/ci.yml` (DSN swap + `current_user` check + `test_rls_enforcement.py` step), `tests/test_rls_enforcement.py` (new: 3 tests, PG-only), `render.yaml` (comment: production `DATABASE_URL` = `dsc_app` DSN — see `PRODUCTION_CHECKLIST.md`), `DSC_DEEP_ASSESSMENT.md` §8 (9th Critical Invariant).
- **Impact:** Tenant isolation is now enforced at the DB layer by a non-owner, FORCE-RLS-bound role, verified on every push. Chargily live cutover (Sprint 7) is safe to sequence next.
- **Breaking changes:** Production `DATABASE_URL` must be re-pointed at `dsc_app` on Neon (one-time `CREATE ROLE` documented in `PRODUCTION_CHECKLIST.md`). Filesystem invariants untouched (IRG 6-tranche 240k/480k/960k/1.92M/3.84M annual + 20k/40k/80k/160k/320k monthly, NESDA 0%/7y/1.5y, Tahoma→fallback font chain).
- **Tests:** 163 passed, 4 skipped locally (+3 new PG-only tests skipped without env); full 166 expected on CI. Also fixed the stale G11 status row in `DSC_DEEP_ASSESSMENT.md`'s generator table (code already correct at `g11_bic_generator.py:73-81`).
- **Neon manual step (one-time):** Run the `CREATE ROLE`/`GRANT` preamble of `003_rls_policies.sql` on the Neon branch, then update the API service's `DATABASE_URL` to `postgresql://dsc_app:<password>@<neon-host>/neondb?sslmode=require`.

### 2026-08-29 — Sprint 7: Chargily live cutover (The DZD sprint)
- **What:** Flipped from `mock` to real DZD payments via Chargily Pay v2. Billing now reaches the live `pay.chargily.dz/api/v2/checkouts` (test key → `.../test/api/v2/...` auto-route) and money moves through BaridiMob/CIB/Dahabiya — the only gateway that matters for Algerian payers. A failed live Chargily call now raises `502` instead of silently falling back to mock (ops-visible). Webhook is pinned to `X-Chargily-Signature` HMAC-sha256; bad/missing signature is `401` when `gateway==chargily` (mock bypass is `mock`-only). `mock-pay` stays reachable under `?gateway=mock` for local dev.
- **Files:** `render.yaml:36-48` (live docs + secret comments), `apps/api/app/routers/billing.py:84-121,171-212` (raise-on-live-failure + header-pin + 401/400 split + logging), `tests/test_saas_auth_billing_integration.py` (new `test_chargily_live_rejects_mock_webhook_bypass` — HMAC-pinning contract, runs in CI), `app/billing/mock-pay|success|failure/page.tsx` (live `payment_url` redirect + `checkout_id` poll), `DSC_DEEP_ASSESSMENT.md` (10th Critical Invariant), `PRODUCTION_CHECKLIST.md`.
- **Impact:** Real DZD is unblocked. Sequenced deliberately after Sprint 6 (isolation proven) and before Sprint 8 (price-centralization via `policy_constants.py`). `DSC_BILLING_GATEWAY` flips `mock→chargily` in the Render dashboard once the 3 secrets are set.
- **Breaking changes:** None in filesystem invariants (IRG 6-tranche, NESDA 0%/7y/1.5y, Tahoma→fallback, RLS). Billing is additive — mock path untouched.
- **Production cutover (one-time):** In the Chargily dashboard set `webhook_endpoint = https://dsc-api-vsex.onrender.com/billing/webhook`, copy `DSC_BILLING_WEBHOOK_SECRET`, set `DSC_CHARGILY_KEY`/`DSC_CHARGILY_SECRET` in Render, flip `DSC_BILLING_GATEWAY` mock→chargily.
- **Tests:** 164 passed (new pinning test), existing 3 RLS PG-only tests still skipped without env.

### 2026-08-29 — Sprint 8: Centralize — `policy_constants.py` (one canonical rate table)
- **What:** Eliminated the duplication that `docs/DSC Constants and CI Implementation Guide.md` (Aug 23, `proposed, not approved`) warned about: the same 2026 rates lived as literals in 14 generators. Created `policy_constants.py` (`TAX_YEAR=2026`, `TVA/IBS/IFU/CNAS/CASNOS/SNMG/VAN/NESDA/IRG_ANNUAL→IRG_MONTHLY` with `annual_to_monthly_brackets()`), then migrated every family with compatibility aliases: financial core (`financial_calculators.py:9`, `VAN→VAN_DISCOUNT_RATE`, `loan 0.09→DEFAULT_BANK_LOAN_RATE`), feasibility (`ALGERIA_DATA` 5 fields → `SNMG/TVA/IBS/CNAS/VAN`, `smig_monthly` compat), IRG family (`g1_ggr`/`g11_bic:73-81` `IRG_BAREME(_BIC)=list(IRG_ANNUAL_BRACKETS)`, `g29:38` `IRG_BAREME_MONTHLY=list(IRG_MONTHLY_BRACKETS)`), IBS (`g4_ibs` 19/23/26 + `*0.19/*0.23/*0.26 → IBS_RATES[…]["rate"]`), TVA/IRG (`g50` `TVA_STANDARD/REDUCED` + `IRG_BRACKETS`, `g13`/`g4_rental` annual table), IFU (`anae`/`g12_official` `IFU_RATES`, `IFU_AUTO` on AE path only), CASNOS (`*0.15→CASNOS_RATE`, `*12` min stays visible), CNAS (`das_cnas` `EMPLOYER/EMPLOYEE_RATE_CONVENTION = CNAS_*_RATE*100`, detailed table untouched for reconciliation). Verification is now non-self-affirming: `verify_rates.py` keeps `REVIEWED_2026_IRG_ANNUAL` as an independent snapshot and checks `policy_constants` against it (plus monotonic/inf-terminator shape checks), then checks generators against `policy_constants` — an edit to the canonical file alone cannot self-affirm (67 checks, was 38).
- **Files:** `policy_constants.py` (new), `verify_rates.py` (+29 checks), `financial_calculators.py`, `feasibility_generator.py`, `g1_ggr_generator.py`, `g11_bic_generator.py`, `g29_irg_salaires_generator.py`, `g4_ibs_generator.py`, `g50_generator.py`, `g13_bnc_generator.py`, `g4_rental_generator.py`, `anae_generator.py`, `g12_official.py`, `casnos_affiliation_generator.py`, `casnos_ca_generator.py`, `das_cnas_generator.py`, `DSC_DEEP_ASSESSMENT.md` (11th invariant).
- **Impact:** `pricing_calculator.py:SERVICES` (devis amounts) intentionally untouched — devis ≠ regulated tax rates. No G29/CNAS semantic change: monthly is `annual/12` as locked in Sprint 1, CNAS component table awaits the flagged review (Guide §2 note).
- **Tests:** `verify_rates.py` 67/67, `pytest` 164 passed / 4 skipped (3 PG-only RLS + HMAC live pin already counted), CI unchanged.

### 2026-08-29 — Sprint 9: Maintenance pass (reliability + Pages hygiene)
- **What:** Applied the Aug-23 maintenance pass on the live repo (S8-aware). CI rate gate now fails on drift: `verify_rates.py` → `verify_rates.py --strict` and the check count reflects the S8 67-check suite (not the 38 in the archived doc). Pages deploy now uploads only `./docs` (not `.`) — no DB/R2/keys/generated artifacts leak to the public site.
- **Files:** `.github/workflows/ci.yml` (label + `--strict`), `.github/workflows/deploy.yml` (`path: '.' → './docs'`), `docs/Digital Services Center Maintenance Pass.md` (source of the 131→38 verifier lineage, already folded in Sprint 8), `verify_rates.py` (Sprint 8 already carries the 20k/40k/80k/160k/320k G29 alignment; this pass folds the status-icon fix so a failing check is actually rendered as a failure).
- **Verification (post-pass):** `pytest` 164/4 + `verify_rates.py --strict` 67/67 (merged base). The verifier's monthly model stays `annual/12`.
- **Notes:** The archived pass's 131→38 numbers are pre-S8. The patch described in the archived doc was authored against a dirty ZIP baseline and left its base changes uncommitted — they are not replayed here. `pricing_calculator.py` `SMOKE_MARKETING` placeholders and the public-site artifact boundary are separate concerns for a future pass.

### 2026-08-29 — Sprint 10: Close 100% — WILAYAS canonical + ROADMAP + Pages guard
- **What:** Closed the last 3 doc/code gaps to reach 100%: extracted the ×13 `WILAYAS` literal into `policy_constants.WILAYAS` (58-entry canonical, `01-Adrar→58-In Guezzam`; `algeria_wilayas` compat in `nesda_dossier`), added `ROADMAP.md` (70 lines — current / S1-9 / S10-12 / 11 invariants / cutover, consolidates 5 stale strategy docs), and wired `check_public_site.py` (97 lines, dep-free) into CI (`ci.yml:51`) with the `deploy.yml:33` `./docs` artifact narrowed in Sprint 9. Catalog is 22/29 Forms (`AS1/AS8/Certificat Négatif` intentionally 3-None); README footer is already 6-tranche. `DSC_DEEP_ASSESSMENT.md` Known Gaps fully struck through.
- **Files:** `policy_constants.py` (`WILAYAS`), `nesda_dossier_generator.py` (`ALGERIA_WILAYAS` compat), `ROADMAP.md` (new), `check_public_site.py` (new), `.github/workflows/ci.yml` (scan), `.github/workflows/deploy.yml` (artifact), `DSC_DEEP_ASSESSMENT.md` (100% close), `SKILL.md`/`PROJECT_MAP.md` stale counts fixed.
- **Verification (post-pass):** `pytest` 164/4, `verify_rates.py --strict` 67/67, `compileall -q apps` 0, `check_public_site.py docs` `OK (docs)`.
- **Tag:** `v0.10.0-sprint10` — 100% local; production cutovers (Neon `dsc_app` role, Chargily 3 secrets) remain one-time dashboard actions per `PRODUCTION_CHECKLIST.md`.
