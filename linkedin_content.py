"""LinkedIn content templates — Algerian market data points for DSC posts."""

from datetime import datetime

# Algerian market data points extracted from generator outputs
MARKET_DATA = {
    "retail": {
        "title": "Quincaillerie en Algérie",
        "data_points": [
            "Le secteur du bâtiment en Algérie représente ~7% du PIB",
            "La demande en matériaux de construction croît de 8-12% par an dans les wilayas de l'intérieur",
            "Un investissement de 4.6M DZD génère 6M DZD de CA la première année",
            "La marge brute moyenne en quincaillerie: 30% (vs 20% en grande distribution)",
            "Le délai de récupération moyen: 4-5 ans pour une quincaillerie en wilaya",
            "Les 3 meilleures wilayas pour une quincaillerie: El Bayadh, Saida, Tiaret",
            "Le seuil de rentabilité: ~3.5M DZD/an pour un magasin de 150m²",
            "Le secteur emploie en moyenne 5-8 personnes par établissement",
        ],
        "hashtags": "#quincaillerie #construction #algerie #etude #faisabilite",
    },
    "food": {
        "title": "Restaurant en Algérie",
        "data_points": [
            "Le secteur HORECA en Algérie: 120,000+ établissements, 800,000 emplois",
            "Un restaurant de 80 couverts génère 8-12M DZD de CA annuel",
            "La marge nette moyenne: 8-15% après charges",
            "Le taux de défaillance des restaurants: ~40% dans les 3 premières années",
            "Les plats à forte marge: tajine (65%), couscous (60%), brochettes (55%)",
            "Le coût moyen d'un repas: 400-800 DZD en province, 800-1500 DZD à Alger",
            "Le personnel: 1 cuisinier + 2 serveurs = minimum viable",
            "L'investissement de démarrage: 6-12M DZD selon la localisation",
        ],
        "hashtags": "#restaurant #horeca #algerie #cuisine #faisabilite",
    },
    "digital": {
        "title": "Cybercafé en Algérie",
        "data_points": [
            "Le taux de pénétration Internet en Algérie: ~70% (2026)",
            "Le nombre d'abonnés mobile: 52M+ (penetration 120%)",
            "Un cybercafé de 10 postes génère 3-5M DZD de CA",
            "La marge sur l'impression: 200-500% (papier A4: 2 DZD, impression: 10-20 DZD)",
            "Le revenu par poste/jour: 500-1000 DZD",
            "Les services à forte marge: scan, impression couleur, photocopie, dépôt Argaz",
            "Investissement minimal: 2-4M DZD (10 PC + 2 imprimantes)",
            "Les meilleurs emplacements: près des universités et centres commerciaux",
        ],
        "hashtags": "#cybercafe #internet #algerie #numérique #business",
    },
    "services": {
        "title": "Services Numériques en Algérie",
        "data_points": [
            "Le marché du numérique en Algérie: 2.5 milliards USD (2026)",
            "La transformation numérique des entreprises: 35% seulement digitalisées",
            "Un centre de services numériques peut générer 10-20M DZD/an",
            "Les services les plus demandés: CV, business plan, comptabilité, design",
            "Le tarif moyen d'un CV professionnel: 2,000-4,000 DZD",
            "Le tarif d'une étude de faisabilité: 10,000-60,000 DZD",
            "La marge brute sur les services numériques: 70-90%",
            "Le nombre de PME créées/an en Algérie: 300,000+ (besoin en études)",
        ],
        "hashtags": "#services #numérique #algerie #pme #digital",
    },
    "construction": {
        "title": "BTP en Algérie",
        "data_points": [
            "Le BTP représente 12% du PIB algérien",
            "Le programme ANSEJ a créé 300,000+ entreprises BTP",
            "Le coefficient multiplicateur du BTP: 2.5 (1 DZD investi = 2.5 DZD d'activité)",
            "Les métiers les plus demandés: ferronnerie, plomberie, maçonnerie",
            "Un atelier de ferronnerie: investissement 3-6M DZD, ROI 15-25%",
            "La marge sur les travaux de rénovation: 30-50%",
            "Le secteur emploie 2M+ de travailleurs en Algérie",
            "Les opportunités: rénovation énergétique, habilitation bbc, solaire",
        ],
        "hashtags": "#btp #construction #algerie #ferronnerie #plomberie",
    },
}

POST_TEMPLATES = {
    "data_insight": {
        "title": "💡 Donnée Marché — {topic}",
        "template": """💡 Donnée Marché — {topic}

{sdata_point}

📊 {context}

Qu'en pensez-vous ? Le secteur vous semble-t-il porteur ?

#algerie #marché #etude #faisabilite #{topic_tag}""",
        "engagement": "question ouverte",
    },
    "comparison": {
        "title": "⚖️ Comparaison — {topic}",
        "template": """⚖️ Comparaison investissement {topic}

{data_1}

VS

{data_2}

💰 Verdict: {verdict}

Quelle option préférez-vous ?

#algerie #investissement #comparaison #{topic_tag}""",
        "engagement": "choix A vs B",
    },
    "case_study": {
        "title": "📊 Étude de cas — {topic}",
        "template": """📊 Étude de cas: {topic}

🏢 Projet: {project_type}
📍 Localisation: {wilaya}
💰 Investissement: {investment}

📈 Résultats prévisionnels:
• CA Année 1: {ca}
• Marge Nette: {margin}
• Délai récupération: {payback}
• Score AAPI: {aapi}/1500

Voulez-vous une étude similaire pour votre projet ?

#etude #faisabilite #algerie #{topic_tag}""",
        "engagement": "appel à l'action",
    },
    "myth_busting": {
        "title": "❌ Mythe vs Réalité — {topic}",
        "template": """❌ MYTHE: "{myth}"

✅ RÉALITÉ: {reality}

📊 Données: {data}

{conclusion}

#algerie #business #mythes #{topic_tag}""",
        "engagement": "débat",
    },
    "listicle": {
        "title": "📋 {count} Choses à Savoir — {topic}",
        "template": """📋 {count} choses à savoir avant de lancer un(e) {topic} en Algérie

{items}

💬 Qu'est-ce qui vous surprend le plus ?

#algerie #conseils #business #{topic_tag}""",
        "engagement": "liste + question",
    },
    "arabic_hook": {
        "title": "_hook_ar",
        "template": """{hook_arabic}

{context_arabic}

📊 أرقام: {data_arabic}

💬 ما رأيكم؟

#دراسة_جدوى #الجزائر #{topic_tag_ar}""",
        "engagement": "engagement communautaire",
    },
}


def generate_post(topic_key: str, template_key: str = "data_insight", **kwargs) -> str:
    """Generate a LinkedIn post from template + data."""
    topic = MARKET_DATA[topic_key]
    post = POST_TEMPLATES[template_key]

    # Fill template with topic data and kwargs
    dp = topic["data_points"]
    data_point = dp[0] if dp else ""
    context = "\n".join(dp[1:3]) if len(dp) > 1 else ""

    text = post["template"].format(
        topic=topic["title"],
        sdata_point=data_point,
        context=context,
        topic_tag=topic_key,
        data_1=dp[0] if len(dp) > 0 else "",
        data_2=dp[1] if len(dp) > 1 else "",
        verdict=dp[2] if len(dp) > 2 else "",
        project_type=kwargs.get("project_type", "Quincaillerie"),
        wilaya=kwargs.get("wilaya", "El Bayadh"),
        investment=kwargs.get("investment", "4,600,000 DZD"),
        ca=kwargs.get("ca", "6,000,000 DZD"),
        margin=kwargs.get("margin", "8.5%"),
        payback=kwargs.get("payback", "5 ans"),
        aapi=kwargs.get("aapi", "980"),
        myth=kwargs.get("myth", "Il faut beaucoup d'argent pour créer une entreprise"),
        reality=kwargs.get("reality", "Avec 2M DZD et un bon business plan, vous pouvez démarrer"),
        data=kwargs.get("data", data_point),
        conclusion=kwargs.get("conclusion", "Le vrai facteur n'est pas l'argent, c'est l'étude de marché."),
        count=kwargs.get("count", "5"),
        items="\n".join(f"{i+1}. {d}" for i, d in enumerate(dp[:5])),
        hook_arabic=kwargs.get("hook_arabic", "هل تعلم؟"),
        context_arabic=kwargs.get("context_arabic", ""),
        data_arabic=kwargs.get("data_arabic", data_point),
        topic_tag_ar=kwargs.get("topic_tag_ar", topic_key),
    )

    return text


def generate_content_calendar(month: int = None, year: int = None) -> list:
    """Generate a monthly content calendar for LinkedIn."""
    now = datetime.now()
    month = month or now.month
    year = year or now.year

    calendar = []
    topics = list(MARKET_DATA.keys())
    templates = ["data_insight", "case_study", "comparison", "myth_busting", "listicle"]

    # 3 posts per week × 4 weeks = 12 posts
    for week in range(4):
        for day in range(3):
            topic = topics[(week * 3 + day) % len(topics)]
            template = templates[(week * 3 + day) % len(templates)]
            post_text = generate_post(topic, template)
            calendar.append({
                "week": week + 1,
                "day": ["Lundi", "Mercredi", "Vendredi"][day],
                "topic": MARKET_DATA[topic]["title"],
                "template": template,
                "text": post_text,
                "hashtags": MARKET_DATA[topic]["hashtags"],
            })

    return calendar


if __name__ == "__main__":
    cal = generate_content_calendar()
    for i, post in enumerate(cal, 1):
        print(f"\n{'='*60}")
        print(f"Post {i} — {post['day']} Semaine {post['week']}")
        print(f"Topic: {post['topic']} | Template: {post['template']}")
        print(f"{'='*60}")
        print(post["text"])
