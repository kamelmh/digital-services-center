"""Generate market research reports for Algerian businesses.

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

MARKET_RESEARCH_PROMPT = """أنت محلل سوق جزائري تعد تقرير بحث سوق احترافي.
اكتب بالعربية الفصحى فقط وبأسلوب واضح. استخدم Markdown منظمًا، والجداول عند الحاجة.
كل الأرقام تقديرية ويجب وصفها بأنها تقديرات أولية قابلة للتحقق.
راعي واقع السوق الجزائري، واستخدم الدينار الجزائري."""

SECTIONS = [
    ("ملخص تنفيذي", """اكتب ملخصًا تنفيجيًا موجزًا: الهدف من البحث، النتائج الرئيسية، التوصيات.
اجعله صفحة واحدة.""", 0.5),
    ("وصف السوق المستهدف", """اكتب وصفًا للسوق المستهدف: حجم السوق، الشرائح المستهدفة،
الاتجاهات الحالية، فرص النمو، العوامل المؤثرة (سياسية، اقتصادية، اجتماعية، تقنية).
استخدم نموذج PESTLE إذا كان مناسبًا.""", 0.45),
    ("تحليل العملاء المستهدفين", """اكتب تحليلًا للعملاء المستهدفين: الشرائح الديموغرافية والنفسية،
السلوكيات الشرائية، الاحتياجات غير المُلباة، نقاط الألم، مسار العميل (Customer Journey).""", 0.45),
    ("تحليل المنافسين", """اكتب تحليلًا للمنافسين الرئيسيون: عدد المنافسين، نقاط القوة والضعف،
الحصة السوقية التقديرية، استراتيجيات التسعير، الميزة التنافسية للمشروع.
استخدم نموذج Porter's Five Forces.""", 0.4),
    ("الفرص والتهديدات", """اكتب تحليلًا للفرص والتهديدات في السوق: فرص النمو، التهديدات المحتملة،
الEntry Barriers، فرص الشراكة، التغييرات التنظيمية المحتملة.""", 0.4),
    ("خطة التسويق المقترحة", """اكتب خطة تسويقية مقترحة: استراتيجية التسعير، قنوات التوزيع،
خطة الإطلاق، الأدوات الترويجية، الميزانية التسويقية، مؤشرات الأداء (KPIs).""", 0.4),
    ("توقعات السوق", """اكتب توقعات thị trường لخمس سنوات: حجم السوق المتوقع، معدل النمو،
الحصة السوقية المستهدفة، نقاط الانكسار (Break-even). استخدم جدول conservateur.""", 0.35),
]


class MarketResearchGenerator:
    """Generate an Arabic market research report through a selected LLM provider."""

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
            "User-Agent": "DSC-MarketResearch-Generator/1.0",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://kamelmh.github.io/digital-services-center/"
            headers["X-OpenRouter-Title"] = "DSC Market Research Generator"
        return headers

    def _call_llm(self, prompt: str, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": MARKET_RESEARCH_PROMPT},
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
        location: str,
        wilaya: str,
        business_name: str = "",
    ) -> dict[str, Any]:
        """Generate a market research report."""
        template = BUSINESS_TEMPLATES.get(business_type)
        if not template:
            raise FeasibilityError(f"Unknown business type: {business_type}")

        context = (
            f"اسم المشروع: {business_name or template['name_ar']}\n"
            f"النشاط: {template['name_ar']} ({template['name_en']}).\n"
            f"الموقع: {location}، ولاية {wilaya}.\n"
            f"التصنيف: {template['category']}.\n"
            f"المنتجات/الخدمات: {template['products']}.\n"
        )

        sections: dict[str, str] = {}
        for i, (name, prompt, temp) in enumerate(SECTIONS, 1):
            print(f"  [{i}/{len(SECTIONS)}] إنشاء {name}...", file=sys.stderr)
            sections[name] = self._call_llm(context + prompt, temp)

        now = datetime.now()
        content = f"""---
title: "بحث سوق — {business_name or template['name_ar']}"
date: {now:%Y-%m-%d}
language: ar
currency: DZD
---

# بحث سوق

## {business_name or template['name_ar']}

| البند | التفاصيل |
|---|---|
| النشاط | {template['name_ar']} |
| الموقع | {location}، ولاية {wilaya} |
| تاريخ الإعداد | {now:%d/%m/%Y} |

---

"""
        for name, body in sections.items():
            content += f"## {name}\n\n{body}\n\n---\n\n"

        content += f"""**إعداد:** Digital Services Center — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** {now:%d/%m/%Y}"""

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="market_research",
                input_params={"business_type": business_type, "location": location, "wilaya": wilaya},
                output_content=content,
                metadata={"sections": list(sections.keys())},
            )
        except Exception:
            pass

        return {
            "title": f"بحث سوق — {business_name or template['name_ar']}",
            "location": f"{location}، {wilaya}",
            "date": now.isoformat(timespec="seconds"),
            "content": content,
            "sections": sections,
        }
