"""Generate tax declaration guides for Algerian businesses and individuals.

Covers G12, G50, CNAS, CASNOS, IRG, and TVA declarations.
Uses the same LLM provider pattern as feasibility_generator.py.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from typing import Any
try:
    from prompts import PROMPT_VERSION
    from prompts import PROMPT_VERSION as _PROMPT_VERSION
    _PROMPT_VERSION = PROMPT_VERSION  # keep linter happy
except ImportError:
    PROMPT_VERSION = "unknown"

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

TAX_SYSTEM_PROMPT = """أنت محاسب ضريبي جزائري متخصص في الإقرارات الضريبية والاشتراكات الاجتماعية.
اكتب بالعربية الفصحى فقط. استخدم جداول Markdown منظمة.
معلومات ضريبية أساسية للجزائر — محدثة 2026 (مطابقة لـ verify_rates.py:38 و ALGERIA_DATA):
- TVA: 19% (معيار), 9% (مخفض لبعض المواد الغذائية), 0% (صادرات)
- IRG (ضريبة الدخل الإجمالي) — 6 شرائح تصاعدية 0–35% (240K/480K/960K/1.92M/3.84M):
  0% ≤240,000؛ 23% 240,001–480,000؛ 27% 480,001–960,000؛ 30% 960,001–1,920,000؛ 33% 1,920,001–3,840,000؛ 35% >3,840,000
- IBS (ضريبة أرباح الشركات — المادة 150 CIDTA): 19% إنتاج, 23% BTPH, 26% تجارة/خدمات
- IFU (نظام جزافي): 5% إنتاج/بيع سلع, 12% خدمات (سقف 8M DZD رقم أعمال)
- CNAS: صاحب عمل 25.5% (26% مع الأعمال الاجتماعية) + حصة عامل 9% — SNMG 24,000 دج/شهر (DP 26-01)
- CASNOS: ~43,200 دج/سنة حد أدنى (15% من SNMG×12)
- ANSEJ/ANSE (NESDA): 0% فائدة مدعمة 100% / 7 سنوات (1.5 إمهال) — سقف 10M, 5% شخصي + 25% PNR + 70% بنك

لا تدّعِ أن هذه معلومات رسمية مؤكدة؛ وصفها بأنها تقديرات أولية قابلة للتحقق مع مصلحة الضرائب."""


DECLARATION_TYPES = {
    "g12": {
        "name_ar": "التصريح الشهري G12 (TVA)",
        "name_en": "Monthly G12 TVA Declaration",
        "prompt": """أنشئ دليلًا خطوة بخطوة للتصريح الشهري G12 (TVA):
1. المطلوب: ما هو G12 ومتى يُقدَّم (الشهرية، قبل 20 من الشهر التالي)
2. المستندات المطلوبة: فواتير المبيعات، فواتير الشراء، سجل القيود
3. طريقة الحساب:
   - TVA المحصلة (المبيعات × 19%)
   - TVA الخاضعة للخصم (الشراء × 19%)
   - الصافي = TVA المحصلة - TVA الخاضعة للخصم
4. المثال العملي: مشروع ببيع 500,000 دج وشراء 300,000 دج شهريًا
5. طريقة التقديم: الموقع الإلكتروني (DGIP) أو الوكالة الضرائب
6. الغرامات: تأخر التقديم = غرامة 5% + 0.2% لكل يوم تأخر
7. النصائح: احتفظ بسجل يومي للمبيعات، لا تخلط TVA الشخصية""",
        "temperature": 0.3,
    },
    "g50": {
        "name_ar": "التصريح السنوي G50 (الدخل)",
        "name_en": "Annual G50 Income Declaration",
        "prompt": """أنشئ دليلًا خطوة بخطوة للتصريح السنوي G50 (الدخل):
1. المطلوب: ما هو G50 ومتى يُقدَّم (قبل 30 أبريل كل سنة)
2. المستندات المطلوبة: كشف ربح وخسائر، كشوفات البنوك، فواتير، إيصالات
3. الدخل الخاضع للضريبة:
   - صافي الربح = الإيرادات - التكاليف المعترف بها
   - الخصومات المسموح بها: الإيجار، الرواتب، الوفقات، الإهلاك، الفوائد
4. حساب IRG:
   - الدخل السنوي × معدل IRG حسب البريم
5. المثال: تاجر بربح سنوي 2,400,000 دج
6. طريقة التقديم: DGIP أو الوكالة الضرائب
7. الغرامات: عدم التقديم = غرامة 5% من الضريبة المستحقة + 0.2%/يوم
8. النصائح: قدّم قبل الموعد بـ 10 أيام على الأقل""",
        "temperature": 0.3,
    },
    "cnas": {
        "name_ar": "تصريح CNAS الشهري",
        "name_en": "Monthly CNAS Declaration",
        "prompt": """أنشئ دليلًا خطوة بخطوة لتصريح CNAS الشهري:
1. المطلوب: ما هو CNAS ومتى يُقدَّم (شهري، قبل 30 من الشهر التالي)
2. المستندات المطلوبة: كشوفات الأجور، عقود العمل، شهادة التأمين
3. حساب Contributions:
   - صاحب العمل: 26% من الأجر الإجمالي (12.35% + 0.75% + 0.5% + 10.5% + 2%)
   - الموظف: 9% من الأجر الصافي
4. الحد الأدنى للأساس: SMIG = 20,000 دج
5. المثال: 5 موظفين برواتب 25,000 دج إجماليًا
6. طريقة الدفع: CCP أو Baridimob أو الوكالة الضرائب
7. الغرامات: تأخر الدفع = غرامة 5%
8. النصائح: سجّل الدفعات مسبقًا، احتفظ بإيصالات الدفع""",
        "temperature": 0.3,
    },
    "casnos": {
        "name_ar": "تصريح CASNOS السنوي",
        "name_en": "Annual CASNOS Declaration",
        "prompt": """أنشئ دليلًا لتصريح CASNOS:
1. المطلوب: ما هو CASNOS ومتى يُقدَّم (سنوي، قبل 30 يونيو)
2. من يُقدِّمه: التجار والحرفيون والمستقلون (auto-entrepreneur)
3. المبلغ: 24,000 دج/سنة (2,000 دج/شهر)
4. المستندات المطلوبة: بطاقة التاجر، شهادة ANAE، إثبات النشاط
5. طريقة الدفع: CCP أو Baridimob
6.enefits: تغطية معاش تقاعد + رعاية صحية
7. الغرامات: عدم السداد = تعليق النشاط التجاري
8. النصائح: سجّل الدفعات الشهرية تلقائيًا""",
        "temperature": 0.3,
    },
    "ifu": {
        "name_ar": "التصريح الشهري IFU",
        "name_en": "Monthly IFU Declaration",
        "prompt": """أنشئ دليلًا للتصريح الشهري IFU (Installateur Forfaitaire Unique):
1. المطلوب: ما هو IFU ومتى يُقدَّم (شهري، قبل 20 من الشهر التالي)
2. من يُقدِّمه: التجار بالجملة والتجزئة والحرفيون
3. الطريقة: 0.5% من الإيرادات الشهرية (بدون خصم التكاليف)
4. المثال: تاجر بإيراد 500,000 دج شهريًا → IFU = 2,500 دج
5. طريقة الدفع: CCP أو الوكالة الضرائب
6. الغرامات: تأخر الدفع = غرامة 5%
7. النصائح: حدد الإيرادات بدقة، لا تنسَ الخصومات""",
        "temperature": 0.3,
    },
    "irg_salaire": {
        "name_ar": "حساب IRG على الرواتب",
        "name_en": "IRG Payroll Tax Calculator",
        "prompt": """أنشئ جدول حساب IRG على الرواتب — محدث 2026 (6 شرائح):
1. بريم IRG 2026:
   - 0% حتى 240,000 دج/سنة
   - 23% من 240,001 إلى 480,000
   - 27% من 480,001 إلى 960,000
   - 30% من 960,001 إلى 1,920,000
   - 33% من 1,920,001 إلى 3,840,000
   - 35% فوق 3,840,000
2. طريقة الحساب التصاعدي (progressif)
3. جدول جاهز لكل mức راتب شهري:
   - 20,000 دج → IRG = ?
   - 25,000 دج → IRG = ?
   - 30,000 دج → IRG = ?
   - 35,000 دج → IRG = ?
   - 40,000 دج → IRG = ?
   - 50,000 دج → IRG = ?
4. الصافي بعد IRG لكل مبلغ
5. كيفية حساب IRG في Excel أو الآلة الحاسبة""",
        "temperature": 0.2,
    },
}


class TaxDeclarationGenerator:
    """Generate Arabic tax declaration guides through a selected LLM provider."""

    def __init__(self, provider: str | None = None, api_key: str | None = None, model: str | None = None, allow_offline: bool = True) -> None:
        self.offline = False
        self.prompt_version = PROMPT_VERSION
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
        self.prompt_version = PROMPT_VERSION

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
            "User-Agent": "DSC-TaxDeclaration/1.0",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://kamelmh.github.io/digital-services-center/"
            headers["X-OpenRouter-Title"] = "DSC Tax Declaration Generator"
        return headers

    def _call_llm(self, prompt: str, temperature: float = 0.3) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": TAX_SYSTEM_PROMPT},
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

    def list_declaration_types(self) -> list[dict[str, str]]:
        return [
            {"key": k, "name_ar": v["name_ar"], "name_en": v["name_en"]}
            for k, v in DECLARATION_TYPES.items()
        ]

    def generate(self, declaration_type: str, business_name: str = "") -> dict[str, Any]:
        """Generate a tax declaration guide."""
        if getattr(self, "offline", False) or not getattr(self, "api_key", None):
            from offline_templates import tax_declaration_offline
            result = tax_declaration_offline(declaration_type, business_name)
            try:
                from quality_scorer import QualityScorer as _QS0
                _qr0 = _QS0().score("tax_declaration", result["content"])
                _qm0 = {"quality_grade": _qr0.grade, "quality_score": round(_qr0.overall_score, 3), "quality_passed": _qr0.passed}
            except Exception:
                _qm0 = {}
            try:
                from training_hook import hook_generation
                hook_generation(generator="tax_declaration", input_params={"declaration_type": declaration_type, "mode": "offline"}, output_content=result["content"], metadata={"offline": True, "prompt_version": getattr(self, "prompt_version", "unknown"), **_qm0})
            except Exception:
                pass
            return result
        config = DECLARATION_TYPES.get(declaration_type)
        if not config:
            raise FeasibilityError(f"Unknown declaration type: {declaration_type}")

        context = f"اسم المشروع أو الشخص: {business_name or 'غير محدد'}\n"
        print(f"  Generating {config['name_en']}...", file=sys.stderr)
        content = self._call_llm(context + config["prompt"], config["temperature"])

        now = datetime.now()
        header = f"""---
title: "دليل {config['name_ar']}"
type: {declaration_type}
date: {now:%Y-%m-%d}
language: ar
---

# {config['name_ar']}

| البند | التفاصيل |
|---|---|
| نوع التصريح | {config['name_ar']} |
| تاريخ الإعداد | {now:%d/%m/%Y} |

> **تنبيه:** هذه معلومات تقديرية أولية. راجع الوكالة الضرائب أو محاسبًا مختصًا للتأكد من الدقة.

---

"""

        full_content = header + content
        full_content += f"""

---

**إعداد:** Digital Services Center — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** {now:%d/%m/%Y}"""

        # Quality gate
        try:
            from quality_scorer import QualityScorer as _QS
            _qr = _QS().score("tax_declaration", full_content)
            _qmeta = {"quality_grade": _qr.grade, "quality_score": round(_qr.overall_score, 3), "quality_passed": _qr.passed}
        except Exception:
            _qmeta = {}
        try:
            from training_hook import hook_generation
            hook_generation(
                generator="tax_declaration",
                input_params={"declaration_type": declaration_type, "business_name": business_name},
                output_content=full_content,
                metadata={"prompt_version": getattr(self, "prompt_version", "unknown"), **_qmeta},
            )
        except Exception:
            pass

        return {
            "title": f"دليل {config['name_ar']}",
            "declaration_type": config["name_ar"],
            "date": now.isoformat(timespec="seconds"),
            "content": full_content,
        }
