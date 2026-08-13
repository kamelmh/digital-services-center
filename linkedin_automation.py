"""LinkedIn Content Automation — auto-generate posts from generator outputs.

Takes any generator output (feasibility, business plan, etc.) and creates
ready-to-post LinkedIn content in Arabic, French, and English.
"""

from __future__ import annotations
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# ── Post Templates ────────────────────────────────────────────────────────────

POST_TEMPLATES = {
    "case_study": {
        "ar": "📊 مشروع ناجح: {title}\n\n✅ النتيجة: {result}\n💡 العبرة: {lesson}\n\n📞 تواصل معنا لبناء مشروعيك\n\n#مشاريع #جزائر #NESDA #RNI #دراسة_جدوى",
        "fr": "📊 Projet réussi : {title}\n\n✅ Résultat : {result}\n💡 Leçon : {lesson}\n\n📞 Contactez-nous pour votre projet\n\n#Projets #Algérie #NESDA #ÉtudeDeViabilité",
        "en": "📊 Success Story: {title}\n\n✅ Result: {result}\n💡 Lesson: {lesson}\n\n📞 Contact us to build your project\n\n#Startups #Algeria #NESDA #FeasibilityStudy",
    },
    "data_insight": {
        "ar": "📈 حقيقة مالية: {fact}\n\n📊 الإحصائيات: {stats}\n💡 ماذا يعني ذلك: {implication}\n\n#أرقام #مشاريع #جزائر",
        "fr": "📈 Fait financier : {fact}\n\n📊 Statistiques : {stats}\n💡 Ce que ça implique : {implication}\n\n#Finance #Business #Algérie",
        "en": "📈 Financial Fact: {fact}\n\n📊 Stats: {stats}\n💡 What this means: {implication}\n\n#Finance #Business #Algeria",
    },
    "myth_busting": {
        "ar": "❌ مفهوم خاطئ: {myth}\n\n✅ الحقيقة: {truth}\n\n📊 الدليل: {evidence}\n\n#حقيقة #مشاريع #جزائر",
        "fr": "❌ Mythe : {myth}\n\n✅ Vérité : {truth}\n\n📊 Preuve : {evidence}\n\n#Vérité #Business #Algérie",
        "en": "❌ Myth: {myth}\n\n✅ Truth: {truth}\n\n📊 Evidence: {evidence}\n\n#Truth #Business #Algeria",
    },
    "listicle": {
        "ar": "🔥 {title}\n\n{items}\n\n💬 أي نقطة تجذبك؟\n\n#نصائح #مشاريع #جزائر",
        "fr": "🔥 {title}\n\n{items}\n\n💬 Quel point vous attire ?\n\n#Conseils #Business #Algérie",
        "en": "🔥 {title}\n\n{items}\n\n💬 Which point attracts you?\n\n#Tips #Business #Algeria",
    },
    "arabic_hook": {
        "ar": "هل تعلم؟ 🤔\n\n{hook}\n\n📊 {stat}\n💡 {takeaway}\n\nشنو رأيك؟ 👇\n\n#هل_تعلم #مشاريع #جزائر",
        "fr": "Le saviez-vous ? 🤔\n\n{hook}\n\n📊 {stat}\n💡 {takeaway}\n\nVotre avis ? 👇\n\n#LeSaviezVous #Business",
        "en": "Did you know? 🤔\n\n{hook}\n\n📊 {stat}\n💡 {takeaway}\n\nWhat do you think? 👇\n\n#DidYouKnow #Business",
    },
    "generator_showcase": {
        "ar": "🛠️ أداة جديدة: {tool_name}\n\n📝 ماذا تفعل: {description}\n⚡ النتيجة: {result}\n\n🔗 جربها الآن: {link}\n\n#أدوات #مشاريع #جزائر #مجانية",
        "fr": "🛠️ Nouvel outil : {tool_name}\n\n📝 Ce qu'il fait : {description}\n⚡ Résultat : {result}\n\n🔗 Essayez maintenant : {link}\n\n#Outils #Business #Algérie",
        "en": "🛠️ New Tool: {tool_name}\n\n📝 What it does: {description}\n⚡ Result: {result}\n\n🔗 Try it now: {link}\n\n#Tools #Business #Algeria",
    },
}


# ── Market Data for Posts ─────────────────────────────────────────────────────

MARKET_DATA = {
    "retail": {
        "fact_ar": "متوسط هامش الربح في تجارة التجزئة الجزائري: 25-40%",
        "fact_fr": "Marge moyenne du commerce de détail en Algérie : 25-40%",
        "fact_en": "Average retail margin in Algeria: 25-40%",
        "stats_ar": "70% من עסקים التجزئة تحقق أرباحاً في السنة الأولى",
        "stats_fr": "70% des commerces sont rentables la première année",
        "stats_en": "70% of retail businesses are profitable in year one",
    },
    "food": {
        "fact_ar": "متوسط هامش الربح في المطاعم الجزائري: 20-35%",
        "fact_fr": "Marge moyenne des restaurants en Algérie : 20-35%",
        "fact_en": "Average restaurant margin in Algeria: 20-35%",
        "stats_ar": "80% من المطاعم تعتمد على التوصيل",
        "stats_fr": "80% des restaurants comptent sur la livraison",
        "stats_en": "80% of restaurants rely on delivery",
    },
    "digital": {
        "fact_ar": "متوسط هامش الربح في الخدمات الرقمية: 50-70%",
        "fact_fr": "Marge moyenne des services numériques : 50-70%",
        "fact_en": "Average digital services margin: 50-70%",
        "stats_ar": "الطلب على الخدمات الرقمية ي增长 30% سنوياً",
        "stats_fr": "La demande de services numériques croît de 30% par an",
        "stats_en": "Digital services demand grows 30% annually",
    },
    "construction": {
        "fact_ar": "قطاع البناء في الجزائر: 800 مليار دж/سنة",
        "fact_fr": "Secteur du bâtiment en Algérie : 800 milliards DA/an",
        "fact_en": "Construction sector in Algeria: 800B DZD/year",
        "stats_ar": "150,000 وحدة سكنية جديدة كل سنة",
        "stats_fr": "150,000 unités neuves par an",
        "stats_en": "150,000 new housing units per year",
    },
    "services": {
        "fact_ar": "متوسط هامش الربح في الخدمات: 35-55%",
        "fact_fr": "Marge moyenne des services : 35-55%",
        "fact_en": "Average services margin: 35-55%",
        "stats_ar": "القطاع الخدماتي يمثل 50% من الناتج الداخلي الخام",
        "stats_fr": "Le secteur des services représente 50% du PIB",
        "stats_en": "Services sector represents 50% of GDP",
    },
}


# ── Content Generator ─────────────────────────────────────────────────────────

class LinkedInContentGenerator:
    """Generates LinkedIn posts from generator outputs."""

    def generate_from_feasibility(self, data: dict) -> dict:
        """Generate LinkedIn post from feasibility study output."""
        biz_type = data.get("business_type", "business")
        investment = data.get("investment", 0)
        wilaya = data.get("wilaya", "Algeria")

        title = f"{biz_type.replace('_', ' ').title()} — {wilaya}"
        result = f"Étude de viabilité complète avec projections financières sur 5 ans"
        lesson = f"Un investissement de {investment:,} DZD peut générer un retour en 24 mois"

        return {
            "ar": POST_TEMPLATES["case_study"]["ar"].format(title=title, result=result, lesson=lesson),
            "fr": POST_TEMPLATES["case_study"]["fr"].format(title=title, result=result, lesson=lesson),
            "en": POST_TEMPLATES["case_study"]["en"].format(title=title, result=result, lesson=lesson),
        }

    def generate_from_business_plan(self, data: dict) -> dict:
        """Generate LinkedIn post from business plan output."""
        biz_type = data.get("business_type", "business")

        items_ar = "1️⃣ تحليل السوق المنافس\n2️⃣ استراتيجية التسويق الرقمي\n3️⃣ خطة مالية تفصيلية\n4️⃣ جدول التنفيذ"
        items_fr = "1️⃣ Analyse concurrentielle\n2️⃣ Stratégie marketing digitale\n3️⃣ Plan financier détaillé\n4️⃣ Calendrier de mise en œuvre"
        items_en = "1️⃣ Competitive analysis\n2️⃣ Digital marketing strategy\n3️⃣ Detailed financial plan\n4️⃣ Implementation timeline"

        return {
            "ar": POST_TEMPLATES["listicle"]["ar"].format(title=f"عناصر خطة العمل الناجحة لـ {biz_type}", items=items_ar),
            "fr": POST_TEMPLATES["listicle"]["fr"].format(title=f"Éléments d'un business plan réussi pour {biz_type}", items=items_fr),
            "en": POST_TEMPLATES["listicle"]["en"].format(title=f"Key elements of a winning business plan for {biz_type}", items=items_en),
        }

    def generate_from_financials(self, data: dict) -> dict:
        """Generate LinkedIn post from financial projections."""
        npv = data.get("npv", 0)
        irr = data.get("irr", 0)
        payback = data.get("payback_months", 0)

        return {
            "ar": POST_TEMPLATES["data_insight"]["ar"].format(
                fact=f" projet avec VAN = {npv:,} دج",
                stats=f"TRI = {irr:.1f}%، مدة الاسترداد = {payback} شهر",
                implication="مشروع مالي صلب بعائد جيد"
            ),
            "fr": POST_TEMPLATES["data_insight"]["fr"].format(
                fact=f"Projet avec VAN = {npv:,} DZD",
                stats=f"TRI = {irr:.1f}%, Payback = {payback} mois",
                implication="Projet financier solide avec bon retour"
            ),
            "en": POST_TEMPLATES["data_insight"]["en"].format(
                fact=f"Project with NPV = {npv:,} DZD",
                stats=f"IRR = {irr:.1f}%, Payback = {payback} months",
                implication="Solid financial project with good returns"
            ),
        }

    def generate_from_aapi(self, data: dict) -> dict:
        """Generate LinkedIn post from AAPI scoring."""
        total = data.get("total", 0)
        rating = data.get("rating", "")
        employment = data.get("employment_score", 0)

        return {
            "ar": POST_TEMPLATES["myth_busting"]["ar"].format(
                myth="دراسة الجدوى الكافية للموافقة",
                truth=f"النتيجة AAPI: {total}/1500 ({rating})",
                evidence=f"التوظيف وحده: {employment}/300 نقطة — يجب تحسين كل المعايير"
            ),
            "fr": POST_TEMPLATES["myth_busting"]["fr"].format(
                myth="L'étude de viabilité suffit pour l'approbation",
                truth=f"Score AAPI : {total}/1500 ({rating})",
                evidence=f"Emploi seul : {employment}/300 points — il faut optimiser tous les critères"
            ),
            "en": POST_TEMPLATES["myth_busting"]["en"].format(
                myth="Feasibility study alone is enough for approval",
                truth=f"AAPI Score: {total}/1500 ({rating})",
                evidence=f"Employment alone: {employment}/300 — all criteria must be optimized"
            ),
        }

    def generate_tool_showcase(self, tool_name: str, description: str, result: str, link: str = "#") -> dict:
        """Generate LinkedIn post showcasing a DSC tool."""
        return {
            "ar": POST_TEMPLATES["generator_showcase"]["ar"].format(
                tool_name=tool_name, description=description, result=result, link=link
            ),
            "fr": POST_TEMPLATES["generator_showcase"]["fr"].format(
                tool_name=tool_name, description=description, result=result, link=link
            ),
            "en": POST_TEMPLATES["generator_showcase"]["en"].format(
                tool_name=tool_name, description=description, result=result, link=link
            ),
        }

    def generate_market_insight(self, sector: str = "retail", lang: str = "ar") -> str:
        """Generate a data insight post from market data."""
        data = MARKET_DATA.get(sector, MARKET_DATA["retail"])
        hook = data.get(f"fact_{lang}", data["fact_ar"])
        stat = data.get(f"stats_{lang}", data["stats_ar"])
        takeaway = "هذا يعني أن السوق مفتوح للمشاريع الناشئة" if lang == "ar" else \
                   "Cela signifie que le marché est ouvert aux startups" if lang == "fr" else \
                   "This means the market is open to new ventures"

        template = POST_TEMPLATES["arabic_hook" if lang == "ar" else "data_insight"]
        return template[lang].format(hook=hook, stat=stat, takeaway=takeaway, fact=hook, stats=stat, implication=takeaway)

    def generate_content_calendar(self, month: int = None, year: int = None) -> list[dict]:
        """Generate a 30-day LinkedIn content calendar."""
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        topics = [
            ("case_study", "retail"),
            ("data_insight", "food"),
            ("myth_busting", "digital"),
            ("listicle", "construction"),
            ("arabic_hook", "services"),
            ("generator_showcase", None),
            ("case_study", "digital"),
            ("data_insight", "services"),
        ]

        calendar = []
        start = datetime(year, month, 1)
        for i in range(30):
            day = start + timedelta(days=i)
            if day.weekday() < 5:  # weekdays only
                topic, sector = topics[i % len(topics)]
                calendar.append({
                    "date": day.strftime("%Y-%m-%d"),
                    "day": day.strftime("%A"),
                    "topic": topic,
                    "sector": sector,
                    "time": "09:00" if i % 2 == 0 else "14:00",
                })

        return calendar

    def save_calendar(self, calendar: list[dict], output_dir: str = None):
        """Save content calendar as JSON + markdown."""
        out = Path(output_dir) if output_dir else Path(__file__).parent / "generated_output"
        out.mkdir(exist_ok=True)

        # JSON
        (out / "linkedin_calendar.json").write_text(json.dumps(calendar, indent=2, ensure_ascii=False), encoding="utf-8")

        # Markdown
        md_lines = ["# LinkedIn Content Calendar\n"]
        for post in calendar:
            md_lines.append(f"## {post['date']} ({post['day']}) — {post['time']}\n")
            md_lines.append(f"- **Topic:** {post['topic']}")
            md_lines.append(f"- **Sector:** {post['sector'] or 'N/A'}")
            md_lines.append(f"- **Action:** Write post in AR/FR/EN\n")

        (out / "linkedin_calendar.md").write_text("\n".join(md_lines), encoding="utf-8")
        return str(out)


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    gen = LinkedInContentGenerator()

    # Generate sample posts
    print("=== Sample Case Study Post (FR) ===")
    post = gen.generate_from_feasibility({"business_type": "quincaillerie", "investment": 3_000_000, "wilaya": "El Bayadh"})
    print(post["fr"])

    print("\n=== Market Insight (AR) ===")
    print(gen.generate_market_insight("digital", "ar"))

    print("\n=== Content Calendar (next 5 entries) ===")
    calendar = gen.generate_content_calendar()
    for c in calendar[:5]:
        print(f"  {c['date']} ({c['day']}) — {c['topic']} @ {c['time']}")
