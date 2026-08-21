"""Quality Scorer — Validate generator outputs before packaging into dossier.

Runs 6 checks on each generated section:
1. Word count (minimum threshold)
2. Section coverage (required sections present)
3. Number specificity (contains actual figures, not placeholders)
4. Language consistency (correct language for section type)
5. Structure (has headings, not just a wall of text)
6. Financial viability (VAN/TRI sign — flags negative VAN/TRI as requiring review)

Returns a QualityReport with per-check scores and overall grade.
"""

import re
from dataclasses import dataclass, field
from typing import Any


# ── Thresholds ──────────────────────────────────────────────────────────────
MIN_WORDS = {
    "feasibility": 1500,
    "business_plan": 1200,
    "market_research": 1000,
    "financial_projections": 800,
    "marketing_plan": 800,
    "social_media": 200,
    "tax_declaration": 400,
    "invoice": 50,
    "quote": 50,
}

REQUIRED_SECTIONS = {
    "feasibility": [
        "وصف المشروع", "دراسة السوق", "الدراسة الفنية",
        "الدراسة المالية", "جدوى المشروع",
    ],
    "business_plan": [
        "الم Executive Summary", "رؤية المشروع", "المنتجات",
        "دراسة السوق", "الخطة التسويقية", "الخطة التشغيلية",
        "التوقعات المالية", "تحليل المخاطر",
    ],
    "market_research": [
        "نظرة عامة", "تحليل السوق", "المنافسة",
        "الفرص", "خطة التسويق",
    ],
    "financial_projections": [
        "الاستثمارات", "التكاليف", "الإيرادات",
        "تحليل الربحية", "التدفقات النقدية",
    ],
}


@dataclass
class CheckResult:
    name: str
    passed: bool
    score: float  # 0.0 to 1.0
    detail: str


@dataclass
class QualityReport:
    generator: str
    checks: list[CheckResult] = field(default_factory=list)
    overall_score: float = 0.0
    grade: str = "F"
    passed: bool = False

    def add(self, check: CheckResult):
        self.checks.append(check)
        self._recalculate()

    def _recalculate(self):
        if not self.checks:
            return
        self.overall_score = sum(c.score for c in self.checks) / len(self.checks)
        if self.overall_score >= 0.9:
            self.grade = "A"
        elif self.overall_score >= 0.8:
            self.grade = "B"
        elif self.overall_score >= 0.7:
            self.grade = "C"
        elif self.overall_score >= 0.5:
            self.grade = "D"
        else:
            self.grade = "F"
        self.passed = self.overall_score >= 0.6


class QualityScorer:
    """Validate generator outputs."""

    def score(self, generator: str, content: str, metadata: dict = None) -> QualityReport:
        """Run all applicable checks and return a report."""
        report = QualityReport(generator=generator)

        # 1. Word count
        words = len(content.split())
        min_w = MIN_WORDS.get(generator, 300)
        ratio = min(words / min_w, 1.0) if min_w > 0 else 1.0
        report.add(CheckResult(
            name="word_count",
            passed=words >= min_w,
            score=ratio,
            detail=f"{words:,} words (min: {min_w:,})",
        ))

        # 2. Section coverage
        required = REQUIRED_SECTIONS.get(generator, [])
        if required:
            found = sum(1 for s in required if s in content)
            coverage = found / len(required)
            report.add(CheckResult(
                name="section_coverage",
                passed=coverage >= 0.6,
                score=coverage,
                detail=f"{found}/{len(required)} required sections found",
            ))

        # 3. Number specificity (contains digits)
        numbers_found = len(re.findall(r"\d[\d,]*\.?\d*", content))
        has_numbers = numbers_found >= 5
        number_score = min(numbers_found / 20, 1.0)
        report.add(CheckResult(
            name="number_specificity",
            passed=has_numbers,
            score=number_score,
            detail=f"{numbers_found} numerical figures found",
        ))

        # 4. Language consistency (check for mixed Arabic/French in wrong places)
        arabic_chars = len(re.findall(r"[\u0600-\u06FF]", content))
        latin_chars = len(re.findall(r"[a-zA-Z]", content))
        total = arabic_chars + latin_chars
        if total > 0:
            arabic_ratio = arabic_chars / total
        else:
            arabic_ratio = 0

        # Most DSC generators output Arabic — expect >30% Arabic
        if generator in ("feasibility", "business_plan", "market_research",
                         "financial_projections", "marketing_plan",
                         "social_media", "tax_declaration"):
            lang_score = 1.0 if arabic_ratio > 0.3 else arabic_ratio / 0.3
        else:
            lang_score = 1.0  # invoices/quotes can be mixed

        report.add(CheckResult(
            name="language_consistency",
            passed=lang_score >= 0.5,
            score=lang_score,
            detail=f"Arabic: {arabic_ratio:.0%}, Latin: {1-arabic_ratio:.0%}",
        ))

        # 5. Structure (has headings)
        headings = len(re.findall(r"^#{1,3}\s|^\*\*[^*]+\*\*", content, re.MULTILINE))
        structure_score = min(headings / 5, 1.0)
        report.add(CheckResult(
            name="structure",
            passed=headings >= 3,
            score=structure_score,
            detail=f"{headings} headings/bold markers found",
        ))

        # 6. Financial viability (negative VAN/TRI requires review)
        # Robust parsing: optional whitespace, both ASCII hyphen '-' (U+002D) and
        # Unicode minus '−' (U+2212). Tests: VAN: -3, VAN: −3, TRI: -44.39%, TRI: −44.39%
        van_negative = False
        tri_negative = False
        van_match = None
        tri_match = None
        # VAN pattern: handles "VAN: -3", "VAN : −3", "VAN-3", and "VAN (…): **-3 700 943 دج**"
        # Primary: requires "**" (markdown bold) to avoid matching methodology polish text
        van_m = re.search(r"VAN[^:\n]*:\s*\*\*\s*([\u2212\-]?\s*[\d][\d\s,\.]*)", content, re.IGNORECASE)
        if not van_m:
            van_m = re.search(r"VAN\s*:?\s*([\u2212\-]?\s*[\d][\d\s,\.]*)", content, re.IGNORECASE)
        if van_m:
            raw_van = van_m.group(1).replace("\u2212", "-").replace(" ", "").replace(",", "")
            try:
                van_val = float(raw_van)
                van_negative = van_val < 0
                van_match = van_m
            except ValueError:
                van_negative = False
        tri_m = re.search(r"TRI[^:\n]*:\s*\*\*\s*([\u2212\-]?\s*[\d][\d\s,\.]*)\s*%?", content, re.IGNORECASE)
        if not tri_m:
            tri_m = re.search(r"TRI\s*:?\s*([\u2212\-]?\s*[\d][\d\s,\.]*)\s*%?", content, re.IGNORECASE)
        if tri_m:
            raw_tri = tri_m.group(1).replace("\u2212", "-").replace(" ", "").replace(",", "")
            try:
                tri_val = float(raw_tri)
                tri_negative = tri_val < 0
                tri_match = tri_m
            except ValueError:
                tri_negative = False

        if van_negative or tri_negative:
            fin_score = 0.3
            parts = []
            if van_negative:
                parts.append(f"VAN {van_match.group(1).strip()} < 0")
            if tri_negative:
                parts.append(f"TRI {tri_match.group(1).strip()} < 0%")
            detail = "; ".join(parts) + " — requires revised assumptions"
        else:
            fin_score = 1.0
            # Distinguish "no data" from "viable" — but treat missing as viable for non-financial docs
            if van_match or tri_match:
                detail = "Project financially viable (VAN/TRI >= 0)"
            else:
                detail = "No VAN/TRI found — financial viability not applicable"

        report.add(CheckResult(
            name="financial_viability",
            passed=not (van_negative or tri_negative),
            score=fin_score,
            detail=detail,
        ))

        return report


def score_all(results: dict[str, str]) -> dict[str, QualityReport]:
    """Score multiple generator outputs at once.
    
    Args:
        results: {generator_name: output_content}
    
    Returns:
        {generator_name: QualityReport}
    """
    scorer = QualityScorer()
    reports = {}
    for gen, content in results.items():
        reports[gen] = scorer.score(gen, content)
    return reports


def format_report(report: QualityReport) -> str:
    """Format a quality report as readable text."""
    lines = [
        f"Quality Report: {report.generator}",
        f"Overall: {report.overall_score:.0%} ({report.grade}) — {'PASS' if report.passed else 'FAIL'}",
        "-" * 50,
    ]
    for check in report.checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(f"  [{status}] {check.name}: {check.detail} ({check.score:.0%})")
    return "\n".join(lines)
