"""DSC Pricing Calculator — instant quotes for all DSC services.

Calculates optimal pricing based on service type, complexity, wilaya, and client profile.
Generates WhatsApp-ready quotes with payment terms.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta


@dataclass
class PricingQuote:
    """Generated pricing quote."""
    # Services
    services: List[dict]
    # Totals
    subtotal: int
    discount_pct: float
    discount_amount: int
    total: int
    # Payment
    deposit_pct: float
    deposit_amount: int
    balance: int
    # Metadata
    validity_days: int
    estimated_delivery: str
    payment_terms: List[str]
    # WhatsApp
    whatsapp_message: str
    whatsapp_url: str


# ── Service Catalog ───────────────────────────────────────────────────────────

SERVICES = {
    # Feasibility & Studies
    "feasibility_express": {"name_fr": "Étude de viabilité Express", "name_ar": "دراسة جدوى سريعة", "price_min": 10_000, "price_max": 15_000, "delivery_days": 3, "category": "studies", "includes": ["Analyse marché", "Projections financières 3 ans", "Score AAPI"]},
    "feasibility_standard": {"name_fr": "Étude de viabilité Standard", "name_ar": "دراسة جدوى عادية", "price_min": 20_000, "price_max": 30_000, "delivery_days": 7, "category": "studies", "includes": ["9 sections complettes", "Projections 5 ans", "AAPI optimisé", "BMC"]},
    "feasibility_complete": {"name_fr": "Étude de viabilité Complète", "name_ar": "دراسة جدوى شاملة", "price_min": 40_000, "price_max": 60_000, "delivery_days": 14, "category": "studies", "includes": ["9 sections + annexes", "Projections 5 ans VAN/TRI", "AAPI 1500pts", "BMC + SWOT", "PDF professionnel"]},
    "business_plan": {"name_fr": "Business Plan", "name_ar": "خطة عمل", "price_min": 25_000, "price_max": 40_000, "delivery_days": 10, "category": "studies", "includes": ["9 chapitres", "Étude concurrentielle", "Plan financier", "Calendrier"]},
    "market_research": {"name_fr": "Étude de marché", "name_ar": "دراسة سوق", "price_min": 10_000, "price_max": 20_000, "delivery_days": 5, "category": "studies", "includes": ["Analyse marché", "Clients", "Concurrence", "Opportunités"]},
    "financial_projections": {"name_fr": "Prévisions financières", "name_ar": "توقعات مالية", "price_min": 15_000, "price_max": 25_000, "delivery_days": 5, "category": "studies", "includes": ["Compte de résultat 5 ans", "Trésorerie 5 ans", "VAN/TRI", "Seuil rentabilité"]},
    "aapi_optimized": {"name_fr": "Dossier AAPI optimisé", "name_ar": "ملف AAPI محسّن", "price_min": 75_000, "price_max": 150_000, "delivery_days": 21, "category": "studies", "includes": ["1500/1500 points cible", "Tous les critères", "Optimisation maximale", "Garde-fou"]},

    # Marketing & Digital
    "marketing_plan": {"name_fr": "Plan marketing", "name_ar": "خطة تسويقية", "price_min": 10_000, "price_max": 20_000, "delivery_days": 7, "category": "marketing", "includes": ["SWOT", "Positionnement", "Canal strategy", "Budget"]},
    "social_media_content": {"name_fr": "Contenu réseaux sociaux", "name_ar": "محتوى شبكات اجتماعية", "price_min": 5_000, "price_max": 10_000, "delivery_days": 3, "category": "marketing", "includes": ["30 posts", "Calendrier éditorial", "3 langues", "Hashtags"]},

    # CV & Documents
    "cv_french": {"name_fr": "CV professionnel français", "name_ar": "سيرة ذاتية فرنسية", "price_min": 2_000, "price_max": 4_000, "delivery_days": 1, "category": "documents", "includes": ["CV 2 pages", "Lettre de motivation", "PDF professionnel"]},
    "cover_letter": {"name_fr": "Lettre de motivation", "name_ar": "رسالة تعريفية", "price_min": 1_000, "price_max": 3_000, "delivery_days": 1, "category": "documents", "includes": ["4 templates", "Personnalisé", "PDF"]},

    # Tax & Admin (G12/G50 are the big-ticket recurring services)
    "tax_declaration": {"name_fr": "Déclarations fiscales (guides LLM)", "name_ar": "تصريحات ضريبية (أدلة)", "price_min": 3_000, "price_max": 5_000, "delivery_days": 1, "category": "admin", "includes": ["G12 guide", "G50 guide", "CNAS guide", "CASNOS guide"]},
    "g12_declaration": {"name_fr": "G12 Déclaration IFU (formulaire rempli)", "name_ar": "تصريح G12 IFU (نموذج مكتمل)", "price_min": 3_000, "price_max": 5_000, "delivery_days": 1, "category": "admin", "includes": ["Formulaire G12 rempli", "Calcul IFU", "Échéancier fractionné", "PDF"]},
    "g50_declaration": {"name_fr": "G50 Déclaration mensuelle (formulaire rempli)", "name_ar": "تصريح G50 الشهري (نموذج مكتمل)", "price_min": 5_000, "price_max": 8_000, "delivery_days": 1, "category": "admin", "includes": ["Formulaire G50 rempli", "TVA + IRG + IBS", "Récapitulatif", "PDF"]},
    "g50_retainer": {"name_fr": "Forfait mensuel G50 (TVA+IRG+IBS)", "name_ar": "اشتراك شهري G50 (TVA+IRG+IBS)", "price_min": 5_000, "price_max": 10_000, "delivery_days": 1, "category": "admin", "includes": ["Préparation mensuelle G50", "TVA nette", "IRG salaires", "Rappels deadlines"]},
    "g4_declaration": {"name_fr": "G4 Déclaration IBS annuelle (sociétés)", "name_ar": "تصريح G4 IBS السنوي (شركات)", "price_min": 8_000, "price_max": 15_000, "delivery_days": 3, "category": "admin", "includes": ["Formulaire G4 rempli", "Calcul IBS (19/23/26%)", "Bilan fiscal", "Acomptes trimestriels"]},
    "g11_declaration": {"name_fr": "G11 Déclaration BIC (régime réel)", "name_ar": "تصريح G11 BIC (نظام الحقيقي)", "price_min": 8_000, "price_max": 15_000, "delivery_days": 3, "category": "admin", "includes": ["Formulaire G11 rempli", "Calcul IRG", "Résultat fiscal", "Solde liquidation"]},
    "g29_declaration": {"name_fr": "G29/G30 Déclaration IRG salaires", "name_ar": "تصريح G29 IRG الرواتب", "price_min": 5_000, "price_max": 10_000, "delivery_days": 2, "category": "admin", "includes": ["G29 récapitulatif", "G30 état nominatif", "Calcul IRG/salarié", "Barème progressif"]},
    "g1_declaration": {"name_fr": "G1 Déclaration générale des revenus", "name_ar": "تصريح G1 الإقرار العام للدخل", "price_min": 3_000, "price_max": 6_000, "delivery_days": 2, "category": "admin", "includes": ["Formulaire G1 rempli", "Tous revenus", "Calcul IRG", "Solde payer/rembourser"]},
    "g8_declaration": {"name_fr": "G8 Déclaration d'existence", "name_ar": "تصريح G8 الإقرار بالوجود", "price_min": 2_000, "price_max": 4_000, "delivery_days": 1, "category": "admin", "includes": ["Formulaire G8 rempli", "Inscription NIF", "Engagement 30 jours"]},
    "cnas_retainer": {"name_fr": "Forfait mensuel CNAS (salariés)", "name_ar": "اشتراك شهري CNAS (موظفين)", "price_min": 5_000, "price_max": 10_000, "delivery_days": 1, "category": "admin", "includes": ["Déclaration mensuelle CNAS", "Affiliation nouveaux", "CHIFA", "Annuel"]},
    "carnet_entreprise": {"name_fr": "Pack création entreprise (SARL/AE)", "name_ar": "باقة إنشاء مؤسسة (SARL/AE)", "price_min": 15_000, "price_max": 30_000, "delivery_days": 14, "category": "admin", "includes": ["Sidjilcom inscription", "NIF", "CASNOS", "NIS", "Guide complet"]},
    "invoice_quote": {"name_fr": "Facture / Devis", "name_ar": "فاتورة / عرض سعر", "price_min": 1_500, "price_max": 3_000, "delivery_days": 1, "category": "admin", "includes": ["Facture TVA", "Devis", "PDF"]},
    "gov_paperwork": {"name_fr": "Aide paperasse administrative", "name_ar": "مساعدة إدارية", "price_min": 1_000, "price_max": 3_000, "delivery_days": 2, "category": "admin", "includes": ["ANEM", "CACI", "CNAS", "Carte grise", "Checklist"]},

    # Design & Web
    "logo_design": {"name_fr": "Design logo", "name_ar": "تصميم شعار", "price_min": 8_000, "price_max": 20_000, "delivery_days": 5, "category": "design", "includes": ["3 propositions", "SVG/PNG", "Charte graphique"]},
    "website": {"name_fr": "Site vitrine", "name_ar": "موقع إلكتروني", "price_min": 25_000, "price_max": 40_000, "delivery_days": 21, "category": "design", "includes": ["5 pages", "Responsive", "SEO", "Contact"]},
    "ecommerce": {"name_fr": "Boutique en ligne", "name_ar": "متجر إلكتروني", "price_min": 40_000, "price_max": 60_000, "delivery_days": 30, "category": "design", "includes": ["Catalogue", "Paiement", "Commandes", "Stock"]},
    "landing_page": {"name_fr": "Landing page", "name_ar": "صفحة هبوط", "price_min": 12_000, "price_max": 20_000, "delivery_days": 7, "category": "design", "includes": ["1 page", "Formulaire", "CTA", "Analytics"]},
    "social_media_mgmt": {"name_fr": "Gestion réseaux sociaux", "name_ar": "إدارة شبكات اجتماعية", "price_min": 5_000, "price_max": 10_000, "delivery_days": 30, "category": "design", "includes": ["12 posts/mois", "Community mgmt", "Rapport mensuel"]},
    "video_content": {"name_fr": "Contenu vidéo", "name_ar": "محتوى فيديو", "price_min": 5_000, "price_max": 12_000, "delivery_days": 7, "category": "design", "includes": ["3 vidéos", "Montage", "Sous-titres"]},
}

# Package deals
PACKAGES = {
    "starter": {
        "name_fr": "Pack Démarrage", "name_ar": "باقة البداية",
        "services": ["feasibility_express", "cv_french"],
        "discount": 10, "price_label": "25k-35k DZD",
    },
    "business": {
        "name_fr": "Pack Business", "name_ar": "باقة الأعمال",
        "services": ["feasibility_standard", "business_plan", "marketing_plan"],
        "discount": 15, "price_label": "50k-70k DZD",
    },
    "premium": {
        "name_fr": "Pack Premium NESDA", "name_ar": "باقة NESDA المميزة",
        "services": ["feasibility_complete", "business_plan", "marketing_plan", "social_media_content", "cv_french"],
        "discount": 20, "price_label": "80k-120k DZD",
    },
    "enterprise": {
        "name_fr": "Pack Entreprise", "name_ar": "باقة المؤسسات",
        "services": ["feasibility_complete", "aapi_optimized", "website", "logo_design"],
        "discount": 25, "price_label": "150k-250k DZD",
    },
}


# ── Calculator ────────────────────────────────────────────────────────────────

def calculate_quote(
    service_keys: List[str],
    custom_prices: dict = None,
    discount_pct: float = 0,
    deposit_pct: float = 50,
    validity_days: int = 30,
    client_name: str = "",
    client_phone: str = "",
) -> PricingQuote:
    """Calculate pricing quote for selected services."""

    custom_prices = custom_prices or {}
    services = []
    subtotal = 0

    for key in service_keys:
        svc = SERVICES.get(key)
        if svc:
            price = custom_prices.get(key, svc["price_min"])
            services.append({
                "key": key,
                "name_fr": svc["name_fr"],
                "name_ar": svc["name_ar"],
                "price": price,
                "delivery_days": svc["delivery_days"],
                "includes": svc["includes"],
            })
            subtotal += price

    discount_amount = int(subtotal * discount_pct / 100)
    total = subtotal - discount_amount
    deposit_amount = int(total * deposit_pct / 100)
    balance = total - deposit_amount

    # Estimated delivery = max delivery days across services
    max_days = max((s["delivery_days"] for s in services), default=1)
    delivery_date = (datetime.now() + timedelta(days=max_days)).strftime("%d/%m/%Y")

    # Payment terms
    payment_terms = [
        f"العربون: {deposit_amount:,} دج ({deposit_pct}%) عند البدء",
        f"المتبقي: {balance:,} دج ({100-deposit_pct}%) عند التسليم",
        f"صالح العرض: {validity_days} يوم",
    ]

    # WhatsApp message
    services_list = "\n".join(f"  ✅ {s['name_ar']} — {s['price']:,} دج" for s in services)
    whatsapp_message = (
        f"📋 عرض سعر — DSC Digital Services Center\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{services_list}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 المجموع الفرعي: {subtotal:,} دج\n"
    )
    if discount_pct > 0:
        whatsapp_message += f"🎁 الخصم: -{discount_amount:,} دج ({discount_pct}%)\n"
    whatsapp_message += (
        f"💎 الإجمالي: {total:,} دج\n"
        f"📅 التسليم المتوقع: {delivery_date}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 للتواصل: +213 676 773 892\n"
        f"📧 kamelmahi71@gmail.com"
    )

    phone_clean = client_phone.replace("+", "").replace(" ", "")
    whatsapp_url = f"https://wa.me/{phone_clean}?text={whatsapp_message}" if phone_clean else ""

    return PricingQuote(
        services=services,
        subtotal=subtotal,
        discount_pct=discount_pct,
        discount_amount=discount_amount,
        total=total,
        deposit_pct=deposit_pct,
        deposit_amount=deposit_amount,
        balance=balance,
        validity_days=validity_days,
        estimated_delivery=delivery_date,
        payment_terms=payment_terms,
        whatsapp_message=whatsapp_message,
        whatsapp_url=whatsapp_url,
    )


def format_quote_markdown(quote: PricingQuote, client_name: str = "") -> str:
    """Format quote as markdown."""
    services_rows = "\n".join(
        f"| {s['name_fr']} | {s['name_ar']} | {s['price']:,} دج | {s['delivery_days']} أيام |"
        for s in quote.services
    )

    return f"""# عرض سعر — DSC Digital Services Center

**العميل:** {client_name or '[Nom du client]'}
**التاريخ:** {datetime.now().strftime("%d/%m/%Y")}
**صالح حتى:** {(datetime.now() + timedelta(days=quote.validity_days)).strftime("%d/%m/%Y")}

---

## الخدمات
| الخدمة | الاسم | السعر | التسليم |
|--------|-------|-------|---------|
{services_rows}

## الملخص
| البند | المبلغ |
|-------|--------|
| المجموع الفرعي | {quote.subtotal:,} دج |
|{' الخصم (' + str(quote.discount_pct) + '%) | -' + str(quote.discount_amount) + ' دج |' if quote.discount_pct > 0 else ''}
| **الإجمالي** | **{quote.total:,} دج** |

## شروط الدفع
| الدفعة | المبلغ | النسبة |
|--------|--------|--------|
| العربون (عند البدء) | {quote.deposit_amount:,} دج | {quote.deposit_pct}% |
| المتبقي (عند التسليم) | {quote.balance:,} دج | {100-quote.deposit_pct}% |

## التسليم
- **التوقيت المتوقع:** {quote.estimated_delivery}
- **صيغة التسليم:** PDF + Markdown + HTML
- **الدعم:** متابعة لمدة 30 يوماً بعد التسليم

---

**DSC Digital Services Center**
📞 +213 676 773 892
📧 kamelmahi71@gmail.com
🌐 kamelmahi.netlify.app
"""


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DSC Pricing Calculator")
    parser.add_argument("--services", nargs="+", default=["feasibility_standard"], help="Service keys")
    parser.add_argument("--discount", type=float, default=0, help="Discount percentage")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    quote = calculate_quote(args.services, discount_pct=args.discount)

    print(f"Services: {len(quote.services)}")
    print(f"Subtotal: {quote.subtotal:,} DZD")
    if quote.discount_pct > 0:
        print(f"Discount: -{quote.discount_amount:,} DZD ({quote.discount_pct}%)")
    print(f"Total: {quote.total:,} DZD")
    print(f"Deposit: {quote.deposit_amount:,} DZD")
    print(f"Balance: {quote.balance:,} DZD")
    print(f"Delivery: {quote.estimated_delivery}")
    print()
    print("WhatsApp preview:")
    print(quote.whatsapp_message[:300])
