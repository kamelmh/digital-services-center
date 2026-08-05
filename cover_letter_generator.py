"""Cover Letter Generator — Arabic and French cover letters with PDF export."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

NAVY = HexColor("#0A1628")
GOLD = HexColor("#D4AF37")
INK = HexColor("#1A1A1A")


class CoverLetterGenerator:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "generated_output")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, data, lang="fr"):
        filename = data.get("filename", f"lettre_{lang}_{data.get('sender_name', 'unnamed').replace(' ', '_')}.pdf")
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        y = height - 25*mm

        c.setFillColor(NAVY)
        c.rect(0, height - 8*mm, width, 8*mm, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(0, height - 10*mm, width, 2*mm, fill=1, stroke=0)

        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 16)
        if lang == "ar":
            c.drawRightString(width - 20*mm, y, data.get("sender_name", ""))
        else:
            c.drawString(20*mm, y, data.get("sender_name", ""))
        y -= 6*mm
        c.setFont("Helvetica", 10)
        for line in data.get("sender_address", []):
            if lang == "ar":
                c.drawRightString(width - 20*mm, y, line)
            else:
                c.drawString(20*mm, y, line)
            y -= 5*mm
        y -= 5*mm

        c.setFont("Helvetica", 10)
        if lang == "ar":
            c.drawRightString(width - 20*mm, y, data.get("date", ""))
        else:
            c.drawRightString(width - 20*mm, y, data.get("date", ""))
        y -= 8*mm

        c.setFont("Helvetica-Bold", 10)
        if lang == "ar":
            c.drawRightString(width - 20*mm, y, data.get("recipient_name", ""))
            c.setFont("Helvetica", 10)
            y -= 5*mm
            for line in data.get("recipient_address", []):
                c.drawRightString(width - 20*mm, y, line)
                y -= 5*mm
        else:
            c.drawString(20*mm, y, data.get("recipient_name", ""))
            c.setFont("Helvetica", 10)
            y -= 5*mm
            for line in data.get("recipient_address", []):
                c.drawString(20*mm, y, line)
                y -= 5*mm
        y -= 8*mm

        c.setFont("Helvetica-Bold", 10)
        subject = data.get("subject", "")
        if lang == "ar":
            c.drawRightString(width - 20*mm, y, subject)
        else:
            c.drawString(20*mm, y, subject)
        y -= 10*mm

        greeting = data.get("greeting", "Madame, Monsieur," if lang == "fr" else "سيدي/سيدتي،")
        c.setFont("Helvetica", 10)
        if lang == "ar":
            c.drawRightString(width - 20*mm, y, greeting)
        else:
            c.drawString(20*mm, y, greeting)
        y -= 8*mm

        c.setFont("Helvetica", 10)
        for paragraph in data.get("body", []):
            words = paragraph.split()
            line = ""
            for word in words:
                test = line + " " + word if line else word
                if c.stringWidth(test, "Helvetica", 10) < width - 40*mm:
                    line = test
                else:
                    if lang == "ar":
                        c.drawRightString(width - 20*mm, y, line)
                    else:
                        c.drawString(20*mm, y, line)
                    y -= 5*mm
                    line = word
            if line:
                if lang == "ar":
                    c.drawRightString(width - 20*mm, y, line)
                else:
                    c.drawString(20*mm, y, line)
                y -= 5*mm
            y -= 5*mm

        closing = data.get("closing", "Cordialement," if lang == "fr" else "وتفضلوا بقبول فائق الاحترام،")
        c.setFont("Helvetica", 10)
        if lang == "ar":
            c.drawRightString(width - 20*mm, y, closing)
        else:
            c.drawString(20*mm, y, closing)
        y -= 15*mm

        c.setFont("Helvetica-Bold", 11)
        if lang == "ar":
            c.drawRightString(width - 20*mm, y, data.get("sender_name", ""))
        else:
            c.drawString(20*mm, y, data.get("sender_name", ""))

        c.save()

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="cover_letter",
                input_params={"sender_name": data.get("sender_name", ""), "lang": lang},
                output_content=f"Cover letter generated: {filename}",
                metadata={"filepath": filepath},
            )
        except Exception:
            pass

        return filepath


TEMPLATES = {
    "spontaneous_fr": {
        "sender_name": "Votre Nom",
        "sender_address": ["123 Rue principale", "El Bayadh 32000", "Algérie"],
        "subject": "Objet: Candidature spontanée",
        "greeting": "Madame, Monsieur,",
        "body": [
            "Je me permets de vous adresser ma candidature spontanée pour un poste au sein de votre entreprise. Fort d'une expérience en [domaine], je suis convaincu que mes compétences pourraient contribuer à votre équipe.",
            "Au cours de mon parcours, j'ai développé des compétences en [compétence 1], [compétence 2] et [compétence 3]. Rigoureux et motivé, je suis prêt à m'investir pleinement dans les missions qui me seront confiées.",
            "Je me tiens à votre disposition pour un entretien à votre convenance afin de vous exposer plus en détail mes motivations et mon parcours."
        ],
        "closing": "Dans l'attente de votre réponse, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées."
    },
    "spontaneous_ar": {
        "sender_name": "الاسم الكامل",
        "sender_address": ["123 الشارع الرئيسي", "البيض 32000", "الجزائر"],
        "subject": "الموضوع: ترشح تلقائي",
        "greeting": "سيدي/سيدتي،",
        "body": [
            "أتقدم إليكم بترشحي التلقائي للعمل في مؤسستكم. بفضل خبرتي في [المجال]، أنا واثق من أن مهاراتي ستساهم في إثراء فريقكم.",
            "طوال مسيرتي المهنية، طورت مهارات في [المهارة 1] و [المهارة 2] و [المهارة 3]. أنا شخص منضبط ومحفز، جاهز للإسهام đầy في المهام التي ستُوكل إلي.",
            "أنا رهن إشارتكم لمقابلة في أقرب وقت ممكن لعرض دوافعي ومسيرتي المهنية بالتفصيل."
        ],
        "closing": "وتفضلوا بقبول فائق الاحترام والتقدير."
    },
    "job_application_fr": {
        "sender_name": "Votre Nom",
        "sender_address": ["123 Rue principale", "El Bayadh 32000", "Algérie"],
        "subject": "Objet: Candidature au poste de [Intitulé du poste]",
        "greeting": "Madame, Monsieur,",
        "body": [
            "Suite à votre annonce parue sur [source], je souhaite vous proposer ma candidature pour le poste de [intitulé]. Mon profil correspond aux compétences recherchées.",
            "Titre d'un [diplôme] en [spécialité], j'ai acquis une expérience de [X] années dans [domaine]. Mes compétences en [compétence 1] et [compétence 2] me permettront de m'intégrer rapidement dans votre équipe.",
            "Motivé et adaptable, je suis disponible immédiatement et prêt à relever de nouveaux défis professionnels."
        ],
        "closing": "Je vous remercie de l'attention portée à ma candidature et reste à votre entière disposition pour un entretien."
    },
    "job_application_ar": {
        "sender_name": "الاسم الكامل",
        "sender_address": ["123 الشارع الرئيسي", "البيض 32000", "الجزائر"],
        "subject": "الموضوع: ترشح لمنصب [اسم المنصب]",
        "greeting": "سيدي/سيدتي،",
        "body": [
            "بناءً على إعلانكم المنشور في [المصدر]، أتقدم بترشحي لمنصب [اسم المنصب]. ملفي الشخصي يتوافق مع المؤهلات المطلوبة.",
            "حاصل على [الشهادة] في [التخصص]، اكتسبت خبرة مهنية مدتها [عدد] سنوات في [المجال]. مهاراتي في [المهارة 1] و [المهارة 2] ستتسعني للاندماج بسرعة في فريقكم.",
            "أنا شخص متحمس ومتكيف، جاهز للعمل فوراً واستقبال تحالفات مهنية جديدة."
        ],
        "closing": "أشكركم على اهتمامكم بترشحي، وأبقى رهن إشارتكم لمقابلة في أقرب وقت."
    }
}


def generate_from_template(template_key="spontaneous_fr"):
    template = TEMPLATES.get(template_key, TEMPLATES["spontaneous_fr"])
    print(f"\n{'='*50}")
    print(f"  Cover Letter Generator — {template_key.upper()}")
    print(f"{'='*50}\n")
    print("Remplissez les champs ( Entrée = valeur par défaut ):\n")

    data = dict(template)
    data["sender_name"] = input(f"Votre nom [{template['sender_name']}]: ").strip() or template["sender_name"]
    data["date"] = input("Date (JJ/MM/AAAA): ").strip() or "05/08/2026"
    data["recipient_name"] = input("Destinataire [Entreprise / Nom]: ").strip() or "À l'attention du Directeur des Ressources Humaines"
    data["recipient_address"] = [input("Adresse destinataire: ").strip() or "Entreprise X, El Bayadh"]

    print(f"\n--- Sujet: {template['subject']} ---")
    custom_subject = input("Sujet personnalisé (vide = garder): ").strip()
    if custom_subject:
        data["subject"] = custom_subject

    gen = CoverLetterGenerator()
    lang = "ar" if "ar" in template_key else "fr"
    filepath = gen.generate(data, lang)
    print(f"\n✅ Lettre générée: {filepath}")
    return filepath


if __name__ == "__main__":
    print("1. Candidature spontanée (FR)")
    print("2. Candidature spontanée (AR)")
    print("3. Réponse à offre (FR)")
    print("4. Réponse à offre (AR)")
    choice = input("Choisir (1-4): ").strip()
    templates = {
        "1": "spontaneous_fr", "2": "spontaneous_ar",
        "3": "job_application_fr", "4": "job_application_ar"
    }
    generate_from_template(templates.get(choice, "spontaneous_fr"))
