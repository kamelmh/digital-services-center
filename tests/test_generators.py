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


# ── G13 BNC Generator ─────────────────────────────────────────────────────────

class TestG13BNCGenerator:
    """G13 — IRG for liberal professions (BNC). 6-tranche annual barème."""

    def test_import(self):
        from g13_bnc_generator import G13Input, calculate_g13, generate_g13_html
        assert callable(calculate_g13)
        assert callable(generate_g13_html)

    def test_net_result_cascnos_auto(self):
        from g13_bnc_generator import calculate_g13
        # 2M revenue, 240k rent, no explicit CASNOS → auto 15% = 300k
        r = calculate_g13(
            annual_revenue=2_000_000, rent_expenses=240_000,
            equipment_expenses=0, insurance_expenses=0,
            other_expenses=0, depreciation=0,
        )
        assert r["net_result"] == 2_000_000 - 240_000 - 300_000

    def test_net_result_cascnos_explicit(self):
        from g13_bnc_generator import calculate_g13
        r = calculate_g13(
            annual_revenue=2_000_000, rent_expenses=0,
            equipment_expenses=0, insurance_expenses=0,
            other_expenses=0, depreciation=0,
            cascnos_contribution=300_000,
        )
        assert r["net_result"] == 1_700_000

    def test_irg_bareme_first_tranche(self):
        from g13_bnc_generator import calculate_g13
        # 400k revenue - 100k rent - 60k CASNOS(auto 15%) = net 240k → 0% tax
        r = calculate_g13(
            annual_revenue=400_000, rent_expenses=100_000,
            equipment_expenses=0, insurance_expenses=0,
            other_expenses=0, depreciation=0,
        )
        assert r["net_result"] == 240_000
        assert r["tax_annual"] == 0

    def test_tax_due_subtracts_advances(self):
        from g13_bnc_generator import calculate_g13
        r = calculate_g13(
            annual_revenue=2_000_000, rent_expenses=240_000,
            equipment_expenses=50_000, insurance_expenses=30_000,
            other_expenses=20_000, depreciation=15_000,
            cascnos_contribution=300_000, advance_payments=100_000,
        )
        assert r["net_result"] == 1_345_000
        assert abs(r["tax_due"] - (r["tax_annual"] - 100_000)) < 0.01

    def test_html_sections(self):
        from g13_bnc_generator import G13Input, calculate_g13, generate_g13_html
        data = G13Input(nif="123", name="T", profession="Consultant", annual_revenue=1_000_000)
        calc = calculate_g13(1_000_000, 0, 0, 0, 0, 0)
        calc = {**calc, "total_deductible_expenses": 150_000}
        html = generate_g13_html(data, calc)
        assert "IDENTIFICATION DU DÉCLARANT" in html
        assert "CALCUL DE L'IRG" in html
        assert "Signature du déclarant" in html


# ── CNRC F1 Generator ─────────────────────────────────────────────────────────

class TestCnrcF1Generator:
    """CNRC F1 — commercial registration (personne morale)."""

    def test_import(self):
        from cnrc_f1_generator import F1Data, AssocieData, calculate_f1, generate_f1
        assert callable(calculate_f1)
        assert callable(generate_f1)

    def test_parts_and_percentages(self):
        from cnrc_f1_generator import F1Data, AssocieData, calculate_f1
        d = F1Data(
            capital_social=1_000_000,
            associes=[
                AssocieData(parts_sociales=600, pourcentage=60.0),
                AssocieData(parts_sociales=400, pourcentage=40.0),
            ],
        )
        c = calculate_f1(d)
        assert c["total_parts"] == 1_000
        assert c["pct_sum"] == 100.0
        assert c["parts_valid"] is True
        assert c["capital_per_part"] == 1_000.0

    def test_apports_mismatch_flagged(self):
        from cnrc_f1_generator import F1Data, calculate_f1
        d = F1Data(capital_social=1_000_000, apports_numeraire=500_000, apports_nature=0)
        c = calculate_f1(d)
        assert c["apports_match"] is False

    def test_timbre_fiscal(self):
        from cnrc_f1_generator import F1Data, calculate_f1
        assert calculate_f1(F1Data())["timbre_cost"] == 4_000

    def test_html_sections(self):
        from cnrc_f1_generator import F1Data, AssocieData, generate_f1
        html = generate_f1(F1Data(
            denomination="SARL TEST",
            associes=[AssocieData(nom_prenom="A", parts_sociales=100, pourcentage=100)],
        ))
        assert "IDENTIFICATION DE LA SOCIÉTÉ" in html
        assert "ASSOCIÉS" in html
        assert "TIMBRE" in html.upper()


# ── DAS CNAS Generator ────────────────────────────────────────────────────────

class TestDasCnasGenerator:
    """DAS — CNAS annual salary declaration. Employer 25.5%, employee 9%."""

    def test_import(self):
        from das_cnas_generator import DASData, DASEmployee, calculate_das, generate_das
        assert callable(calculate_das)

    def test_contribution_rates(self):
        from das_cnas_generator import DASEmployee
        e = DASEmployee(salaire_brut_annuel=720_000)
        assert abs(e.cotisation_employeur - 720_000 * 0.255) < 0.01
        assert abs(e.cotisation_salariale - 720_000 * 0.09) < 0.01

    def test_totals(self):
        from das_cnas_generator import DASData, DASEmployee, calculate_das
        d = DASData(salaries=[
            DASEmployee(salaire_brut_annuel=720_000),
            DASEmployee(salaire_brut_annuel=420_000),
        ])
        c = calculate_das(d)
        assert c["n_salaries"] == 2
        assert c["masse_salariale_brute"] == 1_140_000
        assert abs(c["total_cotisations"] - 1_140_000 * 0.345) < 0.01

    def test_html_sections(self):
        from das_cnas_generator import DASData, generate_das
        html = generate_das(DASData(annee=2026, raison_sociale="T"))
        assert "DÉCLARATION ANNUELLE DES SALAIRES" in html
        assert "RÉCAPITULATIF DES COTISATIONS" in html


# ── SECU 01 Generator ─────────────────────────────────────────────────────────

class TestSecu01Generator:
    """SECU 01 — CNAS employer affiliation."""

    def test_import(self):
        from secu01_generator import Secu01Data, calculate_secu01, generate_secu01
        assert callable(calculate_secu01)

    def test_contribution_estimate(self):
        from secu01_generator import Secu01Data, calculate_secu01
        c = calculate_secu01(Secu01Data(salaire_mensuel_estime=60_000))
        assert c["cotisation_mensuelle_salariale"] == 5_400.0    # 9%
        assert c["cotisation_mensuelle_employeur"] == 15_300.0   # 25.5%
        assert c["cout_total_employeur_mensuel"] == 75_300.0

    def test_html_sections(self):
        from secu01_generator import Secu01Data, generate_secu01
        html = generate_secu01(Secu01Data(raison_sociale="T"))
        assert "DEMANDE D'AFFILIATION" in html
        assert "ESTIMATION DES COTISATIONS" in html


# ── ANAE Generator ────────────────────────────────────────────────────────────

class TestAnaeGenerator:
    """ANAE — auto-entrepreneur declaration. IFU 5% services / 12% production."""

    def test_import(self):
        from anae_generator import AnaeData, calculate_anae, generate_anae
        assert callable(calculate_anae)

    def test_ifu_rates(self):
        from anae_generator import AnaeData, calculate_anae
        assert calculate_anae(AnaeData(type_activite="Services", ca_annuel_prevu=1_000_000))["ifu_rate"] == 0.05
        assert calculate_anae(AnaeData(type_activite="Production / Vente", ca_annuel_prevu=1_000_000))["ifu_rate"] == 0.12

    def test_plafonds(self):
        from anae_generator import AnaeData, calculate_anae
        ok = calculate_anae(AnaeData(type_activite="Services", ca_annuel_prevu=5_000_000))
        over = calculate_anae(AnaeData(type_activite="Services", ca_annuel_prevu=5_000_001))
        prod = calculate_anae(AnaeData(type_activite="Production / Vente", ca_annuel_prevu=8_000_000))
        assert ok["plafond_ok"] and not over["plafond_ok"] and prod["plafond_ok"]

    def test_casnos_flat_and_load(self):
        from anae_generator import AnaeData, calculate_anae
        c = calculate_anae(AnaeData(type_activite="Services", ca_annuel_prevu=1_800_000))
        assert c["casnos_annual"] == 43_200
        assert c["ifu_annual"] == 90_000
        assert abs(c["total_charges"] - 133_200) < 0.01
        assert abs(c["effective_load"] - 7.4) < 0.01

    def test_html_sections(self):
        from anae_generator import AnaeData, generate_anae
        html = generate_anae(AnaeData(type_activite="Services"))
        assert "AUTO-ENTREPRENEUR" in html
        assert "ESTIMATION FINANCIÈRE" in html


# ── G15 Cessation Generator ───────────────────────────────────────────────────

class TestG15CessationGenerator:
    """G15 — cessation d'activité declaration."""

    def test_import(self):
        from g15_cessation_generator import G15Data, calculate_g15, generate_g15
        assert callable(calculate_g15)

    def test_duration_and_deadline(self):
        from g15_cessation_generator import G15Data, calculate_g15
        c = calculate_g15(G15Data(
            date_debut_activite="01/06/2018", date_cessation="31/12/2026",
            date_declaration="10/01/2027",
        ))
        assert c["duree_annees"] == 8.6
        assert c["deadline_declaration"] == "30/01/2027"
        assert c["is_late"] is False

    def test_late_declaration_flag(self):
        from g15_cessation_generator import G15Data, calculate_g15
        c = calculate_g15(G15Data(
            date_debut_activite="01/01/2020", date_cessation="01/01/2026",
            date_declaration="15/03/2026",
        ))
        assert c["is_late"] is True

    def test_final_settlement_by_regime(self):
        from g15_cessation_generator import G15Data, calculate_g15
        assert calculate_g15(G15Data(regime_fiscal="Régime réel"))["final_settlement_required"] is True
        assert calculate_g15(G15Data(regime_fiscal="IFU / Auto-entrepreneur"))["final_settlement_required"] is False

    def test_html_sections(self):
        from g15_cessation_generator import G15Data, generate_g15
        html = generate_g15(G15Data(nom_raison_sociale="T", regime_fiscal="Régime réel"))
        assert "CESSATION D'ACTIVITÉ" in html
        assert "OBLIGATIONS FISCALES" in html


# ── NIS Generator ─────────────────────────────────────────────────────────────

class TestNisGenerator:
    """NIS — ONS statistical identification request."""

    def test_import(self):
        from nis_generator import NisData, calculate_nis, generate_nis
        assert callable(calculate_nis)

    def test_completeness_full(self):
        from nis_generator import NisData, calculate_nis
        c = calculate_nis(NisData(
            nom_raison_sociale="X", nif="1", rc="r", activite_principale="a",
            adresse="ad", representant_nom="n", commune="c",
        ))
        assert c["completeness_pct"] == 100 and c["missing_fields"] == []

    def test_completeness_empty(self):
        from nis_generator import NisData, calculate_nis
        c = calculate_nis(NisData())
        assert c["completeness_pct"] == 0 and len(c["missing_fields"]) == 7

    def test_effectif_tranche(self):
        from nis_generator import NisData, calculate_nis
        assert calculate_nis(NisData(effectif_salarie=0))["effectif_tranche"] == "0 salarié"
        assert calculate_nis(NisData(effectif_salarie=5))["effectif_tranche"] == "1-9"
        assert calculate_nis(NisData(effectif_salarie=60))["effectif_tranche"] == "50-99"
        assert calculate_nis(NisData(effectif_salarie=150))["effectif_tranche"] == "100+"

    def test_auto_entrepreneur_flag(self):
        from nis_generator import NisData, calculate_nis
        assert calculate_nis(NisData(forme_juridique="Auto-entrepreneur"))["is_auto_entrepreneur"] is True
        assert calculate_nis(NisData(forme_juridique="SARL"))["is_auto_entrepreneur"] is False

    def test_html_sections(self):
        from nis_generator import NisData, generate_nis
        html = generate_nis(NisData())
        assert "Numéro d'Identification Statistique" in html
        assert "classification statistique" in html


# ── CNRC F2 Generator ─────────────────────────────────────────────────────────

class TestCnrcF2Generator:
    """CNRC F2 — individual merchant registration."""

    def test_import(self):
        from cnrc_f2_generator import F2Data, calculate_f2, generate_f2
        assert callable(calculate_f2)

    def test_identity_and_age(self):
        from cnrc_f2_generator import F2Data, calculate_f2
        c = calculate_f2(F2Data(nom="Mahi", prenom="Kamel", date_naissance="06/03/1996",
                                date_declaration="10/02/2026"))
        assert c["nom_complet"] == "Mahi Kamel"
        assert c["age"] == 30 and c["age_ok"] is True

    def test_married_community_needs_conjoint(self):
        from cnrc_f2_generator import F2Data, calculate_f2
        c = calculate_f2(F2Data(situation_matrimoniale="Marié(e)", regime_matrimonial="Communauté de biens"))
        assert c["needs_conjoint_info"] is True
        # Séparation de biens → no conjoint info needed
        c2 = calculate_f2(F2Data(situation_matrimoniale="Marié(e)", regime_matrimonial="Séparation de biens"))
        assert c2["needs_conjoint_info"] is False

    def test_bail_requirements(self):
        from cnrc_f2_generator import F2Data, calculate_f2
        c = calculate_f2(F2Data(nature_local="Local loué", duree_bail_annees=5))
        assert c["needs_bail"] is True
        c2 = calculate_f2(F2Data(nature_local="Propriété"))
        assert c2["needs_bail"] is False

    def test_timbre_fiscal(self):
        from cnrc_f2_generator import F2Data, calculate_f2
        assert calculate_f2(F2Data())["timbre_cost"] == 4_000

    def test_html_sections(self):
        from cnrc_f2_generator import F2Data, generate_f2
        html = generate_f2(F2Data(nom="A", prenom="B"))
        assert "PERSONNE PHYSIQUE" in html
        assert "LE FONDS DE COMMERCE" in html


# ── G4 Rental Generator ───────────────────────────────────────────────────────

class TestG4RentalGenerator:
    """G4 — rental income declaration. 30% abattement + annual IRG barème."""

    def test_import(self):
        from g4_rental_generator import RentalProperty, G4RentalData, calculate_g4_rental, generate_g4_rental
        assert callable(calculate_g4_rental)

    def test_loyer_annuel_prorated(self):
        from g4_rental_generator import RentalProperty
        assert RentalProperty(loyer_mensuel=25_000, mois_loues=12).loyer_annuel == 300_000
        assert RentalProperty(loyer_mensuel=40_000, mois_loues=9).loyer_annuel == 360_000

    def test_abattement_and_barème(self):
        from g4_rental_generator import G4RentalData, RentalProperty, calculate_g4_rental
        c = calculate_g4_rental(G4RentalData(propriétés=[
            RentalProperty(loyer_mensuel=25_000, mois_loues=12),
            RentalProperty(loyer_mensuel=40_000, mois_loues=9),
            RentalProperty(loyer_mensuel=15_000, mois_loues=12),
        ]))
        assert c["total_brut"] == 840_000
        assert c["abattement"] == 252_000          # 30%
        assert c["net_foncier"] == 588_000
        # IRG on 588k: 240k×0% + 240k×23% + 108k×27% = 55,200 + 29,160
        assert abs(c["irg_annuel"] - 84_360) < 0.01

    def test_solde_du_subtracts_acomptes(self):
        from g4_rental_generator import G4RentalData, RentalProperty, calculate_g4_rental
        c = calculate_g4_rental(G4RentalData(
            propriétés=[RentalProperty(loyer_mensuel=50_000)],
            acomptes_retenus=24_000,
        ))
        assert c["solde_du"] == c["irg_annuel"] - 24_000

    def test_first_tranche_zero_tax(self):
        from g4_rental_generator import G4RentalData, RentalProperty, calculate_g4_rental
        # 240k brut - 30% = 168k net → 0% tranche
        c = calculate_g4_rental(G4RentalData(propriétés=[RentalProperty(loyer_mensuel=20_000)]))
        assert c["net_foncier"] == 168_000
        assert c["irg_annuel"] == 0

    def test_html_sections(self):
        from g4_rental_generator import G4RentalData, RentalProperty, generate_g4_rental
        html = generate_g4_rental(G4RentalData(
            propriétés=[RentalProperty(adresse="A", loyer_mensuel=10_000)],
        ))
        assert "REVENUS DE LOCATION" in html
        assert "LIQUIDATION DE L'IRG" in html
