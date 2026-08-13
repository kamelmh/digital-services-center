# DSC Signal — Strategic Analysis & Improvement Roadmap
**Date:** August 5, 2026
**Author:** Kamel Mahi

---

## Executive Summary

The DSC has **11 generators** and **12 Violit pages**, but the research reveals critical gaps against the Algerian market. The biggest finding: **Decree 26-154 (April 2026)** now mandates an official 9-part plan-type for feasibility studies — our generators don't comply. Meanwhile, competitors charge 150,000-500,000 DZD for what we offer at 3,000-20,000 DZD. We're leaving money on the table AND missing the compliance angle.

---

## 1. COMPETITIVE LANDSCAPE

### Direct Competitors (Algeria 2026)

| Competitor | What They Offer | Price | Our Advantage |
|-----------|----------------|-------|---------------|
| **ProfitPilot** | Manual consulting, études technico-économiques | 150,000-500,000 DZD | We're 10-50x cheaper, instant generation |
| **SkyStartup** | BMC generator, market analysis, business plan (soon) | Free tier + paid | We have more generators, PDF export |
| **Takdeer** | Predictive simulation platform | 2,000 DZD/project | We have full document generation, not just simulation |
| **DinarSquare** | Hub with calculators, templates, guides | Free | We generate actual documents, not just templates |
| **Sakina DZ** | Company formation + business plan | 435-680€ (~170k-270k DZD) | We're 10x cheaper for the BP alone |
| **Business Plan Al Djazair** | Consulting firm, business plans | Custom pricing | We're automated, instant, affordable |

### Market Positioning

**We're priced as a commodity but should be positioned as:**
> "The only AI-powered compliance tool for Algerian entrepreneurs — generate official-grade études technico-économiques in minutes, not weeks."

**Pricing gap:** ProfitPilot charges 150,000 DZD minimum. We charge 3,000-20,000 DZD. We could easily charge 15,000-50,000 DZD for the feasibility study alone and still be 3-10x cheaper.

---

## 2. CRITICAL GAP: DECREE 26-154 COMPLIANCE

### What the Law Requires (April 2026)

The official 9-part plan-type for **études technico-économiques**:

| Part | Content | Our Coverage |
|------|---------|-------------|
| **I.** Informations porteur de projet | ID, legal form, NIF, capital structure, governance | ❌ Not structured |
| **II.** Présentation générale du projet | Objectives, products, clients, sectoral contribution | ⚠️ Partial |
| **III.** Étude technique | Production process, capacity, equipment, consumables | ❌ Missing |
| **IV.** Étude de marché | Demand, competition, trends, positioning, commercial policy | ⚠️ Separate generator |
| **V.** Plan d'investissement | Equipment, buildings, working capital, operating costs, financing | ⚠️ In financial projections |
| **VI.** Prévisions économiques et financières | P&L, cash flow, balance sheet (3-5 years), VAN/TRI/seuil rentabilité | ⚠️ Partial, no VAN/TRI |
| **VII.** Impact socio-économique | Jobs, supply chain, technology transfer, local integration | ❌ Missing |
| **VIII.** Calendrier de réalisation | Phases, timeline, operational launch | ❌ Missing |
| **IX.** Annexes | Plans, CVs, financial attestations | ❌ Missing |

### AAPI Scoring Grid (1500 points max)

For land allocation (foncier économique), projects are scored:

| Criterion | Coefficient | Max Points | Weight |
|-----------|------------|------------|--------|
| Nature of activity | 7 | 420 | 28% |
| Investment amount | 6 | 360 | 24% |
| Employment created | 5 | 300 | 20% |
| Equity contribution | 4 | 200 | 13% |
| Local content (integration rate) | 2 | 60 | 4% |
| Employment permanence | 1 | 60 | 4% |
| Investment extension | 1 | 70 | 5% |
| Export diversification | 1 | 30 | 2% |

**Our generators don't optimize for this scoring.** A smart generator would:
1. Ask about the targeted land wilaya
2. Show the user how their project scores
3. Suggest improvements to maximize score
4. Generate the study to match the scoring criteria

---

## 3. WHAT WE HAVE vs WHAT WE NEED

### Current State (11 Generators)

| Generator | Quality | LLM? | PDF? | Compliance? |
|-----------|---------|-------|------|-------------|
| Feasibility | ⚠️ Basic | ✅ Groq/OpenRouter | ❌ Text only | ❌ No 9-part |
| Business Plan | ⚠️ Basic | ✅ | ❌ | ❌ |
| Market Research | ⚠️ Basic | ✅ | ❌ | ❌ |
| Financial Projections | ⚠️ Basic | ✅ | ❌ | ❌ No VAN/TRI |
| Marketing Plan | ⚠️ Basic | ✅ | ❌ | N/A |
| Social Media | ✅ Good | ✅ | ❌ | N/A |
| Tax Helper | ✅ Good | ✅ | ❌ | N/A |
| Invoice/Quote | ✅ Good | ❌ | ✅ PDF | N/A |
| CV | ✅ Good | ❌ | ✅ PDF | N/A |
| Cover Letter | ✅ Good | ❌ | ✅ PDF | N/A |
| Gov Paperwork | ✅ Good | ❌ | ❌ | ✅ Procedure-based |

### Priority Improvements

#### Tier 1: Compliance & Revenue (Critical)
1. **Redesign feasibility generator** → 9-part plan-type compliant
2. **Add VAN/TRI/seuil calculators** → Real financial calculations, not LLM guesses
3. **Add AAPI scoring optimizer** → Show users how to maximize their score
4. **Add 3-scenario analysis** → Prudent/Reference/Defavorable
5. **PDF export for all business docs** → Not just CV/cover letter

#### Tier 2: Intelligence & Quality
6. **Training data collection** → Save all generated outputs for fine-tuning
7. **Quality scorer** → Rate generated content against the plan-type
8. **Market data integration** → Real wilaya populations, real economic indicators
9. **Competitor intelligence** → What do similar businesses charge in each wilaya?
10. **Price calculator** → Dynamic pricing based on complexity

#### Tier 3: Scale & Automation
11. **CRM system** → Track customers, follow up, manage relationships
12. **Proposal generator** → Auto-create quotes from service selection
13. **Batch processing** → Generate multiple studies at once
14. **API endpoints** → Let other tools use our generators
15. **Analytics dashboard** → What services are most requested?

---

## 4. TRAINING DATA OPPORTUNITY

### What We Can Collect

Every time a generator runs, we can save:
- **Input parameters** (business type, wilaya, investment, employees)
- **Generated output** (the full text)
- **Provider used** (groq, openrouter, aihubmix)
- **Quality metrics** (length, section count, compliance score)
- **Timestamp** (for trend analysis)

### How to Use Training Data

1. **Fine-tune prompts** → Which prompts produce the best output?
2. **Build a dataset** → For eventual model fine-tuning
3. **Quality improvement** → Identify weak sections and improve
4. **Pricing intelligence** → What investment levels are most common?
5. **Market analysis** → Which wilayas generate the most studies?

### Data Schema

```json
{
  "id": "gen_2026_08_05_001",
  "timestamp": "2026-08-05T22:30:00Z",
  "generator": "feasibility",
  "input": {
    "business_type": "quincaillerie",
    "wilaya": "El Bayadh",
    "investment": 3000000,
    "employees": 5,
    "business_name": "موارد البناء"
  },
  "output": {
    "content": "...",
    "word_count": 2500,
    "section_count": 5,
    "has_financials": true,
    "has_market_analysis": true
  },
  "provider": "groq",
  "model": "llama-3.3-70b",
  "quality_score": null,
  "compliance_score": null
}
```

---

## 5. FINANCIAL CALCULATORS (Missing)

### VAN (Valeur Actuelle Nette) / NPV

```
VAN = Σ (CashFlow_t / (1 + r)^t) - Initial Investment
where r = discount rate (12% default for Algeria)
```

### TRI (Taux de Rentabilité Interne) / IRR

```
TRI = rate where VAN = 0
Solved iteratively: find r such that Σ (CashFlow_t / (1 + r)^t) = 0
```

### Seuil de Rentabilité / Break-Even Point

```
Seuil = Fixed Costs / (Price per unit - Variable Cost per unit)
Seuil en valeur = Fixed Costs / Contribution Margin Rate
```

### Taux de Marge

```
Taux de marge = (Revenue - COGS) / Revenue × 100
```

### These should be CALCULATED, not generated by LLM.

---

## 6. RECOMMENDED NEXT STEPS

### Immediate (This Week)
1. ✅ Push current state (done — 6e11751)
2. 🔨 Add VAN/TRI/seuil calculators to `financial_projections_generator.py`
3. 🔨 Add compliance scoring to feasibility generator
4. 🔨 Add training data collection (save inputs/outputs)

### Short-term (This Month)
5. Redesign feasibility generator → 9-part plan-type
6. Add PDF export for all business documents
7. Add AAPI scoring optimizer
8. Add 3-scenario analysis

### Medium-term (Next Month)
9. Build CRM system
10. Build proposal/quote automation
11. Build analytics dashboard
12. Add more business templates (pharmacy, salon, etc. with real data)

---

## 7. PRICING RECOMMENDATION

### Current vs Proposed

| Service | Current Price | Proposed Price | Market Rate |
|---------|--------------|----------------|-------------|
| Feasibility (Express) | 3,000-5,000 | **10,000-15,000** | 150,000+ |
| Feasibility (Standard) | 5,000-8,000 | **20,000-30,000** | 150,000+ |
| Feasibility (Complete) | 12,000-20,000 | **40,000-60,000** | 300,000-500,000 |
| Business Plan | 15,000-25,000 | **25,000-40,000** | 100,000-200,000 |
| Market Research | 5,000-10,000 | **10,000-20,000** | 50,000-100,000 |
| Financial Projections | 7,000-15,000 | **15,000-25,000** | 80,000-150,000 |
| Full Package | 30,000 | **60,000-100,000** | 500,000+ |

**Still 3-10x cheaper than manual consulting, but 2-4x our current pricing.**

### New Tier: "AAPI Optimized" (Premium)

For clients applying for foncier économique:
- Study compliant with Decree 26-154
- AAPI scoring optimization
- 3-scenario analysis
- VAN/TRI calculations
- Price: **75,000-150,000 DZD** (still cheaper than ProfitPilot's 150k minimum)
