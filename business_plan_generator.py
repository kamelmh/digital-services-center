"""Generate professional business plans for Algerian businesses.

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

# Reuse constants from feasibility_generator
from feasibility_generator import (
    ALGERIA_DATA,
    BUSINESS_TEMPLATES,
    PROVIDERS,
    FeasibilityError,
)

BUSINESS_PLAN_PROMPT = """أنت مستشار أعمال جزائري تعد خطة عمل احترافية لصاحب مشروع.
اكتب بالعربية الفصحى فقط وبأسلوب واضح مناسب لتقديمه لصاحب مشروع أو بنك أو مستثمر.
استخدم Markdown منظمًا، والجداول عند الحاجة. كل الأرقام تقديرية ويجب وصفها بأنها
تقديرات أولية قابلة للتحقق. لا تدّعِ إحصاءات أو مصادر أو جهات حكومية مؤكدة.
راعي واقع السوق الجزائري، واستخدم الدينار الجزائري."""

SECTIONS = [
    ("ملخص تنفيذي", """اكتب ملخصًا تنفيذيًا موجزًا للمشروع يشمل: الفكرة الأساسية، القيمة المضافة،
السوق المستهدف، الحجم الاستثماري، العائد المتوقع، والموارد المطلوبة.
اجعل الملخص صفحة واحدة فقط، واضح ومباشر.""", 0.5),
    ("رؤية المشروع وأهدافه", """اكتب رؤية المشروع وأهدافه على المدى القصير (سنة) والمتوسط (3 سنوات) والطويل (5 سنوات).
حدد المهمة والقيم والرسالة. اذكر الأهداف الذكية (SMART) quantify كمّيًا قدر الإمكان.""", 0.5),
    ("وصف المنتجات والخدمات", """اكتب وصفًا تفصيليًا للمنتجات أو الخدمات التي يقدمها المشروع.
حدد الميزة التنافسية والقيمة المضافة للعميل. اذكر المنتجات الأساسية والثانوية.""", 0.45),
    ("تحليل السوق والمنافسة", """اكتب تحليلًا للسوق المستهدف: حجم السوق، الشرائح المستهدفة، المنافسون الرئيسيون، نقاط القوة والضعف.
استخدم نموذج SWOT أو Porter's Five Forces إذا كان مناسبًا. اذكر خطة التسويق والترويج.""", 0.45),
    ("خطة التسويق والمبيعات", """اكتب خطة التسويق: القنوات المستهدفة، استراتيجية التسعير، خطة الإطلاق، أدوات الترويج،
والمؤشرات الرئيسية للإنجاز (KPIs). حدد الميزانية التسويقية.""", 0.4),
    ("خطة العمليات والإدارة", """اكتب خطة العمليات: هيكل التنظيم، الهيكل الإداري، الموارد البشرية المطلوبة،
سير العمل، الموردون، التراخيص والتراخيص المطلوبة.""", 0.4),
    ("الدراسة المالية", """اكتب الدراسة المالية: تكاليف التأسيس، رأس المال العامل، التكاليف التشغيلية الشهرية،
توقعات الإيرادات لخمس سنوات، مؤشرات الجدوى (TIR، VAN، فترة الاسترداد).
استخدم: TVA 19%، ضريبة الشركات 19%، CNAS 26%، فائدة قروض 9%.""", 0.35),
    ("تحليل المخاطر", """اكتب تحليل للمخاطر الرئيسية: مالية، سوقية، تشغيلية، قانونية.
اقترح استراتيجيات التخفيف من كل مخاطرة. حدد مستوى المخاطرة (عالي/متوسط/منخفض).""", 0.4),
    ("الجدول الزمني للتنفيذ", """اكتب جدولًا زمنيًا للتنفيذ على 3 مراحل:
- مرحلة التأسيس (0-3 أشهر)
- مرحلة الإطلاق (3-6 أشهر)
- مرحلة النمو (6-24 شهر)
اذكر المخرجات الرئيسية لكل مرحلة.""", 0.4),
]


class BusinessPlanGenerator:
    """Generate an Arabic business plan through a selected LLM provider."""

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
            "User-Agent": "DSC-BusinessPlan-Generator/1.0",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://kamelmh.github.io/digital-services-center/"
            headers["X-OpenRouter-Title"] = "DSC Business Plan Generator"
        return headers

    def _call_llm(self, prompt: str, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": BUSINESS_PLAN_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 4000,
        }
        for attempt in range(3):
            try:
                response = self.session.post(self.url, headers=self._headers(), json=payload, timeout=(10, 90))
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
    ) -> dict[str, Any]:
        """Generate a full business plan and return dict with sections + markdown."""
        template = BUSINESS_TEMPLATES.get(business_type)
        if not template:
            raise FeasibilityError(f"Unknown business type: {business_type}")

        context = (
            f"اسم المشروع: {business_name}\n"
            f"النشاط: {template['name_ar']} ({template['name_en']}).\n"
            f"الموقع: {location}، ولاية {wilaya}.\n"
            f"التصنيف: {template['category']}.\n"
            f"الاستثمار التقديري: {investment:,} دج.\n"
            f"المنتجات/الخدمات: {template['products']}.\n"
            f"عدد العمال المتوقع: {template['staff'][0]}–{template['staff'][1]}.\n"
            f"المساحة المقترحة: {template['area_sqm'][0]}–{template['area_sqm'][1]} م².\n"
        )

        sections: dict[str, str] = {}
        for i, (name, prompt, temp) in enumerate(SECTIONS, 1):
            print(f"  [{i}/{len(SECTIONS)}] إنشاء {name}...", file=sys.stderr)
            sections[name] = self._call_llm(context + prompt, temp)

        now = datetime.now()
        content = f"""---
title: "خطة عمل — {business_name}"
date: {now:%Y-%m-%d}
language: ar
currency: DZD
---

# خطة عمل

## {business_name}

| البند | التفاصيل |
|---|---|
| اسم المشروع | {business_name} |
| النشاط | {template['name_ar']} |
| الموقع | {location}، ولاية {wilaya} |
| الاستثمار التقديري | {investment:,} دج |
| تاريخ الإعداد | {now:%d/%m/%Y} |

---

"""
        for name, body in sections.items():
            content += f"## {name}\n\n{body}\n\n---\n\n"

        content += """## ملاحظات ختامية

- يجب استبدال كل التقديرات بأسعار محلية قبل التنفيذ.
- راجع خطة العمل مع محاسب أو مستشار مختص.
- تم إعداد هذه الوثيقة باللغة العربية وللاستخدام المهني داخل الجزائر.

**إعداد:** Digital Services Center — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** """ + now.strftime("%d/%m/%Y")

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="business_plan",
                input_params={"business_type": business_type, "business_name": business_name, "location": location, "wilaya": wilaya, "investment": investment},
                output_content=content,
                metadata={"sections": list(sections.keys())},
            )
        except Exception:
            pass

        return {
            "title": f"خطة عمل — {business_name}",
            "business_name": business_name,
            "business_type": template["name_ar"],
            "location": f"{location}، {wilaya}",
            "investment": investment,
            "date": now.isoformat(timespec="seconds"),
            "content": content,
            "sections": sections,
        }
