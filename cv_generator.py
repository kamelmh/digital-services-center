"""CV Generator — Arabic and French CVs with PDF export via ReportLab."""

import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

NAVY = HexColor("#0A1628")
GOLD = HexColor("#D4AF37")
WHITE = HexColor("#FFFFFF")
INK = HexColor("#1A1A1A")

try:
    pdfmetrics.registerFont(TTFont("NotoSansArabic", "C:/Windows/Fonts/arial.ttf"))
except:
    pass


class CVGenerator:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "generated_output")
        os.makedirs(self.output_dir, exist_ok=True)

    def _draw_header(self, c, name, title, lang="fr"):
        width, height = A4
        c.setFillColor(NAVY)
        c.rect(0, height - 90*mm, width, 90*mm, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(0, height - 90*mm, width, 2*mm, fill=1, stroke=0)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(width/2, height - 30*mm, name)
        c.setFont("Helvetica", 11)
        c.drawCentredString(width/2, height - 40*mm, title)

        return height - 95*mm

    def _draw_section(self, c, title, y, lang="fr"):
        width, height = A4
        c.setFillColor(GOLD)
        c.rect(15*mm, y - 1*mm, width - 30*mm, 0.5*mm, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        if lang == "ar":
            c.drawRightString(width - 15*mm, y - 5*mm, title)
        else:
            c.drawString(15*mm, y - 5*mm, title)
        return y - 10*mm

    def _draw_item(self, c, title, subtitle, details, y, lang="fr"):
        width, height = A4
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10)
        if lang == "ar":
            c.drawRightString(width - 15*mm, y, title)
            c.setFont("Helvetica", 9)
            c.setFillColor(HexColor("#555555"))
            c.drawRightString(width - 15*mm, y - 5*mm, subtitle)
        else:
            c.drawString(15*mm, y, title)
            c.setFont("Helvetica", 9)
            c.setFillColor(HexColor("#555555"))
            c.drawRightString(width - 15*mm, y, subtitle)
        if details:
            c.setFont("Helvetica", 9)
            if lang == "ar":
                c.drawRightString(width - 15*mm, y - 10*mm, details)
            else:
                c.drawString(20*mm, y - 10*mm, details)
        return y - 16*mm

    def _draw_contact(self, c, y, contacts, lang="fr"):
        width, height = A4
        c.setFillColor(HexColor("#555555"))
        c.setFont("Helvetica", 9)
        x = 15*mm if lang == "fr" else width - 15*mm
        for item in contacts:
            if lang == "ar":
                c.drawRightString(width - 15*mm, y, item)
            else:
                c.drawString(x, y, item)
                x += 50*mm
            y -= 4*mm
        return y - 4*mm

    def generate(self, data, lang="fr"):
        filename = data.get("filename", f"cv_{lang}_{data.get('name', 'unnamed').replace(' ', '_')}.pdf")
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        y = self._draw_header(c, data["name"], data["title"], lang)

        contacts = []
        if data.get("phone"):
            contacts.append(f"📞 {data['phone']}")
        if data.get("email"):
            contacts.append(f"✉️ {data['email']}")
        if data.get("location"):
            contacts.append(f"📍 {data['location']}")
        y = self._draw_contact(c, y, contacts, lang)

        if data.get("summary"):
            y = self._draw_section(c, "Profil" if lang == "fr" else "الملف الشخصي", y, lang)
            c.setFillColor(INK)
            c.setFont("Helvetica", 9)
            words = data["summary"].split()
            line = ""
            for word in words:
                test = line + " " + word if line else word
                if c.stringWidth(test, "Helvetica", 9) < width - 40*mm:
                    line = test
                else:
                    if lang == "ar":
                        c.drawRightString(width - 15*mm, y, line)
                    else:
                        c.drawString(15*mm, y, line)
                    y -= 5*mm
                    line = word
            if line:
                if lang == "ar":
                    c.drawRightString(width - 15*mm, y, line)
                else:
                    c.drawString(15*mm, y, line)
                y -= 5*mm
            y -= 5*mm

        for exp in data.get("experience", []):
            if y < 30*mm:
                c.showPage()
                y = height - 15*mm
            y = self._draw_item(c, exp["role"], exp.get("company", "") + " · " + exp.get("period", ""), exp.get("details", ""), y, lang)

        for edu in data.get("education", []):
            if y < 30*mm:
                c.showPage()
                y = height - 15*mm
            y = self._draw_item(c, edu["degree"], edu.get("institution", "") + " · " + edu.get("period", ""), edu.get("details", ""), y, lang)

        if data.get("skills"):
            y = self._draw_section(c, "Compétences" if lang == "fr" else "المهارات", y, lang)
            c.setFillColor(INK)
            c.setFont("Helvetica", 9)
            skills_text = " · ".join(data["skills"])
            words = skills_text.split()
            line = ""
            for word in words:
                test = line + " " + word if line else word
                if c.stringWidth(test, "Helvetica", 9) < width - 30*mm:
                    line = test
                else:
                    if lang == "ar":
                        c.drawRightString(width - 15*mm, y, line)
                    else:
                        c.drawString(15*mm, y, line)
                    y -= 5*mm
                    line = word
            if line:
                if lang == "ar":
                    c.drawRightString(width - 15*mm, y, line)
                else:
                    c.drawString(15*mm, y, line)

        c.save()

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="cv",
                input_params={"name": data.get("name", ""), "template": data.get("template", ""), "lang": lang},
                output_content=f"CV generated: {filename}",
                metadata={"filepath": filepath},
            )
        except Exception:
            pass

        return filepath


TEMPLATES = {
    "student": {
        "name": "Nom de l'Étudiant",
        "title": "Étudiant en [Spécialité]",
        "summary": "Étudiant motivé en [spécialité] à l'université de [nom]. Cherche un stage ou une opportunité professionnelle pour appliquer mes compétences.",
        "experience": [
            {"role": "Stage", "company": "Entreprise X", "period": "2025", "details": "Tâches réalisées lors du stage"}
        ],
        "education": [
            {"degree": "Licence en [Spécialité]", "institution": "Université de [Ville]", "period": "2022 – 2025", "details": ""}
        ],
        "skills": ["Microsoft Office", "Python", "Communication", "Travail d'équipe"]
    },
    "employee": {
        "name": "Nom du Candidat",
        "title": "Poste Actuel",
        "summary": "Professionnel expérimenté avec X ans d'expérience dans [domaine]. Compétences en [compétence 1], [compétence 2] et [compétence 3].",
        "experience": [
            {"role": "Poste Actuel", "company": "Entreprise Y", "period": "2022 – Présent", "details": "Description des responsabilités"},
            {"role": "Poste Précédent", "company": "Entreprise Z", "period": "2019 – 2022", "details": "Description des responsabilités"}
        ],
        "education": [
            {"degree": "Master en [Domaine]", "institution": "Université de [Ville]", "period": "2017 – 2019", "details": ""}
        ],
        "skills": ["Gestion de projet", "Leadership", "Analyse", "Négociation"]
    },
    "freelancer": {
        "name": "Nom du Freelance",
        "title": "Freelance — [Spécialité]",
        "summary": "Freelance spécialisé en [domaine]. Offre des services de [service 1], [service 2] et [service 3] pour des clients en Algérie et à l'international.",
        "experience": [
            {"role": "Freelance", "company": "Indépendant", "period": "2020 – Présent", "details": "Realisations et projets clients"}
        ],
        "education": [
            {"degree": "Formation en [Domaine]", "institution": "Institution", "period": "Année", "details": ""}
        ],
        "skills": ["Créativité", "Autonomie", "Gestion client", "Outils numériques"]
    },
    "cv_ar": {
        "name": "الاسم الكامل",
        "title": "المهنة الحالية",
        "summary": "محترف ذو خبرة في [المجال]. يتقن [المهارة 1] و [المهارة 2] و [المهارة 3].",
        "experience": [
            {"role": "المنصب الحالي", "company": "المؤسسة", "period": "2022 – الحاضر", "details": "وصف المهام والمسؤوليات"}
        ],
        "education": [
            {"degree": "شهادة في [المجال]", "institution": "جامعة [المدينة]", "period": "2017 – 2022", "details": ""}
        ],
        "skills": ["مicrosoft Office", "الإنجليزية", "العمل الجماعي", "التواصل"]
    }
}


def generate_from_input(template_key="student"):
    template = TEMPLATES.get(template_key, TEMPLATES["student"])
    print(f"\n{'='*50}")
    print(f"  CV Generator — {template_key.upper()}")
    print(f"{'='*50}")
    print("Remplissez les champs (appuyez Entrée pour garder la valeur par défaut):\n")

    data = {}
    data["name"] = input(f"Nom [{template['name']}]: ").strip() or template["name"]
    data["title"] = input(f"Poste [{template['title']}]: ").strip() or template["title"]
    data["phone"] = input("Téléphone: ").strip()
    data["email"] = input("Email: ").strip()
    data["location"] = input("Localisation: ").strip()
    data["summary"] = input(f"Résumé [{template['summary'][:50]}...]: ").strip() or template["summary"]
    data["experience"] = template["experience"]
    data["education"] = template["education"]
    data["skills"] = template["skills"]

    gen = CVGenerator()
    lang = "ar" if "ar" in template_key else "fr"
    filepath = gen.generate(data, lang)
    print(f"\n✅ CV généré: {filepath}")
    return filepath


if __name__ == "__main__":
    print("1. Étudiant  2. Employé  3. Freelance  4. CV Arabe")
    choice = input("Choisir (1-4): ").strip()
    templates = {"1": "student", "2": "employee", "3": "freelancer", "4": "cv_ar"}
    generate_from_input(templates.get(choice, "student"))
