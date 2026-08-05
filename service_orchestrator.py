"""Service Orchestrator — One-click dossier generation pipeline.

Runs: feasibility → financial projections → AAPI scoring → quality gate → unified PDF
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Any

# Ensure parent dir is importable
sys.path.insert(0, str(Path(__file__).parent))

from business_defaults import get_defaults, estimate_profitability
from quality_scorer import QualityScorer, QualityReport, format_report
from training_hook import hook_generation


class OrchestratorError(Exception):
    pass


class ServiceOrchestrator:
    """Generate complete client dossier in one call."""

    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider
        self.model = model
        self.scorer = QualityScorer()
        self.output_dir = Path(__file__).parent / "generated_output"
        self.output_dir.mkdir(exist_ok=True)
        self._progress_callback = None

    def on_progress(self, callback):
        """Set a progress callback: callback(stage, message, progress_pct)."""
        self._progress_callback = callback

    def _emit(self, stage: str, msg: str, pct: float):
        if self._progress_callback:
            self._progress_callback(stage, msg, pct)
        print(f"  [{pct:3.0f}%] {stage}: {msg}", file=sys.stderr)

    def generate_dossier(
        self,
        business_type: str,
        location: str,
        wilaya: str,
        investment: int,
        client_name: str = "Client",
        monthly_revenue: int = None,
        skip_quality: bool = False,
    ) -> dict[str, Any]:
        """Generate complete client dossier.

        Returns dict with:
            - feasibility: dict (sections, content)
            - financials: dict (content, sections)
            - aapi: dict (score, suggestions)
            - quality: dict (reports per section)
            - pdf_path: str (path to unified PDF)
            - metadata: dict (timing, defaults used)
        """
        start = time.time()
        defaults = get_defaults(business_type)

        # Auto-fill from defaults
        if monthly_revenue is None:
            from business_defaults import estimate_monthly_revenue
            monthly_revenue = estimate_monthly_revenue(business_type, investment)

        results = {"metadata": {
            "business_type": business_type,
            "location": location,
            "wilaya": wilaya,
            "investment": investment,
            "client_name": client_name,
            "defaults_used": defaults,
            "monthly_revenue_estimated": monthly_revenue,
        }}

        # ── Stage 1: Feasibility Study ──────────────────────────────────────
        self._emit("Feasibility", "Generating 9-section study...", 10)
        try:
            from feasibility_generator import FeasibilityGenerator
            gen = FeasibilityGenerator(provider=self.provider, model=self.model)
            feasibility = gen.generate_full_study(business_type, location, wilaya, investment)
            results["feasibility"] = feasibility
            self._emit("Feasibility", "Done", 25)
        except Exception as e:
            self._emit("Feasibility", f"Error: {e}", 25)
            results["feasibility"] = {"error": str(e), "sections": {}}

        # ── Stage 2: Financial Projections ───────────────────────────────────
        self._emit("Financials", "Generating 5-year projections...", 30)
        try:
            from financial_projections_generator import FinancialProjectionsGenerator
            fin_gen = FinancialProjectionsGenerator(provider=self.provider, model=self.model)
            profitability = estimate_profitability(business_type, investment, monthly_revenue)
            financials = fin_gen.generate(
                business_type=business_type,
                business_name=client_name,
                investment=investment,
                monthly_revenue_estimate=monthly_revenue,
            )
            results["financials"] = financials
            results["profitability_estimate"] = profitability
            self._emit("Financials", "Done", 50)
        except Exception as e:
            self._emit("Financials", f"Error: {e}", 50)
            results["financials"] = {"error": str(e), "content": ""}

        # ── Stage 3: AAPI Scoring ───────────────────────────────────────────
        self._emit("AAPI", "Scoring project...", 55)
        try:
            from aapi_optimizer import AAAPIOptimizer
            optimizer = AAAPIOptimizer()
            aapi_params = {
                "activity_priority": defaults["aapi_priority"],
                "investment_amount": investment,
                "employees": (defaults["staff_range"][0] + defaults["staff_range"][1]) // 2,
                "equity_ratio": 0.65,
                "local_integration": 50,
                "cdd_ratio": 0.10,
                "has_extension": False,
                "export_ratio": 0,
            }
            score = optimizer.score_project(aapi_params)
            suggestions = optimizer.optimize(score, aapi_params)
            results["aapi"] = {
                "total": score.total,
                "percentage": score.percentage,
                "rating": score.rating,
                "details": {
                    "activity_type": score.activity_type,
                    "investment_amount": score.investment_amount,
                    "employment": score.employment,
                    "equity_contribution": score.equity_contribution,
                    "local_content": score.local_content,
                    "employment_permanence": score.employment_permanence,
                    "investment_extension": score.investment_extension,
                    "export_diversification": score.export_diversification,
                },
                "suggestions": suggestions,
                "params_used": aapi_params,
            }
            self._emit("AAPI", f"Score: {score.total}/1500 ({score.rating})", 65)
        except Exception as e:
            self._emit("AAPI", f"Error: {e}", 65)
            results["aapi"] = {"error": str(e), "total": 0}

        # ── Stage 4: Quality Gate ────────────────────────────────────────────
        if not skip_quality:
            self._emit("Quality", "Running quality checks...", 70)
            quality_reports = {}
            if "error" not in results.get("feasibility", {}):
                feas_content = results["feasibility"].get("content", "")
                if not feas_content:
                    feas_content = "\n\n".join(
                        f"## {k}\n\n{v}" for k, v in results["feasibility"].get("sections", {}).items()
                    )
                quality_reports["feasibility"] = self.scorer.score("feasibility", feas_content)

            if "error" not in results.get("financials", {}):
                fin_content = results["financials"].get("content", "")
                quality_reports["financial_projections"] = self.scorer.score("financial_projections", fin_content)

            results["quality"] = quality_reports
            passed = sum(1 for r in quality_reports.values() if r.passed)
            total = len(quality_reports)
            self._emit("Quality", f"{passed}/{total} sections passed", 80)
        else:
            results["quality"] = {}

        # ── Stage 5: Generate Unified PDF ────────────────────────────────────
        self._emit("PDF", "Compiling unified dossier...", 85)
        try:
            pdf_path = self._compile_pdf(results, client_name, business_type, wilaya, investment)
            results["pdf_path"] = pdf_path
            self._emit("PDF", f"Saved: {Path(pdf_path).name}", 95)
        except Exception as e:
            self._emit("PDF", f"Error: {e}", 95)
            results["pdf_path"] = None

        # ── Stage 6: Save Training Data ──────────────────────────────────────
        self._emit("Training", "Saving generation data...", 98)
        try:
            hook_generation(
                generator="dossier",
                input_params={
                    "business_type": business_type,
                    "location": location,
                    "wilaya": wilaya,
                    "investment": investment,
                    "client_name": client_name,
                },
                output_content=json.dumps({
                    "feasibility_sections": len(results.get("feasibility", {}).get("sections", {})),
                    "aapi_score": results.get("aapi", {}).get("total", 0),
                    "quality_grades": {k: v.grade for k, v in results.get("quality", {}).items()},
                }),
                metadata={
                    "provider": self.provider,
                    "model": self.model,
                    "duration_seconds": time.time() - start,
                },
            )
        except Exception:
            pass

        elapsed = time.time() - start
        results["metadata"]["elapsed_seconds"] = round(elapsed, 1)
        self._emit("Done", f"Dossier complete in {elapsed:.1f}s", 100)

        return results

    def _compile_pdf(self, results: dict, client_name: str, business_type: str,
                     wilaya: str, investment: int) -> str:
        """Compile all results into a single professional PDF."""
        from unified_dossier_pdf import UnifiedDossierPDF

        compiler = UnifiedDossierPDF()
        return compiler.compile(
            client_name=client_name,
            business_type=business_type,
            wilaya=wilaya,
            investment=investment,
            feasibility=results.get("feasibility", {}),
            financials=results.get("financials", {}),
            aapi=results.get("aapi", {}),
            quality=results.get("quality", {}),
            profitability=results.get("profitability_estimate", {}),
        )


# ── CLI Entry Point ─────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="DSC Service Orchestrator")
    parser.add_argument("--type", required=True, help="Business type (e.g. quincaillerie)")
    parser.add_argument("--location", required=True, help="City/location")
    parser.add_argument("--wilaya", required=True, help="Wilaya name")
    parser.add_argument("--investment", type=int, required=True, help="Investment in DZD")
    parser.add_argument("--client", default="Client", help="Client name")
    parser.add_argument("--revenue", type=int, default=None, help="Monthly revenue (auto-estimated if omitted)")
    parser.add_argument("--provider", default=None, help="LLM provider")
    parser.add_argument("--model", default=None, help="LLM model")
    parser.add_argument("--skip-quality", action="store_true", help="Skip quality checks")
    args = parser.parse_args()

    orch = ServiceOrchestrator(provider=args.provider, model=args.model)
    orch.on_progress(lambda s, m, p: print(f"[{p:3.0f}%] {s}: {m}"))

    results = orch.generate_dossier(
        business_type=args.type,
        location=args.location,
        wilaya=args.wilaya,
        investment=args.investment,
        client_name=args.client,
        monthly_revenue=args.revenue,
        skip_quality=args.skip_quality,
    )

    if results.get("pdf_path"):
        print(f"\nPDF: {results['pdf_path']}")
    else:
        print("\nPDF generation failed")

    print(f"Time: {results['metadata']['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
