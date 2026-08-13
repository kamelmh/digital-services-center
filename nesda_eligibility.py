"""NESDA Eligibility Checker — verify if a project qualifies for NESDA financing.

Checks: age, activity type, investment range, location, profile, required documents.
Returns eligibility status with score and recommendations.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from nesda_catalog import CATALOG, SECTORS


@dataclass
class EligibilityCheck:
    """Result of eligibility check."""
    eligible: bool
    score: int  # 0-100
    max_score: int
    checks: List[dict]  # individual check results
    documents_needed: List[str]
    recommendations: List[str]
    financing_estimate: dict  # amounts for triangular model
    next_steps: List[str]


def check_eligibility(
    age: int,
    activity_key: str,
    investment: int,
    wilaya: str,
    profile: str = "unemployed",  # unemployed, employed, student
    has_cde_training: bool = False,
    has_anem_registration: bool = False,
    has_business_plan: bool = False,
    has_feasibility_study: bool = False,
) -> EligibilityCheck:
    """Check if a project qualifies for NESDA financing."""

    checks = []
    score = 0
    max_score = 0
    recommendations = []

    # ── Check 1: Age (20 points) ──────────────────────────────────────────────
    max_score += 20
    if 18 <= age <= 55:
        score += 20
        checks.append({"name": "العمر / Âge", "status": "pass", "score": 20, "max": 20,
                        "detail": f"{age} سنة — ضمن النطاق المقبول (18-55)"})
    elif 56 <= age <= 58:
        score += 10
        checks.append({"name": "العمر / Âge", "status": "warning", "score": 10, "max": 20,
                        "detail": f"{age} سنة — فوق النطاق المفضل لكن مقبول للتوسع"})
    else:
        checks.append({"name": "العمر / Âge", "status": "fail", "score": 0, "max": 20,
                        "detail": f"{age} سنة — خارج النطاق المقبول (18-55)"})
        recommendations.append("العمر خارج النطاق — تواصل مع NESDA لاستثناء")

    # ── Check 2: Activity type (25 points) ────────────────────────────────────
    max_score += 25
    activity = CATALOG.get(activity_key)
    if activity:
        score += 15
        checks.append({"name": "النشاط / Activité", "status": "pass", "score": 15, "max": 25,
                        "detail": f"{activity.name_fr} — مدعوم من NESDA"})
        # Bonus for high-priority sectors
        if activity.aapi_priority >= 5:
            score += 10
            checks.append({"name": "أولوية النشاط", "status": "pass", "score": 10, "max": 0,
                            "detail": f"أولوية AAPI عالية ({activity.aapi_priority}/7) — ميزة إضافية"})
        else:
            score += 5
            checks.append({"name": "أولوية النشاط", "status": "info", "score": 5, "max": 0,
                            "detail": f"أولوية AAPI متوسطة ({activity.aapi_priority}/7)"})
    else:
        checks.append({"name": "النشاط / Activité", "status": "fail", "score": 0, "max": 25,
                        "detail": "النشاط غير موجود في قائمة NESDA"})
        recommendations.append("تحقق من قائمة الأنشطة المدعومة في NESDA Catalog")

    # ── Check 3: Investment range (20 points) ─────────────────────────────────
    max_score += 20
    if activity:
        if activity.investment_min <= investment <= activity.investment_max:
            score += 20
            checks.append({"name": "المبلغ المستثمر / Investissement", "status": "pass", "score": 20, "max": 20,
                            "detail": f"{investment:,} دج — ضمن النطاق ({activity.investment_min:,}-{activity.investment_max:,})"})
        elif investment < activity.investment_min:
            ratio = investment / activity.investment_min
            partial = int(20 * ratio)
            score += partial
            checks.append({"name": "المبلغ المستثمر / Investissement", "status": "warning", "score": partial, "max": 20,
                            "detail": f"{investment:,} دج — أقل من الحد الأدنى ({activity.investment_min:,})"})
            recommendations.append(f"الاستثمار أقل من الحد الأدنى — يُنصح بزيادة الميزانية")
        else:
            score += 15
            checks.append({"name": "المبلغ المستثمر / Investissement", "status": "warning", "score": 15, "max": 20,
                            "detail": f"{investment:,} دج — أعلى من النطاق المعتاد ({activity.investment_max:,})"})
            recommendations.append("المبلغ عالي — تأكد من دراسة الجدوى التفصيلية")
    else:
        if 500_000 <= investment <= 20_000_000:
            score += 15
            checks.append({"name": "المبلغ المستثمر / Investissement", "status": "pass", "score": 15, "max": 20,
                            "detail": f"{investment:,} دج — ضمن النطاق العام لـ NESDA"})
        else:
            checks.append({"name": "المبلغ المستثمر / Investissement", "status": "fail", "score": 0, "max": 20,
                            "detail": f"{investment:,} دج — خارج النطاق المقبول"})

    # ── Check 4: Profile (15 points) ──────────────────────────────────────────
    max_score += 15
    profile_scores = {"unemployed": 15, "student": 15, "employed": 10}
    profile_checks = {
        "unemployed": {"ar": "مسجل لدى ANEM", "fr": "Inscrit ANEM"},
        "student": {"ar": "طالب/خريج", "fr": "Étudiant/Diplômé"},
        "employed": {"ar": "موظف/مؤمّن", "fr": "Salarié/Assuré"},
    }
    ps = profile_checks.get(profile, profile_checks["unemployed"])
    pts = profile_scores.get(profile, 10)
    score += pts
    checks.append({"name": "الوضع / Profil", "status": "pass", "score": pts, "max": 15,
                    "detail": f"{ps['ar']} — تمويل {pts}/15"})

    # ── Check 5: Documents (20 points) ────────────────────────────────────────
    max_score += 20
    doc_checks = [
        ("شهادة CDE", "培训CDE", has_cde_training, 8),
        (" تسجيل ANEM", "ANEM", has_anem_registration, 5),
        ("خطة العمل", "Business Plan", has_business_plan, 4),
        ("دراسة الجدوى", "Feasibility", has_feasibility_study, 3),
    ]
    doc_score = 0
    for name, _, has, pts in doc_checks:
        if has:
            doc_score += pts
            checks.append({"name": name, "status": "pass", "score": pts, "max": 0, "detail": "متوفر ✓"})
        else:
            checks.append({"name": name, "status": "warning", "score": 0, "max": 0, "detail": "غير متوفر"})
            recommendations.append(f"الحصول على {name} قبل تقديم الملف")

    score += doc_score
    checks.append({"name": "المستندات / Documents", "status": "pass" if doc_score >= 15 else "warning",
                    "score": doc_score, "max": 20, "detail": f"{doc_score}/20 نقطة"})

    # ── Financing estimate ────────────────────────────────────────────────────
    if profile == "unemployed":
        personal_pct, nesda_pct, bank_pct = 0.05, 0.25, 0.70
    elif profile == "student":
        personal_pct, nesda_pct, bank_pct = 0.05, 0.25, 0.70
    else:
        personal_pct, nesda_pct, bank_pct = 0.15, 0.15, 0.70

    financing = {
        "personal": int(investment * personal_pct),
        "nesda_grant": int(investment * nesda_pct),
        "bank_loan": int(investment * bank_pct),
        "monthly_payment": int(investment * bank_pct * 0.03 / 10 / 12) if investment > 0 else 0,
        "personal_pct": personal_pct,
        "nesda_pct": nesda_pct,
        "bank_pct": bank_pct,
    }

    # ── Documents needed ──────────────────────────────────────────────────────
    documents = [
        "بطاقة التعريف الوطنية (CNI)",
        "شهادة الميلاد",
        "شهادة إيداع تصريح إنشاء النشاط (CACI)",
        "شهادة ANEM (للحوامل)",
        "شهادة CDE (تكوين)",
        "خطة العمل (Business Plan)",
        "دراسة الجدوى (Feasibility Study)",
        "عرض تقني (Dossier Technique)",
        "عقد كراء أو ملكية (Local)",
        "شهادة البنك (Attestation bancaire)",
        "صور شمسية للنشاط",
    ]

    # ── Next steps ────────────────────────────────────────────────────────────
    next_steps = []
    if not has_cde_training:
        next_steps.append("1. التسجيل في CDE + حضور التكوين الإلزامي")
    if not has_anem_registration:
        next_steps.append("2. التسجيل لدى ANEM (للحوامل)")
    next_steps.append(f"{len(next_steps)+1}. إعداد خطة العمل + دراسة الجدوى")
    next_steps.append(f"{len(next_steps)+2}. إيداع الملف لدى agency NESDA ({wilaya})")
    next_steps.append(f"{len(next_steps)+3.}. انتظار الموافقة (1-3 أشهر)")

    # ── Eligibility ───────────────────────────────────────────────────────────
    eligible = score >= 50

    return EligibilityCheck(
        eligible=eligible,
        score=score,
        max_score=max_score,
        checks=checks,
        documents_needed=documents,
        recommendations=recommendations,
        financing_estimate=financing,
        next_steps=next_steps,
    )


def format_eligibility_report(result: EligibilityCheck, name: str = "", activity_key: str = "") -> str:
    """Format eligibility report as markdown."""
    activity = CATALOG.get(activity_key, None)
    activity_name = f"{activity.name_fr} ({activity.name_ar})" if activity else activity_key

    checks_md = ""
    for c in result.checks:
        icon = "✅" if c["status"] == "pass" else "⚠️" if c["status"] == "warning" else "❌" if c["status"] == "fail" else "ℹ️"
        checks_md += f"| {icon} {c['name']} | {c['detail']} | {c['score']}/{c['max']} |\n"

    docs_md = "\n".join(f"- {d}" for d in result.documents_needed)
    next_md = "\n".join(result.next_steps)
    recs_md = "\n".join(f"- {r}" for r in result.recommendations) if result.recommendations else "- لا توجد توصيات إضافية"

    return f"""# تقرير الأهلية لـ NESDA — Eligibility Report

**الاسم:** {name or '[Nom]'}
**النشاط:** {activity_name}
**الوضع:** {result.checks[3]['detail'] if len(result.checks) > 3 else 'N/A'}

---

## النتيجة: {result.score}/{result.max_score} — {'مؤهل ✓' if result.eligible else 'غير مؤهل ✗'}

## فحص الأهلية
| الفحص | التفاصيل | النتيجة |
|-------|----------|---------|
{checks_md}

## هيكل التمويل المتوقع
| المصدر | النسبة | المبلغ |
|--------|--------|--------|
| المساهمة الشخصية | {result.financing_estimate['personal_pct']*100:.0f}% | {result.financing_estimate['personal']:,} دج |
| مساهمة NESDA (PNR) | {result.financing_estimate['nesda_pct']*100:.0f}% | {result.financing_estimate['nesda_grant']:,} دج |
| قرض بنكي | {result.financing_estimate['bank_pct']*100:.0f}% | {result.financing_estimate['bank_loan']:,} دج |
| القسط الشهري التقديري | — | {result.financing_estimate['monthly_payment']:,} دج |

## المستندات المطلوبة
{docs_md}

## التوصيات
{recs_md}

## الخطوات التالية
{next_md}
"""


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NESDA Eligibility Checker")
    parser.add_argument("--age", type=int, default=28)
    parser.add_argument("--activity", default="boulangerie")
    parser.add_argument("--investment", type=int, default=3_000_000)
    parser.add_argument("--wilaya", default="El Bayadh")
    parser.add_argument("--profile", default="unemployed", choices=["unemployed", "employed", "student"])
    args = parser.parse_args()

    result = check_eligibility(
        age=args.age, activity_key=args.activity,
        investment=args.investment, wilaya=args.wilaya, profile=args.profile,
    )
    print(format_eligibility_report(result, "Test User", args.activity))
