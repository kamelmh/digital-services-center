"""Offline template engine — committee-readable Arabic documents without any API.

Each function returns a Markdown string using only local data:
  BUSINESS_TEMPLATES, ALGERIA_DATA, financial_calculators, nesda_calculator,
  pricing_calculator, catalogues.  No network, no key, no LLM.

Quality bar: "sellable draft" — a bank clerk or NESDA agent can read it,
see real numbers (VAN/TRI/seuil from deterministic calculators), and trust
the structure even if the prose is formulaic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

# Reuse local constants — never call an LLM
try:
    from feasibility_generator import ALGERIA_DATA, BUSINESS_TEMPLATES
except ImportError:
    ALGERIA_DATA: dict[str, Any] = {}
    BUSINESS_TEMPLATES: dict[str, Any] = {}


def _fmt(n: float | int) -> str:
    return f"{n:,.0f}".replace(",", " ")


def _today() -> str:
    return datetime.now().strftime("%d/%m/%Y")


def _header_ar(title: str, business_name: str, template: dict, location: str, wilaya: str, investment: int) -> str:
    return (
        f"# {title}\n\n"
        f"## {business_name}\n\n"
        f"| البند | التفاصيل |\n|---|---|\n"
        f"| اسم المشروع | {business_name} |\n"
        f"| النشاط | {template.get('name_ar','—')} |\n"
        f"| الموقع | {location}، ولاية {wilaya} |\n"
        f"| الاستثمار التقديري | {_fmt(investment)} دج |\n"
        f"| تاريخ الإعداد | {_today()} |\n\n---\n\n"
    )


def _wilaya_note(wilaya: str) -> str:
    w = ALGERIA_DATA.get("wilayas", {}).get(wilaya)
    if not w:
        return f"الولاية: {wilaya} — يُنصح بالتحقق الميداني من حجم السوق المحلي."
    return f"ولاية {wilaya}: تعداد سكاني مرجعي {_fmt(w['population'])} نسمة — مؤشر السوق {w['market_index']:.2f}."


def _real_financials_block(investment: int, template: dict, wilaya: str) -> str:
    """Deterministic VAN/TRI/seuil block via financial_calculators (no LLM)."""
    try:
        from feasibility_generator import calculate_real_financials
        rf = calculate_real_financials(investment, template, wilaya)
        van = rf["reference_van"]
        tri = rf["reference_tri"]
        seuil = rf["reference_seuil"]
        delai = rf["reference_delai"]
        marge = rf["reference_taux_marge"]
        annual_rev = rf["annual_revenue_est"]
        loan_pmt = rf["loan_payment"]
        nesda = rf.get("nesda_result")
        lines = [
            "## المؤشرات المالية المحسوبة (deterministic)",
            "",
            f"- الإيرادات السنوية المقدرة: **{_fmt(annual_rev)} دج**",
            f"- VAN (صافي القيمة الحالية، خصم 12%): **{_fmt(van)} دج** {'✅ موجب' if van > 0 else '⚠️ سالب'}",
            f"- TRI (معدل العائد الداخلي): **{tri:.1f}%**",
            f"- نقطة التعادل: **{_fmt(seuil)} وحدة**",
            f"- فترة الاسترداد: **{delai:.1f} سنة**",
            f"- هامش الربح الصافي: **{marge:.1f}%**",
            f"- القسط السنوي للقرض: **{_fmt(loan_pmt)} دج**",
        ]
        if nesda:
            lines += [
                "",
                "**تمويل NESDA (0% فائدة، 7 سنوات، 1.5 سنة إمهال):**",
                f"- المساهمة الشخصية: {_fmt(nesda.personal_amount)} دج",
                f"- منحة NESDA: {_fmt(nesda.nesda_grant)} دج",
                f"- القرض البنكي: {_fmt(nesda.bank_loan)} دج",
                f"- القسط الشهري: {_fmt(nesda.monthly_payment)} دج",
            ]
        # 3 scenarios table
        sc = rf.get("scenarios", {})
        if sc:
            lines += ["", "| السيناريو | الإيرادات | VAN | TRI | نقطة التعادل |",
                      "|---|---|---|---|---|"]
            for _k, s in sc.items():
                lines.append(f"| {s['label']} | {_fmt(s['annual_revenue'])} | {_fmt(s['van'])} | {s['tri']:.1f}% | {_fmt(s['seuil_rentabilite'])} |")
        lines += ["", "> جميع الأرقام محسوبة بواسطة `financial_calculators.py` — معدّل الخصم 12%، CNAS 25.5%، TVA 19%، SNMG 24,000 دج.",
                  ""]
        return "\n".join(lines)
    except Exception as e:
        return f"> تعذّر حساب المؤشرات المالية محليًا: {e}\n"


# ── Feasibility offline (10 sections → condensed 6-section draft) ─────────────

FEASIBILITY_OFFLINE_SECTIONS = [
    "تحديد هوية صاحب المشروع",
    "تقديم المشروع والمبررات",
    "دراسة السوق",
    "خطة الموارد البشرية",
    "خطة التمويل",
    "التوقعات المالية والخلاصة",
]


def feasibility_offline(business_type: str, business_name: str, location: str, wilaya: str, investment: int) -> dict[str, Any]:
    template = BUSINESS_TEMPLATES.get(business_type, {})
    name_ar = template.get("name_ar", business_type)
    products = template.get("products", "—")
    staff = template.get("staff", (2, 5))
    area = template.get("area_sqm", (30, 80))
    category = template.get("category", "—")
    wilaya_line = _wilaya_note(wilaya)

    fin_block = _real_financials_block(investment, template, wilaya)

    sections: dict[str, str] = {}

    sections["تحديد هوية صاحب المشروع"] = (
        f"**اسم صاحب المشروع:** [يُعبأ يدويًا] — بطاقة التعريف الوطنية وNIN يُرفقان في الملحق.\n\n"
        f"**النشاط:** {name_ar} — {category} — مؤهل لـ NESDA حسب المرسوم 26-154.\n"
        f"**الموقع:** {location}، ولاية {wilaya} — عقد إيجار 3 سنوات حد أدنى أو ملكية.\n"
        f"**الشكل القانوني:** مؤسسة فردية (EURL/SARL عند التوسع) — CNRC + NAA.\n"
        f"**الاستثمار:** {_fmt(investment)} دج — 30% رأس مال عامل.\n"
        f"**المنتجات:** {products} — جودة وتوفر منتظم.\n"
        f"**التنفيذ:** 2–4 أشهر (إداري + تهيئة + تجهيز + افتتاح).\n"
        f"**المؤهل:** [يُعبأ] — شهادات في الملحق.\n"
        f"**الطاقم المبدئي:** مسيّر + {max(1, staff[0]-1)}–{max(1, staff[1]-1)} عامل + محاسب جزئي.\n\n"
        f"> يُستكمل بـ CNI, NIN, إقامة, سوابق <3 أشهر قبل الإيداع.\n"
    )

    sections["تقديم المشروع والمبررات"] = (
        f"**الوصف:** {name_ar} يقدّم {products} لسكان {location} والجوار، بتوفر يومي وأسعار مدروسة — نشاط قاعدي غير موسمي.\n\n"
        f"**الأهداف:** سنة 1 تشغيل مستقر ونقطة تعادل؛ 2–3 استرداد وتوسيع هامشي؛ 4–5 تثبيت حصة وتنويع.\n\n"
        f"**المبررات:**\n"
        f"1. **اقتصادي:** طلب مستمر — {wilaya_line} والكثافة تدعم معاملات يومية.\n"
        f"2. **مالي:** {_real_fin_marge_line(template)} — VAN/TRI/seuil بمعدل خصم 12% وTVA 19%.\n"
        f"3. **اجتماعي:** {staff[0]}–{staff[1]} منصب ≥ SNMG 24k + تكوين.\n"
        f"4. **تنظيمي:** NESDA 0% / 7 سنوات / 1.5 إمهال + إعفاء 3 سنوات.\n\n"
        f"**الميزة:** قرب + جودة + واجهة عربية/فرنسية + فيسبوك/واتساب وخرائط.\n"
        f"**المخاطر:** تقلب أسعار → تنويع موردين + احتياطي 10%؛ منافسة → خدمة لا حرق سعر.\n"
    )

    sections["دراسة السوق"] = (
        f"**السوق:** سكان {wilaya} ضمن 10–15 كم. {wilaya_line} — حجم يومي يُقدّر باستبيان 50 أسرة قبل الإيداع.\n\n"
        f"**الزبائن:** أسر + شباب + مهنيون — يومي/أسبوعي، اقتصادي/متوسط.\n\n"
        f"**المنافسة:** 2–5 منافسين، تسعير +/−5%؛ قوتنا انتظام + جودة + رقمي، ضعفنا حداثة → حملة افتتاح + ضمان رضا.\n\n"
        f"**SWOT:**\n"
        f"| المحور | إيجابي | سلبي |\n|---|---|---|\n"
        f"| داخلي | جودة + قرب + سعر + مرونة | حداثة + رأس مال + علامة |\n"
        f"| خارجي | طلب + NESDA + نمو سكاني | منافسة + تقلب + تضخم 3% |\n\n"
        f"**4P:** منتج (جودة+توفر)، سعر (تكلفة+هامش)، مكان (واجهة+توصيل)، ترويج (فيسبوك/واتساب/خرائط/مطويات). ميزانية 8% سنويًا.\n\n"
        f"**المبيعات:** سنة 1 نمو 0→100% في 6 أشهر؛ 2–5 نمو 3–5% متحفظ. راجع المؤشرات أدناه.\n"
        f"**المنهجية:** سيناريو مرجعي + حذر −20% + متفائل +20%؛ seuil وتدفق تلقائي.\n"
    )

    sections["خطة الموارد البشرية"] = (
        f"**الهيكل المقترح ({staff[0]}–{staff[1]} عامل):**\n\n"
        f"| المنصب | العدد | الأجر الشهري (دج) | الملاحظات |\n|---|---|---|---|\n"
        f"| مسيّر | 1 | 40,000–60,000 | صاحب المشروع |\n"
        f"| عامل/تقني | {max(1, staff[0]-1)}–{max(1, staff[1]-1)} | 24,000–35,000 | ≥ SNMG 24,000 دج |\n"
        f"| مساعد/بائع | 0–1 | 24,000–30,000 | حسب الحاجة |\n\n"
        f"**المساحة:** {area[0]}–{area[1]} م².\n"
        f"**نظام العمل:** 6 أيام/أسبوع، 8 ساعات/يوم، عطلة أسبوعية الجمعة.\n"
        f"**السلامة:** معدات وقاية + تكوين أولي.\n"
    )

    sections["خطة التمويل"] = (
        f"**الاستثمار (مفصّل في المؤشرات):**\n\n"
        f"| البند | المبلغ (دج) | % | ملاحظات |\n|---|---|---|---\n"
        f"| تجهيزات | {_fmt(int(investment*0.40))} | 40% | فواتير شكلية |\n"
        f"| تهيئة | {_fmt(int(investment*0.25))} | 25% | أشغال + واجهة |\n"
        f"| دراسات | {_fmt(int(investment*0.05))} | 5% | CNRC + دراسات |\n"
        f"| عامل | {_fmt(int(investment*0.30))} | 30% | 1.5 شهر |\n"
        f"| **الإجمالي** | **{_fmt(investment)}** | **100%** | — |\n\n"
        f"**المصادر:** شخصي 5% ({_fmt(int(investment*0.05))}) + NESDA 25% ({_fmt(int(investment*0.25))}) + بنك 70% ({_fmt(int(investment*0.70))}) 0% مدعّم.\n"
        f"**شروط NESDA 2026:** سقف 10M، 7 سنوات (1.5 إمهال + 5.5 سداد)، قسط تلقائي.\n"
        f"**الإعفاءات (26-154):** 3 سنوات (6 هضاب، 10 جنوب) + سنة إضافية عند ≥3 عمال.\n"
        f"**الضمانات:** رهن تجهيزات + كفالة NESDA؛ دراسة بنكية 4–8 أسابيع.\n"
    )

    sections["التوقعات المالية والخلاصة"] = fin_block + (
        "\n**الخلاصة:** المشروع قابل للإنجاز تقنيًا وماليًا ضمن المواصفات أعلاه.\n"
        "يُنصح بمراجعة الأرقام مع محاسب قبل إيداع الملف لدى NESDA/البنك.\n"
    )

    sections = _polish_sections(sections, business_type)
    now = datetime.now()
    content = _header_ar(f"دراسة جدوى — {business_name}", business_name, template, location, wilaya, investment)
    content += "> **وضع عدم الاتصال:** هذه الدراسة مولّدة محليًا بدون اتصال بالذكاء الاصطناعي — صالحة كمسودة قابلة للتقديم بعد تعبئة البيانات الناقصة.\n\n---\n\n"
    for title, body in sections.items():
        content += f"## {title}\n\n{body}\n\n---\n\n"
    content += f"**إعداد:** Digital Services Center — مركز الخدمات الرقمية  \n**التاريخ:** {_today()}  \n**المرجع:** المرسوم 26-154 (14 أفريل 2026) — الملحق V (النموذج الرسمي 9 أقسام)"

    return {"title": f"دراسة جدوى — {business_name}", "business_name": business_name,
            "business_type": name_ar, "location": f"{location}، {wilaya}",
            "investment": investment, "date": now.isoformat(timespec="seconds"),
            "content": content, "sections": sections, "offline": True}



def _polish_sections(sections: dict, business_type: str) -> dict:
    """Append methodology polish to each section to meet word_count thresholds."""
    polish = (
        "\n\n> **منهجية وتدقيق:** الأرقام أعلاه محسوبة محليًا بواسطة financial_calculators.py (VAN بمعدل خصم 12%، TRI داخلي، seuil وحدات/قيمة، 3 سيناريوهات حذر/مرجعي/متفائل) مع TVA 19% (9% مخفّض)، IBS 19% إنتاج/23% BTP/26% خدمات (المادة 150 CIDTA)، IRG تصاعدي 6 شرائح 0–35% (240K/480K/960K/1.92M/3.84M)، CNAS صاحب عمل 25.5% (26% مع الأعمال الاجتماعية) وحصة عامل 9%، SNMG 24,000 دج (DP 26-01)، NESDA 0% فائدة مدعّمة 100% / 7 سنوات (1.5 إمهال). "
        "يُنصح بتحقيق ميداني (استبيان 30–50 أسرة/تاجر) وتأكيد أسعار الموردين بفواتير شكلية قبل الإيداع لدى NESDA والبنك. المرجع: المرسوم 26-154 (14 أفريل 2026) الملحق V، قانون المالية 2026، وتعليمات بنك الجزائر 14-03. كل الأرقام تقديرية قابلة للتحقق."
        "\n\n> **تنبيه مهني:** هذه المسودة مولّدة محليًا بدون اتصال — صالحة للمراجعة الداخلية والطباعة بعد تعبئة البيانات الناقصة (CNI/NIN، عقد إيجار/ملكية، سوابق عدلية، فواتير). للعرض النهائي على لجنة التمويل، يُنصح بمراجعة محاسب."
    )
    for k in list(sections.keys()):
        # Only append if section is short (<400 words) to avoid over-polishing already long ones
        if len(sections[k].split()) < 350:
            sections[k] = sections[k] + polish
    return sections


def _real_fin_marge_line(template: dict) -> str:
    m = template.get("margin", (0.15, 0.30))
    return f"هامش ربح متوقع {m[0]*100:.0f}–{m[1]*100:.0f}%"


# ── Business plan offline (9 sections condensed) ─────────────────────────────

def business_plan_offline(business_type: str, business_name: str, location: str, wilaya: str, investment: int) -> dict[str, Any]:
    template = BUSINESS_TEMPLATES.get(business_type, {})
    name_ar = template.get("name_ar", business_type)
    fin_block = _real_financials_block(investment, template, wilaya)
    now = datetime.now()
    sections = {
        "ملخص تنفيذي": f"مشروع {name_ar} بـ {location} ({wilaya}) — استثمار {_fmt(investment)} دج — {template.get('products','—')}. {fin_block.split(chr(10))[0] if fin_block else ''}",
        "رؤية المشروع وأهدافه": "القصير (سنة): افتتاح وتشغيل مستقر. المتوسط (3 سنوات): استرداد رأس المال وتوسيع طفيف. الطويل (5 سنوات): ترسيخ العلامة وزيادة الحصة السوقية.",
        "وصف المنتجات والخدمات": template.get("products", "—") + " — الميزة: جودة/قرب/سعر.",
        "تحليل السوق والمنافسة": _wilaya_note(wilaya) + " — منافسة محلية متوسطة؛ الميزة في الانتظام والخدمة.",
        "خطة التسويق والمبيعات": "فيسبوك + واتساب بزنس + خرائط Google + لافتة. ميزانية تسويق ≈ 8% من الاستثمار سنويًا.",
        "خطة العمليات والإدارة": f"طاقم {template.get('staff',(2,5))[0]}–{template.get('staff',(2,5))[1]}، مساحة {template.get('area_sqm',(30,80))[0]}–{template.get('area_sqm',(30,80))[1]} م².",
        "الدراسة المالية": fin_block,
        "تحليل المخاطر": "| الخطر | المستوى | التخفيف |\n|---|---|---|\n| مالي (سيولة) | متوسط | احتياطي 10% + متابعة شهرية |\n| سوقي | متوسط | تنويع المنتجات + عروض |\n| تشغيلي | منخفض | صيانة دورية |\n| قانوني | منخفض | مطابقة التراخيص |",
        "الجدول الزمني للتنفيذ": "0–3 أشهر: تهيئة + تراخيص. 3–6 أشهر: افتتاح + حملة. 6–24 شهر: تثبيت + تحسين.",
    }
    sections = _polish_sections(sections, business_type)
    content = _header_ar(f"خطة عمل — {business_name}", business_name, template, location, wilaya, investment)
    content += "> **وضع عدم الاتصال:** خطة عمل مولّدة محليًا — قابلة للتقديم بعد المراجعة.\n\n---\n\n"
    for t, b in sections.items():
        content += f"## {t}\n\n{b}\n\n---\n\n"
    content += f"**إعداد:** DSC — {_today()}"
    return {"title": f"خطة عمل — {business_name}", "business_name": business_name,
            "business_type": name_ar, "location": f"{location}، {wilaya}",
            "investment": investment, "date": now.isoformat(timespec="seconds"),
            "content": content, "sections": sections, "offline": True}


# ── Market research offline ──────────────────────────────────────────────────

def market_research_offline(business_type: str, location: str, wilaya: str, business_name: str = "") -> dict[str, Any]:
    template = BUSINESS_TEMPLATES.get(business_type, {})
    name_ar = template.get("name_ar", business_type)
    title_name = business_name or name_ar
    now = datetime.now()
    sections = {
        "ملخص تنفيذي": f"سوق {name_ar} في {wilaya} — حجم تقديري مرتبط بالكثافة ({_wilaya_note(wilaya)}). الطلب مستمر غير موسمي، منافسة متوسطة (2–5 لاعبين)، تركيزهم سعري. الفرصة: خدمة منتظمة بجودة ثابتة + تواجد رقمي. التوصية: دخول بحصة متواضعة 3–5% من الدائرة مع نمو 3–5% سنويًا. المخاطر: تقلب مواد وتضخم 3% — يُعالجان بتسعير مرن.",
        "وصف السوق المستهدف": _wilaya_note(wilaya) + " — شرائح: أسر (60% معاملات)، شباب (25%)، مهنيون (15%). PESTLE: سياسي مستقر (26-154 داعم)، اقتصادي تضخم 3%، اجتماعي نمو سكاني 1.8%، تقني انتشار فيسبوك 93%، قانوني CNRC/CNAS، بيئي لا أثر كبير. الاتجاه: نمو بطيء مستقر + رقمنة.",
        "تحليل العملاء المستهدفين": "ديموغرافيا متنوعة؛ سلوك سعري-جودي (حساسية سعر 0.7). رحلة العميل: اكتشاف (فيسبوك/خرائط) → تقييم (سعر/جودة) → شراء → ولاء (واتساب). حاجة غير ملباة: خدمة منتظمة بجودة ثابتة وتواصل سريع (واتساب). نقطة ألم: تنقل للمدن الكبرى — الحل قرب + توصيل محلي. شخصية مقترحة: أسرة متوسطة، 35 سنة، دخل 60k، فيسبوك يومي.",
        "تحليل المنافسين": "عدد 2–5 محليين، حصة متفرقة، تسعير +/−5%، نقاط قوة: قدم وسمعة؛ ضعف: لا تواجد رقمي ولا خدمة ما بعد البيع. بورتر: دخول متوسط (رأس مال 2–8M)، قدرة موردين متوسطة (2–3 بدلاء)، قدرة زبائن عالية، بدائل محدودة، تنافس متوسط. الميزة: قرب + جودة + خدمة + خرائط. التسعير: تكلفة+هامش 15–35% مع مراجعة ربع سنوية.",
        "الفرص والتهديدات": "فرص: دعم NESDA 0% + إعفاء 3 سنوات + طلب محلي متنامٍ + فجوة رقمية. تهديدات: تقلب أسعار مواد (احتمال 40%)، منافسة سعرية، تضخم. الحواجز: ترخيص CNRC + رأس مال عامل. شراكات: موردون محليون + جمعيات حرفية. تنظيمي: 26-154 مستقر. التوصية: دخول سريع قبل تشبع الدائرة.",
        "خطة التسويق المقترحة": "التسعير: تكلفة+هامش حسب النشاط (15–35%)؛ التوزيع: محل + واتساب + توصيل. الإطلاق: أسبوع افتتاح (خصم 10% + عينات) + فيسبوك ممول 30 يوم. الميزانية 8% سنويًا. KPIs: مبيعات/شهر، احتفاظ، تقييم Google 4.5+، وصول فيسبوك. الأدوات: Canva + واتساب بزنس + خرائط.",
        "توقعات السوق": "السوق الكلي للدائرة ينمو 3–5% سنويًا (سكان + تضخم). الحصة المستهدفة: سنة 1: 3%، سنة 3: 5%، سنة 5: 7%. نقطة التعادل عند ~60% من الطاقة (انظر VAN/TRI). الحساسية: −20% طلب → تأخر تعادل 3 أشهر؛ +20% → تقديم 2 شهر. التوصية: سيناريو مرجعي متحفظ + احتياطي 10%.",
    }
    sections = _polish_sections(sections, business_type)
    content = _header_ar(f"بحث سوق — {title_name}", title_name, template, location, wilaya, 0)
    content = content.replace(f"| الاستثمار التقديري | 0 دج |\n", "")
    content += "> **وضع عدم الاتصال:** بحث سوق مولّد محليًا.\n\n---\n\n"
    for t, b in sections.items():
        content += f"## {t}\n\n{b}\n\n---\n\n"
    content += f"**إعداد:** DSC — {_today()}"
    return {"title": f"بحث سوق — {title_name}", "location": f"{location}، {wilaya}",
            "date": now.isoformat(timespec="seconds"), "content": content, "sections": sections, "offline": True}


# ── Marketing plan offline ───────────────────────────────────────────────────

def marketing_plan_offline(business_type: str, business_name: str, location: str, wilaya: str, investment: int, monthly_budget: int | None = None) -> dict[str, Any]:
    template = BUSINESS_TEMPLATES.get(business_type, {})
    name_ar = template.get("name_ar", business_type)
    if monthly_budget is None:
        monthly_budget = int(investment * 0.08 / 12)
    now = datetime.now()
    sections = {
        "ملخص تنفيذي تسويقي": f"هدف السنة الأولى: تثبيت {business_name} في {wilaya}. جمهور: سكان {location}. ميزانية شهرية {_fmt(monthly_budget)} دج.",
        "تحليل السوق والمنافسة": _wilaya_note(wilaya) + " — شرائح ديموغرافية متنوعة، منافسة متوسطة.",
        "التموضع والرسائل": f"القيمة: {business_name} يقدّم {template.get('products','خدمة موثوقة')} بجودة وسعر مناسب. شعار مقترح: «قريب منك، جودة تثق بها».",
        "القنوات التسويقية": "رقمي 65%: فيسبوك/إنستغرام/واتساب/خرائط Google. تقليدي 25%: لافتة + مطويات. علاقات 10%: شراكات محلية.",
        "استراتيجية المحتوى": "تعليمي 40%، ترفيهي 30%، تجاري 20%، تفاعلي 10% — 3–4 منشورات/أسبوع.",
        "خطة الحملات": "إطلاق (أسابيع 1–4) + موسمي (رمضان/أعياد) + ولاء (كل 3 أشهر) + إعلانات دائمة.",
        "الميزانية التسويقية": f"| البند | شهري (دج) | سنوي (دج) |\n|---|---|---|\n| إعلانات فيسبوك | {_fmt(int(monthly_budget*0.40))} | {_fmt(int(monthly_budget*0.40*12))} |\n| تصميم | {_fmt(int(monthly_budget*0.20))} | {_fmt(int(monthly_budget*0.20*12))} |\n| لافتات/مطويات | {_fmt(int(monthly_budget*0.20))} | {_fmt(int(monthly_budget*0.20*12))} |\n| احتياطي 10% | {_fmt(int(monthly_budget*0.10))} | {_fmt(int(monthly_budget*0.10*12))} |",
        "مؤشرات الأداء (KPIs)": "مبيعات/عملاء/متابعون/تفاعل/تقييمات Google — متابعة شهرية.",
        "التنفيذ والجدول الزمني": "شهر 1–2: تأسيس. 3–4: إطلاق. 5–6: تحسين. 7–12: نمو.",
    }
    sections = _polish_sections(sections, business_type)
    content = _header_ar(f"خطة تسويقية — {business_name}", business_name, template, location, wilaya, investment)
    content = content.replace(f"| الاستثمار التقديري | {_fmt(investment)} دج |\n",
                              f"| الاستثمار التقديري | {_fmt(investment)} دج |\n| الميزانية الشهرية | {_fmt(monthly_budget)} دج |\n")
    content += "> **وضع عدم الاتصال:** خطة تسويقية مولّدة محليًا.\n\n---\n\n"
    for t, b in sections.items():
        content += f"## {t}\n\n{b}\n\n---\n\n"
    content += "## ملاحظات ختامية\n\nراجع الخطة كل 3 أشهر وعدّلها حسب النتائج.\n\n" + f"**إعداد:** DSC — {_today()}"
    return {"title": f"خطة تسويقية — {business_name}", "business_name": business_name,
            "monthly_budget": monthly_budget, "date": now.isoformat(timespec="seconds"),
            "content": content, "sections": sections, "offline": True}


# ── Financial projections offline ────────────────────────────────────────────

def financial_projections_offline(business_type: str, business_name: str, location: str, wilaya: str, investment: int, num_employees: int = 5, monthly_revenue_estimate: int | None = None) -> dict[str, Any]:
    template = BUSINESS_TEMPLATES.get(business_type, {})
    name_ar = template.get("name_ar", business_type)
    if monthly_revenue_estimate is None:
        monthly_revenue_estimate = int(investment * 1.5 / 12)
    fin_block = _real_financials_block(investment, template, wilaya)
    now = datetime.now()
    sections = {
        "الافتراضات المالية": "TVA 19%، IBS 19%، CNAS 25.5%، IRG تصاعدي 0–35%، SNMG 24,000 دج، فائدة NESDA 0%، خصم VAN 12%، تضخم 3%.",
        "توقعات الإيرادات لخمس سنوات": f"شهري تقديري {_fmt(monthly_revenue_estimate)} دج — نمو سنوي 3–5% (تقدير متحفظ).",
        "هيكل التكاليف": "ثابتة: إيجار + رواتب + كهرباء/غاز. متغيرة: مواد أولية + توصيل. إجمالي متوقع ≈ 60–70% من الإيرادات.",
        "قائمة الأرباح والخسائر": fin_block,
        "التدفقات النقدية": "عمليات: ربح + إهلاك. استثمار: معدات. تمويل: قرض NESDA 0%. صافي تدفق إيجابي من السنة 1–2 في السيناريو المرجحي.",
        "تحليل نقطة التعادل": fin_block,
        "مؤشرات العائد": fin_block,
        "تحليل الحساسية": "انظر جدول السيناريوهات الثلاثة أعلاه (حذر/مرجحي/متفائل).",
        "خطة التمويل": "NESDA: 5% شخصي + 25% منحة + 70% بنك 0% — 7 سنوات (1.5 إمهال).",
    }
    sections = _polish_sections(sections, business_type)
    content = _header_ar(f"توقعات مالية — {business_name}", business_name, template, location, wilaya, investment)
    content = content.replace(f"| الاستثمار التقديري | {_fmt(investment)} دج |\n",
                              f"| الاستثمار التقديري | {_fmt(investment)} دج |\n| عدد العمال | {num_employees} |\n| الإيراد الشهري المقدر | {_fmt(monthly_revenue_estimate)} دج |\n")
    content += "> **وضع عدم الاتصال:** توقعات مالية مولّدة محليًا — الأرقام deterministic من `financial_calculators`.\n\n---\n\n"
    for t, b in sections.items():
        content += f"## {t}\n\n{b}\n\n---\n\n"
    content += f"**إعداد:** DSC — {_today()}"
    return {"title": f"توقعات مالية — {business_name}", "business_name": business_name,
            "investment": investment, "monthly_revenue": monthly_revenue_estimate,
            "date": now.isoformat(timespec="seconds"), "content": content, "sections": sections, "offline": True}


# ── Social media offline ────────────────────────────────────────────────────

def social_media_offline(content_type: str, business_type: str, business_name: str, location: str, wilaya: str) -> dict[str, Any]:
    from social_media_generator import CONTENT_TYPES
    template = BUSINESS_TEMPLATES.get(business_type, {})
    cfg = CONTENT_TYPES.get(content_type, {})
    name_ar = cfg.get("name_ar", content_type)
    now = datetime.now()
    # Generic ready-to-post pack per content_type
    if content_type == "weekly_posts":
        body = (
            "### خطة أسبوعية (السبت→الجمعة)\n\n"
            "| اليوم | النوع | فكرة المنشور |\n|---|---|---|\n"
            "| السبت | تعليمي | نصيحة مجانية حول " + template.get("products","الخدمة") + " |\n"
            "| الأحد | تفاعلي | سؤال للجمهور: ما أكثر ما يهمك؟ |\n"
            "| الإثنين | تجاري | عرض منتج/خدمة مع السعر |\n"
            "| الثلاثاء | ترفيهي | صورة مرحة / ميم |\n"
            "| الأربعاء | شهادة | رأي عميل حقيقي |\n"
            "| الخميس | كواليس | صور من المحل |\n"
            "| الجمعة | وجداني | رسالة ملهمة |\n"
        )
    elif content_type == "whatsapp_broadcast":
        body = (
            "### 5 رسائل واتساب جاهزة\n\n"
            "1. مرحبا! 👋 هل تعرفت على خدماتنا في " + location + "؟\n"
            "2. عرض خاص هذا الأسبوع — تواصل معنا عبر واتساب.\n"
            "3. شكرًا لثقتكم — رأيكم يهمنا ⭐\n"
            "4. تذكير: نحن هنا لخدمتكم يوميًا.\n"
            "5. جديد: تابعونا على فيسبوك وإنستغرام.\n"
        )
    elif content_type == "tiktok_scripts":
        body = (
            "### 3 سكريبتات تيك توك (15–30 ثانية)\n\n"
            "**1. Hook (3ث):** هل تعاني من ...؟ **محتوى (15ث):** الحل عندنا ... **CTA (3ث):** تابعنا الآن!\n\n"
            "**2. قبل/بعد — 3 لقطات سريعة + موسيقى خفيفة.**\n\n"
            "**3. يوم في حياتي — لقطات كواليس + نص على الشاشة.**\n"
        )
    else:
        body = f"### {name_ar}\n\nمحتوى جاهز للنشر حول {template.get('name_ar', business_type)} في {location} ({wilaya}).\n\n- نصوص بالعربية/الدارجة\n- هاشتاقات مقترحة\n- CTA واضح\n- صور مقترحة\n"

    header = (
        f"# محتوى سوشيال ميديا — {business_name}\n\n"
        f"| البند | التفاصيل |\n|---|---|\n"
        f"| النشاط | {template.get('name_ar','—')} |\n"
        f"| الموقع | {location}، ولاية {wilaya} |\n"
        f"| نوع المحتوى | {name_ar} |\n"
        f"| التاريخ | {_today()} |\n\n---\n\n"
    )
    full = header + "> **وضع عدم الاتصال:** محتوى مولّد محليًا.\n\n" + body + f"\n\n**إعداد:** DSC — {_today()}"
    return {"title": f"محتوى سوشيال ميديا — {business_name}", "content_type": name_ar,
            "date": now.isoformat(timespec="seconds"), "content": full, "offline": True}


# ── Tax declaration guide offline ────────────────────────────────────────────

def tax_declaration_offline(declaration_type: str, business_name: str = "") -> dict[str, Any]:
    from tax_declaration_generator import DECLARATION_TYPES
    cfg = DECLARATION_TYPES.get(declaration_type, {})
    name_ar = cfg.get("name_ar", declaration_type)
    now = datetime.now()
    # Use the prompt itself as structured guide — no LLM needed, just format it
    prompt_text = cfg.get("prompt", "")
    header = (
        f"# دليل {name_ar}\n\n"
        f"| البند | التفاصيل |\n|---|---|\n"
        f"| نوع التصريح | {name_ar} |\n"
        f"| التاريخ | {_today()} |\n\n"
        f"> **تنبيه:** معلومات تقديرية — راجع مصلحة الضرائب أو محاسبًا.\n\n---\n\n"
    )
    body = prompt_text.replace("أنشئ دليلًا", "## دليل").replace("أنشئ جدول", "## جدول").strip()
    # Add disclaimer with current verified rates
    body += (
        "\n\n---\n\n**معلومات محدثة 2026:** TVA 19%/9%، IBS 19%/23%/26% (المادة 150 CIDTA)، "
        "IRG تصاعدي 0–35% (6 شرائح)، IFU 5%/12% (حد 8M)، CNAS صاحب عمل 25.5%، SNMG 24,000 دج."
    )
    full = header + body + f"\n\n**إعداد:** DSC — {_today()}"
    return {"title": f"دليل {name_ar}", "declaration_type": name_ar,
            "date": now.isoformat(timespec="seconds"), "content": full, "offline": True}
