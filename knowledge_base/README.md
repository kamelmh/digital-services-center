# DSC Knowledge Base

> Structured knowledge for Algerian administrative forms and business procedures.
> Designed for DSC app consumption — machines and humans.

## Directory Structure

```
knowledge_base/
├── README.md                          # This file
├── gaps_analysis.md                   # What DSC has vs what's needed
├── forms/
│   ├── catalog.md                     # Master catalog of ALL 29 forms
│   └── g13_deep_dive.md              # Deep dive on G13 (highest priority)
├── agencies/
│   ├── dgi.md                         # Direction Generale des Impots (tax)
│   ├── cnas.md                        # CNAS (employee social security)
│   ├── casnos.md                      # CASNOS (self-employed social security)
│   ├── cnrc.md                        # CNRC (commercial registration)
│   └── ons.md                         # ONS (statistical identification)
└── deadlines/
    └── timeline.md                    # Annual obligation calendar
```

## How the DSC App Uses This KB

### For Form Generation
1. User selects form type (e.g., "G13")
2. App loads `forms/catalog.md` for field definitions
3. App loads relevant `agencies/{agency}.md` for rules and rates
4. Generator fills template with user data
5. PDF export uses `forms/g13_deep_dive.md` for layout reference

### For Deadline Reminders
1. App loads `deadlines/timeline.md`
2. Matches user profile (freelancer, employer, company)
3. Sends reminders before each deadline
4. Pre-fills forms 30 days in advance

### For Content Marketing
1. `forms/catalog.md` provides form descriptions for blog/social posts
2. `agencies/*.md` provide agency info for educational content
3. `gaps_analysis.md` identifies what to build next

### For User Onboarding
1. New user selects: "I am a freelancer" / "I have employees" / "I am starting a business"
2. App reads KB to determine which forms they need
3. Generates personalized checklist
4. Offers to generate each form

## KB Schema (for programmatic access)

Each form entry follows this schema:

```json
{
  "code": "G13",
  "name_fr": "Declaration du resultat des professions non commerciales",
  "name_ar": "اقرار بربح المهنة",
  "agency": "DGI",
  "purpose": "Income tax for liberal professions",
  "who_needs_it": ["lawyers", "doctors", "consultants", "freelancers"],
  "deadline": "April 30",
  "format": ["pdf", "excel"],
  "dsc_generator": "g13_bnc_generator.py",
  "complexity": "moderate",
  "revenue_potential": "very_high",
  "fields": ["nif", "nin", "revenue", "deductions", "irg_calculation"],
  "tax_rates": {
    "type": "IRG",
    "tranches": [[240000, 0], [480000, 0.23], [960000, 0.27], [1920000, 0.3], [3840000, 0.33], [999999999, 0.35]]
  }
}
```

## Maintenance

- **Update frequency:** When DGI/CNAS/CNRC changes rates or forms
- **Verification:** Cross-check with official agency websites
- **Version:** Track in git with DSC releases
- **Sources:** Always cite official sources (mfdgi.gov.dz, cnas.dz, etc.)

## Related DSC Files

- `ALGERIAN_ADMIN_SERVICES.md` — Existing DGI form research
- `RESEARCH_2026.md` — Regulatory reference for 2026
- `financial_calculators.py` — VAN/TRI/break-even (uses rates from this KB)
- `government_paperwork_helper.py` — CNAS/CASNOS/Carte Grise info
