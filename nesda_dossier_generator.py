"""NESDA Dossier Generator — 9-part study aligned with Decree 26-154 (April 2026).

Generates a complete NESDA-compatible dossier in Arabic/French with:
- Part I: Project holder info
- Part II: Project presentation
- Part III: Technical study
- Part IV: Market study
- Part V: Investment plan
- Part VI: Financial projections (VAN, TRI, seuil, DR)
- Part VII: Socio-economic impact
- Part VIII: Implementation calendar
- Part IX: Annexes

Uses OpenAI-compatible API (Groq, OpenRouter, AIHubMix).
"""

from __future__ import annotations
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    raise SystemExit("Missing: requests. Install: python -m pip install requests")

from financial_calculators import FinancialCalculators
from policy_constants import WILAYAS

# Keep legacy alias without codes for backward compatibility
ALGERIA_WILAYAS = tuple(w.split("-", 1)[1] for w in WILAYAS)

# ── NESDA Constants ──────────────────────────────────────────────────────────

# Pull from nesda_catalog as single source of truth
try:
    from nesda_catalog import CATALOG as _CATALOG, NESDAActivity
    def _catalog_to_legacy(key: str) -> dict | None:
        a = _CATALOG.get(key)
        if not a:
            return None
        return {"fr": a.name_fr, "ar": a.name_ar, "sector": a.sector}
    NESDA_ACTIVITIES = {k: _catalog_to_legacy(k) for k in _CATALOG if _catalog_to_legacy(k)}
except ImportError:
    NESDA_ACTIVITIES = {}

NESDA_SECTORS = {
    "industrie": {"fr": "Industrie", "ar": "الصناعات", "priority": "high"},
    "agriculture": {"fr": "Agriculture", "ar": "الفلاحة", "priority": "high"},
    "services": {"fr": "Services", "ar": "الخدمات", "priority": "medium"},
    "numérique": {"fr": "Numérique", "ar": "الرقمي", "priority": "high"},
    "environnement": {"fr": "Environnement", "ar": "البيئة", "priority": "high"},
    "artisanat": {"fr": "Artisanat", "ar": "الحرف", "priority": "medium"},
}

NESDA_FINANCING = {
    "personnel_unemployed": {"personal_pct": 0.05, "nesda_pct": 0.25, "bank_pct": 0.70, "label_fr": "Chômeur / Étudiant"},
    "personnel_employed": {"personal_pct": 0.15, "nesda_pct": 0.15, "bank_pct": 0.70, "label_fr": "Salarié / Assuré"},
}



# ── NESDA Dossier Generator ──────────────────────────────────────────────────

class NESDADossierGenerator:
    """Generates a complete NESDA-compatible 9-part dossier."""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
        self.model = model or os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

    def _chat(self, messages: list, temperature: float = 0.7) -> str:
        """Call LLM API."""
        if not self.api_key:
            return self._generate_offline(messages)

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000,
        }
        try:
            r = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return self._generate_offline(messages)

    def _generate_offline(self, messages: list) -> str:
        """Offline generation using templates + business_defaults."""
        return "[OFFLINE MODE] API not configured. Use with --api-key or set OPENAI_API_KEY."

    def generate(self, params: dict) -> dict:
        """Generate complete NESDA dossier.

        params keys:
            activity_key: str - key from NESDA_ACTIVITIES
            business_type: str - key from business_defaults
            wilaya: str - Algerian wilaya name
            location: str - specific location/commune
            investment: int - total investment in DZD
            client_name: str - project holder name
            client_age: int - age
            client_status: str - unemployed/employed/student
            client_education: str - education level
            description: str - brief project description
        """
        activity = NESDA_ACTIVITIES.get(params.get("activity_key", ""), {})
        defaults = {}
        try:
            from business_defaults import get_defaults
            defaults = get_defaults(params.get("business_type", ""))
        except ImportError:
            pass

        investment = params.get("investment", 5_000_000)
        client_status = params.get("client_status", "unemployed")
        financing = NESDA_FINANCING.get(f"personnel_{client_status}", NESDA_FINANCING["personnel_unemployed"])

        results = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "generator": "DSC NESDA Dossier Generator v1.0",
                "decree": "26-154 (April 2026)",
                "plan_type": "9 parties — Annexe V",
            },
            "params": params,
            "activity": activity,
            "financing": financing,
            "sections": {},
        }

        # ── Part I: Project Holder Info ──────────────────────────────────────
        results["sections"]["partie_1"] = self._generate_part1(params)

        # ── Part II: Project Presentation ────────────────────────────────────
        results["sections"]["partie_2"] = self._generate_part2(params, activity, defaults)

        # ── Part III: Technical Study ─────────────────────────────────────────
        results["sections"]["partie_3"] = self._generate_part3(params, activity, defaults)

        # ── Part IV: Market Study ─────────────────────────────────────────────
        results["sections"]["partie_4"] = self._generate_part4(params, activity, defaults)

        # ── Part V: Investment Plan ───────────────────────────────────────────
        results["sections"]["partie_5"] = self._generate_part5(params, investment, financing)

        # ── Part VI: Financial Projections ────────────────────────────────────
        results["sections"]["partie_6"] = self._generate_part6(params, investment, defaults, financing)

        # ── Part VII: Socio-Economic Impact ───────────────────────────────────
        results["sections"]["partie_7"] = self._generate_part7(params, investment)

        # ── Part VIII: Implementation Calendar ────────────────────────────────
        results["sections"]["partie_8"] = self._generate_part8(params)

        # ── Part IX: Annexes ──────────────────────────────────────────────────
        results["sections"]["partie_9"] = self._generate_part9(params)

        full_text = "\n\n".join(results["sections"].values())
        try:
            from training_hook import hook_generation
            hook_generation(
                generator="nesda_dossier",
                input_params={
                    "activity_key": params.get("activity_key", ""),
                    "business_type": params.get("business_type", ""),
                    "wilaya": params.get("wilaya", ""),
                    "investment": investment,
                    "client_status": client_status,
                },
                output_content=full_text,
                metadata={"decree": results["meta"]["decree"]},
            )
        except Exception:
            pass

        return results

    def _generate_part1(self, params: dict) -> str:
        """Part I: Informations sur le porteur de projet."""
        name = params.get("client_name", "[Nom du porteur]")
        age = params.get("client_age", "[Âge]")
        status = params.get("client_status", "unemployed")
        education = params.get("client_education", "[Niveau d'études]")
        wilaya = params.get("wilaya", "[Wilaya]")
        location = params.get("location", "[Commune]")

        status_fr = {"unemployed": "Chômeur inscrit à l'ANEM", "employed": "Salarié", "student": "Étudiant/Diplômé"}
        status_ar = {"unemployed": "عاطل عن العمل مسجل لدى ANEM", "employed": "موظف", "student": "طالب/خريج"}

        return f"""# الجزء الأول: معلومات حامل المشروع — Partie I: Informations sur le porteur du projet

## Les informations personnelles
- **الاسم الكامل (Nom complet):** {name}
- **تاريخ الميلاد (Date de naissance):** [Date de naissance]
- **العمر (Âge):** {age}
- **العنوان (Adresse):** {location}, ولاية {wilaya}
- **رقم الهاتف (Téléphone):** [Numéro]
- **البريد الإلكتروني (Email):** [Email]

## الحالة المهنية
- **الوضع الحالي:** {status_fr.get(status, status)}
- **التكوين (Qualification):** {education}
- **شهادة CDE:** [ oui / non — Attestation de formation CDE obligatoire]

## المسار المهني
- [Décrire brièvement le parcours professionnel et les compétences pertinentes]

## المساهمة الشخصية
- **نسبة المساهمة الشخصية:** {params.get('financing', {}).get('personal_pct', 0.05)*100:.0f}% du coût total du projet
- **المبلغ:** {params.get('investment', 5_000_000) * params.get('financing', {}).get('personal_pct', 0.05):,.0f} DZD

## الوثائق المطلوبة
- [ ] بطاقة التعريف الوطنية (CNI)
- [ ] شهادة الميلاد
- [ ] شهادة الإقامة
- [ ] كشف الحساب البنكي (3 أشهر)
- [ ] شهادة التكوين CDE
- [ ] بطاقة ANEM (إذا كان عاطلاً)
- [ ] تصريح الضربي G12 (إذا كان موظفاً)
"""

    def _generate_part2(self, params: dict, activity: dict, defaults: dict) -> str:
        """Part II: Présentation générale du projet."""
        name_fr = activity.get("fr", "[Activité]")
        name_ar = activity.get("ar", "[النشاط]")
        sector = activity.get("sector", "services")
        investment = params.get("investment", 5_000_000)
        wilaya = params.get("wilaya", "[Wilaya]")
        location = params.get("location", "[Commune]")

        return f"""# الجزء الثاني: العرض العام للمشروع — Partie II: Présentation générale du projet

## التعريف بالمشروع
- **نوع النشاط:** {name_ar} ({name_fr})
- **القطاع:** {NESDA_SECTORS.get(sector, {}).get('ar', sector)} — {NESDA_SECTORS.get(sector, {}).get('fr', sector)}
- **طبيعة النشاط:** [إنتاج سلع / تقديم خدمات / صناعة تحويلية]
- **الاستثمار الإجمالي:** {investment:,} دج
- **مدة التنفيذ:** 4-6 أشهر

## المبررات الاقتصادية
- **الطلب المحلي:** ارتفاع الطلب على {name_ar} في ولاية {wilaya}
- **المنافسة:** [قلة / متوسطة / وجودة] المنافسة في المنطقة
- **الفرص:** إمكانية التوسع في الولايات المجاورة
- **الاستيراد البديل:** [نعم/لا] — تقليل الاعتماد على المنتجات المستوردة

## القيمة المضافة
- خلق {defaults.get('staff_range', [2, 5])[0]}-{defaults.get('staff_range', [2, 5])[1]} مناصب عمل مباشرة
- تلبية حاجة محلية غير مشبعة
- إمكانية التصدير إلى الولايات المجاورة

## أهداف المشروع
1. **الهدف الأول:** إنشاء مؤسسة مصغرة ذات مردودية اقتصادية
2. **الهدف الثاني:** خلق مناصب عمل مستدامة للشباب
3. **الهدف الثالث:** المساهمة في التنمية الاقتصادية المحلية
4. **الهدف الرابع:** [Objectif spécifique au projet]

## تحليل SWOT
| | إيجابي | سلبي |
|---|---|---|
| **داخلي** | **نقاط القوة:** [Compétences, emplacement] | **نقاط الضعف:** [Expérience limitée, capital] |
| **خارجي** | **الفرص:** [Marché en croissance, subventions] | **التهديدات:** [Concurrence, réglementation] |
"""

    def _generate_part3(self, params: dict, activity: dict, defaults: dict) -> str:
        """Part III: Étude technique."""
        investment = params.get("investment", 5_000_000)
        name_fr = activity.get("fr", "[Activité]")
        staff = defaults.get("staff_range", [2, 5])

        return f"""# الجزء الثالث: الدراسة التقنية — Partie III: Étude technique

## وصف النشاط الإنتاجي
- **النشاط:** {name_fr}
- **القدرة الإنتاجية:** [Nombre d'unités/jour ou mois]
- **ساعات العمل:** 8 صباحاً - 6 مساءً (6 أيام/أسبوع)
- **العملاء المستهدفون:** [Particuliers, entreprises, administration]

## المعدات والمعدات الرئيسية
| المعدة | الكمية | التكلفة التقريبية |
|--------|--------|-------------------|
| [Équipement principal 1] | 1 | {investment*0.30:,.0f} دج |
| [Équipement principal 2] | 2 | {investment*0.15:,.0f} دج |
| نظام كمبيوتر + طابعة | 1 | {investment*0.05:,.0f} دج |
| تجهيزات المكتب | 1 مجموعة | {investment*0.05:,.0f} دج |
| معدات أمان | 1 مجموعة | {investment*0.03:,.0f} دج |

## وصف الموقع
- **الموقع:** [Décrire l'emplacement exact]
- **المساحة:** [120-200] م²
- **الكراء:** [Montant du loyer mensuel] دج/شهر
- **المميزات:** وسط المدينة، قرب الأسواق، وصول المواصلات

## عملية الإنتاج / تقديم الخدمة
1. **المرحلة الأولى:** [Réception des matières premières]
2. **المرحلة الثانية:** [Production / Traitement]
3. **المرحلة الثالثة:** [Contrôle qualité]
4. **المرحلة الرابعة:** [Conditionnement / Livraison]
5. **المرحلة الخامسة:** [Vente au client]

## الموارد البشرية
| المنصب | العدد | الأجر الشهري |
|--------|--------|--------------|
| المدير (حامل المشروع) | 1 | [Non rémunéré au départ] |
| عامل إنتاج | {staff[0]-1} | {24_000:,.0f} دج |
| عامل مبيعات | 1 | {24_000:,.0f} دج |
| **المجموع** | **{staff[0]}** | **{(staff[0]-1)*24_000 + 24_000:,.0f} دج/شهر** |

## المعايير والتوائم
- [Sélectionner les normes applicables: normes algériennes, ISO, etc.]
- [Certifications requises pour le secteur d'activité]

## الأثر البيئي
- [Description des mesures environnementales: déchets, émissions, recyclage]
"""

    def _generate_part4(self, params: dict, activity: dict, defaults: dict) -> str:
        """Part IV: Étude de marché."""
        wilaya = params.get("wilaya", "[Wilaya]")
        name_fr = activity.get("fr", "[Activité]")

        return f"""# الجزء الرابع: دراسة السوق — Partie IV: Étude de marché

## وصف السوق المستهدف
- **السوق الجغرافي:** ولاية {wilaya} والولايات المجاورة
- **السكان المستهدفون:** [Tranche d'âge, CSP, etc.]
- **حجم السوق:** [Volume du marché estimé]
- **معدل النمو:** [Taux de croissance annuel du secteur]

## تحليل الطلب
- **الطلب الحالي:** [Besoin non couvert ou insuffisamment couvert]
- **مصادر الطلب:** [Particuliers, entreprises, administration, export]
- **الموسمية:** [Périodes de forte/faible demande]
- **السعر المستهدف:** [Prix moyen du marché]

## تحليل العرض
- **المنافسون المحليون:**
  | المنافس | الموقع | السعر | نقاط القوة | نقاط الضعف |
  |---------|--------|--------|------------|------------|
  | [Concurrent 1] | [Localisation] | [Prix] | [Forces] | [Faiblesses] |
  | [Concurrent 2] | [Localisation] | [Prix] | [Forces] | [Faiblesses] |
  | [Concurrent 3] | [Localisation] | [Prix] | [Forces] | [Faiblesses] |

- **المنتجات البديلة:** [Produits de substitution disponibles]

## استراتيجية التسويق
- **القناة الرئيسية:** [Vente directe, distribution, en ligne]
- **التواصل:** [Réseaux sociaux, bouche-à-oreille, publicité locale]
- **التسعير:** [Stratégie de prix: pénétration, écrémage, compétitif]
- **الترويج:** [Promotions, échantillons, partenariats]

## توقعات المبيعات (5 سنوات)
| السنة | حجم المبيعات (دج) | نمو |
|-------|---------------------|-----|
| 1 | {defaults.get('monthly_revenue_estimate', 500_000)*12:,.0f} | — |
| 2 | {defaults.get('monthly_revenue_estimate', 500_000)*12*1.10:,.0f} | +10% |
| 3 | {defaults.get('monthly_revenue_estimate', 500_000)*12*1.21:,.0f} | +10% |
| 4 | {defaults.get('monthly_revenue_estimate', 500_000)*12*1.33:,.0f} | +10% |
| 5 | {defaults.get('monthly_revenue_estimate', 500_000)*12*1.46:,.0f} | +10% |
"""

    def _generate_part5(self, params: dict, investment: int, financing: dict) -> str:
        """Part V: Plan d'investissement — with NESDA calculator integration."""
        from nesda_calculator import calculate_nesda_financing

        profile = "unemployed" if financing["personal_pct"] <= 0.10 else "employed"
        calc = calculate_nesda_financing(
            total_cost=investment,
            model="triangular",
            profile=profile,
            monthly_revenue=financing.get("monthly_revenue", 500_000),
        )

        amort_rows = ""
        for s in calc.schedule:
            amort_rows += f"| {s['year']} | {s['balance_start']:,.0f} | {s['payment']:,.0f} | {s['interest']:,.0f} | {s['principal']:,.0f} | {s['balance_end']:,.0f} |\n"

        return f"""# الجزء الخامس: خطة الاستثمار — Partie V: Plan d'investissement

## تكلفة الاستثمار الإجمالية
| البند | التكلفة (دج) | النسبة |
|-------|--------------|--------|
| معدات إنتاجية | {investment*0.35:,.0f} | 35% |
| تجهيزات مكتبية | {investment*0.10:,.0f} | 10% |
| تأثيث المحل | {investment*0.10:,.0f} | 10% |
| تجهيز الموقع (أعمال بناء) | {investment*0.15:,.0f} | 15% |
| رأس المال العامل | {investment*0.20:,.0f} | 20% |
| دراسات وتخطيط | {investment*0.05:,.0f} | 5% |
| مصاريف إدارية وقانونية | {investment*0.05:,.0f} | 5% |
| **المجموع** | **{investment:,.0f}** | **100%** |

## هيكل التمويل — صيغة NESDA الثلاثية
| المصدر | النسبة | المبلغ (دج) |
|--------|--------|------------|
| **المساهمة الشخصية** | {calc.personal_pct*100:.0f}% | {calc.personal_amount:,} |
| **مساهمة NESDA (PNR)** | {calc.nesda_pct*100:.0f}% | {calc.nesda_grant:,} |
| **قرض بنكي** | {calc.bank_pct*100:.0f}% | {calc.bank_loan:,} |
| **المجموع** | **100%** | **{calc.total_cost:,}** |

## شروط القرض البنكي
- **سعر الفائدة:** {calc.interest_rate*100:.1f}% (مدعوم من NESDA)
- **مدة السداد:** {calc.repayment_years} سنة ({calc.grace_years} سنة سماح + {calc.repayment_years - calc.grace_years} سنوات سداد)
- **القسط الشهري:** {calc.monthly_payment:,.0f} دج
- **إجمالي الفائدة:** {calc.total_interest:,.0f} دج
- **الإجمالي المدفوع:** {calc.total_repayment:,.0f} دج

## جدول السداد السنوي
| السنة | رصيد البداية | القسط | الفائدة | Principal | الرصيد النهاية |
|-------|-------------|-------|---------|-----------|---------------|
{amort_rows}

## حساب PNR (مساهمة NESDA)
- **المبلغ:** {calc.nesda_grant:,} دج
- **النوع:** قرض غير مربح (interest-free)
- **شروط السداد:** يُسدد بعد القرض البنكي بالكامل

## مؤشرات الجدوى
| المؤشر | القيمة |
|--------|--------|
| الربح الشهري المتوقع | {calc.monthly_profit:,} دج |
| مدة الاسترداد | {calc.payback_months} شهر |
| العائد السنوي (ROI) | {calc.roi_annual:.1f}% |
"""

    def _generate_part6(self, params: dict, investment: int, defaults: dict, financing: dict) -> str:
        """Part VI: Prévisions économiques et financières."""
        from nesda_calculator import calculate_nesda_financing
        
        monthly_rev = defaults.get("monthly_revenue_estimate", 500_000)
        annual_rev = monthly_rev * 12
        cogs_pct = defaults.get("cogs_pct", 0.65)
        operating_pct = defaults.get("operating_pct", 0.15)
        net_margin = defaults.get("profit_margin_target", 0.10)
        bank_loan = investment * financing["bank_pct"]
        
        # Use correct NESDA terms (0% interest, 7y repayment, 1.5y grace)
        nesda_result = calculate_nesda_financing(investment)
        interest_rate = nesda_result.interest_rate
        repayment_years = nesda_result.repayment_years
        grace_years = nesda_result.grace_years
        annual_payment = nesda_result.annual_payment

        years = []
        balance = bank_loan
        for y in range(1, 6):
            growth = (1 + 0.10) ** (y - 1)
            rev = annual_rev * growth
            cogs = rev * cogs_pct
            gross = rev - cogs
            operating = rev * operating_pct
            ebit = gross - operating
            
            # NESDA amortization with grace period
            interest = balance * interest_rate
            if y <= grace_years:
                principal = 0  # Grace period: interest only
            else:
                principal = annual_payment - interest
            balance = max(0, balance - principal)
            
            net = (ebit - interest) * (1 - 0.19)  # after tax
            cf = net + (investment * 0.08)  # add depreciation
            years.append({
                "year": y, "revenue": rev, "cogs": cogs, "gross": gross,
                "operating": operating, "ebit": ebit, "interest": interest,
                "net_income": net, "cash_flow": cf,
            })

        # VAN calculation (single source of truth — FinancialCalculators)
        cash_flows = [-investment] + [yr["cash_flow"] for yr in years]
        van = FinancialCalculators.van(cash_flows)  # 12% Algerian market rate

        # Break-even
        fixed_costs = annual_rev * operating_pct
        variable_cost_ratio = cogs_pct
        breakeven = fixed_costs / (1 - variable_cost_ratio)

        # Payback
        cumulative = -investment
        payback = 5
        for yr in years:
            cumulative += yr["cash_flow"]
            if cumulative >= 0:
                payback = yr["year"]
                break

        table_rows = ""
        for yr in years:
            table_rows += f"""| {yr['year']} | {yr['revenue']:,.0f} | {yr['cogs']:,.0f} | {yr['gross']:,.0f} | {yr['operating']:,.0f} | {yr['ebit']:,.0f} | {yr['net_income']:,.0f} | {yr['cash_flow']:,.0f} |
"""

        return f"""# الجزء السادس: التوقعات الاقتصادية والمالية — Partie VI: Prévisions économiques et financières

## الجدول التلخيصي (5 سنوات)
| السنة | الإيرادات | تكلفة البضاعة | مarge brute | نفقات تشغيلية | EBIT | صافي الربح | تدفق نقدي |
|-------|----------|--------------|------------|--------------|------|------------|----------|
{table_rows}

## المؤشرات المالية
| المؤشر | القيمة | التفسير |
|--------|--------|---------|
| **VAN (القيمة الحالية الصافية)** | {van:,.0f} دج | {'موجب — المشروع مجدٍ' if van > 0 else 'سالب — يحتاج مراجعة'} |
| **نقطة التعادل** | {breakeven:,.0f} دج/سنة | الحد الأدنى من الإيرادات لتجنب الخسائر |
| **مدة الاسترداد** | {payback} سنوات | {'مقبول' if payback <= 4 else 'طويل — يحتاج تحسين'} |
| **هامش الربح الصافي** | {net_margin*100:.1f}% | {'جيد' if net_margin > 0.08 else 'منخفض'} |
| **العائد على الاستثمار (ROI)** | {(annual_rev * net_margin / investment)*100:.1f}% | سنوي |

## تحليل الحساسية
| السيناريو | تغيير المبيعات | VAN | مدة الاسترداد |
|-----------|----------------|-----|---------------|
| **متفائل** | +20% | {van*1.3:,.0f} | {max(1, payback-1)} سنوات |
| **أساسي** | 0% | {van:,.0f} | {payback} سنوات |
| **متشائم** | -20% | {van*0.6:,.0f} | {payback+2} سنوات |

## جدول سداد القرض البنكي
| السنة | رصيد البداية | القسط | الفائدة |Principal | الرصيد النهاية |
|-------|-------------|-------|---------|----------|---------------|
| 1 | {bank_loan:,.0f} | {annual_payment:,.0f} | {bank_loan*interest_rate:,.0f} | 0 | {bank_loan:,.0f} |
| 2 | {bank_loan:,.0f} | {annual_payment:,.0f} | {bank_loan*interest_rate:,.0f} | {annual_payment - bank_loan*interest_rate:,.0f} | {bank_loan - (annual_payment - bank_loan*interest_rate):,.0f} |
"""

    def _generate_part7(self, params: dict, investment: int) -> str:
        """Part VII: Impact socio-économique."""
        staff = params.get("staff_range", [2, 5])
        wilaya = params.get("wilaya", "[Wilaya]")

        return f"""# الجزء السابع: الأثر الاجتماعي والاقتصادي — Partie VII: Impact socio-économique

## خلق مناصب العمل
- **مناصب مباشرة:** {staff[0]}-{staff[1]} موظف
- **مناصب غير مباشرة:** [Nombre] مناصب في سلسلة التوريد
- **نوعية التوظيف:** [CDD, CDI, saisonnier]
- **الأجور:** SNMG ({24_000:,.0f} دج/شهر) فما فوق

## المساهمة في التنمية المحلية
- **الضريبة على الدخل:** [Montant estimé] دج/سنة
- **ال贡献 사회ية (CNAS):** {investment * 0.26 * 0.01:,.0f} دج/شهر
- **الشراء المحلي:** [Pourcentage d'approvisionnement local]
- **التكوين:** [Programme de formation des employés]

## الأثر على النساء والشباب
- **نسبة التوظيف النسوي:** [Pourcentage de femmes employées]
- **التكوين الشبابي:** [Nombre de jeunes formés]
- **الإدماج الاجتماعي:** [Insertion de personnes vulnérables]

## الأثر البيئي
- **إدارة النفايات:** [Plan de gestion des déchets]
- **توفير الطاقة:** [Mesures d'efficacité énergétique]
- **الامتثال البيئي:** [Normes environnementales respectées]

## المساهمة في الاقتصاد الوطني
- **تقليل الاستيراد:** [Montant des importations remplacées]
- **القدرة التصديرية:** [Possibilité d'exportation vers les pays voisins]
- **تنويع الاقتصاد:** المساهمة في تحول اقتصادولاية {wilaya}
"""

    def _generate_part8(self, params: dict) -> str:
        """Part VIII: Calendrier de réalisation."""
        return f"""# الجزء الثامن: جدول التنفيذ — Partie VIII: Calendrier de réalisation

## مراحل التنفيذ
| المرحلة | المدة | الأشهر | النتائج المتوقعة |
|---------|-------|--------|------------------|
| **1. التخطيط والإعداد** | 1 شهر | الشهر 1 | دراسة الجدوى النهائية، تسجيل NESDA |
| **2. التسجيل NESDA** | 1-2 شهر | الشهر 1-2 | قبول الملف، الحصول على شهادة CDE |
| **3. البحث عن الموقع** | 1 شهر | الشهر 2 | توقيع عقد الكراء |
| **4. الأعمال التحضيرية** | 1-2 شهر | الشهر 2-3 | تجهيز الموقع، طلب التأشيرات |
| **5. شراء المعدات** | 1 شهر | الشهر 3-4 | استلام وتركيب المعدات |
| **6. التوظيف والتكوين** | 1 شهر | الشهر 4 | توظيف وتكوين الأعضاء |
| **7. الاختبار التشغيلي** | 2 أسبوع | الشهر 4-5 | تشغيل تجريبي |
| **8. الافتتاح الرسمي** | — | الشهر 5 | بدء النشاط الفعلي |

## الجدول الزمني التفصيلي
```
الشهر 1: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ├─ الأسبوع 1: إنهاء دراسة الجدوى
  ├─ الأسبوع 2: تسجيل NESDA + طلب CDE
  ├─ الأسبوع 3: بدء البحث عن موقع
  └─ الأسبوع 4: استكمال الوثائق

الشهر 2: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ├─ الأسبوع 1: قبول NESDA
  ├─ الأسبوع 2: توقيع عقد الكراء
  ├─ الأسبوع 3: بدء أعمال التجهيز
  └─ الأسبوع 4: متابعة التأشيرات

الشهر 3: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ├─ الأسبوع 1-2: إنهاء التجهيز
  ├─ الأسبوع 3: طلب شراء المعدات
  └─ الأسبوع 4: استلام المعدات

الشهر 4: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ├─ الأسبوع 1: تركيب المعدات
  ├─ الأسبوع 2: التوظيف
  ├─ الأسبوع 3: التكوين
  └─ الأسبوع 4: التشغيل التجريبي

الشهر 5: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ├─ الأسبوع 1-2: اختبار تشغيلي
  ├─ الأسبوع 3: التحسينات النهائية
  └─ الأسبوع 4: الافتتاح الرسمي
```
"""

    def _generate_part9(self, params: dict) -> str:
        """Part IX: Annexes."""
        return f"""# الجزء التاسع: الملحقات — Partie IX: Annexes

## قائمة الملحقات
- **ملحق 1:** نسخة من بطاقة التعريف الوطنية (CNI) — [À joindre]
- **ملحق 2:** شهادة الميلاد — [À joindre]
- **ملحق 3:** شهادة الإقامة — [À joindre]
- **ملحق 4:** كشف الحساب البنكي (3 أشهر) — [À joindre]
- **ملحق 5:** شهادة تكوين CDE — [À joindre]
- **ملحق 6:** بطاقة ANEM — [À joindre]
- **ملحق 7:** عقد الكراء — [À joindre]
- **ملحق 8:** عروض أسعار المعدات — [À joindre]
- **ملحق 9:** تصريح الضربي G12 — [À joindre]
- **ملحق 10:** خطة الموقع — [À joindre]
- **ملحق 11:** صور للمحل — [À joindre]
- **ملحق 12:** عينات من المنتجات — [À joindre]

## ملاحظات قانونية
- هذا الملف مُعد وفقاً للمرسوم التنفيذي رقم 26-154 (أبريل 2026)
- خطة المشروع تتبع الهيكل الرسمي المكون من 9 أجزاء (Annexe V)
- جميع الأرقام تقديرية وقابلة للتعديل حسب الظروف الفعلية
"""


def format_dossier(dossier: dict, lang: str = "ar") -> str:
    """Format dossier as markdown."""
    sections = dossier.get("sections", {})
    header = f"""# دراسة تقنية اقتصادية — NESDA
# Étude Technico-Économique — NESDA

**المولد:** {dossier['meta']['generator']}
**التاريخ:** {dossier['meta']['generated_at']}
**المرسوم:** {dossier['meta']['decree']}
**الهيكل:** {dossier['meta']['plan_type']}

---

"""
    return header + "\n\n---\n\n".join(sections.values())


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NESDA Dossier Generator")
    parser.add_argument("--activity", default="boulangerie", help="Activity key from NESDA_ACTIVITIES")
    parser.add_argument("--business", default="boulangerie", help="Business type from business_defaults")
    parser.add_argument("--wilaya", default="El Bayadh")
    parser.add_argument("--location", default="Centre-ville")
    parser.add_argument("--investment", type=int, default=3_000_000)
    parser.add_argument("--name", default="Ahmed Benali")
    parser.add_argument("--age", type=int, default=28)
    parser.add_argument("--status", default="unemployed", choices=["unemployed", "employed", "student"])
    parser.add_argument("--education", default="Bac+2")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--output", default=None)

    args = parser.parse_args()

    gen = NESDADossierGenerator(api_key=args.api_key, base_url=args.base_url, model=args.model)
    dossier = gen.generate({
        "activity_key": args.activity,
        "business_type": args.business,
        "wilaya": args.wilaya,
        "location": args.location,
        "investment": args.investment,
        "client_name": args.name,
        "client_age": args.age,
        "client_status": args.status,
        "client_education": args.education,
    })

    output = format_dossier(dossier)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Saved: {args.output}")
    else:
        print(output[:3000])
        print(f"\n... [{len(output)} chars total]")
