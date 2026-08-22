# DSC Gaps Analysis — Forms Coverage vs Market Demand

> What DSC has, what's missing, and what to build next.

## Current DSC Generator Coverage

| Generator | Form | Status | Notes |
|-----------|------|--------|-------|
| g1_ggr_generator.py | G1 (IRG) | Working | 6-tranche bareme, PDF export |
| g4_ibs_generator.py | G4 (IBS) | Working | Corporate tax |
| g8_existence_generator.py | G8 (NIF) | Working | Business start declaration |
| g11_bic_generator.py | G11 (BIC) | Working | Regime reel |
| g12_official.py | G12 (IFU) | Working | Previsionnelle only |
| g29_irg_salaires_generator.py | G29 (IRG salaires) | Working | 6-tranche salary IRG |
| g50_generator.py | G50 (Monthly) | Working | TVA/TAP/IRG combined |
| nesda_dossier_generator.py | NESDA | Working | 9-part financing dossier |

**Total: 8 working generators**

## PRIORITY 1 — High Demand + Low Competition

| Gap | Form | Market | Competition | Effort | Revenue |
|-----|------|--------|-------------|--------|---------|
| G13 BNC | G13 | 500K+ professionals | Almost none | Low | Very high |
| CASNOS affiliation | CASNOS | 200K+ freelancers | None | Low | High |
| G12 bis | G12 bis | 300K+ auto-entrepreneurs | None | Very low | High |
| CASNOS CA declaration | CASNOS CA | 200K+ freelancers | None | Low | High |
| G51 tax clearance | G51 | Frequent requests | Low | Low | Medium |

## PRIORITY 2 — High Demand + Moderate Competition

| Gap | Form | Market | Competition | Effort | Revenue |
|-----|------|--------|-------------|--------|---------|
| CNRC F1/F2 | RC forms | 100K+ new biz/year | Low | Medium | High |
| DAS (CNAS) | DAS | All employers | Medium | Medium | High |
| SECU 01 | CNAS enrollment | New employers | Low | Low | Medium |
| ANAE registration | ANAE | Growing segment | Low | Low | Medium |

## PRIORITY 3 — Lower Volume

| Gap | Form | Market | Effort | Revenue |
|-----|------|--------|--------|---------|
| NIS application | ONS | All businesses | Very low | Low |
| G4 rental | G4 | Property owners | Low | Medium |
| G15 closure | G15 | Closing businesses | Low | Low |

## Revenue Projections (Monthly)

| Service | Price DZD | Users/mo | Revenue/mo |
|---------|-----------|----------|------------|
| G13 generator | 3,000-5,000 | 100 | 300K-500K |
| CASNOS helper | 2,000-3,000 | 50 | 100K-150K |
| G12 bis helper | 1,500-2,500 | 80 | 120K-200K |
| G51 generator | 2,000-3,000 | 30 | 60K-90K |
| CNRC bundle | 10,000-20,000 | 20 | 200K-400K |
| **Total** | | **280** | **780K-1.34M** |

## Recommended Build Order

1. G13 generator (highest demand, easy template)
2. G12 bis (extend existing G12)
3. CASNOS affiliation + CA declaration
4. CNRC F1 startup bundle
5. G51 tax clearance certificate
