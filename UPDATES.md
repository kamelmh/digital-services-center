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
*Last updated: 2026-08-08*
