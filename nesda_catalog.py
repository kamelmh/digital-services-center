"""NESDA Activity Catalog — Searchable database of 60+ NESDA-eligible activities.

Each activity has: French name, Arabic name, sector, investment range,
AAPI priority score, required skills, equipment needs, and profitability indicators.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class NESDAActivity:
    """Single NESDA-eligible activity."""
    key: str
    name_fr: str
    name_ar: str
    sector: str
    # Investment
    investment_min: int  # DZD
    investment_max: int  # DZD
    investment_ideal: int  # DZD — sweet spot for NESDA financing
    # AAPI
    aapi_priority: int  # 1-7 (7 = highest employment score)
    aapi_activity_code: str  # Decree 26-154 section
    # Business
    monthly_revenue_min: int
    monthly_revenue_max: int
    profit_margin_pct: float  # expected margin
    staff_range: tuple  # (min, max)
    # Requirements
    skills: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    # Metadata
    difficulty: str = "medium"  # easy, medium, hard
    time_to_launch: str = "2-3 months"
    success_rate: str = "moyen"  # élevé, moyen, faible
    notes_fr: str = ""
    notes_ar: str = ""


# ── Full NESDA Activity Database ──────────────────────────────────────────────

CATALOG: dict[str, NESDAActivity] = {
    # ── INDUSTRIE ─────────────────────────────────────────────────────────────
    "boulangerie": NESDAActivity(
        key="boulangerie", name_fr="Boulangerie et pâtisserie", name_ar="مخبزة وحلويات",
        sector="industrie", investment_min=1_500_000, investment_max=5_000_000, investment_ideal=3_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-A.1",
        monthly_revenue_min=300_000, monthly_revenue_max=800_000, profit_margin_pct=25,
        staff_range=(2, 6), skills=["pâtisserie", "gestion stock"], equipment=["four", "pétrin", "formes"],
        difficulty="easy", time_to_launch="1-2 months", success_rate="élevé",
        notes_fr="Demande constante, produit de première nécessité",
    ),
    "confiserie": NESDAActivity(
        key="confiserie", name_fr="Confiserie et pâtisserie artisanale", name_ar="حلويات ومعلبات",
        sector="industrie", investment_min=1_000_000, investment_max=4_000_000, investment_ideal=2_000_000,
        aapi_priority=4, aapi_activity_code="Art.3-A.2",
        monthly_revenue_min=200_000, monthly_revenue_max=600_000, profit_margin_pct=35,
        staff_range=(1, 4), skills=["confiserie", "emballage"], equipment=["marmite", "balance", "emballage"],
        difficulty="medium", time_to_launch="1-2 months", success_rate="élevé",
    ),
    "biscuits": NESDAActivity(
        key="biscuits", name_fr="Fabrication de biscuits", name_ar="تصنيع البسكويت",
        sector="industrie", investment_min=2_000_000, investment_max=8_000_000, investment_ideal=4_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-A.3",
        monthly_revenue_min=400_000, monthly_revenue_max=1_200_000, profit_margin_pct=30,
        staff_range=(3, 8), skills=["boulangerie", "emballage", "distribution"], equipment=["four industriel", "mixeur", "packaging"],
        difficulty="medium", time_to_launch="2-3 months", success_rate="moyen",
    ),
    "cafe_torréfaction": NESDAActivity(
        key="cafe_torréfaction", name_fr="Torréfaction de café", name_ar="تحمير القهوة",
        sector="industrie", investment_min=1_500_000, investment_max=6_000_000, investment_ideal=3_000_000,
        aapi_priority=4, aapi_activity_code="Art.3-A.4",
        monthly_revenue_min=300_000, monthly_revenue_max=900_000, profit_margin_pct=40,
        staff_range=(1, 3), skills=["torréfaction", "marketing"], equipment=["torréfacteur", "broyeur", "emballage"],
        difficulty="medium", time_to_launch="1-2 months", success_rate="élevé",
        notes_fr="Forte marge, tendance café artisanal en hausse",
    ),
    "pates_alimentaires": NESDAActivity(
        key="pates_alimentaires", name_fr="Pâtes alimentaires", name_ar="معكرونة",
        sector="industrie", investment_min=2_000_000, investment_max=10_000_000, investment_ideal=5_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-A.5",
        monthly_revenue_min=500_000, monthly_revenue_max=1_500_000, profit_margin_pct=25,
        staff_range=(3, 10), skills=["production", "emballage"], equipment=["extrudeuse", "séchoir", "packaging"],
        difficulty="hard", time_to_launch="3-4 months", success_rate="moyen",
    ),
    "boissons": NESDAActivity(
        key="boissons", name_fr="Boissons gazeuses et jus", name_ar="مشروبات غازية وعصائر",
        sector="industrie", investment_min=3_000_000, investment_max=15_000_000, investment_ideal=7_000_000,
        aapi_priority=6, aapi_activity_code="Art.3-A.6",
        monthly_revenue_min=800_000, monthly_revenue_max=3_000_000, profit_margin_pct=35,
        staff_range=(5, 15), skills=["production", "distribution", "marketing"], equipment=["ligne de remplissage", "broyeur", "étiqueteuse"],
        difficulty="hard", time_to_launch="3-6 months", success_rate="moyen",
        notes_fr="Volume élevé, nécessite investissement important",
    ),
    "eau": NESDAActivity(
        key="eau", name_fr="Production d'eau en bouteille", name_ar="إنتاج الماء المعبأ",
        sector="industrie", investment_min=5_000_000, investment_max=20_000_000, investment_ideal=10_000_000,
        aapi_priority=6, aapi_activity_code="Art.3-A.7",
        monthly_revenue_min=1_000_000, monthly_revenue_max=4_000_000, profit_margin_pct=30,
        staff_range=(5, 20), skills=["production", "distribution"], equipment=["ligne eau", "UV", "emballage"],
        difficulty="hard", time_to_launch="4-6 months", success_rate="moyen",
    ),
    "vetements_homme": NESDAActivity(
        key="vetements_homme", name_fr="Vêtements pour hommes", name_ar="ملابس رجالية",
        sector="industrie", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=5, aapi_activity_code="Art.3-B.1",
        monthly_revenue_min=300_000, monthly_revenue_max=1_000_000, profit_margin_pct=40,
        staff_range=(2, 6), skills=["couture", "design", "vente"], equipment=["machines à coudre", "découpe", "fer à repasser"],
        difficulty="medium", time_to_launch="1-2 months", success_rate="élevé",
    ),
    "vetements_femme": NESDAActivity(
        key="vetements_femme", name_fr="Vêtements pour femmes", name_ar="ملابس نسائية",
        sector="industrie", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=5, aapi_activity_code="Art.3-B.2",
        monthly_revenue_min=300_000, monthly_revenue_max=1_200_000, profit_margin_pct=45,
        staff_range=(2, 6), skills=["couture", "design", "vente"], equipment=["machines à coudre", "découpe", "moulages"],
        difficulty="medium", time_to_launch="1-2 months", success_rate="élevé",
    ),
    "vetements_enfant": NESDAActivity(
        key="vetements_enfant", name_fr="Vêtements pour bébés", name_ar="ملابس حديثي الولادة",
        sector="industrie", investment_min=800_000, investment_max=4_000_000, investment_ideal=2_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-B.3",
        monthly_revenue_min=200_000, monthly_revenue_max=800_000, profit_margin_pct=50,
        staff_range=(1, 4), skills=["couture", "design"], equipment=["machines à coudre", "découpe"],
        difficulty="easy", time_to_launch="1 month", success_rate="élevé",
        notes_fr="Forte marge, demande constante",
    ),
    "vetements_maison": NESDAActivity(
        key="vetements_maison", name_fr="Vêtements de maison / pyjamas", name_ar="ملابس منزلية",
        sector="industrie", investment_min=800_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=4, aapi_activity_code="Art.3-B.4",
        monthly_revenue_min=200_000, monthly_revenue_max=600_000, profit_margin_pct=35,
        staff_range=(1, 3), skills=["couture"], equipment=["machines à coudre"],
        difficulty="easy", time_to_launch="1 month", success_rate="élevé",
    ),
    "vetements_travail": NESDAActivity(
        key="vetements_travail", name_fr="Vêtements de travail /uniformes", name_ar="ملابس عمل وزي موحد",
        sector="industrie", investment_min=1_500_000, investment_max=6_000_000, investment_ideal=3_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-B.5",
        monthly_revenue_min=400_000, monthly_revenue_max=1_200_000, profit_margin_pct=35,
        staff_range=(2, 5), skills=["couture", "broderie", "vente B2B"], equipment=["machines à coudre", "broderie"],
        difficulty="medium", time_to_launch="2 months", success_rate="élevé",
        notes_fr="Clientèle B2B stable (entreprises, hôpitaux)",
    ),
    "accessoires": NESDAActivity(
        key="accessoires", name_fr="Accessoires (ceintures, cravates, etc.)", name_ar="إكسسوارات (أحزمة، ربطة عنق)",
        sector="industrie", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=3, aapi_activity_code="Art.3-B.6",
        monthly_revenue_min=150_000, monthly_revenue_max=500_000, profit_margin_pct=55,
        staff_range=(1, 3), skills=["couture", "design", "vente"], equipment=["machines à coudre", "découpe cuir"],
        difficulty="easy", time_to_launch="1 month", success_rate="moyen",
    ),
    "sacs": NESDAActivity(
        key="sacs", name_fr="Sacs et valises", name_ar="حقائب وأكياس",
        sector="industrie", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=4, aapi_activity_code="Art.3-B.7",
        monthly_revenue_min=250_000, monthly_revenue_max=800_000, profit_margin_pct=40,
        staff_range=(2, 5), skills=["couture", "design"], equipment=["machines à coudre", "découpe"],
        difficulty="medium", time_to_launch="2 months", success_rate="moyen",
    ),
    "meubles": NESDAActivity(
        key="meubles", name_fr="Fabrication de meubles", name_ar="صناعة الأثاث",
        sector="industrie", investment_min=2_000_000, investment_max=10_000_000, investment_ideal=5_000_000,
        aapi_priority=6, aapi_activity_code="Art.3-C.1",
        monthly_revenue_min=500_000, monthly_revenue_max=2_000_000, profit_margin_pct=35,
        staff_range=(3, 10), skills=["menuiserie", "design", "vente"], equipment=["scie", "ponceuse", "visseuse"],
        difficulty="medium", time_to_launch="2-3 months", success_rate="élevé",
    ),
    "matelas": NESDAActivity(
        key="matelas", name_fr="Matelas et literie", name_ar="فراش وأسرّة",
        sector="industrie", investment_min=1_500_000, investment_max=6_000_000, investment_ideal=3_000_000,
        aapi_priority=4, aapi_activity_code="Art.3-C.2",
        monthly_revenue_min=300_000, monthly_revenue_max=1_000_000, profit_margin_pct=40,
        staff_range=(2, 6), skills=["couture matelas", "vente"], equipment=["machine à matelas", "mousse"],
        difficulty="medium", time_to_launch="1-2 months", success_rate="élevé",
    ),
    "imprimerie": NESDAActivity(
        key="imprimerie", name_fr="Imprimerie et reproduction", name_ar="مطبعة وتنقيس",
        sector="industrie", investment_min=3_000_000, investment_max=15_000_000, investment_ideal=7_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-D.1",
        monthly_revenue_min=500_000, monthly_revenue_max=2_000_000, profit_margin_pct=30,
        staff_range=(3, 8), skills=["imprimerie", "design", "vente"], equipment=["imprimante", "découpe", " reliure"],
        difficulty="hard", time_to_launch="3 months", success_rate="moyen",
    ),
    "jouets": NESDAActivity(
        key="jouets", name_fr="Fabrication de jouets", name_ar="صناعة الألعاب",
        sector="industrie", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=4, aapi_activity_code="Art.3-E.1",
        monthly_revenue_min=200_000, monthly_revenue_max=700_000, profit_margin_pct=45,
        staff_range=(1, 4), skills=["fabrication", "design"], equipment=["injection plastique", "outillage"],
        difficulty="medium", time_to_launch="2 months", success_rate="moyen",
    ),
    "caisses_carton": NESDAActivity(
        key="caisses_carton", name_fr="Caisses en carton / emballage", name_ar="كوابس كرتون / تغليف",
        sector="industrie", investment_min=2_000_000, investment_max=8_000_000, investment_ideal=4_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-E.2",
        monthly_revenue_min=400_000, monthly_revenue_max=1_200_000, profit_margin_pct=25,
        staff_range=(3, 8), skills=["production", "vente B2B"], equipment=["machine carton", "découpe", "agrafeuse"],
        difficulty="medium", time_to_launch="2 months", success_rate="élevé",
        notes_fr="Forte demande B2B (industries, exportateurs)",
    ),
    "peau_mouton": NESDAActivity(
        key="peau_mouton", name_fr="Travail du cuir / peaux", name_ar="دباغة وصناعة الجلود",
        sector="industrie", investment_min=1_500_000, investment_max=6_000_000, investment_ideal=3_000_000,
        aapi_priority=4, aapi_activity_code="Art.3-F.1",
        monthly_revenue_min=300_000, monthly_revenue_max=900_000, profit_margin_pct=35,
        staff_range=(2, 5), skills=["cordonnerie", "design"], equipment=["machine à coudre cuir", "outillage"],
        difficulty="medium", time_to_launch="2 months", success_rate="moyen",
    ),
    "ceramique": NESDAActivity(
        key="ceramique", name_fr="Céramique et carrelage artisanal", name_ar="سيراميك وفخار تقليدي",
        sector="industrie", investment_min=2_000_000, investment_max=8_000_000, investment_ideal=4_000_000,
        aapi_priority=4, aapi_activity_code="Art.3-F.2",
        monthly_revenue_min=300_000, monthly_revenue_max=1_000_000, profit_margin_pct=40,
        staff_range=(2, 6), skills=["céramique", "design"], equipment=["four céramique", "tour", "outillage"],
        difficulty="hard", time_to_launch="3 months", success_rate="moyen",
    ),
    "jalousies": NESDAActivity(
        key="jalousies", name_fr="Jalousies et portes en aluminium", name_ar="شُرُف وأبواب ألومنيوم",
        sector="industrie", investment_min=2_000_000, investment_max=8_000_000, investment_ideal=4_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-F.3",
        monthly_revenue_min=400_000, monthly_revenue_max=1_500_000, profit_margin_pct=30,
        staff_range=(2, 6), skills=["menuiserie aluminium", "vente"], equipment=["scie aluminium", "visseuse", "perceuse"],
        difficulty="medium", time_to_launch="2 months", success_rate="élevé",
    ),
    "decoration": NESDAActivity(
        key="decoration", name_fr="Décoration intérieure et aménagement", name_ar="ديكور داخلي وتزيين",
        sector="industrie", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=3, aapi_activity_code="Art.3-F.4",
        monthly_revenue_min=300_000, monthly_revenue_max=1_000_000, profit_margin_pct=45,
        staff_range=(1, 4), skills=["design", "peinture", "plâtrerie"], equipment=["outillage peinture", "échafaudage"],
        difficulty="medium", time_to_launch="1-2 months", success_rate="élevé",
    ),
    "plastique": NESDAActivity(
        key="plastique", name_fr="Plastique thermoformé / injection", name_ar="بلاستيك مصبّغ",
        sector="industrie", investment_min=3_000_000, investment_max=15_000_000, investment_ideal=7_000_000,
        aapi_priority=6, aapi_activity_code="Art.3-F.5",
        monthly_revenue_min=600_000, monthly_revenue_max=2_500_000, profit_margin_pct=30,
        staff_range=(4, 10), skills=["production", "maintenance"], equipment=["injecteur", "thermoformeuse"],
        difficulty="hard", time_to_launch="3-4 months", success_rate="moyen",
    ),
    "articles_menager": NESDAActivity(
        key="articles_menager", name_fr="Articles ménagers en plastique", name_ar="أدوات منزلية بلاستيكية",
        sector="industrie", investment_min=2_000_000, investment_max=8_000_000, investment_ideal=4_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-F.6",
        monthly_revenue_min=400_000, monthly_revenue_max=1_500_000, profit_margin_pct=35,
        staff_range=(3, 8), skills=["production", "vente"], equipment=["injecteur", "moules"],
        difficulty="medium", time_to_launch="2-3 months", success_rate="moyen",
    ),
    "souvenirs": NESDAActivity(
        key="souvenirs", name_fr="Articles de souvenirs et souvenirs touristiques", name_ar="هدايا تذكارية",
        sector="industrie", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=3, aapi_activity_code="Art.3-F.7",
        monthly_revenue_min=100_000, monthly_revenue_max=400_000, profit_margin_pct=50,
        staff_range=(1, 3), skills=["design", "artisanat", "vente"], equipment=["outillage artisanal"],
        difficulty="easy", time_to_launch="1 month", success_rate="moyen",
    ),
    "glacon": NESDAActivity(
        key="glacon", name_fr="Production de glaçons", name_ar="إنتاج الثلج",
        sector="industrie", investment_min=1_000_000, investment_max=4_000_000, investment_ideal=2_000_000,
        aapi_priority=3, aapi_activity_code="Art.3-G.1",
        monthly_revenue_min=150_000, monthly_revenue_max=500_000, profit_margin_pct=40,
        staff_range=(1, 3), skills=["production"], equipment=["machine à glaçons", "froid"],
        difficulty="easy", time_to_launch="1 month", success_rate="élevé",
        notes_fr="Très faible investissement, revenus stables",
    ),
    "souk_cases": NESDAActivity(
        key="souk_cases", name_fr="Souches de ciment / briques", name_ar="بلوك أسمنتي / طوب",
        sector="industrie", investment_min=2_000_000, investment_max=8_000_000, investment_ideal=4_000_000,
        aapi_priority=5, aapi_activity_code="Art.3-G.2",
        monthly_revenue_min=500_000, monthly_revenue_max=2_000_000, profit_margin_pct=20,
        staff_range=(4, 10), skills=["production", "vente B2B"], equipment=["machine bloc", "vibrateur", "cure"],
        difficulty="medium", time_to_launch="2 months", success_rate="élevé",
        notes_fr="Demande constante du BTP",
    ),
    "verrerie": NESDAActivity(
        key="verrerie", name_fr="Verrerie artisanale", name_ar="زجاج يدوي",
        sector="industrie", investment_min=1_500_000, investment_max=6_000_000, investment_ideal=3_000_000,
        aapi_priority=3, aapi_activity_code="Art.3-G.3",
        monthly_revenue_min=200_000, monthly_revenue_max=700_000, profit_margin_pct=45,
        staff_range=(1, 4), skills=["verrerie", "design"], equipment=["four verrerie", "outillage"],
        difficulty="hard", time_to_launch="3 months", success_rate="moyen",
    ),
    # ── AGRICULTURE ───────────────────────────────────────────────────────────
    "elevage_bovins": NESDAActivity(
        key="elevage_bovins", name_fr="Élevage de bovins (vaches laitières)", name_ar="تربية الأبقار (حليب)",
        sector="agriculture", investment_min=3_000_000, investment_max=15_000_000, investment_ideal=7_000_000,
        aapi_priority=6, aapi_activity_code="Art.4-A.1",
        monthly_revenue_min=500_000, monthly_revenue_max=2_000_000, profit_margin_pct=25,
        staff_range=(2, 6), skills=["élevage", "gestion troupeau"], equipment=["étable", "traite", "froid"],
        difficulty="hard", time_to_launch="3-6 months", success_rate="moyen",
        notes_fr="Investissement élevé, revenus stables (lait + viande)",
    ),
    "elevage_ovins": NESDAActivity(
        key="elevage_ovins", name_fr="Élevage d'ovins (moutons et chèvres)", name_ar="تربية الأغنام والماعز",
        sector="agriculture", investment_min=1_000_000, investment_max=6_000_000, investment_ideal=3_000_000,
        aapi_priority=5, aapi_activity_code="Art.4-A.2",
        monthly_revenue_min=200_000, monthly_revenue_max=800_000, profit_margin_pct=30,
        staff_range=(1, 4), skills=["élevage", "pâturage"], equipment=["bergerie", "abreuvoir"],
        difficulty="medium", time_to_launch="2-3 months", success_rate="élevé",
    ),
    "poulet": NESDAActivity(
        key="poulet", name_fr="Élevage de poulets (chair et œufs)", name_ar="تربية الدجاج (لحوم وبياض)",
        sector="agriculture", investment_min=2_000_000, investment_max=10_000_000, investment_ideal=5_000_000,
        aapi_priority=6, aapi_activity_code="Art.4-A.3",
        monthly_revenue_min=500_000, monthly_revenue_max=2_000_000, profit_margin_pct=20,
        staff_range=(2, 6), skills=["aviculture", "sanitaire"], equipment=["poulailler", "abreuvoir", "mangeoire"],
        difficulty="medium", time_to_launch="2 months", success_rate="élevé",
    ),
    "apiculture": NESDAActivity(
        key="apiculture", name_fr="Apiculture (miel et produits)", name_ar="تربية النحل (عسل ومنتجات)",
        sector="agriculture", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=4, aapi_activity_code="Art.4-A.4",
        monthly_revenue_min=100_000, monthly_revenue_max=500_000, profit_margin_pct=55,
        staff_range=(1, 2), skills=["apiculture", "conditionnement"], equipment=["ruches", "extracteur", " pots"],
        difficulty="medium", time_to_launch="3-6 months", success_rate="élevé",
        notes_fr="Très forte marge, miel bio très demandé",
    ),
    "pisciculture": NESDAActivity(
        key="pisciculture", name_fr="Pisciculture (élevage de poissons)", name_ar="تربية الأسماك",
        sector="agriculture", investment_min=2_000_000, investment_max=10_000_000, investment_ideal=5_000_000,
        aapi_priority=5, aapi_activity_code="Art.4-A.5",
        monthly_revenue_min=300_000, monthly_revenue_max=1_500_000, profit_margin_pct=30,
        staff_range=(2, 5), skills=["pisciculture", "qualité eau"], equipment=["bassin", "aérateur", "aliment"],
        difficulty="hard", time_to_launch="3-6 months", success_rate="moyen",
    ),
    "marechellerie": NESDAActivity(
        key="marechellerie", name_fr="Maréchellerie (petits animaux)", name_ar="تربية الحيوانات الصغيرة",
        sector="agriculture", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=3, aapi_activity_code="Art.4-A.6",
        monthly_revenue_min=100_000, monthly_revenue_max=400_000, profit_margin_pct=35,
        staff_range=(1, 2), skills=["élevage"], equipment=["écurie", "alimentation"],
        difficulty="easy", time_to_launch="1-2 months", success_rate="moyen",
    ),
    # ── SERVICES ──────────────────────────────────────────────────────────────
    "formation_informatique": NESDAActivity(
        key="formation_informatique", name_fr="Centre de formation en informatique", name_ar="مركز تكوين في المعلوماتية",
        sector="services", investment_min=2_000_000, investment_max=8_000_000, investment_ideal=4_000_000,
        aapi_priority=6, aapi_activity_code="Art.5-A.1",
        monthly_revenue_min=400_000, monthly_revenue_max=1_500_000, profit_margin_pct=40,
        staff_range=(2, 6), skills=["informatique", "pédagogie", "marketing"], equipment=["PC", "vidéoprojecteur", "climatisation"],
        difficulty="medium", time_to_launch="2 months", success_rate="élevé",
        notes_fr="Très forte demande, jeunes diplômés en quête de compétences",
    ),
    "formation_langues": NESDAActivity(
        key="formation_langues", name_fr="Formation en langues (anglais, français)", name_ar="تكوين في اللغات (إنجليزي، فرنسي)",
        sector="services", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=5, aapi_activity_code="Art.5-A.2",
        monthly_revenue_min=300_000, monthly_revenue_max=1_000_000, profit_margin_pct=45,
        staff_range=(2, 5), skills=["langues", "pédagogie"], equipment=["salle classe", "vidéoprojecteur"],
        difficulty="medium", time_to_launch="1-2 months", success_rate="élevé",
    ),
    "centre_marketing": NESDAActivity(
        key="centre_marketing", name_fr="Centre de marketing numérique", name_ar="مركز التسويق الرقمي",
        sector="services", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=5, aapi_activity_code="Art.5-A.3",
        monthly_revenue_min=300_000, monthly_revenue_max=1_200_000, profit_margin_pct=50,
        staff_range=(2, 5), skills=["marketing digital", "réseaux sociaux", "vente"], equipment=["PC", "caméra", "logiciels"],
        difficulty="medium", time_to_launch="1 month", success_rate="élevé",
    ),
    "coiffure": NESDAActivity(
        key="coiffure", name_fr="Salon de coiffure et barbier", name_ar="صالون حلاقة وتشذيب",
        sector="services", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=4, aapi_activity_code="Art.5-B.1",
        monthly_revenue_min=200_000, monthly_revenue_max=600_000, profit_margin_pct=45,
        staff_range=(1, 4), skills=["coiffure", "barbier"], equipment=["fauteuil", "shampoing", "sèche-cheveux"],
        difficulty="easy", time_to_launch="1 month", success_rate="élevé",
        notes_fr="Très faible investissement, revenus rapides",
    ),
    "esthetique": NESDAActivity(
        key="esthetique", name_fr="Institut de beauté / soins", name_ar="معهد التجميل والعناية",
        sector="services", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=4, aapi_activity_code="Art.5-B.2",
        monthly_revenue_min=250_000, monthly_revenue_max=800_000, profit_margin_pct=50,
        staff_range=(1, 4), skills=["esthétique", "soins"], equipment=["lit", "produits", "appareils"],
        difficulty="easy", time_to_launch="1-2 months", success_rate="élevé",
    ),
    "repetiteur": NESDAActivity(
        key="repetiteur", name_fr="Répétiteur à domicile / soutien scolaire", name_ar="مدرس خصوصي / دعم مدرسي",
        sector="services", investment_min=200_000, investment_max=1_000_000, investment_ideal=500_000,
        aapi_priority=3, aapi_activity_code="Art.5-B.3",
        monthly_revenue_min=100_000, monthly_revenue_max=400_000, profit_margin_pct=80,
        staff_range=(1, 2), skills=["enseignement", "pédagogie"], equipment=["supports pédagogiques"],
        difficulty="easy", time_to_launch="1 week", success_rate="élevé",
        notes_fr="Investissement minimal, très forte demande",
    ),
    "comptable": NESDAActivity(
        key="comptable", name_fr="Bureau comptable / comptabilité", name_ar="مكتب محاسبة",
        sector="services", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=4, aapi_activity_code="Art.5-B.4",
        monthly_revenue_min=200_000, monthly_revenue_max=700_000, profit_margin_pct=55,
        staff_range=(1, 3), skills=["comptabilité", "fiscalité"], equipment=["PC", "logiciel comptable"],
        difficulty="medium", time_to_launch="1 month", success_rate="élevé",
    ),
    "couture": NESDAActivity(
        key="couture", name_fr="Atelier de couture / confection", name_ar="ورشة خياطة وتفصيل",
        sector="services", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=4, aapi_activity_code="Art.5-C.1",
        monthly_revenue_min=150_000, monthly_revenue_max=500_000, profit_margin_pct=45,
        staff_range=(1, 4), skills=["couture", "design"], equipment=["machines à coudre", "découpe"],
        difficulty="easy", time_to_launch="1 month", success_rate="élevé",
    ),
    # ── NUMÉRIQUE / IT ────────────────────────────────────────────────────────
    "developpement_web": NESDAActivity(
        key="developpement_web", name_fr="Développement web et mobile", name_ar="تطوير المواقع والتطبيقات",
        sector="numérique", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=6, aapi_activity_code="Art.6-A.1",
        monthly_revenue_min=300_000, monthly_revenue_max=1_500_000, profit_margin_pct=65,
        staff_range=(1, 4), skills=["HTML/CSS", "JavaScript", "Python", "marketing"], equipment=["PC performant", "internet fibre"],
        difficulty="medium", time_to_launch="1 month", success_rate="élevé",
        notes_fr="Très forte marge, clients B2B potentiels",
    ),
    "maintenance_informatique": NESDAActivity(
        key="maintenance_informatique", name_fr="Maintenance et réparation informatique", name_ar="صيانة وإصلاح الحواسيب",
        sector="numérique", investment_min=500_000, investment_max=3_000_000, investment_ideal=1_500_000,
        aapi_priority=5, aapi_activity_code="Art.6-A.2",
        monthly_revenue_min=200_000, monthly_revenue_max=700_000, profit_margin_pct=50,
        staff_range=(1, 3), skills=["hardware", "software", "réseaux"], equipment=["outillage", "pièces détachées"],
        difficulty="easy", time_to_launch="1 month", success_rate="élevé",
    ),
    "photographie": NESDAActivity(
        key="photographie", name_fr="Photographie et production vidéo", name_ar="تصوير فوتوغرافي وإنتاج فيديو",
        sector="numérique", investment_min=1_000_000, investment_max=5_000_000, investment_ideal=2_500_000,
        aapi_priority=4, aapi_activity_code="Art.6-A.3",
        monthly_revenue_min=200_000, monthly_revenue_max=800_000, profit_margin_pct=50,
        staff_range=(1, 3), skills=["photographie", "montage", "marketing"], equipment=["appareil photo", "trépied", "logiciel"],
        difficulty="medium", time_to_launch="1 month", success_rate="moyen",
    ),
    "graphisme": NESDAActivity(
        key="graphisme", name_fr="Graphisme et design graphique", name_ar="تصميم جرافيك",
        sector="numérique", investment_min=300_000, investment_max=2_000_000, investment_ideal=1_000_000,
        aapi_priority=4, aapi_activity_code="Art.6-A.4",
        monthly_revenue_min=150_000, monthly_revenue_max=600_000, profit_margin_pct=70,
        staff_range=(1, 3), skills=["Photoshop", "Illustrator", "design"], equipment=["PC performant", " tablette graphique"],
        difficulty="easy", time_to_launch="2 weeks", success_rate="élevé",
        notes_fr="Très forte marge, investissement minimal",
    ),
    "marketing_digital": NESDAActivity(
        key="marketing_digital", name_fr="Marketing digital / community management", name_ar="التسويق الرقمي وإدارة المجتمعات",
        sector="numérique", investment_min=300_000, investment_max=2_000_000, investment_ideal=1_000_000,
        aapi_priority=5, aapi_activity_code="Art.6-A.5",
        monthly_revenue_min=200_000, monthly_revenue_max=800_000, profit_margin_pct=65,
        staff_range=(1, 3), skills=["marketing digital", "réseaux sociaux", "vente"], equipment=["PC", "internet"],
        difficulty="easy", time_to_launch="2 weeks", success_rate="élevé",
    ),
    # ── ENVIRONNEMENT ─────────────────────────────────────────────────────────
    "solaire": NESDAActivity(
        key="solaire", name_fr="Installation et maintenance solaire", name_ar="تركيب وصيانة الطاقة الشمسية",
        sector="environnement", investment_min=2_000_000, investment_max=10_000_000, investment_ideal=5_000_000,
        aapi_priority=6, aapi_activity_code="Art.7-A.1",
        monthly_revenue_min=500_000, monthly_revenue_max=2_000_000, profit_margin_pct=30,
        staff_range=(2, 6), skills=["électricité", "solaire", "vente"], equipment=["panneaux", "onduleurs", "outillage"],
        difficulty="medium", time_to_launch="2 months", success_rate="élevé",
        notes_fr="Forte demande subventionnée CAGEX",
    ),
    "recyclage": NESDAActivity(
        key="recyclage", name_fr="Recyclage des déchets / tri", name_ar="إعادة تدوير النفايات وفرزها",
        sector="environnement", investment_min=2_000_000, investment_max=10_000_000, investment_ideal=5_000_000,
        aapi_priority=6, aapi_activity_code="Art.7-A.2",
        monthly_revenue_min=300_000, monthly_revenue_max=1_500_000, profit_margin_pct=25,
        staff_range=(3, 8), skills=["tri", "logistique", "vente"], equipment=["broyeur", "presse", "camion"],
        difficulty="medium", time_to_launch="2-3 months", success_rate="moyen",
    ),
    "eau_usee": NESDAActivity(
        key="eau_usee", name_fr="Traitement des eaux usées", name_ar="معالجة المياه العادمة",
        sector="environnement", investment_min=3_000_000, investment_max=15_000_000, investment_ideal=7_000_000,
        aapi_priority=5, aapi_activity_code="Art.7-A.3",
        monthly_revenue_min=400_000, monthly_revenue_max=2_000_000, profit_margin_pct=30,
        staff_range=(3, 8), skills=["traitement eau", "maintenance"], equipment=["station traitement", "pompes"],
        difficulty="hard", time_to_launch="3-4 months", success_rate="moyen",
    ),
}

SECTORS = {
    "industrie": {"fr": "Industrie / Manufacturing", "ar": "الصناعات التحويلية", "count": 26, "color": "#1565c0"},
    "agriculture": {"fr": "Agriculture / Élevage", "ar": "الفلاحة وتربية الحيوان", "count": 6, "color": "#2e7d32"},
    "services": {"fr": "Services", "ar": "الخدمات", "count": 7, "color": "#7b1fa2"},
    "numérique": {"fr": "Numérique / IT", "ar": "المعلوماتية والتقنيات الرقمية", "count": 5, "color": "#e65100"},
    "environnement": {"fr": "Environnement", "ar": "البيئة والطاقة المتجددة", "count": 3, "color": "#00838f"},
}


# ── Search Functions ──────────────────────────────────────────────────────────

def search_catalog(query: str = "", sector: str = None, min_investment: int = None,
                   max_investment: int = None, difficulty: str = None) -> list[NESDAActivity]:
    """Search NESDA activities with filters."""
    results = list(CATALOG.values())

    if query:
        q = query.lower()
        results = [a for a in results if q in a.name_fr.lower() or q in a.name_ar or q in a.key.lower()]

    if sector:
        results = [a for a in results if a.sector == sector]

    if min_investment is not None:
        results = [a for a in results if a.investment_min <= min_investment <= a.investment_max]

    if max_investment is not None:
        results = [a for a in results if a.investment_min <= max_investment and a.investment_max >= max_investment]

    if difficulty:
        results = [a for a in results if a.difficulty == difficulty]

    return sorted(results, key=lambda a: (a.aapi_priority, -a.investment_ideal), reverse=True)


def get_sector_stats(sector: str) -> dict:
    """Get statistics for a sector."""
    activities = [a for a in CATALOG.values() if a.sector == sector]
    if not activities:
        return {}
    investments = [a.investment_ideal for a in activities]
    margins = [a.profit_margin_pct for a in activities]
    return {
        "count": len(activities),
        "avg_investment": sum(investments) // len(investments),
        "min_investment": min(investments),
        "max_investment": max(investments),
        "avg_margin": sum(margins) / len(margins),
        "high_priority": sum(1 for a in activities if a.aapi_priority >= 5),
    }


def recommend_activity(budget: int, skills: list[str] = None, sector_pref: str = None) -> list[NESDAActivity]:
    """Recommend activities based on budget and skills."""
    candidates = [a for a in CATALOG.values() if a.investment_min <= budget <= a.investment_max * 1.5]

    if skills:
        def skill_score(a):
            return sum(1 for s in skills if any(s.lower() in sk.lower() for sk in a.skills))
        candidates.sort(key=lambda a: (a.aapi_priority, skill_score(a), a.profit_margin_pct), reverse=True)
    else:
        candidates.sort(key=lambda a: (a.aapi_priority, a.profit_margin_pct), reverse=True)

    if sector_pref:
        sector_matches = [a for a in candidates if a.sector == sector_pref]
        if sector_matches:
            return sector_matches[:5]

    return candidates[:5]


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NESDA Activity Catalog")
    parser.add_argument("--search", default="", help="Search query")
    parser.add_argument("--sector", default=None, help="Filter by sector")
    parser.add_argument("--budget", type=int, default=None, help="Budget in DZD")
    parser.add_argument("--recommend", action="store_true", help="Get recommendations")
    parser.add_argument("--list-sectors", action="store_true", help="List all sectors")
    args = parser.parse_args()

    if args.list_sectors:
        for key, s in SECTORS.items():
            stats = get_sector_stats(key)
            print(f"{s['ar']} — {s['fr']}: {stats['count']} activities, avg {stats['avg_investment']:,} DZD, margin {stats['avg_margin']:.0f}%")
    elif args.recommend and args.budget:
        recs = recommend_activity(args.budget)
        for a in recs:
            print(f"  {a.name_fr} ({a.name_ar}) — {a.investment_ideal:,} DZD, margin {a.profit_margin_pct}%, priority {a.aapi_priority}")
    else:
        results = search_catalog(args.search, args.sector)
        print(f"Found {len(results)} activities:")
        for a in results:
            print(f"  [{a.sector}] {a.name_fr} ({a.name_ar}) — {a.investment_min:,}-{a.investment_max:,} DZD, priority {a.aapi_priority}")
