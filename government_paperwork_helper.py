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
        "description_fr": "Affiliation employeur et déclarations mensuelles CNAS (26% du salaire brut)",
        "description_ar": "انتماء صاحب العمل والتصريحات الشهرية CNAS (26% من الأجر الإجمالي)",
        "documents_fr": [
            "CNI du dirigeant",
            "Extrait de commerce ou RC",
            "Attestation de domiciliation",
            "Relevé d'identité bancaire (RIB)",
            "Contrats de travail des salariés",
            "Bulletins de paie du mois"
        ],
        "documents_ar": [
            "بطاقة التعريف الوطنية للمدير",
            "extract من سجل التجارة أو رقم السجلCommerce",
            "شهادة الإقامة",
            "كشف الحساب البنكي (RIB)",
            "عقود عمل الموظفين",
            "كشوفات الرواتب الشهرية"
        ],
        "cost_fr": "Cotisation: 26% du salaire brut mensuel (12% retraite + 12.35% ass. sociales + 1.5% décès + 0.15% accident)",
        "cost_ar": "اشتراكات: 26% من الأجر الإجمالي الشهري (12% تقاعد + 12.35% تأمينات + 1.5% وفاة + 0.15% حوادث)",
        "duration_fr": "Affiliation: 10 jours / Déclaration: mensuelle avant fin du mois suivant",
        "duration_ar": "الانتماء: 10 أيام / التصريح: شهري قبل نهاية الشهر التالي",
        "link_fr": "https://teledeclaration.cnas.dz",
        "link_ar": "https://teledeclaration.cnas.dz",
        "steps_fr": [
            "1. S'affilier via la CNAS dans les 10 jours suivant l'embauche (SÉCU 01)",
            "2. Créer un compte sur teledeclaration.cnas.dz",
            "3. Déclarer mensuellement les salariés et salaires",
            "4. Payer la cotisation (26% du brut) via CCP, BaridiMob ou virement",
            "5. Attester les bulletins de paie avec IRG retenu",
            "6. Demander la CHIFA (carte santé) pour chaque salarié"
        ],
        "steps_ar": [
            "1. التسجيل في CNAS خلال 10 أيام من التوظيف (SÉCU 01)",
            "2. إنشاء حساب على teledeclaration.cnas.dz",
            "3. التصريح الشهري بالموظفين والرواتب",
            "4. دفع الاشتراكات (26% من الإجمالي) عبر CCP أو BaridiMob أو تحويل بنكي",
            "5. تأكيد كشوفات الرواتب مع IRG المحتسب",
            "6. طلب CHIFA (بطاقة صحية) لكل موظف"
        ],
        "notes_fr": "Obligatoire pour tout employeur. CHIFA = carte santé pour les salariés. Pénalité: 5% en retard. Télédéclaration obligatoire depuis 2024.",
        "notes_ar": "إلزامي لكل صاحب عمل. CHIFA = بطاقة صحية للموظفين. غرامة: 5% في حالة التأخر. التصريح الإلكتروني إلزامي منذ 2024."
    },
    "casisd_declaration": {
        "name_fr": "Déclaration CASNOS (Caisse de Sécurité Sociale des Non-Salariés)",
        "name_ar": "تصريح CASNOS (صندوق الضمان الاجتماعي لغير الموظفين)",
        "category": "social",
        "description_fr": "Affiliation et cotisations pour travailleurs indépendants, commerçants, professions libérales",
        "description_ar": "الانتماء والاشتراكات للعمال المستقلين والتجار والمهن الحرة",
        "documents_fr": [
            "CNI en cours de validité",
            "Extrait de commerce ou RC",
            "Agrément ou autorisation (si activité réglementée)",
            "Attestation de existence DGI",
            "Carte d'artisan/agriculteur (si applicable)",
            "Relevé d'identité bancaire (RIB)",
            "2 photos d'identité"
        ],
        "documents_ar": [
            "بطاقة التعريف الوطنية السارية",
            "extract من سجل التجارة أو رقم السجل",
            "رخصة أو ترخيص (إذا كان النشاط منظماً)",
            "شهادة الوجود من DGI",
            "بطاقة حرفي/فلاح (إذا كان معملاً)",
            "كشف الحساب البنكي (RIB)",
            "صورتان بحجم جواز السفر"
        ],
        "cost_fr": "Cotisation: 15% du revenu annuel (7.5% ass. sociales + 7.5% retraite). Min: 43,200 DA/an. Auto-entrepreneur: 24,000 DA/an forfaitaire.",
        "cost_ar": "اشتراكات: 15% من الدخل السنوي (7.5% تأمينات + 7.5% تقاعد). الحد الأدنى: 43,200 دج/سنة. مؤسسة فردية: 24,000 دج/سنة ثابتة.",
        "duration_fr": "Affiliation: 10 jours / Paiement: trimestriel ou annuel / Déclaration annuelle: avant le 1er mars",
        "duration_ar": "الانتماء: 10 أيام / الدفع: ربع سنوي أو سنوي / التصريح السنوي: قبل 1 مارس",
        "link_fr": "https://damancom.casnos.dz",
        "link_ar": "https://damancom.casnos.dz",
        "steps_fr": [
            "1. S'affilier via damancom.casnos.dz (e-affiliation) ou au guichet CIR",
            "2. Remplir le formulaire d'inscription (10 jours max après démarrage)",
            "3. Soumettre les documents (RC, CNI, RIB, photos)",
            "4. Payer la cotisation (trimestrielle ou annuelle)",
            "5. Recevoir la CHIFA (carte d'assurance maladie)",
            "6. Déclarer annuellement le revenu avant le 1er mars"
        ],
        "steps_ar": [
            "1. التسجيل عبر damancom.casnos.dz (إلكتروني) أو عند نافذة CIR",
            "2. ملء نموذج التسجيل (10 أيام كحد أقصى بعد بدء النشاط)",
            "3. تقديم الوثائق (سجل التجارة، بطاقة التعريف، حساب بنكي، صور)",
            "4. دفع الاشتراك (ربع سنوي أو سنوي)",
            "5. الحصول على CHIFA (بطاقة التأمين الصحي)",
            "6. التصريح السنوي بالدخل قبل 1 مارس"
        ],
        "notes_fr": "Obligatoire pour tout non-salarié. Pénalité retard: 11% 1er mois + 1%/mois. Déclaration annuelle tardive: 162,000 DA. Auto-entrepreneur: forfait 24,000 DA/an.",
        "notes_ar": "إلزامي لكل غير موظف. غرامة التأخر: 11% أول شهر + 1%/شهر. التصريح السنوي المتأخر: 162,000 دج. مؤسسة فردية: 24,000 دج/سنة."
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
        "name_fr": "Carte grise — Immatriculation véhicule (SINNV 2026)",
        "name_ar": "بطاقة رمادية — تسجيل مركبة (SINNV 2026)",
        "category": "vehicule",
        "description_fr": "Immatriculation ou transfert de propriété via le nouveau système SINNV (avril 2026). Tout au guichet de la Daïra.",
        "description_ar": "تسجيل أو نقل ملكية عبر النظام الجديد SINNV (أبريل 2026). كل الإجراءات عند نافذة الدائرة.",
        "documents_fr": [
            "CNIBE biométrique du vendeur + acheteur (tous les deux présents)",
            "Certificat de résidence récent (même wilaya ou wilaya d'origine)",
            "Carte grise originale barrée (si transfert)",
            "Photos d'identité (2 par personne)",
            "Timbre fiscal (~800 DA selon puissance)",
            "Contrat de vente généré automatiquement par le système"
        ],
        "documents_ar": [
            "CNIBE بيومترية للمبيع + المشتري (كلاهما حاضر)",
            "شهادة إقامة حديثة (نفس الولاية أو ولاية المنشأ)",
            "بطاقة رمادية أصلية مخطوطة (في حالة النقل)",
            "صور تعريف (2 لكل شخص)",
            "طابع بريدي (~800 دج حسب القوة)",
            "عقد بيع يُولّد تلقائياً من النظام"
        ],
        "cost_fr": "~5,200 DA (digital) + ~1,500 DA (timbre) — total ~6,700 DA selon puissance",
        "cost_ar": "~5,200 دج (رقمي) + ~1,500 دج (طابع بريدي) — الإجمالي ~6,700 دج حسب القوة",
        "duration_fr": "Même wilaya: 1-3 semaines / Autre wilaya: 3-5 semaines / Importé: 2-6 semaines",
        "duration_ar": "نفس الولاية: 1-3 أسابيع / ولاية أخرى: 3-5 أسابيع / مستورد: 2-6 أسابيع",
        "link_fr": "https://www.service-public.dz",
        "link_ar": "https://www.service-public.dz",
        "steps_fr": [
            "1. Vendeur + acheteur se rendent ENSEMBLE au guichet de la Daïra (mairie)",
            "2. Le vendeur présente sa CNIBE + carte grise barrée + certificat de résidence",
            "3. L'acheteur présente sa CNIBE + certificat de résidence + photos",
            "4. Le système SINNV génère automatiquement la déclaration de vente",
            "5. Paiement du timbre fiscal et des frais d'immatriculation",
            "6. Réception de la nouvelle carte grise avec QR code",
            "⚠️ NOUVEAU: Ne peut plus se faire à la mairie — uniquement au guichet Daïra (depuis avril 2026)"
        ],
        "steps_ar": [
            "1. المبيع + المشتري يذهبون معاً لنافذة الدائرة ( البلدية )",
            "2. المبيع يقدم CNIBE + بطاقة رمادية مخطوطة + شهادة إقامة",
            "3. المشتري يقدم CNIBE + شهادة إقامة + صور",
            "4. نظام SINNV يولّد تلقائياً عقد البيع",
            "5. دفع الطابع البريدي ورسوم التسجيل",
            "6. استلام البطاقة الرمادية الجديدة مع رمز QR",
            "⚠️ جديد: لم يعد ممكناً في البلدية — فقط عند نافذة الدائرة (منذ أبريل 2026)"
        ],
        "notes_fr": "SINNV: nouveau système national numérique depuis avril 2026. QR code sur chaque carte. Obligatoire pour vente, changement adresse, héritage, modification technique.",
        "notes_ar": "SINNV: النظام الرقمي الوطني الجديد منذ أبريل 2026. رمز QR على كل بطاقة. إلزامي للبيع، تغيير العنوان، الإرث، التعديل التقني."
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
