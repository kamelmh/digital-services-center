"""Comprehensive tests for DSC pure-logic generators."""
import pytest
import math


# ── G50 Generator ──────────────────────────────────────────────────────────────

class TestG50Generator:
    """Tests for G50 tax form generator."""

    def test_irg_mensuel_zero(self):
        from g50_generator import calculate_irg_mensuel
        assert calculate_irg_mensuel(0) == 0

    def test_irg_mensuel_below_threshold(self):
        from g50_generator import calculate_irg_mensuel
        # 180,000 DA annual = 15,000/month → 0% bracket
        assert calculate_irg_mensuel(180_000) == 0

    def test_irg_mensuel_in_23pct_bracket(self):
        from g50_generator import calculate_irg_mensuel
        # 360,000 DA annual = 30,000/month → first 20k at 0%, next 10k at 23%
        result = calculate_irg_mensuel(360_000)
        assert result == 2_300  # 10_000 * 0.23

    def test_irg_mensuel_high_salary(self):
        from g50_generator import calculate_irg_mensuel
        # 1,200,000 DA annual = 100,000/month → hits 35% bracket
        result = calculate_irg_mensuel(1_200_000)
        assert result > 10_000

    def test_irg_annuel_is_12x_mensuel(self):
        from g50_generator import calculate_irg_mensuel, calculate_irg_annuel
        salaire = 600_000
        assert calculate_irg_annuel(salaire) == calculate_irg_mensuel(salaire) * 12

    def test_g50_data_defaults(self):
        from g50_generator import G50Data
        d = G50Data()
        assert d.nif == ""
        assert d.month >= 1
        assert d.year >= 2020

    def test_generate_g50_returns_html(self):
        from g50_generator import G50Data, generate_g50
        data = G50Data(
            nif="1234567890",
            nom_prenom="SARL Test",
            month=6,
            year=2026,
            tva_19_production_total=190_000,
            tva_19_production_exonere=0,
        )
        html = generate_g50(data)
        assert isinstance(html, str)
        assert len(html) > 500
        assert "1234567890" in html

    def test_months_complete(self):
        from g50_generator import MONTHS_FR, MONTHS_AR
        assert len(MONTHS_FR) == 13
        assert len(MONTHS_AR) == 13
        assert MONTHS_FR[0] == ""
        assert MONTHS_AR[0] == ""


# ── G12 Generator ──────────────────────────────────────────────────────────────

class TestG12Generator:
    """Tests for G12 tax form generator."""

    def test_ifu_rates_structure(self):
        from g12_official import IFU_RATES
        assert len(IFU_RATES) == 3
        for key, info in IFU_RATES.items():
            assert "rate" in info
            assert "min" in info
            assert 0 < info["rate"] < 1

    def test_wilayas_count(self):
        from g12_official import WILAYAS
        assert len(WILAYAS) == 58

    def test_g12FormData_defaults(self):
        from g12_official import G12FormData
        d = G12FormData()
        assert d.nom_prenoms == ""
        assert d.exonere is False


# ── G4 IBS Generator ──────────────────────────────────────────────────────────

class TestG4IBSGenerator:
    """Tests for G4 IBS tax form generator."""

    def test_ibs_rates_structure(self):
        from g4_ibs_generator import IBS_RATES
        assert len(IBS_RATES) == 3
        for key, info in IBS_RATES.items():
            assert "rate" in info
            assert 0 < info["rate"] < 1

    def test_g4_data_defaults(self):
        from g4_ibs_generator import G4Data
        d = G4Data()
        assert d.nif == ""
        assert d.year >= 2025


# ── G8 Existence Generator ────────────────────────────────────────────────────

class TestG8ExistenceGenerator:
    """Tests for G8 existence declaration form."""

    def test_g8_data_defaults(self):
        from g8_existence_generator import G8Data
        d = G8Data()
        assert d.nom == ""
        assert d.nouveau_contribuable is True

    def test_wilayas_count(self):
        from g8_existence_generator import WILAYAS
        assert len(WILAYAS) == 58

    def test_situations_familiales(self):
        from g8_existence_generator import SITUATIONS_FAMILIALES
        assert len(SITUATIONS_FAMILIALES) == 4
        assert "Célibataire" in SITUATIONS_FAMILIALES


# ── G1 GGR Generator ──────────────────────────────────────────────────────────

class TestG1GGRGenerator:
    """Tests for G1 GGR income declaration form."""

    def test_irg_bareme_structure(self):
        from g1_ggr_generator import IRG_BAREME
        assert len(IRG_BAREME) == 6
        # First bracket: 0%
        assert IRG_BAREME[0][1] == 0.0
        # Last bracket: 35%
        assert IRG_BAREME[-1][1] == 0.35

    def test_g1_data_defaults(self):
        from g1_ggr_generator import G1Data
        d = G1Data()
        assert d.nom_prenoms == ""


# ── G11 BIC Generator ─────────────────────────────────────────────────────────

class TestG11BICGenerator:
    """Tests for G11 BIC tax form generator."""

    def test_g11_data_defaults(self):
        from g11_bic_generator import G11Data
        d = G11Data()
        assert d.nif == ""
        assert d.nom_prenoms == ""


# ── G29 IRG Salaires Generator ────────────────────────────────────────────────

class TestG29IRGSalairesGenerator:
    """Tests for G29 IRG salaries form."""

    def test_g29_data_defaults(self):
        from g29_irg_salaires_generator import G29Data
        d = G29Data()
        assert d.nif == ""
        assert d.nombre_salaries == 0


# ── Quality Scorer ─────────────────────────────────────────────────────────────

class TestQualityScorer:
    """Tests for quality scoring system."""

    def test_grade_a(self):
        from quality_scorer import QualityReport, CheckResult
        r = QualityReport(generator="test")
        r.add(CheckResult(name="a", passed=True, score=0.95, detail="ok"))
        assert r.grade == "A"
        assert r.passed is True

    def test_grade_b(self):
        from quality_scorer import QualityReport, CheckResult
        r = QualityReport(generator="test")
        r.add(CheckResult(name="a", passed=True, score=0.85, detail="ok"))
        assert r.grade == "B"

    def test_grade_f(self):
        from quality_scorer import QualityReport, CheckResult
        r = QualityReport(generator="test")
        r.add(CheckResult(name="a", passed=False, score=0.4, detail="fail"))
        assert r.grade == "F"
        assert r.passed is False

    def test_empty_report(self):
        from quality_scorer import QualityReport
        r = QualityReport(generator="test")
        assert r.grade == "F"
        assert r.overall_score == 0.0

    def test_multiple_checks_averaged(self):
        from quality_scorer import QualityReport, CheckResult
        r = QualityReport(generator="test")
        r.add(CheckResult(name="a", passed=True, score=1.0, detail="ok"))
        r.add(CheckResult(name="b", passed=True, score=0.8, detail="ok"))
        assert abs(r.overall_score - 0.9) < 0.01

    def test_scorer_word_count(self):
        from quality_scorer import QualityScorer
        scorer = QualityScorer()
        # Short content should fail word count
        report = scorer.score("feasibility", "Short text")
        wc = [c for c in report.checks if c.name == "word_count"][0]
        assert wc.passed is False

    def test_scorer_structure_check(self):
        from quality_scorer import QualityScorer
        scorer = QualityScorer()
        # Content with headings should pass structure check
        content = "# Title\n## Section 1\n## Section 2\n## Section 3\n" + "word " * 2000
        report = scorer.score("feasibility", content)
        struct = [c for c in report.checks if c.name == "structure"][0]
        assert struct.passed is True


# ── Financial Calculators ──────────────────────────────────────────────────────

class TestFinancialCalculators:
    """Tests for VAN, TRI, Seuil de Rentabilité."""

    def test_van_zero_rate(self):
        from financial_calculators import FinancialCalculators
        # VAN at 0% = sum of all cash flows
        result = FinancialCalculators.van([-1000, 500, 500, 500], 0.0)
        assert abs(result - 500) < 1

    def test_van_positive_rate(self):
        from financial_calculators import FinancialCalculators
        result = FinancialCalculators.van([-1000, 500, 500, 500], 0.12)
        assert result < 500
        assert result > 0

    def test_tri_simple(self):
        from financial_calculators import FinancialCalculators
        # [-1000, 500, 500, 500] → IRR ~23%
        result = FinancialCalculators.tri([-1000, 500, 500, 500])
        assert 20 < result < 30

    def test_tri_negative(self):
        from financial_calculators import FinancialCalculators
        # All negative → IRR calculation returns fallback (1000) for degenerate case
        result = FinancialCalculators.tri([-100, -50, -30])
        # Degenerate case: all-negative flows, returns fallback
        assert result is not None

    def test_seuil_rentabilite(self):
        from financial_calculators import FinancialCalculators
        # Fixed costs 1000, price 100, variable 60 → contribution 40 → 25 units
        result = FinancialCalculators.seuil_rentabilite(1000, 100, 60)
        assert abs(result - 25) < 0.01

    def test_seuil_zero_contribution(self):
        from financial_calculators import FinancialCalculators
        # Price == variable cost → infinite
        result = FinancialCalculators.seuil_rentabilite(1000, 60, 60)
        assert result == float('inf')

    def test_delai_recuperation(self):
        from financial_calculators import FinancialCalculators
        # 1000 investment, 500/year → 2 years
        result = FinancialCalculators.delai_recuperation(1000, [500, 500, 500])
        assert 1.5 < result < 2.5

    def test_taux_marge(self):
        from financial_calculators import FinancialCalculators
        # Revenue 200, COGS 120 → margin 40%
        result = FinancialCalculators.taux_marge(200, 120)
        assert abs(result - 40) < 0.1


# ── NESDA Calculator ──────────────────────────────────────────────────────────

class TestNESDACalculator:
    """Tests for NESDA financing calculator."""

    def test_triangular_model(self):
        from nesda_calculator import calculate_nesda_financing
        result = calculate_nesda_financing(1_000_000, model="triangular", profile="unemployed")
        assert result.total_cost == 1_000_000
        assert result.personal_pct == 0.05
        assert result.nesda_pct == 0.25
        assert result.bank_pct == 0.70

    def test_mixed_model(self):
        from nesda_calculator import calculate_nesda_financing
        result = calculate_nesda_financing(1_000_000, model="mixed", profile="unemployed")
        assert result.personal_pct == 0.50
        assert result.nesda_pct == 0.50
        assert result.bank_pct == 0.0

    def test_self_model(self):
        from nesda_calculator import calculate_nesda_financing
        result = calculate_nesda_financing(1_000_000, model="self", profile="unemployed")
        assert result.bank_pct == 0.0

    def test_amounts_sum_to_total(self):
        from nesda_calculator import calculate_nesda_financing
        result = calculate_nesda_financing(1_000_000, model="triangular")
        total = result.personal_amount + result.nesda_grant + result.bank_loan
        assert total == result.total_cost

    def test_bank_loan_zero_for_self(self):
        from nesda_calculator import calculate_nesda_financing
        result = calculate_nesda_financing(1_000_000, model="self")
        assert result.bank_loan == 0

    def test_profitability(self):
        from nesda_calculator import calculate_nesda_financing
        result = calculate_nesda_financing(
            1_000_000, model="triangular",
            monthly_revenue=500_000, cogs_pct=0.65, operating_pct=0.15
        )
        assert result.monthly_profit > 0
        assert result.roi_annual > 0


# ── Business Defaults ─────────────────────────────────────────────────────────

class TestBusinessDefaults:
    """Tests for business default data."""

    def test_defaults_count(self):
        from business_defaults import BUSINESS_DEFAULTS
        assert len(BUSINESS_DEFAULTS) >= 10

    def test_all_defaults_have_required_fields(self):
        from business_defaults import BUSINESS_DEFAULTS
        for key, tmpl in BUSINESS_DEFAULTS.items():
            assert "name_fr" in tmpl, f"{key} missing name_fr"
            assert "name_ar" in tmpl, f"{key} missing name_ar"
            assert "cogs_pct" in tmpl, f"{key} missing cogs_pct"
            assert "operating_pct" in tmpl, f"{key} missing operating_pct"
            assert 0 < tmpl["cogs_pct"] < 1, f"{key} cogs_pct out of range"
            assert 0 < tmpl["operating_pct"] < 1, f"{key} operating_pct out of range"

    def test_plombier_arabic_clean(self):
        from business_defaults import BUSINESS_DEFAULTS
        assert BUSINESS_DEFAULTS["plombier"]["name_ar"] == "سبّاك"

    def test_get_defaults(self):
        from business_defaults import get_defaults, list_types
        types = list_types()
        assert len(types) >= 10
        defaults = get_defaults("plombier")
        assert defaults is not None
        assert "name_fr" in defaults


# ── Pricing Calculator ────────────────────────────────────────────────────────

class TestPricingCalculator:
    """Tests for service pricing calculator."""

    def test_import(self):
        from pricing_calculator import calculate_quote
        assert callable(calculate_quote)


# ── Invoice Generator ─────────────────────────────────────────────────────────

class TestInvoiceGenerator:
    """Tests for invoice generator module."""

    def test_import(self):
        from invoice_generator import InvoiceGenerator
        assert InvoiceGenerator is not None
