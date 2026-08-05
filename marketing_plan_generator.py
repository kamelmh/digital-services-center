"""Generate comprehensive marketing plans for Algerian businesses.

Covers positioning, channels, content strategy, budget, KPIs, and campaigns.
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

MARKETING_SYSTEM_PROMPT = """أنت مستشار تسويق جزائري متخصص في التخطيط التسويقي للمشاريع الناشئة والقائمة.
اكتب بالعربية الفصحى فقط وبأسلوب واضح. استخدم Markdown منظمًا، والجداول عند الحاجة.
راعي واقع السوق الجزائري:
- الفيسبوك هو المنصة الأولى في الجزائر (93% من المستخدمين)
- إنستغرام وتيك توك في نمو سريع خاصة عند الشباب
- واتساب هو أداة التواصل الأولى للبيع المباشر
- التواجد الرقمي عبر خرائط Google ضروري للأنشطة المحلية
- الإعلانات المطبوعة واللافتات لا تزال فعّالة في المدن الصغيرة
- المحتوى بالعربية أو بالدارجة الجزائرية هو الأنجع
- ثقافة التوصية (Wasta) قوية — سجّل آراء العملاء
- التسعير الحسّي (999 دج بدلاً من 1000) فعّال
لا تدّعِ إحصاءات أو مصادر رسمية مؤكدة؛ سمّي كل رقم بأنه تقدير."""


SECTIONS = [
    ("ملخص تنفيذي تسويقي", """اكتب ملخصًا تنفيذيًا موجزًا لخطة التسويق:
- الهدف التسويقي الرئيسي للسنة الأولى
- الجمهور المستهدف الأساسي والثانوي
- الميزة التنافسية الرئيسية (UVP)
- استراتيجية التسعير
- الميزانية التسويقية الإجمالية كنسبة من الإيرادات (عادة 5-15%)
- أبرز الحملات الم计划ة""", 0.45),
    ("تحليل السوق والمنافسة", """اكتب تحليلًا تسويقيًا للسوق:
- حجم السوق المستهدف ونسبة الاختراق المطلوبة
- الشرائح المستهدفة (Demo + Psycho + Behavioral)
- تحليل المنافسين: القناة، التسعير، نقاط القوة والضعف
- SWOT Analysis للمشروع من منظور تسويقي
- نقاط الألم للعملاء التي يحلها المشروع
- Buyer Persona واحد على الأقل (جنس، عمر، دخل، عادات شرائية، منصات مفضلة)""", 0.4),
    ("ال定位 والمessaging", """اكتب استراتيجية الت positioning والرسائل:
- العرض القيمي الرئيسي (Value Proposition): [اسم المشروع] يساعد [الشريحة] على [الفايدة] من خلال [الطريقة]
- الرسائل الأساسية (3 رسائل رئيسية)
- نبرة التواصل (Tone of Voice): رسمي / ودي / مرح / مهني
- شعار الدعاية (Tagline) بالعربية
- الميزات التنافسية الرئيسية (3-4 نقاط)
- قصة العلامة التجارية (Brand Story) — 3 جمل""", 0.4),
    ("القنوات التسويقية", """حدد القنوات التسويقية مع توزيع الميزانية:
- **رقمي** (60-70% من الميزانية):
  - فيسبوك: منشورات + إعلانات مدفوعة (الميزانية الرئيسية)
  - إنستغرام: محتوى بصري + Reels
  - واتساب: قائمة بث + خدمة العملاء
  - خرائط Google: تسجيل + مراجعات
  - الموقع الإلكتروني: بسيط، متوافق مع الهاتف
- **تقليدي** (20-30%):
  - لافتات خارجية (Panneau)
  - مطويات / فلايرات
  - إعلانات محلية (راديو، جريدة محلية)
- **علاقات عامة** (5-10%):
  - شراكات محلية
  - رعاية أحداث محلية
  - برنامج الإحالة (Referral)
وضّح سبب اختيار كل قناة ونسبة التوزيع.""", 0.4),
    ("استراتيجية المحتوى", """اكتب استراتيجية المحتوى:
- **أنواع المحتوى**: تعليمي (40%)، ترفيهي (30%)، تجاري (20%)، تفاعلي (10%)
- **تقويم المحتوى الأسبوعي**: كم منشور لكل منصة
- **أنواع المحتوى**: صور، فيديو قصير، Reels، Stories، منشورات نصية، بث مباشر
- **مواضيع المحتوى** (10 أفكار جاهزة للتطبيق)
- **محتوى UGC** (User-Generated Content): كيف تحفّز العملاء على المشاركة
- **SEO المحلي**: الكلمات المفتاحية المستهدفة
- **أدوات الإنتاج**: هاتف ذكي + Canva + واتساب بزنس""", 0.4),
    ("خطة الحملات", """اكتب خطة حملات تفصيلية:
- **حملة الإطلاق** (الأسبوع 1-4):
  - الهدف، الجمهور، الرسالة، القناة، الميزانية، النتائج المتوقعة
  - عرض الإطلاق (خصم أو هدية)
- **حملة موسمية** ( Ramadan، عيد الأضحى، البونط، 1 نوفمبر):
  - رسائل خاصة لكل مناسبة
- **حملة ولاء** (كل 3 أشهر):
  - برنامج نقاط / خصومات للعملاء الحاليين
  - برنامج الإحالة (ادعُ صديق = خصم)
- **حملة أفقية** (مستمرة):
  - إعلانات فيسبوك مدفوعة دائمة
  - محتوى Reels أسبوعي""", 0.4),
    ("الميزانية التسويقية", """أنشئ جدول الميزانية التسويقية الشهرية والسنوية:
```
البند | شهري (دج) | سنوي (دج) | % من الميزانية
```
- إعلانات فيسبوك/إنستغرام
- تصميم المحتوى
- لافتات ومطويات
- عروض وأحداث
- أدوات رقمية (Canva Pro، واتساب بزنس)
- علاقات عامة ورعايات
- احتياطي (10%)
احسب كنسبة من الإيرادات المتوقعة. اذكر أن الميزانية قابلة للتعديل كل 3 أشهر.""", 0.35),
    ("مؤشرات الأداء (KPIs)", """حدد مؤشرات الأداء التسويقية:
- **مبيعات**: عدد المعاملات الشهرية، متوسط قيمة المعاملة، الإيراد الشهري
- **عملاء**: عدد العملاء الجدد، معدل الاحتفاظ، تكلفة اكتساب العميل (CAC)
- **رقمي**: عدد المتابعين، معدل التفاعل (Engagement Rate)، الوصول، النقرات
- **مراجعات**: تقييمات Google، مراجعات فيسبوك، رضا العملاء
- ** Retorna sur Investissement**: ROI لكل قناة، عائد الحملة
- **جدول متابعة شهري**: كيف تقيّم الأداء كل شهر""", 0.35),
    ("التنفيذ والجدول الزمني", """اكتب خطة التنفيذ التفصيلية:
- **الشهر 1-2**: التأسيس (تسجيل المنصات، تصميم الهوية، إنشاء المحتوى الأساسي)
- **الشهر 3-4**: الإطلاق (حملة الإطلاق، أولى الإعلانات، قياس النتائج)
- **الشهر 5-6**: التحسين (تعديل الاستراتيجية بناءً على البيانات)
- **الشهر 7-12**: النمو (توسيع القنوات، زيادة الميزانية)
- **مسؤول**: من المسؤول عن كل مهمة (صاحب المشروع / موظف / وكالة)
- **أدوات المتابعة**: Google Analytics، Facebook Insights، واتساب بزنس""", 0.35),
]


class MarketingPlanGenerator:
    """Generate an Arabic marketing plan through a selected LLM provider."""

    def __init__(self, provider: str | None = None, api_key: str | None = None, model: str | None = None) -> None:
        self.provider = self._resolve_provider(provider, api_key)
        config = PROVIDERS[self.provider]
        self.api_key = api_key or next(
            (os.getenv(k) for k in config["key_env"] if os.getenv(k)), None
        )
        if not self.api_key:
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
            "User-Agent": "DSC-MarketingPlan/1.0",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://kamelmh.github.io/digital-services-center/"
            headers["X-OpenRouter-Title"] = "DSC Marketing Plan Generator"
        return headers

    def _call_llm(self, prompt: str, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": MARKETING_SYSTEM_PROMPT},
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
        monthly_budget: int | None = None,
    ) -> dict[str, Any]:
        """Generate a comprehensive marketing plan."""
        template = BUSINESS_TEMPLATES.get(business_type)
        if not template:
            raise FeasibilityError(f"Unknown business type: {business_type}")

        # Estimate marketing budget if not provided
        if monthly_budget is None:
            # 8% of annual investment as marketing budget
            monthly_budget = int(investment * 0.08 / 12)

        min_margin, max_margin = template["margin"]

        context = (
            f"اسم المشروع: {business_name}\n"
            f"النشاط: {template['name_ar']} ({template['name_en']}).\n"
            f"الموقع: {location}، ولاية {wilaya}.\n"
            f"الاستثمار: {investment:,} دج.\n"
            f"الميزانية التسويقية الشهرية المقدرة: {monthly_budget:,} دج.\n"
            f"هامش الربح: {min_margin*100:.0f}%-{max_margin*100:.0f}%.\n"
            f"المنتجات/الخدمات: {template['products']}.\n"
            f"عدد العمال: {template['staff'][0]}-{template['staff'][1]}.\n"
        )

        sections: dict[str, str] = {}
        for i, (name, prompt, temp) in enumerate(SECTIONS, 1):
            print(f"  [{i}/{len(SECTIONS)}] إنشاء {name}...", file=sys.stderr)
            sections[name] = self._call_llm(context + prompt, temp)

        now = datetime.now()
        content = f"""---
title: "خطة تسويقية — {business_name}"
date: {now:%Y-%m-%d}
language: ar
currency: DZD
---

# خطة تسويقية

## {business_name}

| البند | التفاصيل |
|---|---|
| اسم المشروع | {business_name} |
| النشاط | {template['name_ar']} |
| الموقع | {location}، ولاية {wilaya} |
| الاستثمار | {investment:,} دج |
| الميزانية الشهرية | {monthly_budget:,} دج |
| تاريخ الإعداد | {now:%d/%m/%Y} |

---

"""
        for name, body in sections.items():
            content += f"## {name}\n\n{body}\n\n---\n\n"

        content += """## ملاحظات ختامية

- راجع هذه الخطة كل 3 أشهر وعدّلها بناءً على النتائج الفعلية.
- ركّز على القنوات التي تجلب أفضل عائد (ROI).
- لا ت分散 الميزانية على كل القنوات في البداية؛ ابدأ بالأساسيات.
- قيّم أداء كل حملة خلال 48 ساعة من إطلاقها.

**إعداد:** Digital Services Center — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** """ + now.strftime("%d/%m/%Y")

        return {
            "title": f"خطة تسويقية — {business_name}",
            "business_name": business_name,
            "monthly_budget": monthly_budget,
            "date": now.isoformat(timespec="seconds"),
            "content": content,
            "sections": sections,
        }
