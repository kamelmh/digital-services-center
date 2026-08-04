"""
Academix DSS — Feasibility Study Generator
Generates professional 27-page feasibility studies for Algerian businesses
Based on Hany Sewilam template structure, localized for Algeria
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─── ALGERIAN REFERENCE DATA ────────────────────────────────────────────────

ALGERIA_DATA = {
    "country": "الجزائر",
    "currency": "دج",
    "currency_code": "DZD",
    "population": 45_000_000,
    "growth_rate": 0.018,  # 1.8% annual population growth
    "smig": 20_000,  # SMIG minimum wage (monthly)
    "smig_hourly": 120,  # SMIG hourly
    "tax_rate_corporate": 0.19,  # IS tax rate (standard)
    "tax_rate_small": 0.19,  # IS for small enterprises
    "tva_rate": 0.19,  # TVA standard
    "cnas_employer": 0.26,  # CNAS employer contribution
    "cnas_employee": 0.09,  # CNAS employee contribution
    "casnos_rate": 0.02,  # CASNOS for self-employed
    "interest_rate": 0.09,  # Average bank loan rate
    "discount_rate": 0.12,  # NPV discount rate
    "inflation": 0.03,  # Annual inflation
    "wilayas": {
        "El Bayadh": {"population": 228_000, "index": 0.85},
        "Alger": {"population": 3_915_000, "index": 1.15},
        "Oran": {"population": 1_560_000, "index": 1.05},
        "Constantine": {"population": 938_000, "index": 0.95},
        "Blida": {"population": 1_002_000, "index": 0.95},
        "Setif": {"population": 1_489_000, "index": 0.90},
        "Tlemcen": {"population": 949_000, "index": 0.90},
        "Bejaia": {"population": 912_000, "index": 0.90},
        "Tizi Ouzou": {"population": 1_127_000, "index": 0.95},
        "Annaba": {"population": 640_000, "index": 0.95},
    },
    "business_registration": {
        "ANAE": "السجل التجاري + الضرائب",
        "CNAS": "الصندوق الوطني للتأمينات",
        "cost_registration": 5_000,  # Approximate
        "time_days": 15,
    },
}

# ─── BUSINESS TEMPLATES ──────────────────────────────────────────────────────

BUSINESS_TEMPLATES = {
    "quincaillerie": {
        "name_ar": "متجر مواد بناء و معدنية",
        "name_en": "Hardware & Building Materials Store",
        "category": "تجارة",
        "typical_investment": {"min": 2_000_000, "max": 8_000_000},
        "typical_margin": {"min": 0.15, "max": 0.35},
        "typical_staff": {"min": 3, "max": 8},
        "typical_area_sqm": {"min": 80, "max": 300},
        "products": [
            "مواد بناء (أسمنت، رمل، حجارة)",
            "أنابيب وأدوات سباكة",
            "أسلاك كهربائية ولوحات",
            "أدوات يدوية",
            "دهانات ومواد لاصقة",
            "أقفال وأبواب",
            "سيراميك وبلاط",
        ],
        "seasonal_peak": "مارس - يونيو (موسم البناء)",
        "competition_level": "متوسط - مرتفع",
        "success_factors": ["موقع جيد", "تنوع المنتجات", "أسعار تنافسية", "خدمة ما بعد البيع"],
    },
    "supermarche": {
        "name_ar": "سوبر ماركت",
        "name_en": "Supermarket",
        "category": "تجارة تجزئة",
        "typical_investment": {"min": 3_000_000, "max": 15_000_000},
        "typical_margin": {"min": 0.12, "max": 0.25},
        "typical_staff": {"min": 5, "max": 20},
        "typical_area_sqm": {"min": 150, "max": 500},
        "products": [
            "مواد غذائية أساسية",
            "مشروبات",
            "مواد تنظيف",
            "منتجات ألبان",
            "لحوم ودواجن",
            "فواكه وخضار",
        ],
        "seasonal_peak": "رمضان + الأعياد",
        "competition_level": "مرتفع",
        "success_factors": ["موقع حيوي", "جودة المنتجات", "نظافة المحل", "أسعار منافسة"],
    },
    "restaurant": {
        "name_ar": "مطعم",
        "name_en": "Restaurant",
        "category": "ضيافة",
        "typical_investment": {"min": 1_500_000, "max": 6_000_000},
        "typical_margin": {"min": 0.20, "max": 0.40},
        "typical_staff": {"min": 4, "max": 15},
        "typical_area_sqm": {"min": 60, "max": 200},
        "products": [
            "وجبات مطبوخة",
            "مشروبات ساخنة وباردة",
            "حلويات",
            "مشاوي",
        ],
        "seasonal_peak": "رمضان + عطل نهاية الأسبوع",
        "competition_level": "مرتفع جداً",
        "success_factors": ["جودة الطعام", "خدمة سريعة", "نظافة", "سعر مناسب", "موقع"],
    },
    "atelier_ferro": {
        "name_ar": "ورشة حدادة و التلحيم",
        "name_en": "Welding & Fabrication Workshop",
        "category": "صناعة",
        "typical_investment": {"min": 1_000_000, "max": 4_000_000},
        "typical_margin": {"min": 0.25, "max": 0.45},
        "typical_staff": {"min": 2, "max": 6},
        "typical_area_sqm": {"min": 50, "max": 150},
        "products": [
            "أبواب وشبابيك",
            "درابزينات",
            "هياكل معدنية",
            "أعمال لحام",
        ],
        "seasonal_peak": "طوال السنة",
        "competition_level": "متوسط",
        "success_factors": ["جودة اللحام", "سرعة التسليم", "سعر مناسب", "خبرة تقنية"],
    },
    "pharmacie": {
        "name_ar": "صيدلية",
        "name_en": "Pharmacy",
        "category": "صحة",
        "typical_investment": {"min": 3_000_000, "max": 10_000_000},
        "typical_margin": {"min": 0.25, "max": 0.35},
        "typical_staff": {"min": 2, "max": 5},
        "typical_area_sqm": {"min": 40, "max": 100},
        "products": [
            "أدوية عامة",
            "مستلزمات طبية",
            "مستحضرات تجميل",
            "مكملات غذائية",
        ],
        "seasonal_peak": "موسم البرد + الإنفلونزا",
        "competition_level": "مرتفع",
        "success_factors": ["موقع مركزي", "توافر الأدوية", "خبرة صيدلانية", "ثقة المرضى"],
    },
    "cafe_patisserie": {
        "name_ar": "مقهى وحلويات",
        "name_en": "Café & Pastry Shop",
        "category": "ضيافة",
        "typical_investment": {"min": 1_000_000, "max": 4_000_000},
        "typical_margin": {"min": 0.30, "max": 0.55},
        "typical_staff": {"min": 3, "max": 8},
        "typical_area_sqm": {"min": 40, "max": 120},
        "products": [
            "قهوة ومشروبات ساخنة",
            "عصائر طبيعية",
            "حلويات تقليدية",
            "كعكات وكيك",
        ],
        "seasonal_peak": "طوال السنة + رمضان",
        "competition_level": "مرتفع جداً",
        "success_factors": ["جودة المنتجات", "أجواء مريحة", "خدمة ممتازة", "موقع حيوي"],
    },
}


# ─── FEASIBILITY STUDY SECTIONS ──────────────────────────────────────────────

TEMPLATE_SECTIONS = {
    "cover": {
        "title_ar": "دراسة جدوى أولية",
        "fields": ["project_name", "location", "date", "center_name"],
    },
    "toc": {
        "title_ar": "المحتويات",
        "sections": [
            "١. وصف المشروع",
            "٢. دراسة السوق",
            "٣. الدراسة الفنية",
            "٤. الدراسة المالية",
        ],
    },
    "section_1": {
        "title_ar": "١. وصف المشروع",
        "subsections": [
            "١.١ وصف المشروع",
            "١.٢ مبررات المشروع",
            "١.٣ الموقع العام للمشروع",
        ],
    },
    "section_2": {
        "title_ar": "٢. دراسة السوق",
        "subsections": [
            "٢.١ وصف المنتج",
            "٢.٢ الطلب الحالي",
            "٢.٣ الطلب المتوقع",
            "٢.٤ حصة المشروع من السوق والطاقة الإنتاجية",
            "٢.٥ المنافسة والبيع بأسعار مناسبة",
            "٢.٦ إيرادات المشروع المتوقعة",
        ],
    },
    "section_3": {
        "title_ar": "٣. الدراسة الفنية",
        "subsections": [
            "٣.١ موقع المشروع",
            "٣.٢ البناء",
            "٣.٣ عملية التصنيع / النشاط",
            "٣.٤ الآلات والأجهزة والمعدات",
            "٣.٥ الأثاث والتجهيزات",
            "٣.٦ السيارات",
            "٣.٧ القوى العاملة",
            "٣.٨ المواد الأولية",
            "٣.٩ الخدمات الضرورية",
            "٣.١٠ برنامج تنفيذ المشروع",
        ],
    },
    "section_4": {
        "title_ar": "٤. الدراسة المالية",
        "subsections": [
            "٤.١ تكاليف التشغيل السنوية",
            "٤.٢ رأس المال العامل",
            "٤.٣ نفقات التأسيس والتشغيل قبل",
            "٤.٤ تكاليف المشروع",
            "٤.٥ وسائل التمويل",
            "٤.٦ الفرضيات المالية",
            "٤.٧ الخلاصة",
        ],
    },
    "appendices": {
        "title_ar": "٥. الملحقات",
        "tables": [
            "حساب الأرباح والخسائر",
            "التدفقات النقدية",
            "الميزانية العمومية",
            "تحليل الحساسية",
            "المعايير المالية",
        ],
    },
}


# ─── GROQ API GENERATOR ──────────────────────────────────────────────────────

class FeasibilityGenerator:
    """Generate professional feasibility studies using LLM API"""

    PROVIDERS = {
        "openrouter": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "env_key": "OPENROUTER_API_KEY",
            "model": "google/gemma-4-26b-a4b-it:free",
        },
        "openrouter-nemotron": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "env_key": "OPENROUTER_API_KEY",
            "model": "nvidia/nemotron-3-super-120b-a12b:free",
        },
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "env_key": "GROQ_API_KEY",
            "model": "llama-3.3-70b-versatile",
        },
        "aihubmix": {
            "url": "https://aihubmix.com/v1/chat/completions",
            "env_key": "OPENAI_API_KEY",
            "model": "gpt-4.1-mini",
        },
    }

    def __init__(self, provider: str = None, api_key: str = None):
        # Auto-detect provider
        if provider and provider in self.PROVIDERS:
            self.provider = provider
        else:
            # Try providers in order
            for name, cfg in self.PROVIDERS.items():
                key = os.environ.get(cfg["env_key"])
                if key and len(key) > 10:
                    self.provider = name
                    break
            else:
                raise ValueError("No valid API key found. Set GROQ_API_KEY, OPENROUTER_API_KEY, or OPENAI_API_KEY.")

        cfg = self.PROVIDERS[self.provider]
        self.api_key = api_key or os.environ.get(cfg["env_key"])
        self.base_url = cfg["url"]
        self.model = cfg["model"]
        print(f"Using provider: {self.provider} ({self.model})")

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Call LLM API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 4000,
        }
        resp = requests.post(self.base_url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def generate_section_1(self, biz: dict, location: str, wilaya: str) -> str:
        """Section 1: Project Description"""
        system = """You are an Algerian business consultant writing feasibility studies.
Write in Arabic (Modern Standard Arabic). Be professional and specific to Algeria.
Use real Algerian data: SMIG (20,000 DZD), CNAS rates (26% employer), TVA (19%).
Output ONLY the content for this section, no headers."""

        prompt = f"""Write Section 1 (وصف المشروع) of a feasibility study for:
- Business type: {biz['name_ar']} ({biz['name_en']})
- Location: {location}, {wilaya}
- Category: {biz['category']}

Include:
1.1 وصف المشروع: What the business does, products/services, target customers
1.2 مبررات المشروع: 3 clear justifications (market demand, import substitution, job creation)
1.3 الموقع العام: Why this location in {location} is strategic

Be specific with Algerian context. Use real numbers where possible.
Write 400-500 words."""
        return self._call_llm(system, prompt, temperature=0.7)

    def generate_section_2(self, biz: dict, location: str, wilaya: str, investment: int) -> str:
        """Section 2: Market Study"""
        system = """You are an Algerian market analyst writing feasibility studies.
Write in Arabic (Modern Standard Arabic). Use real Algerian market data.
Include specific numbers, percentages, and market analysis.
Output ONLY the content for this section."""

        wilaya_data = ALGERIA_DATA["wilayas"].get(wilaya, {"population": 500_000, "index": 0.90})

        prompt = f"""Write Section 2 (دراسة السوق) of a feasibility study for:
- Business: {biz['name_ar']} in {location}, {wilaya}
- Investment: {investment:,} DZD
- Wilaya population: {wilaya_data['population']:,}
- Products: {', '.join(biz['products'][:5])}

Include:
2.1 وصف المنتج: Product descriptions and categories
2.2 الطلب الحالي: Current demand, imports vs local production, customs data
2.3 الطلب المتوقع: Population growth (1.8%/year), demand projection for 5 years
2.4 حصة المشروع: Realistic market share (start 2-5%, grow to 10-15%)
2.5 المنافسة: Competitive landscape, pricing strategy
2.6 الإيرادات المتوقعة: Revenue projections for 5 years

Use tables for projections. Be realistic, not optimistic.
Write 500-700 words."""
        return self._call_llm(system, prompt, temperature=0.7)

    def generate_section_3(self, biz: dict, location: str, investment: int) -> str:
        """Section 3: Technical Study"""
        system = """You are an Algerian technical consultant writing feasibility studies.
Write in Arabic (Modern Standard Arabic). Use real Algerian costs and suppliers.
Include specific equipment lists with prices in DZD.
Output ONLY the content for this section."""

        prompt = f"""Write Section 3 (الدراسة الفنية) of a feasibility study for:
- Business: {biz['name_ar']} in {location}
- Total investment: {investment:,} DZD
- Staff: {biz['typical_staff']['min']}-{biz['typical_staff']['max']} employees
- Area: {biz['typical_area_sqm']['min']}-{biz['typical_area_sqm']['max']} sqm

Include:
3.1 الموقع: Industrial zone or commercial area in {location}
3.2 البناء: Area breakdown (workspace, storage, office), rent estimate
3.3 عملية النشاط: Step-by-step business operations
3.4 الآلات والمعدات: Equipment list with DZD costs (use Algerian suppliers)
3.5 الأثاث: Office furniture, computer, phone
3.6 السيارات: Delivery vehicle if needed
3.7 القوى العاملة: Staff table (position, count, monthly salary in DZD, CNAS)
3.8 المواد الأولية: Initial inventory with quantities and costs
3.9 الخدمات: Electricity, water, fuel estimates
3.10 البرنامج: 3-6 month implementation timeline

Use tables for equipment and staff lists.
Write 600-800 words."""
        return self._call_llm(system, prompt, temperature=0.7)

    def generate_section_4(self, biz: dict, investment: int) -> str:
        """Section 4: Financial Study"""
        system = """You are an Algerian financial analyst writing feasibility studies.
Write in Arabic (Modern Standard Arabic). Use real Algerian financial data:
- Interest rate: 9% bank loans
- TVA: 19%
- IS tax: 19%
- SMIG: 20,000 DZD/month
- CNAS employer: 26%
- Discount rate for NPV: 12%
- Inflation: 3%/year
Output ONLY the content for this section."""

        prompt = f"""Write Section 4 (الدراسة المالية) of a feasibility study for:
- Business: {biz['name_ar']}
- Total investment: {investment:,} DZD
- Typical margin: {biz['typical_margin']['min']*100:.0f}-{biz['typical_margin']['max']*100:.0f}%

Include:
4.1 تكاليف التشغيل: Annual operating costs breakdown (rent, salaries, utilities, marketing)
4.2 رأس المال العامل: Working capital calculation (2-3 months of operating costs)
4.3 نفقات التأسيس: Pre-establishment costs (registration, permits, deposits)
4.4 تكاليف المشروع: Summary table of all costs
4.5 وسائل التمويل: 50% own capital + 50% bank loan (CNAC/BND)
4.6 الفرضيات: Financial assumptions (growth 5%/year, tax 19%, interest 9%)
4.7 الخلاصة: NPV, IRR, payback period, B/C ratio

Include 5-year projections table. Be conservative.
Write 500-700 words."""
        return self._call_llm(system, prompt, temperature=0.6)

    def generate_financial_tables(self, biz: dict, investment: int) -> str:
        """Generate financial projection tables"""
        system = """You are an Algerian financial analyst. Generate ONLY financial tables in Arabic.
Use DZD currency. Be conservative and realistic for an Algerian small business.
Output markdown tables only."""

        prompt = f"""Generate financial tables for {biz['name_ar']} with {investment:,} DZD investment.

Create these tables:

1. جدول الأرباح والخسائر (5 سنوات):
   - الإيرادات (المبيعات)
   - تكلفة البضاعة المباعة
   - الربح الإجمالي
   - مصاريف تشغيلية (رواتب، إيجار، خدمات، تسويق)
   - الربح قبل الضرائب
   - الضرائب (19%)
   - الربح الصافي

2. جدول التدفقات النقدية (5 سنوات):
   - التدفق الداخلي
   - التدفق الخارجي
   - الرصيد النقدي

3. تحليل الحساسية:
   - زيادة التكاليف 10%
   - زيادة التكاليف 20%
   - تخفيض المبيعات 5%
   - تخفيض المبيعات 10%

Use realistic numbers for Algeria. Format as markdown tables."""
        return self._call_llm(system, prompt, temperature=0.5)

    def generate_full_study(self, business_type: str, location: str, wilaya: str,
                            investment: int = None) -> dict:
        """Generate complete 27-page feasibility study"""
        biz = BUSINESS_TEMPLATES.get(business_type)
        if not biz:
            raise ValueError(f"Unknown business type: {business_type}. Available: {list(BUSINESS_TEMPLATES.keys())}")

        if investment is None:
            investment = (biz["typical_investment"]["min"] + biz["typical_investment"]["max"]) // 2

        print(f"Generating feasibility study for {biz['name_ar']} in {location}, {wilaya}...")
        print(f"Estimated investment: {investment:,} DZD")

        # Generate each section
        sections = {}

        print("  [1/5] Section 1: Project Description...")
        sections["section_1"] = self.generate_section_1(biz, location, wilaya)

        print("  [2/5] Section 2: Market Study...")
        sections["section_2"] = self.generate_section_2(biz, location, wilaya, investment)

        print("  [3/5] Section 3: Technical Study...")
        sections["section_3"] = self.generate_section_3(biz, location, investment)

        print("  [4/5] Section 4: Financial Study...")
        sections["section_4"] = self.generate_section_4(biz, investment)

        print("  [5/5] Financial Tables...")
        sections["tables"] = self.generate_financial_tables(biz, investment)

        # Assemble full study
        study = self._assemble_study(biz, location, wilaya, investment, sections)

        return study

    def _assemble_study(self, biz: dict, location: str, wilaya: str,
                        investment: int, sections: dict) -> dict:
        """Assemble all sections into a complete study"""
        now = datetime.now()

        full_study = f"""# دراسة جدوى أولية — {biz['name_ar']}

## بيانات المشروع
| البند | التفاصيل |
|-------|----------|
| اسم المشروع | {biz['name_ar']} ({biz['name_en']}) |
| الموقع | {location}، ولاية {wilaya} |
| التصنيف | {biz['category']} |
| إجمالي الاستثمار | {investment:,} دج |
| تاريخ الإعداد | {now.strftime('%Y-%m-%d')} |
| إعداد | أكاديمكس DSS — مركز الدراسات |

---

## المحتويات
{TEMPLATE_SECTIONS['toc']['title_ar']}

١. وصف المشروع
٢. دراسة السوق
٣. الدراسة الفنية
٤. الدراسة المالية
٥. الملحقات

---

## {TEMPLATE_SECTIONS['section_1']['title_ar']}

{sections['section_1']}

---

## {TEMPLATE_SECTIONS['section_2']['title_ar']}

{sections['section_2']}

---

## {TEMPLATE_SECTIONS['section_3']['title_ar']}

{sections['section_3']}

---

## {TEMPLATE_SECTIONS['section_4']['title_ar']}

{sections['section_4']}

---

## الملحقات — الجداول المالية

{sections['tables']}

---

## ملاحظات ختامية

1. هذه دراسة جدوى أولية قابلة للتعديل حسب الظروف الفعلية
2. يُنصح بمراجعة الأرقام مع محاسب أو مستشار مالي
3. التكاليف تقريبية وقابلة للتغيير حسب المنطقة والتوقيت
4. يُنصح بإجراء دراسة سوق ميدانية قبل البدء

---

**إعداد:** أكاديمكس DSS
**التاريخ:** {now.strftime('%d/%m/%Y')}
**للتواصل:** kamelmahi71@gmail.com | +213 676 77 38 92
"""
        return {
            "title": f"دراسة جدوى — {biz['name_ar']}",
            "business_type": biz["name_ar"],
            "location": f"{location}, {wilaya}",
            "investment": investment,
            "date": now.isoformat(),
            "content": full_study,
            "sections": sections,
        }


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Algerian Feasibility Studies")
    parser.add_argument("--business", "-b", required=True,
                        help="Business type: quincaillerie, supermarche, restaurant, atelier_ferro, pharmacie, cafe_patisserie")
    parser.add_argument("--location", "-l", required=True, help="City/location name")
    parser.add_argument("--wilaya", "-w", required=True, help="Wilaya name")
    parser.add_argument("--investment", "-i", type=int, default=None,
                        help="Total investment in DZD (default: average for business type)")
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    parser.add_argument("--api-key", "-k", default=None, help="API key")
    parser.add_argument("--provider", "-p", default=None, choices=["groq", "openrouter", "aihubmix"],
                        help="LLM provider (auto-detect if not specified)")

    args = parser.parse_args()

    try:
        generator = FeasibilityGenerator(provider=args.provider, api_key=args.api_key)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    study = generator.generate_full_study(
        business_type=args.business,
        location=args.location,
        wilaya=args.wilaya,
        investment=args.investment,
    )

    # Output
    output_path = args.output or f"FEASIBILITY_STUDY_{args.business}_{args.location.replace(' ', '_')}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(study["content"])

    print(f"\nStudy generated: {output_path}")
    print(f"Business: {study['business_type']}")
    print(f"Location: {study['location']}")
    print(f"Investment: {study['investment']:,} DZD")
    print(f"Length: {len(study['content']):,} characters")


if __name__ == "__main__":
    main()
