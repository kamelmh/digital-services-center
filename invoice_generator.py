"""Generate professional invoices and quotes (devis) for Algerian businesses.

Uses the same LLM provider pattern as feasibility_generator.py.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta
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

INVOICE_SYSTEM_PROMPT = """أنت محاسب جزائري متخصص في إعداد الفواتير وعروض الأسعار (Devis).
اكتب بالعربية الفصحى فقط. استخدم جداول Markdown منظمة.
قواعد الفاتورة الجزائرية:
- رقم الفاتورة: AT-YYYYMMDD-XXXX (AT = Activité Taxable)
- TVA: 19% على كل بند
- TVA الإجمالية = مجموع (الكمية × السعر × 19%)
- الإجمالي قبل TVA = مجموع (الكمية × السعر)
- الإجمالي شامل TVA = الإجمالي قبل TVA + TVA
- العملة: دج (DINAR ALGERIEN)
- الشروط: الدفع خلال 30 يومًا (أو حسب الاتفاق)
- الخصم: يمكن إضافة خصم % مع ذكر السبب
لا تستخدم أي روابط خارجية. اكتب محتوى جاهز للطباعة."""


class InvoiceGenerator:
    """Generate Arabic invoices and quotes through a selected LLM provider."""

    def __init__(self, provider: str | None = None, api_key: str | None = None, model: str | None = None, allow_offline: bool = True) -> None:
        self.offline = False
        try:
            self.provider = self._resolve_provider(provider, api_key)
            config = PROVIDERS[self.provider]
            self.api_key = api_key or next(
                (os.getenv(k) for k in config["key_env"] if os.getenv(k)), None
            )
            if not self.api_key:
                if allow_offline:
                    self.offline = True
                    self.provider = "offline"
                    self.api_key = None
                    self.model = "offline-templates"
                    self.url = ""
                    self.session = requests.Session()
                    return
                variables = " or ".join(config["key_env"])
                raise FeasibilityError(f"No API key found for {self.provider}. Set {variables}.")
            self.model = model or config["model"]
            self.url = config["url"]
            self.session = requests.Session()
        except FeasibilityError:
            if allow_offline:
                self.offline = True
                self.provider = "offline"
                self.api_key = None
                self.model = "offline-templates"
                self.url = ""
                self.session = requests.Session()
                return
            raise

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
            "User-Agent": "DSC-InvoiceGenerator/1.0",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://kamelmh.github.io/digital-services-center/"
            headers["X-OpenRouter-Title"] = "DSC Invoice Generator"
        return headers

    def _call_llm(self, prompt: str, temperature: float = 0.2) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": INVOICE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 3000,
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

    def generate_invoice(
        self,
        business_name: str,
        client_name: str,
        items: list[dict[str, Any]],
        discount_percent: float = 0,
        notes: str = "",
        payment_terms: str = "30 jours",
    ) -> dict[str, Any]:
        """Generate a professional invoice."""
        now = datetime.now()
        invoice_number = f"AT-{now:%Y%m%d}-0001"
        due_date = now + timedelta(days=30)

        # Calculate totals
        subtotal = sum(item.get("qty", 1) * item.get("price", 0) for item in items)
        discount_amount = subtotal * (discount_percent / 100)
        taxable_amount = subtotal - discount_amount
        tva_amount = taxable_amount * 0.19
        total = taxable_amount + tva_amount

        items_text = ""
        for i, item in enumerate(items, 1):
            qty = item.get("qty", 1)
            price = item.get("price", 0)
            desc = item.get("description", "")
            line_total = qty * price
            line_tva = line_total * 0.19
            items_text += f"| {i} | {desc} | {qty} | {price:,} | {line_total:,} | {line_tva:,} | {line_total + line_tva:,} |\n"

        prompt = f"""أنشئ فاتورة رسمية بالبيانات التالية:

**معلومات المورد:**
- الاسم: {business_name}
- التاريخ: {now:%d/%m/%Y}
- رقم الفاتورة: {invoice_number}

**معلومات العميل:**
- الاسم: {client_name}

**بنود الفاتورة:**
| # | الوصف | الكمية | السعر | المجموع قبل TVA | TVA (19%) | المجموع شامل |
|---|-------|--------|-------|-----------------|-----------|--------------|
{items_text}

**الحسابات:**
- المجموع قبل TVA: {subtotal:,} دج
- الخصم ({discount_percent}%): {discount_amount:,.0f} دج
- المبلغ الخاضع: {taxable_amount:,.0f} دج
- TVA (19%): {tva_amount:,.0f} دج
- الإجمالي: {total:,.0f} دج

**شروط الدفع:** {payment_terms}
**تاريخ الاستحقاق:** {due_date:%d/%m/%Y}
**ملاحظات:** {notes or 'لا توجد'}

اكتب الفاتورة بتنسيق احترافي جاهز للطباعة، مع شعار واسم المشروع في الأعلى.
أضف خانة التوقيع في الأسفل."""

        if getattr(self, "offline", False):
            # Offline deterministic rendering — same numbers, no LLM
            content = f"""# فاتورة — {invoice_number}

**المورد:** {business_name}
**العميل:** {client_name}
**التاريخ:** {now:%d/%m/%Y} — **الاستحقاق:** {due_date:%d/%m/%Y}
**شروط الدفع:** {payment_terms}

| # | الوصف | الكمية | السعر | المجموع قبل TVA | TVA (19%) | المجموع شامل |
|---|-------|--------|-------|-----------------|-----------|--------------|
{items_text}
|   | **المجموع** |  |  | **{subtotal:,}** | **{tva_amount:,.0f}** | **{total:,.0f}** |

- المجموع قبل TVA: {subtotal:,} دج
- الخصم ({discount_percent}%): {discount_amount:,.0f} دج
- TVA (19%): {tva_amount:,.0f} دج
- **الإجمالي: {total:,.0f} دج**

> **وضع عدم الاتصال:** فاتورة مولّدة محليًا بدون LLM — صالحة للطباعة بعد المراجعة.
"""
        else:
            print("  Generating invoice...", file=sys.stderr)
            content = self._call_llm(prompt, 0.2)

        full_content = f"""---
title: "فاتورة — {invoice_number}"
date: {now:%Y-%m-%d}
invoice_number: {invoice_number}
client: {client_name}
total: {total:,.0f}
currency: DZD
---

# فاتورة — {invoice_number}

{content}

---

**إعداد:** Digital Services Center — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** {now:%d/%m/%Y}"""

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="invoice",
                input_params={"invoice_number": invoice_number, "client_name": client_name, "items": items},
                output_content=full_content,
            )
        except Exception:
            pass

        return {
            "invoice_number": invoice_number,
            "client": client_name,
            "subtotal": subtotal,
            "tva": tva_amount,
            "discount": discount_amount,
            "total": total,
            "due_date": due_date.strftime("%d/%m/%Y"),
            "date": now.isoformat(timespec="seconds"),
            "content": full_content,
        }

    def generate_quote(
        self,
        business_name: str,
        client_name: str,
        items: list[dict[str, Any]],
        validity_days: int = 30,
        notes: str = "",
    ) -> dict[str, Any]:
        """Generate a professional quote (devis)."""
        now = datetime.now()
        quote_number = f'DE-{now:%Y%m%d}-0001'
        valid_until = now + timedelta(days=validity_days)

        subtotal = sum(item.get("qty", 1) * item.get("price", 0) for item in items)
        tva_amount = subtotal * 0.19
        total = subtotal + tva_amount

        items_text = ""
        for i, item in enumerate(items, 1):
            qty = item.get("qty", 1)
            price = item.get("price", 0)
            desc = item.get("description", "")
            line_total = qty * price
            line_tva = line_total * 0.19
            items_text += f"| {i} | {desc} | {qty} | {price:,} | {line_total:,} | {line_tva:,} | {line_total + line_tva:,} |\n"

        prompt = f"""أنشئ عرض سعر (Devis) رسمي بالبيانات التالية:

**معلومات المورد:**
- الاسم: {business_name}
- التاريخ: {now:%d/%m/%Y}
- رقم العرض: {quote_number}

**معلومات العميل:**
- الاسم: {client_name}

**بنود العرض:**
| # | الوصف | الكمية | السعر | المجموع قبل TVA | TVA (19%) | المجموع شامل |
|---|-------|--------|-------|-----------------|-----------|--------------|
{items_text}

**الحسابات:**
- المجموع قبل TVA: {subtotal:,} دج
- TVA (19%): {tva_amount:,.0f} دج
- الإجمالي: {total:,.0f} دج

**مدة الصلاحية:** {validity_days} يوم (حتى {valid_until:%d/%m/%Y})
**ملاحظات:** {notes or 'لا توجد'}

اكتب العرض بتنسيق احترافي جاهز للطباعة. أضف شروط عامة في الأسفل."""

        if getattr(self, "offline", False):
            content = f"""# عرض سعر — {quote_number}

**المورد:** {business_name}
**العميل:** {client_name}
**التاريخ:** {now:%d/%m/%Y} — **الصلاحية:** {valid_until:%d/%m/%Y} ({validity_days} يوم)

| # | الوصف | الكمية | السعر | المجموع قبل TVA | TVA (19%) | المجموع شامل |
|---|-------|--------|-------|-----------------|-----------|--------------|
{items_text}
|   | **المجموع** |  |  | **{subtotal:,}** | **{tva_amount:,.0f}** | **{total:,.0f}** |

> **وضع عدم الاتصال:** عرض سعر مولّد محليًا بدون LLM — صالحة للطباعة بعد المراجعة.
"""
        else:
            print("  Generating quote...", file=sys.stderr)
            content = self._call_llm(prompt, 0.2)

        full_content = f"""---
title: "عرض سعر — {quote_number}"
date: {now:%Y-%m-%d}
quote_number: {quote_number}
client: {client_name}
total: {total:,.0f}
valid_until: {valid_until:%Y-%m-%d}
currency: DZD
---

# عرض سعر — {quote_number}

{content}

---

**إعداد:** Digital Services Center — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** {now:%d/%m/%Y}"""

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="quote",
                input_params={"quote_number": quote_number, "client_name": client_name, "items": items},
                output_content=full_content,
            )
        except Exception:
            pass

        return {
            "quote_number": quote_number,
            "client": client_name,
            "subtotal": subtotal,
            "tva": tva_amount,
            "total": total,
            "valid_until": valid_until.strftime("%d/%m/%Y"),
            "date": now.isoformat(timespec="seconds"),
            "content": full_content,
        }
