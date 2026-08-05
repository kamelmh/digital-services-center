"""Generate professional Arabic feasibility studies for Algerian businesses.

The generator uses OpenAI-compatible chat-completions APIs.  It supports Groq,
OpenRouter, and AIHubMix without storing keys in source control.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError as error:  # pragma: no cover - depends on local installation
    raise SystemExit(
        "Missing dependency: requests. Install it with: python -m pip install requests"
    ) from error


class FeasibilityError(RuntimeError):
    """Raised when a feasibility study cannot be generated safely."""


ALGERIA_DATA = {
    "currency": "دج",
    "currency_code": "DZD",
    "population_growth_rate": 0.018,
    "smig_monthly": 20_000,
    "tva_rate": 0.19,
    "corporate_tax_rate": 0.19,
    "cnas_employer_rate": 0.26,
    "loan_interest_rate": 0.09,
    "discount_rate": 0.12,
    "inflation_rate": 0.03,
    "wilayas": {
        "El Bayadh": {"population": 228_000, "market_index": 0.85},
        "Alger": {"population": 3_915_000, "market_index": 1.15},
        "Oran": {"population": 1_560_000, "market_index": 1.05},
        "Constantine": {"population": 938_000, "market_index": 0.95},
        "Blida": {"population": 1_002_000, "market_index": 0.95},
        "Sétif": {"population": 1_489_000, "market_index": 0.90},
        "Tlemcen": {"population": 949_000, "market_index": 0.90},
        "Béjaïa": {"population": 912_000, "market_index": 0.90},
        "Tizi Ouzou": {"population": 1_127_000, "market_index": 0.95},
        "Annaba": {"population": 640_000, "market_index": 0.95},
        "Batna": {"population": 1_119_000, "market_index": 0.85},
        "Djelfa": {"population": 1_092_000, "market_index": 0.80},
        "M'sila": {"population": 990_000, "market_index": 0.80},
        "Chlef": {"population": 1_002_000, "market_index": 0.85},
        "Tlemcen": {"population": 949_000, "market_index": 0.90},
        "Biskra": {"population": 721_000, "market_index": 0.80},
        "Boumerdès": {"population": 802_000, "market_index": 0.90},
        "Tiaret": {"population": 846_000, "market_index": 0.80},
        "Bordj Bou Arréridj": {"population": 628_000, "market_index": 0.80},
        "Médéa": {"population": 819_000, "market_index": 0.85},
    },
}

BUSINESS_TEMPLATES = {
    "quincaillerie": {
        "name_ar": "متجر مواد البناء والعتاد",
        "name_en": "Hardware & Building Materials Store",
        "category": "تجارة",
        "investment": (2_000_000, 8_000_000),
        "margin": (0.15, 0.35),
        "staff": (3, 8),
        "area_sqm": (80, 300),
        "products": "مواد البناء، السباكة، الكهرباء، الأدوات اليدوية، الدهانات، السيراميك",
    },
    "supermarche": {
        "name_ar": "سوبر ماركت",
        "name_en": "Supermarket",
        "category": "تجارة التجزئة",
        "investment": (3_000_000, 15_000_000),
        "margin": (0.12, 0.25),
        "staff": (5, 20),
        "area_sqm": (150, 500),
        "products": "مواد غذائية، مشروبات، منتجات ألبان، مواد تنظيف، خضر وفواكه",
    },
    "restaurant": {
        "name_ar": "مطعم",
        "name_en": "Restaurant",
        "category": "خدمات الإطعام",
        "investment": (1_500_000, 6_000_000),
        "margin": (0.20, 0.40),
        "staff": (4, 15),
        "area_sqm": (60, 200),
        "products": "وجبات مطبوخة، مشروبات، حلويات ومشاوي",
    },
    "atelier_ferro": {
        "name_ar": "ورشة حدادة ولحام",
        "name_en": "Welding & Fabrication Workshop",
        "category": "صناعة حرفية",
        "investment": (1_000_000, 4_000_000),
        "margin": (0.25, 0.45),
        "staff": (2, 6),
        "area_sqm": (50, 150),
        "products": "أبواب وشبابيك، درابزين، هياكل معدنية وأعمال لحام",
    },
    "pharmacie": {
        "name_ar": "صيدلية",
        "name_en": "Pharmacy",
        "category": "الصحة",
        "investment": (3_000_000, 10_000_000),
        "margin": (0.25, 0.35),
        "staff": (2, 5),
        "area_sqm": (40, 100),
        "products": "أدوية، مستلزمات طبية، مستحضرات تجميل ومكملات غذائية",
    },
    "cafe_patisserie": {
        "name_ar": "مقهى وحلويات",
        "name_en": "Café & Pastry Shop",
        "category": "خدمات الإطعام",
        "investment": (1_000_000, 4_000_000),
        "margin": (0.30, 0.55),
        "staff": (3, 8),
        "area_sqm": (40, 120),
        "products": "قهوة ومشروبات، عصائر، حلويات تقليدية وكعكات",
    },
    "boulangerie": {
        "name_ar": "مخبزة",
        "name_en": "Bakery",
        "category": "خدمات الإطعام",
        "investment": (800_000, 3_000_000),
        "margin": (0.20, 0.40),
        "staff": (2, 5),
        "area_sqm": (30, 80),
        "products": "خبز عادي، خبز تقليدي، ملوي، كعكات، معجنات، حلويات جافة",
    },
    "epicerie": {
        "name_ar": "بقالة / دكّانة",
        "name_en": "Grocery / Corner Shop",
        "category": "تجارة التجزئة",
        "investment": (500_000, 2_500_000),
        "margin": (0.10, 0.25),
        "staff": (1, 3),
        "area_sqm": (20, 80),
        "products": "مواد غذائية أساسية، مشروبات، سجائر، منتجات ألبان، خضر وفواكه، مواد تنظيف",
    },
    "garage": {
        "name_ar": "ورشة إصلاح السيارات",
        "name_en": "Auto Repair Garage",
        "category": "خدمات",
        "investment": (2_000_000, 8_000_000),
        "margin": (0.25, 0.50),
        "staff": (2, 6),
        "area_sqm": (80, 250),
        "products": "إصلاح المحركات، تغيير الزيوت، إصلاح الإطارات، الفحص الفني، قطع الغيار",
    },
    "salon_coiffure": {
        "name_ar": "صالون حلاقة وتصفيف الشعر",
        "name_en": "Hair Salon & Barber Shop",
        "category": "خدمات",
        "investment": (500_000, 2_500_000),
        "margin": (0.35, 0.65),
        "staff": (2, 5),
        "area_sqm": (20, 60),
        "products": "حلاقة رجالية، تصفيف نسائي، صبغ الشعر، علاجات الشعر، مانيكير وباديكير",
    },
    "cybercafe": {
        "name_ar": "محل إنترنت",
        "name_en": "Cybercafé / Internet Café",
        "category": "خدمات رقمية",
        "investment": (1_000_000, 4_000_000),
        "margin": (0.20, 0.40),
        "staff": (1, 3),
        "area_sqm": (30, 80),
        "products": "استخدام الحواسيب، طباعة المستندات، المسح الضوئي، تصحيح السيرة الذاتية، التسجيل عبر الإنترنت",
    },
    "plombier": {
        "name_ar": "سبّاك / كهربائي منزلي",
        "name_en": "Plumber / Electrician (Mobile Service)",
        "category": "خدمات منزلية",
        "investment": (300_000, 1_500_000),
        "margin": (0.30, 0.55),
        "staff": (1, 3),
        "area_sqm": (0, 0),
        "products": "إصلاح التوصيلات المائية، إصلاح الكهرباء، تركيب الأدوات الصحية، صيانة المنزية",
    },
    "centre_services_num": {
        "name_ar": "مركز الخدمات الرقمية",
        "name_en": "Digital Services Center",
        "category": "خدمات رقمية",
        "investment": (200_000, 500_000),
        "margin": (0.40, 0.70),
        "staff": (1, 3),
        "area_sqm": (15, 40),
        "products": "التصريحات الضريبية، التأشيرات، طباعة المستندات، السيرة الذاتية، التسجيلات الإلكترونية، الفواتير",
    },
}

PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": ("GROQ_API_KEY",),
        "model": "llama-3.3-70b-versatile",
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": ("OPENROUTER_API_KEY",),
        "model": "google/gemma-4-26b-a4b-it:free",
    },
    "aihubmix": {
        "url": "https://aihubmix.com/v1/chat/completions",
        "key_env": ("AIHUBMIX_API_KEY", "OPENAI_API_KEY"),
        "model": "gpt-4.1-free",
    },
}

SYSTEM_PROMPT = """أنت مستشار أعمال جزائري تعد دراسة جدوى أولية احترافية.
اكتب بالعربية الفصحى فقط وبأسلوب واضح مناسب لتقديمه لصاحب مشروع أو بنك.
استخدم Markdown منظمًا، والجداول عند الحاجة. كل الأرقام تقديرية ويجب وصفها بأنها
تقديرات أولية قابلة للتحقق، ولا تخترع إحصاءات أو مصادر أو جهات حكومية مؤكدة.
راعِ واقع السوق الجزائري، واستخدم الدينار الجزائري. لا تكتب مقدمة عامة ولا عنوانًا
مكررًا للقسم؛ أجب بمحتوى القسم المطلوب فقط."""


class FeasibilityGenerator:
    """Generate an Arabic feasibility study through a selected LLM provider."""

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int = 90,
        retries: int = 3,
    ) -> None:
        self.provider = self._resolve_provider(provider, api_key)
        config = PROVIDERS[self.provider]
        self.api_key = api_key or self._read_api_key(config["key_env"])
        if not self.api_key:
            variables = " or ".join(config["key_env"])
            raise FeasibilityError(f"No API key found for {self.provider}. Set {variables} or use --api-key.")

        self.model = model or os.getenv(f"FEASIBILITY_{self.provider.upper()}_MODEL") or config["model"]
        self.url = os.getenv(f"FEASIBILITY_{self.provider.upper()}_URL", config["url"])
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()

    @staticmethod
    def _read_api_key(names: tuple[str, ...]) -> str | None:
        return next((os.getenv(name) for name in names if os.getenv(name)), None)

    def _resolve_provider(self, requested: str | None, api_key: str | None) -> str:
        if requested:
            if requested not in PROVIDERS:
                raise FeasibilityError(f"Unsupported provider: {requested}.")
            return requested
        if api_key:
            raise FeasibilityError("Specify --provider when using --api-key.")
        for name, config in PROVIDERS.items():
            if self._read_api_key(config["key_env"]):
                return name
        raise FeasibilityError("No API key found. Set GROQ_API_KEY, OPENROUTER_API_KEY, or AIHUBMIX_API_KEY.")

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Academix-DSS-Feasibility-Generator/1.0",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = os.getenv("OPENROUTER_SITE_URL", "https://kamelmahi.netlify.app")
            headers["X-OpenRouter-Title"] = "Academix DSS Feasibility Generator"
        return headers

    @staticmethod
    def _error_detail(response: requests.Response) -> str:
        try:
            payload = response.json()
            detail = payload.get("error", payload)
            if isinstance(detail, dict):
                detail = detail.get("message", detail)
            return str(detail)[:600]
        except ValueError:
            return response.text.strip()[:600] or "No response body."

    def _call_llm(self, prompt: str, temperature: float) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 4_000,
        }
        retryable_statuses = {408, 409, 429, 500, 502, 503, 504}
        last_error: Exception | None = None

        for attempt in range(self.retries + 1):
            try:
                response = self.session.post(
                    self.url,
                    headers=self._headers(),
                    json=payload,
                    timeout=(10, self.timeout),
                )
                if response.status_code in retryable_statuses:
                    raise requests.HTTPError(
                        f"HTTP {response.status_code}: {self._error_detail(response)}", response=response
                    )
                if not response.ok:
                    raise FeasibilityError(
                        f"{self.provider} rejected the request (HTTP {response.status_code}): "
                        f"{self._error_detail(response)}"
                    )
                return self._extract_content(response.json())
            except FeasibilityError:
                raise
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError, ValueError) as error:
                last_error = error
                if attempt == self.retries:
                    break
                delay = min(2**attempt, 8)
                if isinstance(error, requests.HTTPError) and error.response is not None:
                    retry_after = error.response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        delay = min(int(retry_after), 30)
                print(f"  Provider request failed ({error}); retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)

        raise FeasibilityError(
            f"{self.provider} could not generate this section after {self.retries + 1} attempts: {last_error}"
        )

    @staticmethod
    def _extract_content(payload: dict[str, Any]) -> str:
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise FeasibilityError("Provider returned an unexpected response format.") from error
        if not isinstance(content, str) or not content.strip():
            raise FeasibilityError("Provider returned an empty response.")
        return content.strip().removeprefix("```markdown").removeprefix("```").removesuffix("```").strip()

    def check_connection(self) -> None:
        """Send a minimal request to confirm credentials, endpoint, and model."""
        self._call_llm("أجب بكلمة واحدة فقط: تم", temperature=0.1)

    def generate_full_study(self, business_type: str, location: str, wilaya: str, investment: int | None = None) -> dict[str, Any]:
        business = BUSINESS_TEMPLATES.get(business_type)
        if business is None:
            choices = ", ".join(BUSINESS_TEMPLATES)
            raise FeasibilityError(f"نوع النشاط غير معروف: {business_type}. الأنواع المتاحة: {choices}")
        if not location.strip() or not wilaya.strip():
            raise FeasibilityError("يجب إدخال اسم المدينة والولاية.")
        if investment is None:
            minimum, maximum = business["investment"]
            investment = (minimum + maximum) // 2
        if investment <= 0:
            raise FeasibilityError("يجب أن يكون مبلغ الاستثمار رقمًا موجبًا.")

        prompts = self._build_prompts(business, location.strip(), wilaya.strip(), investment)
        sections: dict[str, str] = {}
        for index, (name, prompt, temperature) in enumerate(prompts, start=1):
            print(f"  [{index}/{len(prompts)}] إنشاء {name}...", file=sys.stderr)
            sections[name] = self._call_llm(prompt, temperature)
        return self._assemble_study(business, location.strip(), wilaya.strip(), investment, sections)

    @staticmethod
    def _build_prompts(business: dict[str, Any], location: str, wilaya: str, investment: int) -> list[tuple[str, str, float]]:
        wilaya_data = ALGERIA_DATA["wilayas"].get(wilaya, {"population": None, "market_index": None})
        population_note = f"تعداد سكان الولاية المرجعي: {wilaya_data['population']:,}." if wilaya_data["population"] else "لا تتوفر بيانات سكانية محلية مؤكدة؛ اذكر الحاجة إلى التحقق الميداني."
        context = (
            f"النشاط: {business['name_ar']} ({business['name_en']}).\n"
            f"الموقع: {location}، ولاية {wilaya}.\n"
            f"التصنيف: {business['category']}.\n"
            f"الاستثمار التقديري: {investment:,} دج.\n"
            f"المنتجات/الخدمات: {business['products']}.\n"
            f"عدد العمال المتوقع: {business['staff'][0]}–{business['staff'][1]}.\n"
            f"المساحة المقترحة: {business['area_sqm'][0]}–{business['area_sqm'][1]} م².\n"
        )
        return [
            ("وصف المشروع", context + """
اكتب القسم الأول: وصف المشروع، مبرراته، العملاء المستهدفون، والموقع. اعرض ثلاثة مبررات عملية على الأقل، مع تنبيه صريح إلى أن التراخيص والطلب المحلي يجب التحقق منهما ميدانيًا. استخدم عناوين فرعية من المستوى الثالث فقط.""", 0.5),
            ("دراسة السوق", context + f"\n{population_note}\n" + """
اكتب القسم الثاني: السوق والطلب والمنافسة وخطة التسويق وتوقع المبيعات لخمس سنوات. قدّم جدول توقعات محافظًا. لا تنسب أرقامًا إلى الجمارك أو جهات رسمية ما لم تكن موفرة في المعطيات؛ سمّها افتراضات تقديرية.""", 0.45),
            ("الدراسة الفنية", context + """
اكتب القسم الثالث: اختيار الموقع، المساحة، سير العمل، المعدات، الموارد البشرية، المخزون/المواد الأولية والخدمات، وبرنامج تنفيذ من 3 إلى 6 أشهر. أدرج جداول للمعدات والعمالة، وبيّن أن عروض الأسعار الفعلية يجب جمعها محليًا.""", 0.45),
            ("الدراسة المالية", context + f"""
اكتب القسم الرابع: التكاليف التشغيلية، رأس المال العامل، مصاريف التأسيس، الاستثمار، التمويل، الافتراضات، ومؤشرات أولية للجدوى. استخدم: TVA 19%، ضريبة الشركات 19%، CNAS صاحب العمل 26%، فائدة قروض 9%، ومعدل خصم 12% كافتراضات قابلة للتحقق. لا تدّعِ دقة محاسبية نهائية.""", 0.4),
            ("الجداول المالية", context + """
أنشئ الجداول المالية فقط: قائمة أرباح وخسائر لخمس سنوات، تدفقات نقدية لخمس سنوات، وتحليل حساسية لارتفاع التكاليف 10% و20% وانخفاض المبيعات 5% و10%. استخدم أرقامًا محافظة ومتسقة، وضع جميع القيم بالدينار الجزائري.""", 0.35),
        ]

    @staticmethod
    def _assemble_study(business: dict[str, Any], location: str, wilaya: str, investment: int, sections: dict[str, str]) -> dict[str, Any]:
        now = datetime.now()
        content = f"""---
title: "دراسة جدوى أولية — {business['name_ar']}"
date: {now:%Y-%m-%d}
language: ar
currency: DZD
---

# دراسة جدوى أولية

## {business['name_ar']}

| البند | التفاصيل |
|---|---|
| موقع المشروع | {location}، ولاية {wilaya} |
| التصنيف | {business['category']} |
| الاستثمار التقديري | {investment:,} دج |
| تاريخ الإعداد | {now:%d/%m/%Y} |
| جهة الإعداد | Academix DSS — مركز الخدمات الرقمية |

> **تنبيه مهني:** هذه دراسة أولية لاتخاذ القرار. يجب التحقق من الأسعار والتراخيص والضرائب والطلب الفعلي ميدانيًا، ومراجعة محاسب أو مستشار مختص قبل التمويل أو التنفيذ.

## المحتويات

1. وصف المشروع
2. دراسة السوق
3. الدراسة الفنية
4. الدراسة المالية
5. الجداول المالية والتحليل الحساس

---

## 1. وصف المشروع

{sections['وصف المشروع']}

---

## 2. دراسة السوق

{sections['دراسة السوق']}

---

## 3. الدراسة الفنية

{sections['الدراسة الفنية']}

---

## 4. الدراسة المالية

{sections['الدراسة المالية']}

---

## 5. الجداول المالية وتحليل الحساسية

{sections['الجداول المالية']}

---

## ملاحظات ختامية

- يجب استبدال كل التقديرات بعروض أسعار محلية قبل اعتماد المشروع.
- تتطلب بعض الأنشطة، ومنها الصيدليات، شروطًا مهنية وتنظيمية خاصة يجب التحقق منها لدى الجهات المختصة.
- تم إعداد هذه الوثيقة باللغة العربية وللاستخدام المهني داخل الجزائر.

**إعداد:** Academix DSS — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** {now:%d/%m/%Y}
"""
        return {
            "title": f"دراسة جدوى أولية — {business['name_ar']}",
            "business_type": business["name_ar"],
            "location": f"{location}، {wilaya}",
            "investment": investment,
            "date": now.isoformat(timespec="seconds"),
            "content": content,
            "sections": sections,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="إنشاء دراسة جدوى أولية للمشاريع الجزائرية.")
    parser.add_argument("--business", "-b", choices=sorted(BUSINESS_TEMPLATES))
    parser.add_argument("--location", "-l", help="المدينة أو المنطقة")
    parser.add_argument("--wilaya", "-w", help="اسم الولاية")
    parser.add_argument("--investment", "-i", type=int, help="الاستثمار الإجمالي بالدينار الجزائري")
    parser.add_argument("--output", "-o", type=Path, help="مسار ملف Markdown الناتج")
    parser.add_argument("--provider", "-p", choices=sorted(PROVIDERS), help="مزود LLM")
    parser.add_argument("--api-key", help="مفتاح API؛ يفضّل استخدام متغيرات البيئة")
    parser.add_argument("--model", help="اسم النموذج؛ يتجاوز النموذج الافتراضي للمزود")
    parser.add_argument("--timeout", type=int, default=90, help="مهلة الاستجابة بالثواني")
    parser.add_argument("--retries", type=int, default=3, help="عدد محاولات إعادة الاتصال")
    parser.add_argument("--check-provider", action="store_true", help="اختبر الاتصال فقط، دون إنشاء دراسة")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.timeout <= 0 or args.retries < 0:
        print("خطأ: يجب أن تكون المهلة موجبة وعدد المحاولات صفرًا أو أكثر.", file=sys.stderr)
        return 2
    if not args.check_provider and not all((args.business, args.location, args.wilaya)):
        print("خطأ: --business و--location و--wilaya مطلوبة لإنشاء دراسة.", file=sys.stderr)
        return 2
    try:
        generator = FeasibilityGenerator(args.provider, args.api_key, args.model, args.timeout, args.retries)
        print(f"المزود: {generator.provider} | النموذج: {generator.model}", file=sys.stderr)
        if args.check_provider:
            generator.check_connection()
            print("تم التحقق من اتصال المزود بنجاح.")
            return 0
        study = generator.generate_full_study(args.business, args.location, args.wilaya, args.investment)
        output = args.output or Path(f"دراسة_جدوى_{args.business}_{args.location.strip().replace(' ', '_')}.md")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(study["content"], encoding="utf-8")
    except FeasibilityError as error:
        print(f"فشل إنشاء الدراسة: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"تعذر حفظ الملف: {error}", file=sys.stderr)
        return 1

    print(f"تم إنشاء الدراسة: {output.resolve()}")
    print(f"النشاط: {study['business_type']}")
    print(f"الموقع: {study['location']}")
    print(f"الاستثمار التقديري: {study['investment']:,} دج")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
