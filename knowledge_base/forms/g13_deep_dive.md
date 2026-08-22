# G13 — Deep Dive: Déclaration du Résultat des Professions Non Commerciales

> The G13 is Algeria's annual income tax declaration for non-commercial professions
> (professions libérales). This is the #1 priority form for DSC based on market demand.

---

## What Is the G13?

The G13 is the tax form used by **liberal professions** to declare their annual income
and calculate their **IRG (Impôt sur le Revenu Global)** — personal income tax.

**Arabic name:** إقرار بربح المهنة (المهن غير التجارية)
**French name:** Déclaration du Résultat des Professions Non Commerciales
**Legal basis:** Article 31 bis du Code des Impôts Directs et Taxes Assimilées

## Who Must File G13?

| Profession | Arabic | Typical Income Range |
|------------|--------|---------------------|
| Lawyers (avocats) | محامون | 500K-5M DZD/year |
| Doctors (médecins) | أطباء | 1M-10M DZD/year |
| Engineers (ingénieurs) | مهندسون | 600K-3M DZD/year |
| Accountants (comptables) | محاسبون | 400K-2M DZD/year |
| Consultants | مستشارون | 500K-5M DZD/year |
| Teachers (professeurs) | أساتذة | 300K-1.5M DZD/year |
| Translators (traducteurs) | مترجمون | 300K-2M DZD/year |
| Notaires (notaires) | كتاب عدول | 1M-10M DZD/year |
| Architects (architectes) | مهندسون معماريون | 800K-5M DZD/year |
| Pharmacist (pharmaciens) | صيادلة | 1M-8M DZD/year |

## Form Structure (From Screenshot)

The G13 form from the screenshot shows:

### Header Section
```
République Algérienne Démocratique et Populaire
Ministère des Finances
Direction Générale des Impôts
DIW de Structure

Série G N°13 (2023)
```

### Identification Fields
| Field | Description | Format |
|-------|-------------|--------|
| Numéro d'Identification Fiscale (NIF) | Tax ID number | 15 digits |
| Numéro d'article d'imposition | Tax article number | Alphanumeric |
| Numéro d'Identification National (NIN) | National ID number | 18 digits |

### Declaration Type
```
IMPÔT SUR LE REVENU GLOBAL
Déclaration des bénéfices des professions non commerciales
(Régime simplifié des professions non commerciales)
Année de souscription: ___________
Résultat de l'année: ___________
```

### Key Sections
1. **Identité du déclarant** — Name, address, profession, NIF
2. **Chiffre d'affaires** — Annual turnover/revenue
3. **Charges déductibles** — Deductible expenses
4. **Résultat net** — Net taxable income
5. **Calcul de l'IRG** — Tax calculation using bareme
6. **Acomptes versés** — Advance payments made
7. **Solde dû** — Tax balance due

## Tax Calculation (IRG Bareme 2026)

The G13 uses the same 6-tranche IRG scale as G1:

| Tranche (DZD net income) | Rate | Cumulative Tax |
|--------------------------|------|----------------|
| 0 — 240,000 | 0% | 0 |
| 240,001 — 480,000 | 23% | Up to 55,200 |
| 480,001 — 960,000 | 27% | Up to 184,800 |
| 960,001 — 1,920,000 | 30% | Up to 472,800 |
| 1,920,001 — 3,840,000 | 33% | Up to 1,106,400 |
| 3,840,001+ | 35% | Uncapped |

**Formula:**
```
1. Calculate net result = Revenue - Deductible expenses
2. Divide by 12 to get monthly average
3. Apply tranche rates to monthly average
4. Multiply by 12 for annual tax
5. Subtract advance payments (acomptes)
6. Result = Tax due (solde)
```

## Deductible Expenses (Charges Déductibles)

| Category | Items | Limit |
|----------|-------|-------|
| Professional costs | Office rent, equipment, supplies | Actual |
| Social contributions | CASNOS (15% of turnover) | Actual |
| Insurance | Professional liability | Actual |
| Depreciation | Equipment, furniture | 10-25%/year |
| Travel | Professional travel | Actual |
| Training | Professional development | Actual |
| Accounting fees | Auditor/bookkeeper | Actual |

**NOT deductible:**
- Personal expenses
- Fines and penalties
- Client entertainment (limited)
- Private vehicle (unless professional use proven)

## Filing Deadline

- **Standard:** April 30 of each year (for previous year's income)
- **Extension:** Sometimes granted by DGI circular
- **Late penalty:** 5% per month of unpaid tax + interest

## Where to File

- **Paper:** At your local tax centre (centre d'impôt)
- **Online:** Via Jibayatic portal (jibayatic.mf.gov.dz)
- **Required copies:** 2 copies (original + copy)

## Why G13 Is a Massive Opportunity

### Market Evidence
- **205 likes + 22 shares** on a Facebook post about "G13 Excel template"
- Post by "Formateur Nadir" — educational content creator
- Comments show demand from: accountants, students, small business owners
- **"La déclaration G13 en format Excel — قريبا"** = "Coming soon" — nobody has a good tool yet

### Who Needs This
1. **All liberal professionals** (~500K+ in Algeria)
2. **Accountants** who prepare G13 for clients (multiplied demand)
3. **Tax students** learning the form
4. **Small accounting firms** (no budget for enterprise software)

### What DSC Can Build
1. **G13 Excel Template** — Auto-calculating with IRG bareme built in
2. **G13 Web App** — Fill form online, export PDF
3. **G13 API** — For accountants to batch-process client declarations
4. **G13 Guide** — Arabic/French tutorial (content marketing)

### Competitor Landscape
- Formateur Nadir: "Coming soon" — no product yet
- ConformePro: General tax guides, no specific G13 tool
- ComptaLegal: Accounting software, no standalone G13
- Mostaql freelancers: Individual offers, no scalable product

## G13 Generator Design (For DSC)

### Input Fields
```python
g13_input = {
    # Identity
    "nif": "123456789012345",
    "nin": "123456789012345678",
    "name": "Kamel Abdelghani",
    "profession": "Consultant",
    "address": "El Bayadh, Algeria",
    "wilaya": "05",
    
    # Financial
    "annual_revenue": 2_000_000,      # DZD
    "cascnos_contribution": 300_000,  # 15% of revenue
    "rent_expenses": 240_000,         # Office rent
    "equipment_expenses": 50_000,     # Equipment
    "insurance_expenses": 30_000,     # Professional insurance
    "other_expenses": 20_000,         # Misc professional
    "depreciation": 15_000,           # Equipment depreciation
    
    # Tax
    "advance_payments": 100_000,      # Acomptes already paid
    "year": 2026,
}
```

### Output
```python
g13_output = {
    "net_result": 1_345_000,          # Revenue - all deductions
    "monthly_average": 112_083,       # net_result / 12
    "irg_amount": 234_600,            # Calculated from bareme
    "total_tax": 234_600,             # Same as irg_amount (BNC)
    "advance_paid": 100_000,
    "tax_due": 134_600,               # Final balance
    "effective_rate": 11.7%,          # tax / revenue
}
```

### Generator File
- **Location:** `g13_bnc_generator.py` (to be created)
- **Dependencies:** None (template-based, no LLM needed)
- **PDF export:** Via `tax_form_pdf_exporter.py`
- **Template:** Arabic/French bilingual
