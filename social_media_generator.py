"""Generate social media content for Algerian businesses.

Produces ready-to-post content for Facebook, Instagram, WhatsApp, and TikTok.
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

SOCIAL_MEDIA_SYSTEM_PROMPT = """أنت مدير محتوى سوشيال ميديا جزائري متخصص في صناعة محتوى الشركات الصغيرة والمتوسطة.
اكتب بالعربية الفصحى والدارجة الجزائرية حسب المنصة. قواعد المحتوى:
- فيسبوك: منشورات طويلة نسبيًا، emoji، سؤال تفاعلي في النهاية، هاشتاقات
- إنستغرام: caption قصير + 10-15 هاشتاق، CTA واضح
- واتساب: رسالة مباشرة ومختصرة، CTA فوري (اتصل، أرسل رسالة)
- تيك توك: سكريبت فيديو قصير (15-30 ثانية)، hook في أول 3 ثوانٍ
لا تستخدم روابط خارجية. اكتب محتوى جاهز للنشر مباشرة.
كل المحتوى بالعملة الدينار الجزائري (دج)."""


# Content types and their generation parameters
CONTENT_TYPES = {
    "weekly_posts": {
        "name_ar": "7 منشورات أسبوعية",
        "name_en": "7 Weekly Posts (Facebook + Instagram)",
        "prompt": """أنشئ 7 منشورات سوشيال ميديا أسبوعية (واحد لكل يوم السبت إلى الجمعة):
لكل منشور:
- **النشرة:** (فيسبوك أو إنستغرام)
- **النص:** (3-6 سطور)
- **الهاشتاقات:** (5-10 للإنستغرام، 2-3 للفيسبوك)
- **وقت النشر المقترح:** (أفضل ساعة للنشر)
- **نوع المحتوى:** (تعليمي / ترفيهي / تجاري / تفاعلي / شهادة عميل)

مواضيع الأسبوع:
1. السبت: منشور تعليمي (نصيحة مجانية)
2. الأحد: منشور تفاعلي (سؤال / استطلاع)
3. الاثنين: منشور تجاري (عرض أو منتج)
4. الثلاثاء: منشور ترفيهي (ميم / صورة مرحة)
5. الأربعاء: شهادة عميل أو قصة نجاح
6. الخميس: منشور خلف الكواليس
7. الجمعة: منشور وجداني / ملهم""",
        "temperature": 0.5,
    },
    "product_showcase": {
        "name_ar": "عرض المنتجات (5 منشورات)",
        "name_en": "Product Showcase (5 Posts)",
        "prompt": """أنشئ 5 منشورات لعرض المنتجات/الخدمات:
لكل منشور:
- **المنتج/الخدمة:**
- **العنوان الجذاب:** (بالعربية أو الدارجة)
- **النص التسويقي:** (4-8 سطور)
- **السعر:** (إن وجد)
- **CTA:** (ما يجب أن يفعله العميل)
- **منصة النشر:** (فيسبوك / إنستغرام / واتساب)
- **الصورة المقترحة:** (وصف للتصميم)
- **الهاشتاقات:**

اجعل المحتوى يركز على الفائدة للعميل لا على وصف المنتج فقط.""",
        "temperature": 0.45,
    },
    "launch_campaign": {
        "name_ar": "حملة إطلاق (10 منشورات)",
        "name_en": "Launch Campaign (10 Posts)",
        "prompt": """أنشئ حملة إطلاق كاملة من 10 منشورات على 10 أيام:
الأيام 1-3: Teaser (تشويق — ما نقول اسم المشروع بعد)
الأيام 4-5: Announcement (إعلان رسمي — الاسم، الموقع، الخدمات)
الأيام 6-7: Offer (عرض خاص للعملاء الأوائل)
الأيام 8-9: Social Proof (شهادات أو behind-the-scenes)
اليوم 10: Last Chance (عرض الإطلاق ينتهي قريبًا)

لكل منشور:
- **اليوم:**
- **النوع:** (Teaser / Announcement / Offer / Social Proof / Last Chance)
- **النص:** (جاهز للنشر)
- **المنصة:** (فيسبوك + إنستغرام + واتساب)
- **الصورة المقترحة:**
- **الهاشتاقات:**

اجعل الحملة تتصاعد في الحماس من اليوم 1 إلى اليوم 10.""",
        "temperature": 0.5,
    },
    "ramadan_campaign": {
        "name_ar": "حملة رمضان (15 منشور)",
        "name_en": "Ramadan Campaign (15 Posts)",
        "prompt": """أنشئ حملة رمضان كاملة من 15 منشور (30 يوم / 2 منشور يوميًا):
- **النشرة الصباحية:** (قبل الإفطار — رسالة رمضانية + عرض خاص)
- **النشرة المسائية:** (بعد الإفطار — محتوى تفاعلي أو شهادة)

مواضيع رمضان:
1. تهنئة بداية رمضان
2. عروض رمضان الخاصة
3. محتوى رمضاني (أحاديث، إسلاميات)
4. شهادات عملاء
5. عروض العيد
6. آخر أيام رمضان (عرض أخير)
7. تهنئة العيد

لكل منشور:
- **اليوم:**
- **الوقت:**
- **النص:** (جاهز للنشر)
- **الصورة المقترحة:**
- **المنصة:**""",
        "temperature": 0.45,
    },
    "whatsapp_broadcast": {
        "name_ar": "رسائل واتساب بث (10 رسائل)",
        "name_en": "WhatsApp Broadcast Messages (10 Messages)",
        "prompt": """أنشئ 10 رسائل واتساب بث جاهزة للإرسال:
لكل رسالة:
- **النوع:** (ترحيب / عرض / تذكير / شهادة / خبر)
- **النص:** (مختصر — 2-4 سطورmaximum)
- **الصورة المرفقة:** (نعم/لا + وصف)
- **الوقت المقترح:**
- **CTA:** (اتصل بنا / أرسل رسالة / تعليق)

قواعد واتساب:
- لا روابط
- لا فواصل كثيرة
- CTA واحد فقط
- emoji بسيطة
- رسالة واحدة كافية (لا ترسل سلسلة)""",
        "temperature": 0.4,
    },
    "tiktok_scripts": {
        "name_ar": "سكريبتات تيك توك (5 فيديوهات)",
        "name_en": "TikTok Scripts (5 Videos)",
        "prompt": """أنشئ 5 سكريبتات فيديو تيك توك (15-30 ثانية لكل فيديو):
لكل فيديو:
- **الموضوع:**
- **Hook (أول 3 ثوانٍ):** (يجب أن يوقف السكرول)
- **المحتوى الرئيسي:** (15-20 ثانية)
- **CTA:** (آخر 3 ثوانٍ)
- **الموسيقى المقترحة:** (نوع أو وصف)
- **النص على الشاشة:**
- **الوصف:**
- **الهاشتاقات:**

أنواع الفيديوهات:
1. How-to (شرح سريع)
2. Before/After (قبل وبعد)
3. Day in the life (يوم في حياتي)
4. Tips (نصائح سريعة)
5. Customer reaction (رد فعل العميل)""",
        "temperature": 0.55,
    },
}


class SocialMediaGenerator:
    """Generate Arabic social media content through a selected LLM provider."""

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
            "User-Agent": "DSC-SocialMedia-Generator/1.0",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://kamelmh.github.io/digital-services-center/"
            headers["X-OpenRouter-Title"] = "DSC Social Media Generator"
        return headers

    def _call_llm(self, prompt: str, temperature: float = 0.5) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SOCIAL_MEDIA_SYSTEM_PROMPT},
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

    def list_content_types(self) -> list[dict[str, str]]:
        """Return available content types."""
        return [
            {"key": k, "name_ar": v["name_ar"], "name_en": v["name_en"]}
            for k, v in CONTENT_TYPES.items()
        ]

    def generate(
        self,
        content_type: str,
        business_type: str,
        business_name: str,
        location: str,
        wilaya: str,
    ) -> dict[str, Any]:
        """Generate social media content."""
        if getattr(self, "offline", False) or not getattr(self, "api_key", None):
            from offline_templates import social_media_offline
            return social_media_offline(content_type, business_type, business_name, location, wilaya)
        template = BUSINESS_TEMPLATES.get(business_type)
        if not template:
            raise FeasibilityError(f"Unknown business type: {business_type}")
        content_config = CONTENT_TYPES.get(content_type)
        if not content_config:
            raise FeasibilityError(f"Unknown content type: {content_type}")

        context = (
            f"اسم المشروع: {business_name}\n"
            f"النشاط: {template['name_ar']} ({template['name_en']}).\n"
            f"الموقع: {location}، ولاية {wilaya}.\n"
            f"المنتجات/الخدمات: {template['products']}.\n"
            f"الفئة المستهدفة: {template['category']}.\n"
        )

        print(f"  Generating {content_config['name_en']}...", file=sys.stderr)
        content = self._call_llm(context + content_config["prompt"], content_config["temperature"])

        now = datetime.now()
        header = f"""---
title: "محتوى سوشيال ميديا — {business_name}"
content_type: {content_type}
date: {now:%Y-%m-%d}
language: ar
---

# محتوى سوشيال ميديا

## {business_name}

| البند | التفاصيل |
|---|---|
| اسم المشروع | {business_name} |
| النشاط | {template['name_ar']} |
| الموقع | {location}، ولاية {wilaya} |
| نوع المحتوى | {content_config['name_ar']} |
| تاريخ الإعداد | {now:%d/%m/%Y} |

---

"""

        full_content = header + content
        full_content += f"""

---

**إعداد:** Digital Services Center — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** {now:%d/%m/%Y}"""

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="social_media",
                input_params={"business_type": business_type, "content_type": content_type},
                output_content=full_content,
            )
        except Exception:
            pass

        return {
            "title": f"محتوى سوشيال ميديا — {business_name}",
            "content_type": content_config["name_ar"],
            "date": now.isoformat(timespec="seconds"),
            "content": full_content,
        }
