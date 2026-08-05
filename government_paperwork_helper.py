"""Government Paperwork Helper — Guides for Algerian administrative procedures."""

import os
import json
from datetime import datetime


PROCEDURES = {
    "anem_registration": {
        "name_fr": "Inscription ANEM (Agence Nationale de l'Emploi)",
        "name_ar": "التسجيل في ANEM (الوكالة الوطنية للتشغيل)",
        "category": "emploi",
        "description_fr": "Inscription pour recherche d'emploi, formation et allocation chômage",
        "description_ar": "التسجيل للبحث عن عمل والتكوين وبدل البطالة",
        "documents_fr": [
            "CNI (Carte Nationale d'Identité) en cours de validité",
            "Extrait de naissance",
            "Diplôme(s) ou attestation(s) de formation",
            "Photo d'identité (format passeport)",
            "Relevé d'identité bancaire (RIB)",
            "Attestation de domicile",
            "CV (curriculum vitae)"
        ],
        "documents_ar": [
            "البطاقة الوطنية للتعريف السارية المفعول",
            "extract من شهادة الميلاد",
            "الشهادات أو شهادات التكوين",
            "صورة بحجم جواز السفر",
            "كشف الحساب البنكي (RIB)",
            "شهادة الإقامة",
            "السيرة الذاتية"
        ],
        "cost_fr": "Gratuit",
        "cost_ar": "مجاني",
        "duration_fr": "Immédiat (inscription en ligne ou sur place)",
        "duration_ar": "فوري (تسجيل عبر الإنترنت أو في المقر)",
        "link_fr": "https://www.anem.dz",
        "link_ar": "https://www.anem.dz",
        "steps_fr": [
            "1. Créer un compte sur le site ANEM (www.anem.dz) ou se rendre à l'agence la plus proche",
            "2. Remplir le formulaire d'inscription en ligne",
            "3. Télécharger les documents requis (CNI, diplôme, photo, RIB)",
            "4. Valider l'inscription et obtenir un numéro d'inscription",
            "5. Passer l'entretien d'orientation si demandé",
            "6. Recevoir l'attestation d'inscription"
        ],
        "steps_ar": [
            "1. إنشاء حساب على موقع ANEM (www.anem.dz) أو التوجه لأقرب وكالة",
            "2. ملء نموذج التسجيل عبر الإنترنت",
            "3. تحميل الوثائق المطلوبة (بطاقة التعريف، الشهادة، صورة، حساب بنكي)",
            "4. التحقق من التسجيل والحصول على رقم تسجيل",
            "5. إجراء مقابلة التوجيه إذا لزم الأمر",
            "6. الحصول على شهادة التسجيل"
        ],
        "notes_fr": "Obligatoire pour bénéficier des formations ANEM et de l'allocation chômage (ACEM). Renouvellement tous les 6 mois.",
        "notes_ar": "إلزامي للاستفادة من تكوينات ANEM وبدل البطالة (ACEM). التجديد كل 6 أشهر."
    },
    "caci_declaration": {
        "name_fr": "Déclaration CACI (Centre d'Animation et de Conseil en Informatique)",
        "name_ar": "تصريح CACI (مركز التنشيط والاستشارات في المعلوماتية)",
        "category": "creation",
        "description_fr": "Déclaration de création d'activité pour les travailleurs indépendants et micro-entreprises",
        "description_ar": "تصريح إنشاء نشاط للم.workers الحر والمؤسسات الصغيرة",
        "documents_fr": [
            "CNI en cours de validité",
            "Extrait de naissance récent (< 3 mois)",
            "Attestation de domicile ou contrat de bail",
            "Photo d'identité",
            "Justificatif de qualification (diplôme ou attestation)",
            "Relevé d'identité bancaire (RIB)",
            "Déclaration de non-condamnation"
        ],
        "documents_ar": [
            "بطاقة التعريف الوطنية السارية",
            "extract من شهادة الميلاد الحديثة (أقل من 3 أشهر)",
            "شهادة الإقامة أو عقد الإيجار",
            "صورة بحجم جواز السفر",
            "إثبات الأهلية (شهادة أو مؤهل)",
            "كشف الحساب البنكي (RIB)",
            "إفصال بعدم السوابق العدلية"
        ],
        "cost_fr": "Gratuit (déclaration) + frais de publication (~2,000 DA)",
        "cost_ar": "مجاني (تصريح) + رسوم النشر (~2,000 دج)",
        "duration_fr": "1-3 jours ouvrables",
        "duration_ar": "1-3 أيام عمل",
        "link_fr": "https://www.caci.dz",
        "link_ar": "https://www.caci.dz",
        "steps_fr": [
            "1. Rassembler tous les documents requis",
            "2. Se rendre au CACI le plus proche ou utiliser le portail en ligne",
            "3. Remplir le formulaire de déclaration d'activité",
            "4. Soumettre les documents et payer les frais de publication",
            "5. Recevoir l'attestation de déclaration d'activité",
            "6. Publier dans un journal officiel (JALO) si nécessaire"
        ],
        "steps_ar": [
            "1. تجميع جميع الوثائق المطلوبة",
            "2. التوجه لأقرب CACI أو استخدام البوابة الإلكترونية",
            "3. ملء نموذج تصريح النشاط",
            "4. تقديم الوثائق ودفع رسوم النشر",
            "5. الحصول على شهادة تصريح النشاط",
            "6. النشر في الجريدة الرسمية (JALO) إذا لزم الأمر"
        ],
        "notes_fr": "Première étape pour créer une auto-entreprise ou une société unipersonnelle. Valable 1 an, renouvelable.",
        "notes_ar": "الخطوة الأولى لإنشاء مؤسسة فردية أو مؤسسة فردية. صالحة لمدة سنة، قابلة للتجديد."
    },
    "cnas_affiliation": {
        "name_fr": "Affiliation CNAS (Caisse Nationale des Assurances Sociales)",
        "name_ar": "الانتماء CNAS (الصندوق الوطني للتأمينات الاجتماعية)",
        "category": "social",
        "description_fr": "Déclaration d'activité et affiliation à la sécurité sociale pour travailleurs indépendants",
        "description_ar": "تصريح النشاط والانتماء للضمان الاجتماعي للم.workers الحر",
        "documents_fr": [
            "CNI en cours de validité",
            "Attestation de déclaration d'activité (CACI)",
            "Relevé d'identité bancaire (RIB)",
            "Photo d'identité",
            "Contrat de bail ou attestation de domicile"
        ],
        "documents_ar": [
            "بطاقة التعريف الوطنية السارية",
            "شهادة تصريح النشاط (CACI)",
            "كشف الحساب البنكي (RIB)",
            "صورة بحجم جواز السفر",
            "عقد الإيجار أو شهادة الإقامة"
        ],
        "cost_fr": "Cotisation: 26% du revenu annuel (toutes activités confondues)",
        "cost_ar": "الاشتراكات: 26% من الدخل السنوي (جميع الأنشطة مجتمعة)",
        "duration_fr": "Immédiat à 15 jours",
        "duration_ar": "فوري إلى 15 يوماً",
        "link_fr": "https://www.cnas.dz",
        "link_ar": "https://www.cnas.dz",
        "steps_fr": [
            "1. Créer un compte sur le portail CNAS (www.cnas.dz)",
            "2. Remplir le formulaire d'affiliation",
            "3. Joindre les documents requis",
            "4. Soumettre la déclaration en ligne ou au guichet",
            "5. Recevoir le numéro d'affiliation",
            "6. Payer les cotisations mensuelles via CCP ou banque"
        ],
        "steps_ar": [
            "1. إنشاء حساب على بوابة CNAS (www.cnas.dz)",
            "2. ملء نموذج الانتماء",
            "3. إرفاق الوثائق المطلوبة",
            "4. تقديم التصريح عبر الإنترنت أو عند النافذة",
            "5. الحصول على رقم الانتماء",
            "6. دفع الاشتراكات الشهرية عبر CCP أو البنك"
        ],
        "notes_fr": "Obligatoire pour tout travailleur indépendant. Couvre: maladie, maternité, retraite, accident du travail. Cotisation minimale basée sur le SMIG (20,000 DA/mois).",
        "notes_ar": "إلزامي لكل عامل حر. يشمل: المرض، الأمومة، التقاعد، حوادث العمل. الاشتراكات تعتمد على SMIG (20,000 دج/شهر)."
    },
    "casisd_declaration": {
        "name_fr": "Déclaration CASNOS (Caisse de Sécurité Sociale des Non-Salariés)",
        "name_ar": "تصريح CASNOS (صندوق الضمان الاجتماعي لغير الموظفين)",
        "category": "social",
        "description_fr": "Assurance maladie obligatoire pour les travailleurs indépendants non affiliés à la CNAS",
        "description_ar": "التأمين الصحي الإلزامي للم.workers الحر غير المنتمين لـ CNAS",
        "documents_fr": [
            "CNI en cours de validité",
            "Attestation de déclaration d'activité",
            "Justificatif de domicile",
            "Relevé d'identité bancaire (RIB)",
            "Photo d'identité"
        ],
        "documents_ar": [
            "بطاقة التعريف الوطنية السارية",
            "شهادة تصريح النشاط",
            "إثبات الإقامة",
            "كشف الحساب البنكي (RIB)",
            "صورة بحجم جواز السفر"
        ],
        "cost_fr": "Cotisation: ~5,000 DA/an (tarif forfaitaire)",
        "cost_ar": "اشتراك: ~5,000 دج/سنة (سعر ثابت)",
        "duration_fr": "Immédiat",
        "duration_ar": "فوري",
        "link_fr": "https://www.casnos.dz",
        "link_ar": "https://www.casnos.dz",
        "steps_fr": [
            "1. Se rendre à la CIR (Caisse Inter-Régionale) CASNOS la plus proche",
            "2. Remplir le formulaire d'inscription",
            "3. Soumettre les documents requis",
            "4. Payer la cotisation annuelle",
            "5. Recevoir la carte d'assurance maladie"
        ],
        "steps_ar": [
            "1. التوجه لأقرب CIR (الصندوق بين الجهوي) CASNOS",
            "2. ملء نموذج التسجيل",
            "3. تقديم الوثائق المطلوبة",
            "4. دفع الاشتراك السنوي",
            "5. الحصول على بطاقة التأمين الصحي"
        ],
        "notes_fr": "Obligatoire si vous n'êtes pas affilié à la CNAS. Couvre les soins médicaux de base. Renouvellement annuel.",
        "notes_ar": "إلزامي إذا كنت غير منتمي لـ CNAS. يشمل الرعاية الصحية الأساسية. تجديد سنوي."
    },
    "entreprise_creation": {
        "name_fr": "Création d'entreprise (SARL, SARLAU, Auto-entreprise)",
        "name_ar": "إنشاء مؤسسة (SARL، SARLAU، مؤسسة فردية)",
        "category": "creation",
        "description_fr": "Procédure complète de création d'une entreprise en Algérie",
        "description_ar": "الإجراء الكامل لإنشاء مؤسسة في الجزائر",
        "documents_fr": [
            "CNI des associés/fondateurs",
            "Extrait de naissance de chaque associé (< 3 mois)",
            "Statuts de la société (rédigés par notaire)",
            "Attestation de dépôt de capital social",
            "Attestation de domiciliation (bail commercial ou domiciliation)",
            "Déclaration de non-condamnation des associés",
            "Publication au JALO (Journal d'Annonces Légales et Obligatoires)"
        ],
        "documents_ar": [
            "بطاقات تعريف الشركاء/المؤسسين",
            "شهادات ميلاد كل شريك (أقل من 3 أشهر)",
            "نظام الشركة (مسودة من عند الوسيط)",
            "شهادة إيداع رأس المال الاجتماعي",
            "شهادة الإقامة (عقد تجاري أو إقامة مؤسسة)",
            "إفصال الشركاء بعدم السوابق العدلية",
            "النشر في JALO (جريدة الإعلانات القانونية والإلزامية)"
        ],
        "cost_fr": "Capital minimum: 100,000 DA (SARL) / Frais: ~30,000-80,000 DA",
        "cost_ar": "رأس المال الأدنى: 100,000 دج (SARL) / الرسوم: ~30,000-80,000 دج",
        "duration_fr": "15-30 jours ouvrables",
        "duration_ar": "15-30 يوم عمل",
        "link_fr": "https://www.cnrc.dz",
        "link_ar": "https://www.cnrc.dz",
        "steps_fr": [
            "1. Choisir le type d'entreprise (SARL, SARLAU, Auto-entreprise)",
            "2. Rédiger les statuts avec un notaire",
            "3. Déposer le capital social dans une banque",
            "4. Obtenir l'attestation de dépôt de capital",
            "5. Déposer le dossier au CNRC (Centre National du Registre de Commerce)",
            "6. Publier au JALO",
            "7. Immatriculer au registre de commerce",
            "8. S'inscrire à la DGI, CNAS, CACI selon l'activité"
        ],
        "steps_ar": [
            "1. اختيار نوع المؤسسة (SARL، SARLAU، مؤسسة فردية)",
            "2. إعداد النظام مع الوسيط",
            "3. إيداع رأس المال الاجتماعي في بنك",
            "4. الحصول على شهادة إيداع رأس المال",
            "5. تقديم الملف إلى CNRC (المركز الوطني لسجل التجارة)",
            "6. النشر في JALO",
            "7. التسجيل في سجل التجارة",
            "8. التسجيل في DGI و CNAS و CACI حسب النشاط"
        ],
        "notes_fr": "Auto-entreprise: capital libre, chiffre d'affaires < 5M DA/an. SARL: capital min 100,000 DA, 2 associés minimum. SARLAU: capital min 1,000,000 DA.",
        "notes_ar": "مؤسسة فردية: رأس مال حر، رقم أعمال أقل من 5 ملايين دج/سنة. SARL: رأس مال أدنى 100,000 دج، شريكان على الأقل. SARLAU: رأس مال أدنى 1,000,000 دج."
    },
    "carte_grise": {
        "name_fr": "Carte grise (Certificat d'immatriculation)",
        "name_ar": "بطاقة رمادية (شهادة التسجيل)",
        "category": "vehicule",
        "description_fr": "Immatriculation ou transfert de propriété d'un véhicule",
        "description_ar": "تسجيل أو نقل ملكية مركبة",
        "documents_fr": [
            "CNI du propriétaire",
            "Certificat de conformité du véhicule",
            "Attestation d'assurance automobile",
            "Facture d'achat du véhicule",
            "Contrat de vente (si transfert)",
            "Visite technique (si occasion)"
        ],
        "documents_ar": [
            "بطاقة التعريف الوطنية للمالك",
            "شهادة مطابقة المركبة",
            "شهادة التأمين على السيارة",
            "فاتورة شراء المركبة",
            "عقد البيع (في حالة النقل)",
            "الفحص الفني (إذا كانت مستعملة)"
        ],
        "cost_fr": "~5,000 – 15,000 DA selon le type de véhicule",
        "cost_ar": "~5,000 – 15,000 دج حسب نوع المركبة",
        "duration_fr": "1-5 jours ouvrables",
        "duration_ar": "1-5 أيام عمل",
        "link_fr": "https://www.service-public.dz",
        "link_ar": "https://www.service-public.dz",
        "steps_fr": [
            "1. Passer la visite technique (véhicules d'occasion)",
            "2. Obtenir l'attestation d'assurance",
            "3. Remplir le formulaire de demande de carte grise",
            "4. Déposer les documents au guichet de la wilaya ou de la commune",
            "5. Payer les frais de immatriculation",
            "6. Recevoir la carte grise sous 1-5 jours"
        ],
        "steps_ar": [
            "1. خضوع الفحص الفني (المركبات المستعملة)",
            "2. الحصول على شهادة التأمين",
            "3. ملء نموذج طلب البطاقة الرمادية",
            "4. تقديم الوثائق عند نافذة الولاية أو البلدية",
            "5. دفع رسوم التسجيل",
            "6. الحصول على البطاقة الرمادية خلال 1-5 أيام"
        ],
        "notes_fr": "Obligatoire pour circuler. Renouvellement si changement d'adresse ou de propriétaire.",
        "notes_ar": "إلزامي للتنقل. التجديد عند تغيير العنوان أو المالك."
    },
    "amende_routiere": {
        "name_fr": "Paiement d'amende routière",
        "name_ar": "دفع غرامة مرورية",
        "category": "vehicule",
        "description_fr": "Règlement des amendes pour infractions au code de la route",
        "description_ar": "تسوية الغرامات المترتبة على مخالفات قانون المرور",
        "documents_fr": [
            "Numéro de l'amende (PV - Procès-Verbal)",
            "CNI du contrevenant",
            "Carte grise du véhicule"
        ],
        "documents_ar": [
            "رقم الغرامة (PV - المحضر)",
            "بطاقة التعريف الوطنية للمخالف",
            "البطاقة الرمادية للمركبة"
        ],
        "cost_fr": "Variable selon l'infraction (500 – 50,000+ DA)",
        "cost_ar": "متغير حسب المخالفة (500 – 50,000+ دج)",
        "duration_fr": "Immédiat (en ligne ou au guichet)",
        "duration_ar": "فوري (عبر الإنترنت أو عند النافذة)",
        "link_fr": "https://www.service-public.dz",
        "link_ar": "https://www.service-public.dz",
        "steps_fr": [
            "1. Vérifier le montant de l'amende sur le PV",
            "2. Payer en ligne via le portail de l'État (www.service-public.dz) ou à la banque",
            "3. Conserver le reçu de paiement",
            "4. En cas de contestation: se rendre au tribunal dans les 10 jours"
        ],
        "steps_ar": [
            "1. التحقق من مبلغ الغرامة في المحضر",
            "2. الدفع عبر الإنترنت عبر بوابة الدولة (www.service-public.dz) أو في البنك",
            "3. الاحتفاظ بإيصال الدفع",
            "4. في حالة الاعتراض: التوجه إلى المحكمة خلال 10 أيام"
        ],
        "notes_fr": "Paiement sous 30 jours pour bénéficier de 50% de réduction. Après 60 jours: majoration de 100%.",
        "notes_ar": "الدفع خلال 30 يوماً للاستفادة من خصم 50%. بعد 60 يوماً: زيادة 100%."
    }
}


class GovernmentPaperworkHelper:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "generated_output")
        os.makedirs(self.output_dir, exist_ok=True)

    def get_procedure(self, key):
        return PROCEDURES.get(key)

    def list_procedures(self, category=None, lang="fr"):
        results = []
        for key, proc in PROCEDURES.items():
            if category and proc["category"] != category:
                continue
            name = proc[f"name_{lang}"]
            results.append({"key": key, "name": name, "category": proc["category"]})
        return results

    def generate_checklist(self, key, lang="fr"):
        proc = PROCEDURES.get(key)
        if not proc:
            return None

        name = proc[f"name_{lang}"]
        docs = proc[f"documents_{lang}"]
        steps = proc[f"steps_{lang}"]
        cost = proc[f"cost_{lang}"]
        duration = proc[f"duration_{lang}"]
        notes = proc[f"notes_{lang}"]

        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  {name}")
        lines.append(f"{'='*60}")
        lines.append("")
        lines.append(f"💰 Coût: {cost}" if lang == "fr" else f"💰 التكلفة: {cost}")
        lines.append(f"⏱️ Délai: {duration}" if lang == "fr" else f"⏱️ المدة: {duration}")
        lines.append("")
        lines.append(f"{'─'*60}")
        lines.append("📄 Documents requis:" if lang == "fr" else "📄 الوثائق المطلوبة:")
        lines.append(f"{'─'*60}")
        for doc in docs:
            lines.append(f"  □ {doc}")
        lines.append("")
        lines.append(f"{'─'*60}")
        lines.append("📋 Étapes:" if lang == "fr" else "📋 الخطوات:")
        lines.append(f"{'─'*60}")
        for step in steps:
            lines.append(f"  {step}")
        lines.append("")
        lines.append(f"{'─'*60}")
        lines.append("📌 Notes:" if lang == "fr" else "📌 ملاحظات:")
        lines.append(f"{'─'*60}")
        lines.append(f"  {notes}")
        lines.append("")

        result = "\n".join(lines)

        try:
            from training_hook import hook_generation
            hook_generation(
                generator="gov_paperwork",
                input_params={"procedure": key, "lang": lang},
                output_content=result,
            )
        except Exception:
            pass

        return result

    def save_checklist(self, key, lang="fr"):
        text = self.generate_checklist(key, lang)
        if not text:
            return None

        proc = PROCEDURES[key]
        filename = f"procedure_{key}_{lang}.txt"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        return filepath

    def save_all_checklists(self, lang="fr"):
        paths = []
        for key in PROCEDURES:
            path = self.save_checklist(key, lang)
            if path:
                paths.append(path)
        return paths


if __name__ == "__main__":
    helper = GovernmentPaperworkHelper()
    print("\n📋 Procédures disponibles:\n")
    categories = {"emploi": "Emploi", "creation": "Création d'entreprise", "social": "Sécurité sociale", "vehicule": "Véhicule"}
    for key, proc in PROCEDURES.items():
        cat = categories.get(proc["category"], proc["category"])
        print(f"  [{cat}] {proc['name_fr']}")
        print(f"    {proc['description_fr']}\n")

    choice = input("Choisir une procédure (clé): ").strip()
    if choice in PROCEDURES:
        print(helper.generate_checklist(choice, "fr"))
    else:
        print("Procédure non trouvée.")
