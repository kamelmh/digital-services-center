"""AAPI Scoring Optimizer — 1500-point grid for foncier économique.

Decree 26-154 (April 2026), Annex I.
Projects scored on 8 criteria, max 1500 points.
"""

from dataclasses import dataclass


# AAPI Scoring Grid — Annex I, Decree 26-154
AAPI_CRITERIA = {
    "activity_type": {
        "name_fr": "Nature de l'activité",
        "name_ar": "طبيعة النشاط",
        "coefficient": 7,
        "max_score": 420,
        "levels": [
            {"label": "Priorité 1 (industrie, agroalimentaire, BTP)", "score": 60, "points": 420},
            {"label": "Priorité 2 (services, transport, digital)", "score": 40, "points": 280},
            {"label": "Priorité 3 (commerce, restauration)", "score": 20, "points": 140},
        ],
    },
    "investment_amount": {
        "name_fr": "Montant de l'investissement",
        "name_ar": "مبلغ الاستثمار",
        "coefficient": 6,
        "max_score": 360,
        "levels": [
            {"label": "≥ 100 milliards DA", "score": 60, "points": 360},
            {"label": "50 – 100 milliards DA", "score": 55, "points": 330},
            {"label": "10 – 50 milliards DA", "score": 50, "points": 300},
            {"label": "7 – 10 milliards DA", "score": 40, "points": 240},
            {"label": "5 – 7 milliards DA", "score": 35, "points": 210},
            {"label": "2 – 5 milliards DA", "score": 30, "points": 180},
            {"label": "1 – 2 milliards DA", "score": 20, "points": 120},
            {"label": "0,5 – 1 milliard DA", "score": 15, "points": 90},
            {"label": "0,1 – 0,5 milliard DA", "score": 10, "points": 60},
            {"label": "< 0,1 milliard DA", "score": 5, "points": 30},
        ],
    },
    "employment": {
        "name_fr": "Emploi",
        "name_ar": "التوظيف",
        "coefficient": 5,
        "max_score": 300,
        "levels": [
            {"label": "≥ 500 postes", "score": 60, "points": 300},
            {"label": "250 – 500 postes", "score": 50, "points": 250},
            {"label": "100 – 250 postes", "score": 40, "points": 200},
            {"label": "50 – 100 postes", "score": 30, "points": 150},
            {"label": "10 – 50 postes", "score": 20, "points": 100},
            {"label": "< 10 postes", "score": 10, "points": 50},
        ],
    },
    "equity_contribution": {
        "name_fr": "Montant des apports en fonds propres",
        "name_ar": "مبلغ الحصص في الأموال الخاصة",
        "coefficient": 4,
        "max_score": 200,
        "levels": [
            {"label": "Apport ≥ 70%", "score": 50, "points": 200},
            {"label": "50% ≤ apport < 70%", "score": 40, "points": 160},
            {"label": "30% ≤ apport < 50%", "score": 30, "points": 120},
            {"label": "Apport < 30%", "score": 20, "points": 80},
        ],
    },
    "local_content": {
        "name_fr": "Contenu local (taux d'intégration)",
        "name_ar": "المحتوى المحلي (نسبة التكامل)",
        "coefficient": 2,
        "max_score": 60,
        "levels": [
            {"label": "Taux > 50%", "score": 30, "points": 60},
            {"label": "25% ≤ taux ≤ 50%", "score": 20, "points": 40},
            {"label": "Taux < 25%", "score": 10, "points": 20},
            {"label": "Taux = 0", "score": 0, "points": 0},
        ],
    },
    "employment_permanence": {
        "name_fr": "Pérennité de l'emploi",
        "name_ar": "استمرارية التوظيف",
        "coefficient": 1,
        "max_score": 60,
        "levels": [
            {"label": "Part de CDD < 20%", "score": 60, "points": 60},
            {"label": "20% ≤ part CDD < 30%", "score": 40, "points": 40},
            {"label": "Part CDD ≥ 30%", "score": 10, "points": 10},
        ],
    },
    "investment_extension": {
        "name_fr": "Extension de l'investissement",
        "name_ar": "امتداد الاستثمار",
        "coefficient": 1,
        "max_score": 70,
        "levels": [
            {"label": "Bien mitoyen attenant", "score": 70, "points": 70},
            {"label": "Autre bien immobilier", "score": 35, "points": 35},
            {"label": "Aucun", "score": 0, "points": 0},
        ],
    },
    "export_diversification": {
        "name_fr": "Contribution à la diversification des exportations",
        "name_ar": "المساهمة في تنويع الصادرات",
        "coefficient": 1,
        "max_score": 30,
        "levels": [
            {"label": "Part > 50%", "score": 30, "points": 30},
            {"label": "25% ≤ part ≤ 50%", "score": 20, "points": 20},
            {"label": "Part < 25%", "score": 10, "points": 10},
            {"label": "Part = 0", "score": 0, "points": 0},
        ],
    },
}


@dataclass
class AAPIScore:
    activity_type: int = 0
    investment_amount: int = 0
    employment: int = 0
    equity_contribution: int = 0
    local_content: int = 0
    employment_permanence: int = 0
    investment_extension: int = 0
    export_diversification: int = 0

    @property
    def total(self) -> int:
        return (
            self.activity_type + self.investment_amount + self.employment +
            self.equity_contribution + self.local_content + self.employment_permanence +
            self.investment_extension + self.export_diversification
        )

    @property
    def percentage(self) -> float:
        return (self.total / 1500) * 100

    @property
    def rating(self) -> str:
        pct = self.percentage
        if pct >= 80:
            return "Excellent — Forte chance d'acceptation"
        elif pct >= 60:
            return "Bon — Compétitif"
        elif pct >= 40:
            return "Moyen — Des améliorations recommandées"
        else:
            return "Faible — Refonte nécessaire"


class AAAPIOptimizer:
    """Score and optimize AAPI applications."""

    @staticmethod
    def score_project(params: dict) -> AAPIScore:
        """Score a project based on AAPI criteria.
        
        params keys:
            activity_priority: 1, 2, or 3
            investment_amount: in DZD
            employees: number
            equity_ratio: 0.0 to 1.0
            local_integration: 0 to 100 (%)
            cdd_ratio: 0.0 to 1.0 (temporary contracts)
            has_extension: bool
            export_ratio: 0 to 100 (%)
        """
        score = AAPIScore()

        # 1. Activity type
        priority = params.get("activity_priority", 3)
        for level in AAPI_CRITERIA["activity_type"]["levels"]:
            if priority == 1 and "Priorité 1" in level["label"]:
                score.activity_type = level["points"]
                break
            elif priority == 2 and "Priorité 2" in level["label"]:
                score.activity_type = level["points"]
                break
            elif priority == 3 and "Priorité 3" in level["label"]:
                score.activity_type = level["points"]
                break

        # 2. Investment amount
        amount = params.get("investment_amount", 0)
        for level in AAPI_CRITERIA["investment_amount"]["levels"]:
            label = level["label"]
            if "milliards" in label:
                continue  # Too large for most small businesses
            if "milliard" in label and "0,1" in label:
                if amount >= 100_000_000:
                    score.investment_amount = level["points"]
                    break
            elif "0,5" in label:
                if 50_000_000 <= amount < 100_000_000:
                    score.investment_amount = level["points"]
                    break
            elif "< 0,1" in label:
                if amount < 100_000_000:
                    score.investment_amount = level["points"]

        # More granular scoring for small-medium investments
        if amount >= 2_000_000_000:
            score.investment_amount = 180
        elif amount >= 1_000_000_000:
            score.investment_amount = 120
        elif amount >= 500_000_000:
            score.investment_amount = 90
        elif amount >= 100_000_000:
            score.investment_amount = 60
        elif amount >= 50_000_000:
            score.investment_amount = 40
        elif amount >= 10_000_000:
            score.investment_amount = 30
        elif amount >= 5_000_000:
            score.investment_amount = 20
        else:
            score.investment_amount = 10

        # 3. Employment
        employees = params.get("employees", 1)
        if employees >= 500:
            score.employment = 300
        elif employees >= 250:
            score.employment = 250
        elif employees >= 100:
            score.employment = 200
        elif employees >= 50:
            score.employment = 150
        elif employees >= 10:
            score.employment = 100
        else:
            score.employment = 50

        # 4. Equity contribution
        equity = params.get("equity_ratio", 0.3)
        if equity >= 0.70:
            score.equity_contribution = 200
        elif equity >= 0.50:
            score.equity_contribution = 160
        elif equity >= 0.30:
            score.equity_contribution = 120
        else:
            score.equity_contribution = 80

        # 5. Local content
        local = params.get("local_integration", 0)
        if local > 50:
            score.local_content = 60
        elif local >= 25:
            score.local_content = 40
        elif local > 0:
            score.local_content = 20
        else:
            score.local_content = 0

        # 6. Employment permanence
        cdd = params.get("cdd_ratio", 0.1)
        if cdd < 0.20:
            score.employment_permanence = 60
        elif cdd < 0.30:
            score.employment_permanence = 40
        else:
            score.employment_permanence = 10

        # 7. Investment extension
        if params.get("has_extension", False):
            score.investment_extension = 70
        else:
            score.investment_extension = 0

        # 8. Export diversification
        export = params.get("export_ratio", 0)
        if export > 50:
            score.export_diversification = 30
        elif export >= 25:
            score.export_diversification = 20
        elif export > 0:
            score.export_diversification = 10
        else:
            score.export_diversification = 0

        return score

    @staticmethod
    def optimize(score: AAPIScore, params: dict) -> list[dict]:
        """Suggest improvements to maximize AAPI score."""
        suggestions = []
        current = score.total

        # Check each criterion for improvement potential
        if score.activity_type < 420:
            suggestions.append({
                "criterion": "Nature de l'activité",
                "current": score.activity_type,
                "max": 420,
                "gap": 420 - score.activity_type,
                "advice": "Choisir une activité Priorité 1 (industrie, agroalimentaire, BTP) pour maximiser ce score",
            })

        if score.investment_amount < 360:
            suggestions.append({
                "criterion": "Montant investissement",
                "current": score.investment_amount,
                "max": 360,
                "gap": 360 - score.investment_amount,
                "advice": "Augmenter le montant total de l'investissement (équipements, bâtiment, fonds de roulement)",
            })

        if score.employment < 300:
            suggestions.append({
                "criterion": "Emploi",
                "current": score.employment,
                "max": 300,
                "gap": 300 - score.employment,
                "advice": "Augmenter le nombre d'emplois créés (minimum 10 pour 100 points)",
            })

        if score.equity_contribution < 200:
            suggestions.append({
                "criterion": "Apports fonds propres",
                "current": score.equity_contribution,
                "max": 200,
                "gap": 200 - score.equity_contribution,
                "advice": f"Augmenter les apports personnels (actuellement {params.get('equity_ratio', 0)*100:.0f}%, viser ≥70%)",
            })

        if score.local_content < 60:
            suggestions.append({
                "criterion": "Contenu local",
                "current": score.local_content,
                "max": 60,
                "gap": 60 - score.local_content,
                "advice": "Augmenter le taux d'intégration local (acheter local, sous-traitance algérienne)",
            })

        if score.employment_permanence < 60:
            suggestions.append({
                "criterion": "Pérennité emploi",
                "current": score.employment_permanence,
                "max": 60,
                "gap": 60 - score.employment_permanence,
                "advice": "Réduire la part de CDD en dessous de 20%",
            })

        # Sort by gap (biggest improvement potential first)
        suggestions.sort(key=lambda x: x["gap"], reverse=True)

        total_potential = sum(s["gap"] for s in suggestions)
        suggestions.append({
            "criterion": "TOTAL",
            "current": current,
            "max": 1500,
            "gap": 1500 - current,
            "potential_improvement": total_potential,
            "advice": f"Score actuel: {current}/1500 ({score.percentage:.0f}%). Amélioration possible: +{total_potential} points.",
        })

        return suggestions

    @staticmethod
    def format_report(score: AAPIScore, params: dict, suggestions: list[dict]) -> str:
        """Generate a formatted AAPI scoring report."""
        lines = []
        lines.append("=" * 60)
        lines.append("  RAPPORT DE SCORING AAPI — Grille d'Évaluation")
        lines.append("  Décret Exécutif n° 26-154, Annexe I")
        lines.append("=" * 60)
        lines.append("")

        for key, criterion in AAPI_CRITERIA.items():
            attr = key
            score_val = getattr(score, attr, 0)
            max_val = criterion["max_score"]
            pct = (score_val / max_val * 100) if max_val > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            lines.append(f"  {criterion['name_fr']}")
            lines.append(f"    Coefficient: {criterion['coefficient']}  |  Score: {score_val}/{max_val}  |  {bar} {pct:.0f}%")
            lines.append("")

        lines.append("─" * 60)
        lines.append(f"  SCORE TOTAL: {score.total}/1500  ({score.percentage:.0f}%)")
        lines.append(f"  ÉVALUATION: {score.rating}")
        lines.append("─" * 60)
        lines.append("")

        if suggestions:
            lines.append("  💡 RECOMMANDATIONS D'AMÉLIORATION:")
            lines.append("")
            for s in suggestions[:-1]:  # Skip total
                lines.append(f"  • {s['criterion']}: +{s['gap']} points possibles")
                lines.append(f"    {s['advice']}")
                lines.append("")

        return "\n".join(lines)


if __name__ == "__main__":
    # Example: Quincaillerie in El Bayadh
    params = {
        "activity_priority": 3,  # Commerce = Priority 3
        "investment_amount": 4_600_000,  # 4.6M DZD
        "employees": 5,
        "equity_ratio": 0.65,  # 65% equity
        "local_integration": 40,  # 40% local
        "cdd_ratio": 0.10,  # 10% temporary
        "has_extension": False,
        "export_ratio": 0,
    }

    optimizer = AAAPIOptimizer()
    score = optimizer.score_project(params)
    suggestions = optimizer.optimize(score, params)
    report = optimizer.format_report(score, params, suggestions)
    print(report)
