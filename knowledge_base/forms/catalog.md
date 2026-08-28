# Algerian Administrative Forms — Master Catalog

> Knowledge Base for DSC Digital Services Center
> Last updated: 2026-08-22
> Sources: DGI, CNAS, CASNOS, CNRC, ONS official sites

---

## How to Use This Catalog

Each form entry contains:
- **Code** — Official form reference (e.g., G13)
- **Name** — French + Arabic
- **Agency** — Issuing authority
- **Purpose** — What it's for
- **Who needs it** — Target users
- **Deadline** — Filing deadline
- **Format** — PDF / Excel / Online
- **DSC generator** — Whether DSC has a generator for it (link to source file)
- **Complexity** — simple / moderate / complex
- **Revenue potential** — free / low / medium / high (for DSC monetization)

---

## CATEGORY 1: DGI Tax Forms (Série G)

### G1 — Liasse Fiscale Personne Physique
| Field | Value |
|-------|-------|
| Name | Déclaration du Résultat Global / إقرار بالدخل الإجمالي |
| Arabic | إقرار بالدخل الإجمالي للم sergeant(non-commercial) |
| Agency | DGI |
| Purpose | Annual income tax return for individuals |
| Who needs it | All individual taxpayers (employees, freelancers, business owners) |
| Deadline | April 30 annually |
| Format | PDF (fillable) |
| DSC generator | `g1_ggr_generator.py` — 6-tranche IRG calculation |
| Complexity | moderate |
| Revenue potential | medium |
| Fields | NIF, revenue by category, deductions, tax credits, total tax due |
| IRG tranches | 0-240K: 0%, 240K-480K: 23%, 480K-960K: 27%, 960K-1.92M: 30%, 1.92M-3.84M: 33%, 3.84M+: 35% |

### G4 — Déclaration des Revenus Locatifs
| Field | Value |
|-------|-------|
| Name | Déclaration des revenus de location / إقرار بالدخل العقاري |
| Agency | DGI |
| Purpose | Declare rental income from property |
| Who needs it | Property owners receiving rent |
| Deadline | With annual return (April 30) |
| Format | PDF |
| DSC generator | `g4_rental_generator.py` — multi-property prorated rent, 30% abattement, 6-tranche IRG |
| Complexity | simple |
| Revenue potential | medium |
| Fields | Property details, rental income, expenses, net taxable income |
| Note | Also see `g4_ibs_generator.py` for G4 IBS (corporate tax, separate form) |

### G8 — Déclaration d'Existence
| Field | Value |
|-------|-------|
| Name | Déclaration d'ouverture d'activité / التصريح بالانطلاقة |
| Arabic | التصريح بالانطلاقة |
| Agency | DGI |
| Purpose | Register new business activity, obtain NIF |
| Who needs it | ALL new businesses and freelancers |
| Deadline | Within 30 days of starting activity |
| Format | PDF (fillable) |
| DSC generator | `g8_existence_generator.py` |
| Complexity | simple |
| Revenue potential | high |
| Fields | Personal info, business type, activity code (APE/NAF), address, NIF request |
| Note | First form every entrepreneur needs — high demand, gateway to other services |

### G11 — BIC Régime Réel
| Field | Value |
|-------|-------|
| Name | Déclaration du résultat des BIC / إقرار بربح البضائع |
| Agency | DGI |
| Purpose | Industrial/commercial profits declaration (regime reel) |
| Who needs it | Businesses on regime reel (actual profit) |
| Deadline | With annual return (April 30) |
| Format | PDF |
| DSC generator | `g11_bic_generator.py` — 6-tranche IRG bareme (Art. 104 CIDTA) |
| Complexity | moderate |
| Revenue potential | high |

### G12 — Déclaration Prévisionnelle du CA (IFU)
| Field | Value |
|-------|-------|
| Name | Déclaration prévisionnelle du chiffre d'affaires / التصريح التقديمي للفاتورة |
| Agency | DGI |
| Purpose | Forecast turnover for auto-entrepreneurs (IFU regime) |
| Who needs it | Auto-entrepreneurs, micro-enterprise owners |
| Deadline | June 30 annually |
| Format | PDF |
| DSC generator | `g12_official.py` |
| Complexity | simple |
| Revenue potential | high |
| Fields | Projected annual turnover, activity type, IFU rate |
| IFU rate | 10,000 DZD minimum flat tax for auto-entrepreneurs |

### G12 bis — Déclaration Définitive du CA
| Field | Value |
|-------|-------|
| Name | Déclaration définitive du chiffre d'affaires / التصريح النهائي للفاتورة |
| Agency | DGI |
| Purpose | Final actual turnover declaration for IFU |
| Who needs it | Auto-entrepreneurs |
| Deadline | January 20 of following year |
| Format | PDF |
| DSC generator | `g12_bis_generator.py` — IFU final declaration |
| Complexity | simple |
| Revenue potential | high |

### G13 — IRG des Professions Non Commerciales
| Field | Value |
|-------|-------|
| Name | Déclaration du résultat des professions non commerciales / إقرار بربح المهنة |
| Arabic | إقرار بربح المهنة (المهن غير التجارية) |
| Agency | DGI |
| Purpose | Income tax declaration for non-commercial professions (liberal professions) |
| Who needs it | Lawyers, doctors, consultants, accountants, engineers, teachers, freelancers |
| Deadline | April 30 annually (or as specified by DGI) |
| Format | PDF (fillable), Excel (unofficial) |
| DSC generator | `g13_bnc_generator.py` — IRG professions non commerciales |
| Note | Previously highest-demand gap; built 2026-08-22 |
| Complexity | moderate |
| Revenue potential | very high |
| Fields | NIF, NIN, activity description, annual revenue, deductible expenses, professional costs, net result, tax calculation |
| Note | 205 likes + 22 shares on Facebook post about G13 Excel template — massive demand |
| See also | `knowledge_base/forms/g13_deep_dive.md` |

### G15 — Déclaration de Cessation d'Activité
| Field | Value |
|-------|-------|
| Name | Déclaration de cessation d'activité / التصريح بتوقف النشاط |
| Agency | DGI |
| Purpose | Declare business closure |
| Who needs it | Closing businesses |
| Deadline | Within 30 days of cessation |
| Format | PDF |
| DSC generator | `g15_cessation_generator.py` — duration calc, late flag, obligations checklist |
| Complexity | simple |
| Revenue potential | low |

### G29 — Déclaration des Traitements et Émoluments
| Field | Value |
|-------|-------|
| Name | Déclaration annuelle des salaires / الإقرار السنوي للرواتب |
| Agency | DGI |
| Purpose | Annual salary declaration for employees |
| Who needs it | ALL employers |
| Deadline | Annual |
| Format | PDF, Excel |
| DSC generator | `g29_irg_salaires_generator.py` — 6-tranche IRG |
| Complexity | moderate |
| Revenue potential | high |

### G50 — Déclaration Mensuelle TVA/TAP/IRG
| Field | Value |
|-------|-------|
| Name | Déclaration mensuelle / الإقرار الشهري |
| Agency | DGI |
| Purpose | Monthly combined return: VAT + Professional Activity Tax + IRG on salaries |
| Who needs it | Companies on actual-profit regime (SMEs with employees, VAT-subject) |
| Deadline | 20th of following month |
| Format | PDF, Excel |
| DSC generator | `g50_generator.py` |
| Complexity | complex |
| Revenue potential | high |
| Fields | TVA collectée, TVA déductible, TAP, IRG salaires, timbre |

### G51 — Attestation Fiscale
| Field | Value |
|-------|-------|
| Name | Attestation fiscale / شهادة ضريبية |
| Agency | DGI |
| Purpose | Tax clearance certificate |
| Who needs it | Businesses needing fiscal clearance (for tenders, contracts) |
| Deadline | On request |
| Format | PDF |
| DSC generator | `g51_generator.py` — attestation fiscale generation |
| Complexity | simple |
| Revenue potential | medium |

---

## CATEGORY 2: Social Security Forms (CNAS/CASNOS)

### CNAS — For Employees

#### AS 1 — Feuille de Soins Médicaux
| Field | Value |
|-------|-------|
| Name | Feuille de soins médicaux / وصفة طبية |
| Agency | CNAS |
| Purpose | Medical care claim |
| Who needs it | Employees seeking medical reimbursement |
| Deadline | 2 years from care date |
| Format | PDF |
| DSC generator | None |
| Complexity | simple |
| Revenue potential | low |

#### AS 8 — Attestation de Travail et de Salaire
| Field | Value |
|-------|-------|
| Name | Attestation de travail et de salaire / شهادة عمل وراتب |
| Agency | CNAS |
| Purpose | Work and salary certificate |
| Who needs it | Employees (for bank loans, visa applications) |
| Deadline | On request |
| Format | PDF |
| DSC generator | None |
| Complexity | simple |
| Revenue potential | medium |

#### DAS — Déclaration Annuelle des Salaires
| Field | Value |
|-------|-------|
| Name | Déclaration annuelle des salaires / الإقرار السنوي للرواتب |
| Agency | CNAS |
| Purpose | Annual salary declaration to social security |
| Who needs it | ALL employers |
| Deadline | January 31 |
| Format | Excel (bulk), PDF |
| DSC generator | `das_cnas_generator.py` — employer 25.5% / employee 9% contributions, masse salariale |
| Complexity | moderate |
| Revenue potential | high |
| Note | Separate from DGI's G29 — both must be filed |

#### SECU 01 — Affiliation CNAS
| Field | Value |
|-------|-------|
| Name | Déclaration et demande d'affiliation / طلب الالتحاق |
| Agency | CNAS |
| Purpose | Social security enrollment |
| Who needs it | New employers hiring first employee |
| Deadline | Before first salary payment |
| Format | PDF |
| DSC generator | `secu01_generator.py` — monthly contribution estimator, first-hire docs checklist |
| Complexity | moderate |
| Revenue potential | medium |

### CASNOS — For Self-Employed/Freelancers

#### Formulaire d'Affiliation CASNOS
| Field | Value |
|-------|-------|
| Name | Demande d'affiliation CASNOS / طلب الالتحاق بالصندوق الوطني لتأمينات غير الأجراء |
| Agency | CASNOS |
| Purpose | Self-employed social security enrollment |
| Who needs it | ALL freelancers, self-employed, liberal professions |
| Deadline | Within 10 days of starting activity |
| Format | PDF |
| DSC generator | `casnos_affiliation_generator.py` — auto vs explicit contribution modes |
| Complexity | moderate |
| Revenue potential | high |
| Fields | Personal info, activity type, NIF, RC number, estimated turnover |

#### Déclaration du CA — CASNOS
| Field | Value |
|-------|-------|
| Name | Déclaration du chiffre d'affaires / إقرار بالفاتورة |
| Agency | CASNOS |
| Purpose | Annual turnover declaration for social security contribution |
| Who needs it | All CASNOS-affiliated self-employed |
| Deadline | March 1 annually (payment by June 30) |
| Format | PDF |
| DSC generator | `casnos_ca_generator.py` — annual turnover declaration |
| Complexity | simple |
| Revenue potential | high |
| CASNOS rate | 15% of declared annual turnover |

---

## CATEGORY 3: Commercial Registration (CNRC)

### F1 — Registre du Commerce (Personne Morale)
| Field | Value |
|-------|-------|
| Name | Formulaire d'immatriculation / استمارة التسجيل في السجل التجاري |
| Agency | CNRC |
| Purpose | Commercial registration for companies (SARL, EURL, SPA) |
| Who needs it | All companies |
| Deadline | Before starting commercial activity |
| Format | Paper + SIDJILCOM online |
| DSC generator | `cnrc_f1_generator.py` — partners table, capital validation, timbre fiscal |
| Complexity | complex |
| Revenue potential | high |
| Required docs | Statutes (notarized), NIF, manager ID, lease contract, casier judiciaire n3 |
| Cost | 4,000 DA timbre fiscal |

### F2 — Registre du Commerce (Personne Physique)
| Field | Value |
|-------|-------|
| Name | Formulaire d'immatriculation commerçant / استمارة تسجيل تاجر |
| Agency | CNRC |
| Purpose | Commercial registration for individual traders |
| Who needs it | Individual merchants |
| Deadline | Before starting commercial activity |
| Format | Paper + SIDJILCOM |
| DSC generator | `cnrc_f2_generator.py` — marital-status logic, bail/age checks |
| Complexity | moderate |
| Revenue potential | medium |

### Certificat Négatif — Denomination
| Field | Value |
|-------|-------|
| Name | Certificat négatif / شهادة النفي |
| Agency | CNRC |
| Purpose | Company name reservation (verify name is available) |
| Who needs it | New companies |
| Deadline | Before F1 filing |
| Format | Paper / SIDJILCOM |
| DSC generator | None |
| Complexity | simple |
| Revenue potential | medium |

---

## CATEGORY 4: Statistical Identification (ONS)

### NIS — Numéro d'Identification Statistique
| Field | Value |
|-------|-------|
| Name | Formulaire de demande NIS / استمارة طلب رقم التعريف الإحصائي |
| Agency | ONS |
| Purpose | Statistical identification number |
| Who needs it | ALL businesses (auto-obtained after RC in some cases) |
| Deadline | After RC registration |
| Format | PDF |
| DSC generator | `nis_generator.py` — completeness scorer, ONS section checkboxes |
| Complexity | simple |
| Revenue potential | medium |
| Note | Required for: bank accounts, CNAS/CASNOS, public tenders, import/export |

---

## CATEGORY 5: Specialized Forms

### ANAE — Auto-Entrepreneur
| Field | Value |
|-------|-------|
| Name | Déclaration d'activité / تصريح النشاط |
| Agency | ANAE |
| Purpose | Auto-entrepreneur status registration |
| Who needs it | Micro-business owners, freelancers under auto-entrepreneur regime |
| Deadline | Before starting activity |
| Format | Online (anae.dz) |
| DSC generator | `anae_generator.py` — IFU 5%/12% (Art.282sexies), plafond checks, CASNOS 43.2k |
| Complexity | simple |
| Revenue potential | high |

### NESDA — Financing Dossier
| Field | Value |
|-------|-------|
| Name | Dossier de financement NESDA / ملف تمويل نesda |
| Agency | ANSEJ / NESDA |
| Purpose | Youth entrepreneurship financing application |
| Who needs it | Young entrepreneurs (19-40 years) |
| Deadline | Rolling |
| Format | 9-part dossier (paper) |
| DSC generator | `nesda_dossier_generator.py` |
| Complexity | complex |
| Revenue potential | very high |
| NESDA terms | 0% interest, 7 years repayment, 1.5 year grace, max 10M DZD |

---

## SUMMARY STATISTICS

| Category | Total Forms | DSC Has Generator | Gap |
|----------|-------------|-------------------|-----|
| DGI Tax Forms | 13 | 13 | 0 |
| CNAS (Employees) | 6 | 2 | 4 |
| CASNOS (Self-Employed) | 3 | 2 | 1 |
| CNRC (Commercial Reg) | 4 | 2 | 2 |
| ONS (Statistics) | 1 | 1 | 0 |
| ANAE (Auto-Entrepreneur) | 1 | 1 | 0 |
| NESDA (Financing) | 1 | 1 | 0 |
| **TOTAL** | **29** | **22** | **7** |

## PRIORITY GAPS (Remaining)

1. **AS 1** — Medical care claim (low volume)
2. **AS 8** — Work/salary certificate (medium demand)
3. **Certificat Négatif** — Company name reservation
4. **Remaining CNAS forms** — AS1, AS8, plus other employee declarations

## BUILT GENERATORS (as of 2026-08-22)

All P1 and P2 priority gaps have been filled. 22 form/document generators covering 20 DGI/CNAS/CASNOS/CNRC/ONS/ANAE forms plus 2 special forms (NESDA dossier + G4 IBS).

See `gaps_analysis.md` for detailed status.
