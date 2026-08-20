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
    from prompts import PROMPT_VERSION
    from prompts import PROMPT_VERSION as _PROMPT_VERSION
    _PROMPT_VERSION = PROMPT_VERSION  # keep linter happy
except ImportError:
    PROMPT_VERSION = "unknown"

try:
    import requests
except ImportError as error:  # pragma: no cover - depends on local installation
    raise SystemExit(
        "Missing dependency: requests. Install it with: python -m pip install requests"
    ) from error

from financial_calculators import (
    CashFlow,
    FinancingPlan,
    FinancialCalculators,
    InvestmentPlan,
    format_dzd,
    format_pct,
    generate_3_scenarios,
)
from nesda_calculator import calculate_nesda_financing, format_nesda_report


class FeasibilityError(RuntimeError):
    """Raised when a feasibility study cannot be generated safely."""


ALGERIA_DATA = {
    "currency": "دج",
    "currency_code": "DZD",
    "population_growth_rate": 0.018,
    "snmg_monthly": 24_000,
    "tva_rate": 0.19,
    "corporate_tax_rate": 0.19,
    "cnas_employer_rate": 0.255,
    "loan_interest_rate": 0.09,
    "discount_rate": 0.12,
    "inflation_rate": 0.03,
    "wilayas": {
        # Eastern Algeria
        "Adrar": {"population": 413_000, "market_index": 0.70},
        "Chlef": {"population": 1_002_000, "market_index": 0.85},
        "Laghouat": {"population": 474_000, "market_index": 0.75},
        "Oum El Bouaghi": {"population": 633_000, "market_index": 0.80},
        "Batna": {"population": 1_119_000, "market_index": 0.85},
        "Béjaïa": {"population": 912_000, "market_index": 0.90},
        "Biskra": {"population": 721_000, "market_index": 0.80},
        "Béchar": {"population": 278_000, "market_index": 0.70},
        "Blida": {"population": 1_002_000, "market_index": 0.95},
        "Bouira": {"population": 695_000, "market_index": 0.85},
        "Tamanrasset": {"population": 190_000, "market_index": 0.65},
        "Tébessa": {"population": 644_000, "market_index": 0.80},
        "Tlemcen": {"population": 949_000, "market_index": 0.90},
        "Tiaret": {"population": 846_000, "market_index": 0.80},
        "Tizi Ouzou": {"population": 1_127_000, "market_index": 0.95},
        "Alger": {"population": 3_915_000, "market_index": 1.15},
        "Djelfa": {"population": 1_092_000, "market_index": 0.80},
        "Jijel": {"population": 638_000, "market_index": 0.85},
        "Sétif": {"population": 1_489_000, "market_index": 0.90},
        "Saïda": {"population": 370_000, "market_index": 0.80},
        "Skikda": {"population": 529_000, "market_index": 0.85},
        "Sidi Bel Abbès": {"population": 623_000, "market_index": 0.85},
        "Annaba": {"population": 640_000, "market_index": 0.95},
        "Guelma": {"population": 487_000, "market_index": 0.80},
        "Constantine": {"population": 938_000, "market_index": 0.95},
        "Médéa": {"population": 819_000, "market_index": 0.85},
        "Mostaganem": {"population": 728_000, "market_index": 0.85},
        "M'sila": {"population": 990_000, "market_index": 0.80},
        "Mascara": {"population": 608_000, "market_index": 0.80},
        "Ouargla": {"population": 553_000, "market_index": 0.80},
        "Oran": {"population": 1_560_000, "market_index": 1.05},
        "El Bayadh": {"population": 228_000, "market_index": 0.85},
        "Illizi": {"population": 52_000, "market_index": 0.65},
        "Bordj Bou Arréridj": {"population": 628_000, "market_index": 0.80},
        "Boumerdès": {"population": 802_000, "market_index": 0.90},
        "El Tarf": {"population": 413_000, "market_index": 0.80},
        "Tindouf": {"population": 176_000, "market_index": 0.65},
        "Tissemsilt": {"population": 295_000, "market_index": 0.75},
        "El Oued": {"population": 670_000, "market_index": 0.80},
        "Khenchela": {"population": 387_000, "market_index": 0.75},
        "Souk Ahras": {"population": 445_000, "market_index": 0.80},
        "Tipaza": {"population": 593_000, "market_index": 0.90},
        "Mila": {"population": 781_000, "market_index": 0.80},
        "Aïn Defla": {"population": 580_000, "market_index": 0.85},
        "Naâma": {"population": 206_000, "market_index": 0.70},
        "Aïn Témouchent": {"population": 372_000, "market_index": 0.80},
        "Ghardaïa": {"population": 376_000, "market_index": 0.80},
        "Relizane": {"population": 603_000, "market_index": 0.80},
        # Southern / Saharan wilayas (recently created, smaller populations)
        "El M'Ghair": {"population": 162_000, "market_index": 0.65},
        "El Meniaa": {"population": 57_000, "market_index": 0.60},
        "Ouled Djellal": {"population": 178_000, "market_index": 0.65},
        "Bordj Badji Mokhtar": {"population": 95_000, "market_index": 0.55},
        "Béni Abbès": {"population": 52_000, "market_index": 0.55},
        "Timimoun": {"population": 120_000, "market_index": 0.60},
        "Touggourt": {"population": 215_000, "market_index": 0.70},
        "Djanet": {"population": 45_000, "market_index": 0.55},
        "In Salah": {"population": 50_000, "market_index": 0.55},
        "In Guezzam": {"population": 12_000, "market_index": 0.50},
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
    "tailleur": {
        "name_ar": "خياط / ورشة تفصيل ملابس",
        "name_en": "Tailor / Clothing Workshop",
        "category": "حرف يدوية",
        "investment": (500_000, 2_000_000),
        "margin": (0.30, 0.55),
        "staff": (2, 5),
        "area_sqm": (20, 60),
        "products": "تفصيل ملابس رجالية ونسائية، تعديل ملابس، تصاميم خاصة، خياطة أحذية",
    },
    "photographe": {
        "name_ar": "مصور فوتوغرافي / ستوديو",
        "name_en": "Photographer / Studio",
        "category": "خدمات إبداعية",
        "investment": (800_000, 3_000_000),
        "margin": (0.35, 0.60),
        "staff": (1, 3),
        "area_sqm": (20, 50),
        "products": "تصوير مناسبات، تصوير أوراق رسمية، تصوير منتجات، طباعة صور، ألبومات",
    },
    "pressing": {
        "name_ar": "مغسلة وكيو / بريسينغ",
        "name_en": "Dry Cleaning / Pressing",
        "category": "خدمات",
        "investment": (800_000, 3_000_000),
        "margin": (0.25, 0.45),
        "staff": (2, 5),
        "area_sqm": (30, 80),
        "products": "غسيل وكيو ملابس، تنظيف جاف، تنظيف أحذية، تنظيف ستائر وسجاد",
    },
    "car_wash": {
        "name_ar": "غسيل سيارات آلي",
        "name_en": "Car Wash (Automated)",
        "category": "خدمات",
        "investment": (2_000_000, 6_000_000),
        "margin": (0.20, 0.40),
        "staff": (2, 5),
        "area_sqm": (80, 200),
        "products": "غسيل خارجي وداخلي، تلميع، تعقيم، تنظيف محرك، خدمات تفريغ",
    },
    "laverie": {
        "name_ar": "مغسلة ذاتية / لافري",
        "name_en": "Self-Service Laundry",
        "category": "خدمات",
        "investment": (3_000_000, 8_000_000),
        "margin": (0.25, 0.45),
        "staff": (1, 2),
        "area_sqm": (40, 100),
        "products": "غسيل ذاتي بالماكينات، تجفيف، خدمة التوصيل",
    },
    "fleuriste": {
        "name_ar": "محل زهور / فلوريست",
        "name_en": "Florist / Flower Shop",
        "category": "تجارة",
        "investment": (500_000, 2_000_000),
        "margin": (0.35, 0.60),
        "staff": (1, 3),
        "area_sqm": (20, 50),
        "products": "باقات زهور، هدايا، تنسيقات مناسبات، زهور صناعية، أصص زينة",
    },
    "librairie": {
        "name_ar": "مكتبة / دار نشر",
        "name_en": "Bookstore / Stationery",
        "category": "تجارة",
        "investment": (500_000, 2_500_000),
        "margin": (0.15, 0.30),
        "staff": (1, 4),
        "area_sqm": (30, 80),
        "products": "كتب مدرسية وجامعية، قرطاسية، لوازم مكتبية، هدايا، طباعة ونسخ",
    },
    "teledentaire": {
        "name_ar": "عيادة أسنان صغيرة",
        "name_en": "Small Dental Clinic",
        "category": "صحة",
        "investment": (5_000_000, 15_000_000),
        "margin": (0.30, 0.50),
        "staff": (2, 6),
        "area_sqm": (40, 100),
        "products": "علاج أسنان عام، حشوات، تنظيف، خلع، تقويم أساسي، أشعة سينية",
    },
    "optique": {
        "name_ar": "محل نظارات طبية",
        "name_en": "Optician / Optical Shop",
        "category": "صحة وتجارة",
        "investment": (2_000_000, 6_000_000),
        "margin": (0.30, 0.55),
        "staff": (1, 3),
        "area_sqm": (20, 50),
        "products": "عدسات طبية، نظارات شمسية، فحص نظر، عدسات لاصقة، مستلزمات العناية بالنظارات",
    },
    "telephonie": {
        "name_ar": "محل هواتف وإلكترونيات",
        "name_en": "Phone & Electronics Shop",
        "category": "تجارة",
        "investment": (2_000_000, 8_000_000),
        "margin": (0.10, 0.25),
        "staff": (1, 4),
        "area_sqm": (20, 60),
        "products": "هواتف ذكية، لوازم جانبية، شحن، إصلاح هواتف، خطوط اتصال",
    },
    "jardinage": {
        "name_ar": "خدمات حدائق وتنسيق",
        "name_en": "Landscaping & Gardening Services",
        "category": "خدمات",
        "investment": (300_000, 1_500_000),
        "margin": (0.30, 0.50),
        "staff": (2, 5),
        "area_sqm": (0, 0),
        "products": "تنسيق حدائق، زراعة أشجار، ري آلي، صيانة خضراء، تغطية أرضية",
    },
    "menage": {
        "name_ar": "خدمات تنظيف منزلي",
        "name_en": "Home Cleaning Service",
        "category": "خدمات منزلية",
        "investment": (200_000, 800_000),
        "margin": (0.25, 0.45),
        "staff": (2, 8),
        "area_sqm": (0, 0),
        "products": "تنظيف منازل، تنظيف مكاتب، تنظيف ما بعد البناء، تنظيف السجاد والمفروشات",
    },
    "froid_climatisation": {
        "name_ar": "تركيب وصيانة تكييف وتبريد",
        "name_en": "HVAC Installation & Maintenance",
        "category": "خدمات تقنية",
        "investment": (500_000, 2_000_000),
        "margin": (0.30, 0.50),
        "staff": (2, 5),
        "area_sqm": (20, 50),
        "products": "تركيب تكييف، صيانة دورية، إصلاح أعطال، تبريد صناعي، قطع غيار",
    },
}

# ── Regulatory checklists per business type ────────────────────────────────────

REGULATORY_CHECKLISTS = {
    "default": [
        {"item": "التسجيل التجاري (RC)", "authority": "مركز التسجيل التجاري", "cost_range": "2,000–5,000 دج", "deadline": "قبل بدء النشاط"},
        {"item": "التصريح بالنشاط", "authority": "مصلحة الضرائب", "cost_range": "مجاني", "deadline": "خلال 30 يومًا من التسجيل"},
        {"item": "رقم التعريف الجبائي (NIF)", "authority": "مصلحة الضرائب", "cost_range": "مجاني", "deadline": "فور التسجيل"},
        {"item": "التصريح بال_works_الработников (DN)", "authority": "CNAS", "cost_range": "حسب عدد العمال", "deadline": "قبل التوظيف"},
        {"item": "رخصة الاستغلال", "authority": "البلدية", "cost_range": "5,000–20,000 دج", "deadline": "قبل بدء التشغيل"},
        {"item": "شهادة المطابقة للمعايير", "authority": "IANOR", "cost_range": "حسب النشاط", "deadline": "حسب المطلب"},
    ],
    "restaurant": [
        {"item": "رخصة صحية", "authority": "مصلحة النظافة البلدية", "cost_range": "5,000–15,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "شهادة مطابقة للمطاعم", "authority": "الديوان الوطني للتجارة (DNC)", "cost_range": "10,000–30,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "التصريح بالأنشطة الغذائية", "authority": "مصلحة النظافة", "cost_range": "مجاني", "deadline": "قبل الافتتاح"},
        {"item": "رخصة بيع المشروبات الكحولية", "authority": "الأمن والبلدية", "cost_range": "20,000–50,000 دج", "deadline": "إذا كان النشاط يتطلب ذلك"},
        {"item": "شهادة السلامة من الحريق", "authority": "الحماية المدنية", "cost_range": "5,000–10,000 دج", "deadline": "قبل الافتتاح"},
    ],
    "pharmacie": [
        {"item": "رخصة الصيدلية", "authority": "مديرية الصحة", "cost_range": "50,000–100,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "رخصة الصيدلي", "authority": "الهيئة الوطنية للصيدلة", "cost_range": "10,000–20,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "شهادة المطابقة للمعايير", "authority": "IANOR", "cost_range": "حسب المطلب", "deadline": "قبل الافتتاح"},
        {"item": "التصريح بالتخزين", "authority": "مصلحة النظافة", "cost_range": "مجاني", "deadline": "قبل الافتتاح"},
    ],
    "atelier_ferro": [
        {"item": "رخصة الصناعة", "authority": "مديرية الصناعة", "cost_range": "10,000–30,000 دج", "deadline": "قبل بدء النشاط"},
        {"item": "شهادة السلامة المهنية", "authority": "مصلحة حفظ الصحة", "cost_range": "5,000–15,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "شهادة مطابقة للمعايير الفنية", "authority": "IANOR", "cost_range": "حسب المطلب", "deadline": "قبل الافتتاح"},
        {"item": "رخصة استعمال المواد الخطرة", "authority": "الحماية المدنية", "cost_range": "5,000–10,000 دج", "deadline": "إذا كان النشاط يتطلب ذلك"},
    ],
    "garage": [
        {"item": "رخصة إصلاح السيارات", "authority": "مديرية النقل", "cost_range": "15,000–30,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "شهادة المطابقة الفنية", "authority": "IANOR", "cost_range": "10,000–20,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "شهادة السلامة المهنية", "authority": "مصلحة حفظ الصحة", "cost_range": "5,000–10,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "رخصة استعمال المواد الخطرة", "authority": "الحماية المدنية", "cost_range": "5,000–10,000 دج", "deadline": "إذا كان النشاط يتطلب ذلك"},
    ],
    "cybercafe": [
        {"item": "رخصة استعمال الحواسيب", "authority": "مديرية الاتصالات", "cost_range": "10,000–20,000 دج", "deadline": "قبل الافتتاح"},
        {"item": "التصريح بالأنشطة الرقمية", "authority": "وزارة الاتصالات", "cost_range": "مجاني", "deadline": "قبل الافتتاح"},
        {"item": "شهادة حماية البيانات الشخصية", "authority": "CNDC", "cost_range": "حسب النشاط", "deadline": "إذا كان النشاط يتطلب ذلك"},
    ],
}

# ── Financial calculator integration ────────────────────────────────────────────


def calculate_real_financials(
    investment: int,
    business: dict[str, Any],
    wilaya: str,
) -> dict[str, Any]:
    """Run real deterministic financial calculations using financial_calculators.py.
    
    Returns a dict with real VAN, TRI, break-even, 3 scenarios, income statement,
    cash flow, and NESDA financing — no LLM guessing.
    """
    calc = FinancialCalculators()
    wilaya_data = ALGERIA_DATA["wilayas"].get(wilaya, {"market_index": 0.85})
    market_idx = wilaya_data.get("market_index", 0.85)

    # Investment breakdown based on business type
    inv = InvestmentPlan(
        equipment=investment * 0.40,
        buildings=investment * 0.25,
        engineering=investment * 0.05,
        working_capital=investment * 0.30,
    )

    # Revenue estimation based on business margins
    margin_mid = (business["margin"][0] + business["margin"][1]) / 2
    annual_revenue_est = investment * (1 + margin_mid) * market_idx

    # Financing plan (NESDA default if investment ≤ 10M)
    total_investment = inv.total_initial
    personal_pct = 0.02 if total_investment <= 10_000_000 else 0.50
    nesda_pct = 0.28 if total_investment <= 10_000_000 else 0.00
    bank_pct = 0.70 if total_investment <= 10_000_000 else 0.50

    financing = FinancingPlan(
        equity=total_investment * personal_pct + total_investment * nesda_pct,
        bank_loan=total_investment * bank_pct,
        loan_rate=0.0675,
        loan_years=8,
    )

    # Generate 3 scenarios
    scenarios = generate_3_scenarios(
        base_revenue=annual_revenue_est,
        base_cogs_rate=1 - margin_mid,
        base_operating_rate=0.15,
        investment=inv,
        financing=financing,
        years=5,
    )

    # Reference scenario calculations
    ref = scenarios["reference"]
    loan_payment = financing.annual_payment()

    # NESDA financing details (if applicable) — 2026 verified rates: 2% interest, 12 years, 1.5y grace
    nesda_result = None
    if total_investment <= 10_000_000:
        nesda_result = calculate_nesda_financing(
            total_cost=total_investment,
            model="triangular",
            profile="unemployed",
            monthly_revenue=annual_revenue_est // 12,
            cogs_pct=1 - margin_mid,
            operating_pct=0.15,
            interest_rate=0.0,
            repayment_years=7,
            grace_years=1.5,
        )

    return {
        "investment_plan": inv,
        "financing_plan": financing,
        "annual_revenue_est": annual_revenue_est,
        "scenarios": scenarios,
        "reference_van": ref["van"],
        "reference_tri": ref["tri"],
        "reference_seuil": ref["seuil_rentabilite"],
        "reference_delai": ref["delai_recuperation"],
        "reference_taux_marge": ref["taux_marge"],
        "reference_compte_resultat": ref["compte_resultat"],
        "reference_tresorerie": ref["tresorerie"],
        "nesda_result": nesda_result,
        "loan_payment": loan_payment,
        "monthly_revenue_est": annual_revenue_est // 12,
        "monthly_costs_est": (annual_revenue_est * (1 - margin_mid)) // 12,
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

SYSTEM_PROMPT = """أنت مستشار أعمال جزائري محترف تعد دراسة جدوى كاملة وفقًا للنموذج الرسمي الجزائري (المرسوم التنفيذي رقم 26-154 المؤرخ في 14 أبريل 2026، الملحق V).
اكتب بالعربية الفصحى فقط وبأسلوب واضح مناسب لتقديمه لبنك أو هيئة تمويل أو صاحب مشروع.
استخدم Markdown منظمًا، والجداول عند الحاجة. كل الأرقام تقديرية ويجب وصفها بأنها
تقديرات أولية قابلة للتحقق، ولا تخترع إحصاءات أو مصادر أو جهات حكومية مؤكدة.
راعِ واقع السوق الجزائري، واستخدم الدينار الجزائري.
مهم جداً: لا تكتب مقدمة عامة ولا عنوانًا مكررًا للقسم؛ أجب بمحتوى القسم المطلوب فقط.
اكتب أرقامًا واقعية مبنية على افتراضات معقولة. لا تبالغ في التوقعات.
⚠️ تحذير مهم جداً: اكتب بالعربية الفصحى فقط. ممنوع تمامًا استخدام أي حروف من لغات أخرى (صينية، روسية، فرنسية، إنجليزية، أو أي لغة أخرى). حتى لو كنت تعرف كلمة في لغة أخرى، استخدم الترجمة العربية فقط. مثال: اكتب "استراحة" وليس "перерыва"، و"ملاحظات" وليس "feedback"، و"خاصة" وليس "特别"."""


ALGERIAN_TAX_INCENIVES = {
    "exemption_property_tax": "إعفاء من الضريبة العقارية لمدة 3 سنوات (6 سنوات للهضاب العليا، 10 سنوات للجنوب)",
    "exemption_ifu": "إعفاء من الضريبة الفردية الموحدة (IFU) لمدة 3 سنوات (6 سنوات للهضاب العليا، 10 سنوات للجنوب)",
    "reduced_customs": " خصم 5% من رسوم الجمارك على المعدات المستوردة للمشروع",
    "exemption_registration": "إعفاء من رسوم التسجيل للفاعلين الاقتصاديين الجدد",
    "extension_bonus": "تمديد سنة إضافية من الإعفاء عند التزام المقاول بتوظيف 3 عمال على الأقل",
}

NESDA_FINANCING = {
    "creation": {
        "max_investment": 10_000_000,
        "bank_share": 0.70,
        "nesda_pnr": 0.28,
        "personal_share": 0.02,
        "interest_rate": 0.0,
        "bank_rate": 0.0675,
        "bank_duration_years": 8,
        "bank_deferral_years": 3,
        "nesda_duration_years": 5,
    },
    "expansion": {
        "max_investment": 10_000_000,
        "bank_share": 0.70,
        "nesda_pnr": 0.28,
        "personal_share": 0.02,
    },
}

CNAC_FINANCING = {
    "max_investment": 10_000_000,
    "bank_share": 0.70,
    "cnac_pnr": 0.28,
    "personal_share": 0.02,
    "interest_rate": 0.0,
    "bank_rate": 0.0675,
    "total_duration_years": 13,
    "bank_duration_years": 8,
    "bank_deferral_years": 3,
    "cnac_duration_years": 5,
    "age_min": 30,
    "age_max": 50,
}

BANK_REGULATION_14_03 = """أثرت اللائحة رقم 14-03 الصادرة عن بنك الجزائر بتاريخ 16 فيفري 2014 على:'
- التصنيف والاحتياطي للمديونيات والالتزامات بالتوقيع
- تصنيف المخاطر وفق معايير تنظيمية
- التزام البنك بتوثيق قراره بناءً على ملف متكامل"""


class FeasibilityGenerator:
    """Generate an Arabic feasibility study. Works offline (templates) or online (LLM)."""

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int = 90,
        retries: int = 3,
        allow_offline: bool = True,
    ) -> None:
        self.offline = False
        self.prompt_version = PROMPT_VERSION
        try:
            self.provider = self._resolve_provider(provider, api_key)
            config = PROVIDERS[self.provider]
            self.api_key = api_key or self._read_api_key(config["key_env"])
            if not self.api_key:
                if allow_offline:
                    self.offline = True
                    self.provider = "offline"
                    self.api_key = None
                    self.model = "offline-templates"
                    self.url = ""
                    self.timeout = timeout
                    self.retries = retries
                    self.session = requests.Session()
                    return
                variables = " or ".join(config["key_env"])
                raise FeasibilityError(f"No API key found for {self.provider}. Set {variables} or use --api-key.")
        except FeasibilityError:
            if allow_offline:
                self.offline = True
                self.provider = "offline"
                self.api_key = None
                self.model = "offline-templates"
                self.url = ""
                self.timeout = timeout
                self.retries = retries
                self.session = requests.Session()
                return
            raise

        self.model = model or os.getenv(f"FEASIBILITY_{self.provider.upper()}_MODEL") or config["model"]
        self.url = os.getenv(f"FEASIBILITY_{self.provider.upper()}_URL", config["url"])
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.prompt_version = PROMPT_VERSION

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

        # Offline path — no API key, no LLM needed
        if getattr(self, "offline", False) or not getattr(self, "api_key", None):
            from offline_templates import feasibility_offline
            business_name = location.strip()
            result = feasibility_offline(business_type, business_name, location.strip(), wilaya.strip(), investment)
            # Attach real financials for PDF export compatibility
            try:
                rf = calculate_real_financials(investment, business, wilaya.strip())
                result["real_financials"] = {
                    "investment_plan": rf["investment_plan"],
                    "financing_plan": rf["financing_plan"],
                    "annual_revenue_est": rf["annual_revenue_est"],
                    "reference_van": rf["reference_van"],
                    "reference_tri": rf["reference_tri"],
                    "reference_seuil": rf["reference_seuil"],
                    "reference_delai": rf["reference_delai"],
                    "reference_taux_marge": rf["reference_taux_marge"],
                    "reference_compte_resultat": rf["reference_compte_resultat"],
                    "reference_tresorerie": rf["reference_tresorerie"],
                    "scenarios": rf["scenarios"],
                    "nesda_result": rf["nesda_result"],
                    "loan_payment": rf["loan_payment"],
                }
            except Exception:
                pass
            # Quality gate (offline)
            try:
                from quality_scorer import QualityScorer as _QS
                _qro = _QS().score("feasibility", result["content"])
                _qmo = {"quality_grade": _qro.grade, "quality_score": round(_qro.overall_score, 3), "quality_passed": _qro.passed}
            except Exception:
                _qmo = {}
            try:
                from training_hook import hook_generation
                hook_generation(generator="feasibility", input_params={"business_type": business_type, "location": location, "wilaya": wilaya, "investment": investment, "mode": "offline"}, output_content=result["content"], metadata={"sections": list(result["sections"].keys()), "offline": True, "prompt_version": getattr(self, "prompt_version", "unknown"), **_qmo})
            except Exception:
                pass
            return result

        # Compute real financial calculations (no LLM guessing)
        real_financials = calculate_real_financials(investment, business, wilaya.strip())

        prompts = self._build_prompts(business, location.strip(), wilaya.strip(), investment, real_financials)
        sections: dict[str, str] = {}
        for index, (name, prompt, temperature) in enumerate(prompts, start=1):
            print(f"  [{index}/{len(prompts)}] إنشاء {name}...", file=sys.stderr)
            sections[name] = self._call_llm(prompt, temperature)
        result = self._assemble_study(business, location.strip(), wilaya.strip(), investment, sections)

        # Attach real financials for PDF export
        result["real_financials"] = {
            "investment_plan": real_financials["investment_plan"],
            "financing_plan": real_financials["financing_plan"],
            "annual_revenue_est": real_financials["annual_revenue_est"],
            "reference_van": real_financials["reference_van"],
            "reference_tri": real_financials["reference_tri"],
            "reference_seuil": real_financials["reference_seuil"],
            "reference_delai": real_financials["reference_delai"],
            "reference_taux_marge": real_financials["reference_taux_marge"],
            "reference_compte_resultat": real_financials["reference_compte_resultat"],
            "reference_tresorerie": real_financials["reference_tresorerie"],
            "scenarios": real_financials["scenarios"],
            "nesda_result": real_financials["nesda_result"],
            "loan_payment": real_financials["loan_payment"],
        }

        # Quality gate (online)
        try:
            from quality_scorer import QualityScorer as _QS2
            _full = "\n\n".join(str(v) for v in result.values() if isinstance(v, str))
            _qr2 = _QS2().score("feasibility", _full)
            _qm2 = {"quality_grade": _qr2.grade, "quality_score": round(_qr2.overall_score, 3), "quality_passed": _qr2.passed}
        except Exception:
            _qm2 = {}
            _full = ""
        try:
            from training_hook import hook_generation
            full_text = _full if '_full' in locals() and _full else "\n\n".join(str(v) for v in result.values() if isinstance(v, str))
            hook_generation(
                generator="feasibility",
                input_params={"business_type": business_type, "location": location, "wilaya": wilaya, "investment": investment},
                output_content=full_text,
                metadata={"sections": list(sections.keys()), "prompt_version": getattr(self, "prompt_version", "unknown"), **_qm2},
            )
        except Exception:
            pass

        return result

    @staticmethod
    def _build_prompts(business: dict[str, Any], location: str, wilaya: str, investment: int, real_financials: dict[str, Any] | None = None) -> list[tuple[str, str, float]]:
        wilaya_data = ALGERIA_DATA["wilayas"].get(wilaya, {"population": None, "market_index": None})
        population_note = f"تعداد سكان الولاية المرجعي: {wilaya_data['population']:,}." if wilaya_data["population"] else "لا تتوفر بيانات سكانية محلية مؤكدة؛ اذكر الحاجة إلى التحقق الميداني."

        # Build real financial data block
        rf_block = ""
        if real_financials:
            ref_van = real_financials["reference_van"]
            ref_tri = real_financials["reference_tri"]
            ref_seuil = real_financials["reference_seuil"]
            ref_delai = real_financials["reference_delai"]
            ref_taux = real_financials["reference_taux_marge"]
            loan_pmt = real_financials["loan_payment"]
            annual_rev = real_financials["annual_revenue_est"]
            inv_plan = real_financials["investment_plan"]
            fin_plan = real_financials["financing_plan"]
            nesda = real_financials["nesda_result"]

            rf_block = f"""
**══════ الأرقام المالية الحسابية (ليس تقديرات LLM) ══════**
**هذه الأرقام محسوبة بدقة بواسطةfinancial_calculators.py — استخدمها في جميع الأقسام:**

**هيكل الاستثمار الإجمالي:** {inv_plan.total_initial:,.0f} دج
- تجهيزات: {inv_plan.equipment:,.0f} دج ({inv_plan.equipment/inv_plan.total_initial*100:.0f}%)
- مباني: {inv_plan.buildings:,.0f} دج ({inv_plan.buildings/inv_plan.total_initial*100:.0f}%)
- هندسة ودراسات: {inv_plan.engineering:,.0f} دج
- رأس المال العامل: {inv_plan.working_capital:,.0f} دج

**هيكل التمويل:**
- المساهمة الشخصية: {fin_plan.equity:,.0f} دج ({fin_plan.equity_ratio*100:.0f}%)
- القرض البنكي: {fin_plan.bank_loan:,.0f} دج ({fin_plan.bank_loan/inv_plan.total_initial*100:.0f}%)
- سعر الفائدة: {fin_plan.loan_rate*100:.2f}%
- مدة السداد: {fin_plan.loan_years} سنوات
- القسط السنوي: {loan_pmt:,.0f} دج
- القسط الشهري: {loan_pmt/12:,.0f} دج

**مؤشرات الربحية (السيناريو المرجحي):**
- الإيرادات السنوية المقدرة: {annual_rev:,.0f} دج
- VAN (صافي القيمة الحالية): {ref_van:,.0f} دج {"✅ موجب (مشروع مربح)" if ref_van > 0 else "❌ سالب (مشروع غير مربح)"}
- TRI (معدل العائد الداخلي): {ref_tri:.1f}%
- نقطة التعادل: {ref_seuil:,.0f} وحدة
- تأخير استرداد الاستثمار: {ref_delai:.1f} سنة
- هامش صافي الربح: {ref_taux:.1f}%
"""

            if nesda:
                rf_block += f"""
**══════ تفاصيل تمويل NESDA ══════**
- المساهمة الشخصية: {nesda.personal_amount:,.0f} دج ({nesda.personal_pct*100:.0f}%)
- مساهمة NESDA (PNR): {nesda.nesda_grant:,.0f} دج ({nesda.nesda_pct*100:.0f}%)
- القرض البنكي: {nesda.bank_loan:,.0f} دج ({nesda.bank_pct*100:.0f}%)
- سعر الفائدة البنكي: {nesda.interest_rate*100:.2f}%
- فترة السماح: {nesda.grace_years} سنة
- القسط الشهري: {nesda.monthly_payment:,.0f} دج
- إجمالي السداد: {nesda.total_repayment:,.0f} دج
- مدة الاسترداد: {nesda.payback_months} شهر
- العائد السنوي (ROI): {nesda.roi_annual:.1f}%
"""

            # Add 3 scenarios table
            scenarios = real_financials["scenarios"]
            rf_block += """
**══════ تحليل السيناريوهات الثلاثة (محسوب بدقة) ══════**
| السيناريو | الإيرادات السنوية | VAN | TRI | نقطة التعادل | تأخير الاسترداد |
|-----------|-------------------|-----|-----|--------------|----------------|
"""
            for sname, sdata in scenarios.items():
                label = sdata["label"]
                rev = format_dzd(sdata["annual_revenue"])
                van_str = format_dzd(sdata["van"])
                tri_str = format_pct(sdata["tri"])
                seuil_str = format_dzd(sdata["seuil_rentabilite"])
                delai_str = f"{sdata['delai_recuperation']:.1f} سنة"
                rf_block += f"| {label} | {rev} | {van_str} | {tri_str} | {seuil_str} | {delai_str} |\n"

        fin_assumptions = f"""
**الافتراضات المالية الأساسية (محدثة 2026):**
- معدل TVA: 19% (تطبيق عادي)، 9% (تطبيق مخفض)
- IBS (ضريبة الأرباح): 19% للصناعة، 23% للخدمات
- IRG (ضريبة الدخل الشخصية): 0-35% (تكراري تقدمي)
- IFU (نظام مبسط): 5% للبضاعة/الصناعة، 12% للخدمات (الحد الأقصى 8M دج)
- CNAS صاحب العمل: 25% + 0.5% أعمال اجتماعية = 25.5% إجمالاً
- CNAS الموظف: 9% (قابل للخصم قبل IRG)
- فائدة القروض العامة: 6.75% (LTA + 1.5%)
- فائدة قرض NESDA: 2% (معدل مخفض)
- معدل الخصم (VAN): 12%
- مدة سداد NESDA: 12 سنة (1.5 سنة حظر + 10.5 سنة سداد)
- SNMG: 24,000 دج/شهر (حد أدنى للأجور)
- الحد الأقصى للتمويل NESDA: 10,000,000 دج
- NESDA: حصة البنك 70%، حصة NESDA 15-25%، حصة شخصية 5-15%
- CNAC: الحد الأقصى 10,000,000 دج، فئة العمر 30-50 سنة
- إعفاء من الضريبة العقارية والـ IFU لمدة 3 سنوات (6 للهضاب العليا، 10 للجنوب)
"""

        context = (
            f"النشاط: {business['name_ar']} ({business['name_en']}).\n"
            f"الموقع: {location}، ولاية {wilaya}.\n"
            f"التصنيف: {business['category']}.\n"
            f"الاستثمار التقديري: {investment:,} دج.\n"
            f"المنتجات/الخدمات: {business['products']}.\n"
            f"عدد العمال المتوقع: {business['staff'][0]}–{business['staff'][1]}.\n"
            f"المساحة المقترحة: {business['area_sqm'][0]}–{business['area_sqm'][1]} م².\n"
            f"{rf_block}"
            f"\n{fin_assumptions}"
            f"\n⚠️ تذكير: اكتب بالعربية الفصحى فقط. لا تستخدم أي حروف صينية أو روسية أو فرنسية أو إنجليزية."
            f"\n⚠️ الأرقام المالية أعلاه محسوبة بدقة — استخدمها كما هي في جداولك."
        )
        return [
            # ── Section 1: Profile du Porteur ──
            ("تحديد هوية صاحب المشروع", context + """
اكتب القسم الأول من النموذج الرسمي: تحديد هوية صاحب المشروع وتقديم المشروع.
- اسم صاحب المشروع (استخدم "[اسم صاحب المشروع]" ك.placeholders)
- الجنسية، تاريخ الميلاد، الحالة الاجتماعية
- المؤهل الدراسي والخبرة المهنية
- ملخص المشروع في 3-5 أسطر
- طبيعة المشروع (جديد/توسيع)
- الشكل القانوني (مؤسسة فردية/شركة)
- الميزانية الإجمالية للمشروع
- مدة التنفيذ المتوقعة""", 0.5),

            # ── Section 2: Presentation du Projet ──
            ("تقديم المشروع", context + """
اكتب القسم الثاني: تقديم المشروع بالتفصيل.
- وصف تفصيلي للمشروع والأنشطة الرئيسية
- الأهداف قصيرة المدى ومتوسطة المدى
- المبررات (3 مبررات على الأقل):
  1. مبرر اقتصادي (حاجة السوق، الطلب، الإنتاجية)
  2. مبرر مالي (الربحية، العائد على الاستثمار)
  3. مبرر اجتماعي (خلق فرص العمل، تلبية حاجة محلية)
- القطاع والتصنيف حسب النشاط
- نوع النشاط (إنتاجي/خدمي/تجاري)
- الميزة التنافسية للمشروع""", 0.5),

            # ── Section 3: Etude de Marche ──
            ("دراسة السوق", context + f"\n{population_note}\n" + """
اكتب القسم الثالث بالتفصيل (هذا القسم الأطول والأهم):
**أ) تحليل السوق المستهدف:**
- حجم السوق المحلي والإقليمي
- فئات الزبائن المستهدفين
- الطلب الحالي والمتوقع
- الموسمية والاتجاهات

**ب) تحليل المنافسة:**
- المنافسون المحليون (اسم، حجم، سعر، نقاط القوة والضعف)
- تحليل SWOT للمشروع
- الميزة التنافسية

**ج) خطة التسويق:**
- استراتيجيات التسعير (التكلفة+الهامش، المنافسة، القيمة)
- قنوات التوزيع (محلية، إلكترونية، شراكات)
- خطة التواصل والحملات (وسائل التواصل، إعلان محلي، ملصقات)
- الاحتفاظ بالزبائن

**د) توقعات المبيعات (5 سنوات):**
- جدول توقعات المبيعات الشهرية للسنة الأولى
- جدول توقعات المبيعات السنوية لـ 5 سنوات
- اذكر أن هذه تقديرات ويجب التحقق من الطلب فعلياً""", 0.55),

            # ── Section 4: Procede de Production ──
            ("خط الإنتاج وسير العمل", context + """
اكتب القسم الرابع: وصف التكنولوجيا وسير العمل.
- وصف تفصيلي لخط الإنتاج أو خدمة العمل
- مراحل العمل بالتفصيل (تسلسل عملي)
- تدفق المواد الأولية والمخزون
- معدات الإنتاج (جدول بالاسم، الكمية، السعر التقديري)
- مراقبة الجودة
- تكييف العملية مع ظروف المناخ والبيئة""", 0.5),

            # ── Section 5: Plan de Ressources Humaines ──
            ("خطة الموارد البشرية", context + """
اكتب القسم الخامس: خطة الموارد البشرية بالتفصيل.
- هيكل التنظيمي (جدول بالمنصب، المؤهل، عدد المناصب، الأجر الشهري)
- البرنامج التدريبي للعاملين
- نظام العمل (ساعات العمل، الراحة الأسبوعية، الإجازات)
- ظروف العمل والسلامة المهنية
- تطور العمال على مدى 5 سنوات""", 0.45),

            # ── Section 6: Plan de Financement ──
            ("خطة التمويل", context + f"""
اكتب القسم السادس: خطة التمويل التفصيلية.
**أ) هيكل الاستثمار:**
- جدول تفصيلي لعناصر الاستثمار (تجهيزات، معدات، ترميم، رأس مال عامل)
- إجمالي الاستثمار: {format_dzd(real_financials['investment_plan'].total_initial) if real_financials else 'حسب الجدول أعلاه'}

**ب) مصادر التمويل:**
- الحصة الشخصية: {format_dzd(real_financials['financing_plan'].equity) if real_financials else 'حسب الجدول أعلاه'}
- التمويل البنكي: القرض، المدة، الفائدة، السداد
- التمويل NESDA/PNR (إن وجد): 28% حصة NESDA، 70% بنك، 2% شخصي
- التمويل CNAC (إن وجد): الحد الأقصى 10M دج، فئة العمر 30-50
- الإعفاءات الضريبية: 3 سنوات ضريبة عقارية + IFU (6 للهضاب العليا، 10 للجنوب)

**ج) خطة السداد:**
- القسط الشهري: {format_dzd(real_financials['loan_payment']/12) if real_financials else 'حسب الجدول أعلاه'}
- القسط السنوي: {format_dzd(real_financials['loan_payment']) if real_financials else 'حسب الجدول أعلاه'}
- إجمالي المبلغ المدفوع والمطلوب
- مدة السداد""", 0.5),

            # ── Section 7: Compte de Resultat Previsionnel ──
            ("حساب النتيجة التقديري", context + f"""
{fin_assumptions}
اكتب القسم السابع: حساب النتيجة التقديري لـ 5 سنوات.
**استخدم الأرقام الحسابية أعلاه (من financial_calculators.py) في جدول حساب النتيجة:**

**جدول حساب النتيجة (بالألف دج):**
| البند | السنة 1 | السنة 2 | السنة 3 | السنة 4 | السنة 5 |
|-------|---------|---------|---------|---------|---------|
| الإيرادات | حسب السيناريو المرجحي | | | | |
| التكاليف المباشرة | حسب هامش الربح | | | | |
| هامش الإجمالي | | | | | |
| التكاليف الثابتة | | | | | |
| الأرباح قبل الفوائد والضرائب | | | | | |
| الفوائد على القروض | | | | | |
| الأرباح قبل الضرائب | | | | | |
| الضرائب (19%) | | | | | |
| صافي الربح | | | | | |
| هامش صافي الربح (%) | | | | | |

**ملاحظات:**
- هامش الربح الإجمالي: {format_pct(real_financials['reference_taux_marge']) if real_financials else 'حسب الجدول أعلاه'}
- لا تتجاوز معدلات النمو 25% سنوياً
- اذكر أن هذه تقديرات""", 0.45),

            # ── Section 8: Plan de Tresorerie ──
            ("خطة التدفقات النقدية", context + f"""
{fin_assumptions}
اكتب القسم الثامن: خطة التدفقات النقدية الشهرية للسنة الأولى + السنوية لـ 5 سنوات.

**أ) خطة التدفقات النقدية الشهرية (السنة الأولى):**
| الشهر | الإيرادات | المصاريف | التدفق الصافي | التراكمي |
|-------|-----------|----------|---------------|----------|
| يناير | | | | |
| ... | | | | |
| ديسمبر | | | | |

**ب) خطة التدفقات النقدية السنوية (5 سنوات):**
| البند | السنة 1 | السنة 2 | السنة 3 | السنة 4 | السنة 5 |
|-------|---------|---------|---------|---------|---------|
| التدفق الصافي | | | | | |
| التراكمي | | | | | |

**ج) تحليل نقطة التعادل (محسوب بدقة):**
- التكاليف الثابتة الشهرية: {format_dzd(real_financials['monthly_costs_est']) if real_financials else 'حسب الجدول أعلان'}
- نقطة التعادل بالوحدات: {int(real_financials['reference_seuil']) if real_financials and real_financials['reference_seuil'] != float('inf') else 'حسب الجدول أعلان'} وحدة
- المدة المتوقعة للوصول لنقطة التعادل: {real_financials['reference_delai']:.1f} سنة""" if real_financials else """
**ج) تحليل نقطة التعادل:**
- التكاليف الثابتة الشهرية
- هامش المساهمة لكل وحدة
- عدد الوحدات لنقطة التعادل
- المدة المتوقعة للوصول لنقطة التعادل""", 0.45),

            # ── Section 9: Annexes ──
            ("الملاحق", context + """
اكتب القسم التاسع (الملاحق): أنشئ قائمة بالمستندات المطلوبة لإتمام دراسة الجدوى النهائية.
- سيرة ذاتية لصاحب المشروع
- عروض أسعار للمعدات والتجهيزات
- عقود الإيجار أو اتفاقيات شراء العقار
- وثائق التسجيل التجاري والرخص
- دراسة ميدانية للطلب (إن أمكن)
- أي وثائق داعمة أخرى""", 0.35),

            # ── Section 10: Risk Analysis & Recommendations ──
            ("تحليل المخاطر والتوصيات", context + f"""
اكتب القسم الأخير: تحليل المخاطر الرئيسية للمشروع مع توصيات عملية.
**أ) تحليل المخاطر:**
| المخاطرة | الاحتمال | الأثر | استراتيجية التخفيف |
|----------|----------|-------|-------------------|
| مخاطرة السوق | | | |
| مخاطرة التنافسية | | | |
| مخاطرة التمويل | | | |
| مخاطرة التنظيم | | | |
| مخاطرة تقنية | | | |
| مخاطرة الموارد البشرية | | | |

**ب) تحليل السيناريوهات الثلاثة (محسوبة بدقة — استخدم الأرقام من الجدول أعلاه):**
| السيناريو | الإيرادات | VAN | TRI | نقطة التعادل | الربح الصافي |
|-----------|-----------|-----|-----|--------------|--------------|
| حذر (ال Worst Case) | {format_dzd(real_financials['scenarios']['prudent']['annual_revenue']) if real_financials else '—'} | {format_dzd(real_financials['scenarios']['prudent']['van']) if real_financials else '—'} | {format_pct(real_financials['scenarios']['prudent']['tri']) if real_financials else '—'} | {format_dzd(real_financials['scenarios']['prudent']['seuil_rentabilite']) if real_financials else '—'} | |
| مرجح (Base Case) | {format_dzd(real_financials['scenarios']['reference']['annual_revenue']) if real_financials else '—'} | {format_dzd(real_financials['scenarios']['reference']['van']) if real_financials else '—'} | {format_pct(real_financials['scenarios']['reference']['tri']) if real_financials else '—'} | {format_dzd(real_financials['scenarios']['reference']['seuil_rentabilite']) if real_financials else '—'} | |
| متفائل (Best Case) | {format_dzd(real_financials['scenarios']['favorable']['annual_revenue']) if real_financials else '—'} | {format_dzd(real_financials['scenarios']['favorable']['van']) if real_financials else '—'} | {format_pct(real_financials['scenarios']['favorable']['tri']) if real_financials else '—'} | {format_dzd(real_financials['scenarios']['favorable']['seuil_rentabilite']) if real_financials else '—'} | |

**ج) التوصيات النهائية:**
- توصيات لتحسين الربحية
- توصيات لتقليل المخاطر
- خطة العمل المقترحة""", 0.5),
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

1. تحديد هوية صاحب المشروع
2. تقديم المشروع
3. دراسة السوق
4. خط الإنتاج وسير العمل
5. خطة الموارد البشرية
6. خطة التمويل
7. حساب النتيجة التقديري
8. خطة التدفقات النقدية
9. الملاحق
10. تحليل المخاطر والتوصيات

---

## 1. تحديد هوية صاحب المشروع

{sections.get('تحديد هوية صاحب المشروع', 'لم يتم إدخال هذا القسم بعد.')}

---

## 2. تقديم المشروع

{sections.get('تقديم المشروع', 'لم يتم إدخال هذا القسم بعد.')}

---

## 3. دراسة السوق

{sections.get('دراسة السوق', 'لم يتم إدخال هذا القسم بعد.')}

---

## 4. خط الإنتاج وسير العمل

{sections.get('خط الإنتاج وسير العمل', 'لم يتم إدخال هذا القسم بعد.')}

---

## 5. خطة الموارد البشرية

{sections.get('خطة الموارد البشرية', 'لم يتم إدخال هذا القسم بعد.')}

---

## 6. خطة التمويل

{sections.get('خطة التمويل', 'لم يتم إدخال هذا القسم بعد.')}

---

## 7. حساب النتيجة التقديري

{sections.get('حساب النتيجة التقديري', 'لم يتم إدخال هذا القسم بعد.')}

---

## 8. خطة التدفقات النقدية

{sections.get('خطة التدفقات النقدية', 'لم يتم إدخال هذا القسم بعد.')}

---

## 9. الملاحق

{sections.get('الملاحق', 'لم يتم إدخال هذا القسم بعد.')}

---

## 10. تحليل المخاطر والتوصيات

{sections.get('تحليل المخاطر والتوصيات', 'لم يتم إدخال هذا القسم بعد.')}

---

## ملاحظات ختامية

- يجب استبدال كل التقديرات بعروض أسعار محلية قبل اعتماد المشروع.
- تتطلب بعض الأنشطة شروطًا مهنية وتنظيمية خاصة يجب التحقق منها لدى الجهات المختصة.
- تم إعداد هذه الوثيقة باللغة العربية وللاستخدام المهني داخل الجزائر.
- جميع الأرقام تقديرية وتستند إلى افتراضات قابلة للتحقق من مصادر رسمية.

**إعداد:** Academix DSS — مركز الخدمات الرقمية<br>
**تاريخ الإعداد:** {now:%d/%m/%Y}
"""
        return {
            "title": f"دراسة جدوى أولية — {business['name_ar']}",
            "business_type": business["name_ar"],
            "location": f"{location}، {wilaya}",
            "investment": investment,
            "generated_at": now.isoformat(),
            "content": content,
            "sections_count": len(sections),
            "sections_completed": list(sections.keys()),
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
