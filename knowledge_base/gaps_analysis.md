# DSC Gaps Analysis — Forms Coverage vs Market Demand

> What DSC has, what's missing, and what to build next.
> Last updated: 2026-08-22 — all P1/P2/P3 gaps filled in Sprint 1.

## Current DSC Generator Coverage

### Form Generators (20 built)

| Generator | Form | Status | Notes |
|-----------|------|--------|-------|
| g1_ggr_generator.py | G1 (GGR) | ✅ Working | 6-tranche IRG barème, PDF export |
| g4_ibs_generator.py | G4 (IBS) | ✅ Working | Corporate tax (IBS) |
| g4_rental_generator.py | G4 (Rental) | ✅ Working | Revenus locatifs, 30% abattement, 6-tranche IRG |
| g8_existence_generator.py | G8 (NIF) | ✅ Working | Business start declaration |
| g11_bic_generator.py | G11 (BIC) | ✅ Working | Regime reel, 6-tranche IRG bareme |
| g12_official.py | G12 (IFU) | ✅ Working | Prévisionnelle |
| g12_bis_generator.py | G12 bis | ✅ Working | IFU final declaration |
| g13_bnc_generator.py | G13 (BNC) | ✅ Working | Professions non commerciales |
| g15_cessation_generator.py | G15 | ✅ Working | Cessation d'activité, duration/deadline/late flag |
| g29_irg_salaires_generator.py | G29 (IRG salaires) | ✅ Working | 6-tranche monthly IRG (20K/40K/80K/160K/320K) |
| g50_generator.py | G50 (Monthly) | ✅ Working | TVA/TAP/IRG combined |
| g51_generator.py | G51 | ✅ Working | Attestation fiscale |
| cnrc_f1_generator.py | CNRC F1 | ✅ Working | Commercial registration (companies) |
| cnrc_f2_generator.py | CNRC F2 | ✅ Working | Commercial registration (individual traders) |
| das_cnas_generator.py | DAS (CNAS) | ✅ Working | Annual salary declaration, 25.5%/9% contributions |
| secu01_generator.py | SECU 01 | ✅ Working | CNAS employer affiliation |
| nis_generator.py | NIS | ✅ Working | ONS statistical ID, completeness scorer |
| anae_generator.py | ANAE | ✅ Working | Auto-entrepreneur, IFU 5%/12%, plafond checks |
| casnos_affiliation_generator.py | CASNOS Affil. | ✅ Working | Self-employed enrollment |
| casnos_ca_generator.py | CASNOS CA | ✅ Working | Annual turnover declaration |

### Document Generators (12 + NESDA infra)

| Generator | Form | Status | Notes |
|-----------|------|--------|-------|
| nesda_dossier_generator.py | NESDA | ✅ Working | 9-part financing dossier (0%/7y/1.5y) |
| feasibility_generator.py | Feasibility | ✅ Working | 9-part Decree 26-154, offline capable |
| business_plan_generator.py | Business Plan | ✅ Working | Full business plan, offline capable |
| Plus 10 more | BMC, market research, etc. | ✅ Working | See SKILL.md for full list |

**Total: 22 working form/document generators (20 form-specific + NESDA dossier + G4 IBS)**

## GAP STATUS — All P1/P2/P3 Filled

### PRIORITY 1 — ✅ ALL BUILT

| Gap | Form | Status | Generator |
|-----|------|--------|-----------|
| G13 BNC | G13 | ✅ Built | `g13_bnc_generator.py` |
| CASNOS affiliation | CASNOS | ✅ Built | `casnos_affiliation_generator.py` |
| G12 bis | G12 bis | ✅ Built | `g12_bis_generator.py` |
| CASNOS CA declaration | CASNOS CA | ✅ Built | `casnos_ca_generator.py` |
| G51 tax clearance | G51 | ✅ Built | `g51_generator.py` |

### PRIORITY 2 — ✅ ALL BUILT

| Gap | Form | Status | Generator |
|-----|------|--------|-----------|
| CNRC F1 | RC (companies) | ✅ Built | `cnrc_f1_generator.py` |
| DAS (CNAS) | DAS | ✅ Built | `das_cnas_generator.py` |
| SECU 01 | CNAS enrollment | ✅ Built | `secu01_generator.py` |
| ANAE registration | ANAE | ✅ Built | `anae_generator.py` |

### PRIORITY 3 — ✅ ALL BUILT

| Gap | Form | Status | Generator |
|-----|------|--------|-----------|
| NIS application | ONS | ✅ Built | `nis_generator.py` |
| G4 rental | G4 (rental) | ✅ Built | `g4_rental_generator.py` |
| G15 closure | G15 | ✅ Built | `g15_cessation_generator.py` |

### Remaining Gaps (Low Priority)

| Gap | Form | Market | Effort | Revenue |
|-----|------|--------|--------|---------|
| AS 1 (medical claim) | CNAS | Employees | Very low | Low |
| AS 8 (work certificate) | CNAS | Employees | Low | Medium |
| Certificat Négatif | CNRC | New companies | Low | Medium |
| Other CNAS employee forms | CNAS | Employees | Low | Low |

## Revenue Impact — Gaps Closed

All high-revenue gaps have been filled. The 13 new generators built in Sprint 1 cover:
- 500K+ professionals (G13 BNC)
- 300K+ auto-entrepreneurs (G12 bis)
- 200K+ freelancers (CASNOS affiliation + CA)
- All employers (DAS, G29)
- All new businesses (CNRC F1/F2, NIS, ANAE)

## Build Order Completed

1. ✅ G13 generator (highest demand)
2. ✅ G12 bis (extend existing G12)
3. ✅ CASNOS affiliation + CA declaration
4. ✅ CNRC F1/F2 startup bundle
5. ✅ G51 tax clearance certificate
6. ✅ G15 cessation, NIS, SECU 01, ANAE, DAS, G4 rental
