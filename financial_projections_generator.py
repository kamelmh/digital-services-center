"""Generate detailed financial projections for Algerian businesses.

Covers P&L, cash flow, break-even, ROI, NPV, IRR, and sensitivity analysis.
Uses the same LLM provider pattern as feasibility_generator.py.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from typing import Any

try:
    import requests
except ImportError as error:
    raise SystemExit(
        "Missing dependency: requests. Install it with: python -m pip install requests"
    ) from error

from feasibility_generator import (
    ALGERIA_DATA,
    BUSINESS_TEMPLATES,
    PROVIDERS,
    FeasibilityError,
)

FINANCIAL_SYSTEM_PROMPT = """أنت محاسب مالي جزائري متخصص في إعداد التوقعات المالية للمشاريع.
اكتب بالعربية الفصحى فقط. استخدم جداول Markdown منظمة، وتأكد من تجانس الأرقام
عبر جميع الجداول (إيرادات - تكاليف = أرباح = تدفقات). كل الأرقام بالدينار الجزائري.
استخدم الافتراضات المالية الجزائرية التالية كمرجع أساسي:
- TVA: 19%
- ضريبة الشركات: 19%
- CNAS صاحب العمل: 26% من الأجر الإجمالي
- IRG (ضريبة الدخل): 0% حتى 180,000 دج/سنة، 20% من 180,001-360,000، 30% من 360,001-720,000، 35% فوق 720,000
- SMIG 2025: 20,000 دج/شهر
- معدل الفائدة على القروض البنكية: 9% (تقديري)
- معدل التضخم: 3-5% سنويًا
- معدل النمو في الجزائر: 3-4% سنويًا
- هامش الربح الصافي المتوقع: 10-25% حسب النشاط
لا تدّعِ دقة محاسبية نهائية؛ وصف كل الأرقام بأنها تقديرات أولية قابلة للتحقق."""


SECTIONS = [
    ("الافتراضات المالية", """اذكر الافتراضات المالية الأساسية للمشروع:
- معدل النمو في الإيرادات (السنة الأولى، 이후)
- معدل التضخم المطبق على التكاليف
- هامش الربح الإجمالي والصافي المتوقع
- معدل استهلاك المخزون
- متوسط أجر الموظف (≥ SMIG 20,000 دج)
- معدل CNAS المدفوع
- معدل TVA المطبّق
- معدل الفائدة على التمويل
- معدل الضرائب
- فترة استرداد رأس المال المتوقعة
- عدد أيام العمل الشهرية
ضع جدولًا مركزيًا لكل الافتراضات.""", 0.3),
    ("توقعات الإيرادات لخمس سنوات", """أنشئ جدول إيرادات مفصلاً لخمس سنوات:
- السنة الأولى: إيرادات شهرية (يناير→ديسمبر) مع مراعاة الموسمية
- Years 2-5: نمو سنوي مقدر
- قسّم الإيرادات حسب مصدرها: مبيعات، خدمات، أخرى
- اذكر متوسط سعر البيع لكل منتج/خدمة
- احسب متوسط المعاملات اليومية/الشهرية
- استخدم نموذج conservateur (ليس optimiste)
وضّح أي افتراضات موسمية.""", 0.35),
    ("هيكل التكاليف", """أنشئ جدول التكاليف المفصلاً:
- **تكاليف ثابتة** (لا تتغير بالحجم): الإيجار، الرواتب الأساسية، الكهرباء والغاز، التأمين، الربط، الضرائب الجماعية
- **تكاليف متغيرة** (تتغير بالحجم): المواد الأولية، العمالة الإضافية، التوصيل، التغليف
- **تكاليف شهرية** vs **تكاليف سنوية**
- **نسبة التكاليف الثابتة من الإيرادات** (يجب أن تكون < 50% للمشاريع الصغيرة)
- **نسبة التكاليف المتغيرة من الإيرادات** (عادة 40-70%)
- استخدم SMIG كحد أدنى للأجور
وضّح أي تكاليف استثنائية (صيانة سنوية، تحديث معدات، إلخ).""", 0.35),
    ("قائمة الأرباح والخسائر", """أنشئ قائمة أرباح وخسائر (Income Statement) لخمس سنوات:
```
السنة | الإيرادات | تكلفة البضاعة المباعة | الربح الإجمالي | التكاليف التشغيلية | صافي الربح قبل الضرائب | الضرائب | صافي الربح
```
- احسب TVA على كل إيراد (19%)
- احسب CNAS على كل أجر (26%)
- احسب IRG على الأرباح الصافية
- اذكر أرقامًا متسقة عبر جميع السنوات
- احسب هامش الربح الصافي كنسبة من الإيرادات""", 0.3),
    ("التدفقات النقدية", """أنشئ جدول تدفقات نقدية (Cash Flow Statement) لخمس سنوات:
```
السنة | التدفقات من العمليات | التدفقات من الاستثمارات | التدفقات من التمويل | صافي التدفق النقدي | التدفق النقدي التراكمي
```
- التدفقات من العمليات: صافي الربح + الإهلاك - التغير في رأس المال العامل
- التدفقات من الاستثمارات: شراء المعدات، التحسينات، التأسيس
- التدفقات من التمويل: القروض المقبوضة، أقساط القروض المدفوعة
- احسب رأس المال العامل الصافي (ال短期 الأصول - ال短期 الخصوم)
- اذكر التدفق النقدي الأقصى المطلوب (peak cash requirement)""", 0.3),
    ("تحليل نقطة التعادل", """احسب نقطة التعادل (Break-even Point):
- **نقطة التعادل بالوحدات**: التكاليف الثابتة / (سعر الوحدة - تكلفة الوحدة المتغيرة)
- **نقطة التعادل بالقيمة**: التكاليف الثابتة / نسبة هامش الربح الإجمالي
- **فترة الوصول لنقطة التعادل**: شهور
- اعرض تحليلًا بصريًا: إيرادات vs تكاليف عبر الزمن
- احسب **نسبة Safety Margin**: (المبيعات المتوقعة - التعادل) / المبيعات المتوقعة
- اذكر ماذا يحدث لو انخفضت المبيعات 10% أو 20%""", 0.35),
    ("مؤشرات العائد", """احسب مؤشرات العائد الرئيسية:
- **ROI** (عائد الاستثمار): صافي الربح / الاستثمار الإجمالي × 100
- ** VAN** (صافي القيمة الحالية): بسعر خصم 12%
- **TIR** (معدل العائد الداخلي)
- **فترة الاسترداد** (Payback Period): متى يتعافى الاستثمار
- **نسبة الربح على المبيعات** (Net Profit Margin)
- **دوران رأس المال العامل** (Working Capital Turnover)
وضّح طريقة حساب كل مؤشر. اذكر أن هذه تقديرات أولية.""", 0.3),
    ("تحليل الحساسية", """أنشئ تحليل حساسية (Sensitivity Analysis) لثلاث سيناريوهات:
- **السيناريو الأساسي** (Base Case): الافتراضات الأصلية
- **السيناريو الحذر** (Conservative): انخفاض المبيعات 15%، ارتفاع التكاليف 10%
- **السيناريو Optimization** (Optimistic): زيادة المبيعات 15%، انخفاض التكاليف 5%

لكل سيناريو، اعرض: الإيرادات، التكاليف، صافي الربح، نقطة التعادل، فترة الاسترداد.
أيضًا: تأثير تغير سعر الصرف +/- 10%، تأثير تغير معدل التضخم +/- 2%.""", 0.35),
    ("خطة التمويل", """اكتب خطة التمويل:
- هيكل التمويل: الذاتي + القروض (النسبة لكل один)
- جدول سداد القروض (_amortization schedule) لـ 5 سنوات
- الفائدة الإجمالية المدفوعة
- الحد الأدنى للعائد لتغطية القرض
- خيارات التمويل البديلة (قروض بنكية، تمويل حكومي، شراكة)
- المخاطر المالية (ماذا لو تأخر السداد؟)""", 0.4),
]


class FinancialProjectionsGenerator:
    """Generate detailed Arabic financial projections through a selected LLM provider."""

    def __init__(self, provider: str | None = None, api_key: str | None = None, model: str | None = None, allow_offline: bool = True) -> None:
        self.offline = False
        try:
            self.provider = self._resolve_provider(provider, api_key)
        except FeasibilityError:
            if allow_offline:
                self.offline = True
                self.provider = "offline"
                self.api_key = None
                self.model = "offline-templates"
                self.url = ""
                self.session = __import__("requests").Session()
                return
            raise
        config = PROVIDERS[self.provider]
        self.api_key = api_key or next(
            (os.getenv(k) for k in config["key_env"] if os.getenv(k)), None
        )
        if not self.api_key:
            if allow_offline:
                self.offline = True
                self.provider = "offline"
                self.model = "offline-templates"
                self.url = ""
                self.session = __import__("requests").Session()
                return
            variables = " or ".join(config["key_env"])
            raise FeasibilityError(f"No API key found for {self.provider}. Set {variables}.")
        self.model = model or config["model"]
        self.url = config["url"]
        self.session = requests.Session()

    def _resolve_provider(self, requested: str | None, api_key: str | None) -> str:
        if requested:
            if requested not in PROVIDERS:
                raise FeasibilityError(f"Unsupported provider: {requested}.")
            return requested
        for name, config in PROVIDERS.items():
            if os.getenv(config["key_env"][0]):
                return name
        raise FeasibilityError("No API key found.")

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DSC-FinancialProjections/1.0",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://kamelmh.github.io/digital-services-center/"
            headers["X-OpenRouter-Title"] = "DSC Financial Projections Generator"
        return headers

    def _call_llm(self, prompt: str, temperature: float = 0.35) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": FINANCIAL_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 4000,
        }
        for attempt in range(3):
            try:
                response = self.session.post(self.url, headers=self._headers(), json=payload, timeout=(10, 120))
                if response.ok:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                if response.status_code in {429, 500, 502, 503}:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                raise FeasibilityError(f"Provider error (HTTP {response.status_code})")
            except requests.Timeout:
                if attempt == 2:
                    raise FeasibilityError("Provider timed out after 3 attempts")
                time.sleep(min(2 ** attempt, 8))
        raise FeasibilityError("Provider unavailable")

    def generate(
        self,
        business_type: str,
        business_name: str,
        location: str,
        wilaya: str,
        investment: int,
        num_employees: int = 5,
        monthly_revenue_estimate: int | None = None,
    ) -> dict[str, Any]:
        """Generate full financial projections."""
        if getattr(self, "offline", False) or not getattr(self, "api_key", None):
            from offline_templates import financial_projections_offline
            return financial_projections_offline(business_type, business_name, location, wilaya, investment, num_employees, monthly_revenue_estimate)
        template = BUSINESS_TEMPLATES.get(business_type)
        if not template:
            raise FeasibilityError(f"Unknown business type: {business_type}")

        # Estimate monthly revenue if not provided
        if monthly_revenue_estimate is None:
            min_margin, max_margin = template["margin"]
            avg_margin = (min_margin + max_margin) / 2
            # Assume investment turns over 1.5x per year
            monthly_revenue_estimate = int(investment * 1.5 / 12)

        context = (
            f"اسم المشروع: {business_name}\n"
            f"النشاط: {template['name_ar']} ({template['name_en']}).\n"
            f"الموقع: {location}، ولاية {wilaya}.\n"
            f"الاستثمار الإجمالي: {investment:,} دج.\n"
            f"عدد العمال: {num_employees}.\n"
            f"الإيراد الشهري المقدر: {monthly_revenue_estimate:,} دج.\n"
            f"هامش الربح النشاط: {template['margin'][0]*100:.0f}%-{template['margin'][1]*100:.0f}%.\n"
            f"المساحة: {template['area_sqm'][0]}-{template['area_sqm'][1]} م².\n"
        )

        sections: dict[str, str] = {}
        for i, (name, prompt, temp) in enumerate(SECTIONS, 1):
            print(f"  [{i}/{len(SECTIONS)}] إنشاء {name}...", file=sys.stderr)
            sections[name] = self._call_llm(context + prompt, temp)

        now = datetime.now()
        content = f"""---
title: "توقعات مالية — {business_name}"
date: {now:%Y-%m-%d}
language: ar
currency: DZD
---

# التوقعات المالية

## {business_name}

| البند | التفاصيل |
|---|---|
| اسم المشروع | {business_name} |
| النشاط | {template['name_ar']} |
| الموقع | {location}، ولاية {wilaya} |
| الاستثمار الإجمالي | {investment:,} دج |
| عدد العمال | {num_employees} |
| الإيراد الشهري المقدر | {monthly_revenue_estimate:,} دج |
| تاريخ الإعداد | {now:%d/%m/%Y} |

---

"""
        for name, body in sections.items():
            content += f"## {name}\n\n{body}\n\n---\n\n"

        content += """## ملاحظات ختامية

- جميع الأرقام تقديرية أولية ويجب التحقق منها ميدانيًا.
- راجع خطة التمويل مع بنك أو مستشار مالي قبل البدء.
- راعِ التقلبات المحتملة في أسعار الصرف ومعدلات التضخم.
- يُنصح بتحديث هذه التوقعات كل 6 أشهر.

**إعداد:** Digital Services Center — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** """ + now.strftime("%d/%m/%Y")

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="financial_projections",
                input_params={"business_type": business_type, "investment": investment, "monthly_revenue": monthly_revenue_estimate},
                output_content=content,
                metadata={"sections": list(sections.keys())},
            )
        except Exception:
            pass

        return {
            "title": f"توقعات مالية — {business_name}",
            "business_name": business_name,
            "investment": investment,
            "monthly_revenue": monthly_revenue_estimate,
            "date": now.isoformat(timespec="seconds"),
            "content": content,
            "sections": sections,
        }
