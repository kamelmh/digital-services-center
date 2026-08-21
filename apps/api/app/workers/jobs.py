"""RQ jobs — LLM (60-90s) + offline fallback + ReportLab + R2."""
from pathlib import Path

from sqlalchemy.orm import Session

from ..core.config import settings


def _get_db():
    # Lazy import to avoid circular deps; supports both Postgres and SQLite fallback
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from ..models.base import Base

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    # For SQLite, Base already exists via dsc_utils; for Postgres, create via Alembic in prod
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    return sessionmaker(bind=engine)()


def _r2_upload(local_path: str, r2_key: str) -> str:
    if settings.storage_backend != "r2" or not settings.r2_bucket:
        return local_path
    try:
        import boto3

        s3 = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key,
            aws_secret_access_key=settings.r2_secret_key,
            region_name="auto",
        )
        s3.upload_file(local_path, settings.r2_bucket, r2_key)
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.r2_bucket, "Key": r2_key},
            ExpiresIn=settings.r2_presign_seconds,
        )
    except Exception as e:
        print(f"R2 upload failed, falling back to local: {e}")
        return local_path


def job_generate_feasibility(job_id: str, business_type: str, location: str, wilaya: str, investment: int):
    """RQ job: generate feasibility study (offline fallback if no LLM key)."""
    db: Session = _get_db()
    try:
        from ..models.job import Job
        from ..models.dossier import Dossier

        job = db.get(Job, job_id)
        if not job:
            return
        job.status = "running"
        job.progress = 5
        db.commit()

        # Try LLM, fallback to offline_templates
        try:
            from feasibility_generator import FeasibilityGenerator

            gen = FeasibilityGenerator(allow_offline=True)
            result = gen.generate_full_study(business_type, location, wilaya, investment)
            provider = gen.provider
        except Exception as e:
            # Offline fallback is already inside generate_full_study, but handle hard import error
            from offline_templates import feasibility_offline

            result = feasibility_offline(business_type, location, location, wilaya, investment)
            # Attach canonical financials for fallback
            try:
                from feasibility_generator import calculate_real_financials
                from feasibility_generator import BUSINESS_TEMPLATES

                tpl = BUSINESS_TEMPLATES.get(business_type, {})
                rf = calculate_real_financials(investment, {**tpl, "margin": [0.2, 0.3]}, wilaya)
                result["real_financials"] = {
                    "reference_van": rf["reference_van"],
                    "reference_tri": rf["reference_tri"],
                    "reference_seuil": rf["reference_seuil"],
                    "reference_delai": rf["reference_delai"],
                    "reference_taux_marge": rf["reference_taux_marge"],
                    "annual_revenue_est": rf["annual_revenue_est"],
                    "loan_payment": rf["loan_payment"],
                    "nesda_result": rf["nesda_result"],
                }
            except Exception:
                result["real_financials"] = {}
            provider = f"offline-fallback:{e.__class__.__name__}"

        job.progress = 70
        db.commit()

        # Quality gate (financial_viability already in quality_scorer)
        try:
            from quality_scorer import QualityScorer

            qr = QualityScorer().score("feasibility", result.get("content", ""))
            result["quality"] = {"grade": qr.grade, "score": qr.overall_score, "passed": qr.passed}
        except Exception:
            pass

        # Persist dossier — ensure data_json is JSON-serializable (NESDAFinancingResult etc.)
        import json as _json

        def _serializable(o):
            if hasattr(o, "__dict__"):
                return o.__dict__
            return str(o)

        try:
            serializable_result = _json.loads(_json.dumps(result, default=_serializable))
        except Exception:
            # Fallback: store only safe fields
            serializable_result = {
                "content": result.get("content", "")[:20000],
                "sections": list(result.get("sections", {}).keys()),
                "business_name": result.get("business_name"),
                "offline": result.get("offline"),
            }

        dossier = Dossier(
            tenant_id=job.tenant_id,
            project_name=result.get("business_name", location),
            beneficiary_name=result.get("business_name"),
            wilaya=wilaya,
            activity_type=business_type,
            total_cost=investment,
            content=result.get("content"),
            data_json=serializable_result,
            status="ready",
        )
        db.add(dossier)
        db.flush()

        # PDF — unified or business
        pdf_path = None
        try:
            from business_pdf_exporter import BusinessDocumentPDF

            exporter = BusinessDocumentPDF(output_dir=str(Path.cwd() / "generated_output"))
            rf = result.get("real_financials") or {}
            pdf_data = {
                "project_name": result.get("business_name", location),
                "business_type": business_type,
                "wilaya": wilaya,
                "investment_amount": investment,
                "sections": [{"title": k, "content": v} for k, v in result.get("sections", {}).items()],
                "real_financials": {
                    "van": rf.get("reference_van", 0),
                    "tri": (rf.get("reference_tri", 0) / 100.0) if rf.get("reference_tri") else 0,
                    "payback": rf.get("reference_delai", 0),
                    "breakeven": rf.get("reference_seuil", 0),
                    "net_margin_year1": rf.get("reference_taux_marge", 0),
                },
            }
            local_pdf = exporter.feasibility(pdf_data)
            r2_key = f"dossiers/{job.tenant_id}/{dossier.id}.pdf"
            pdf_url = _r2_upload(local_pdf, r2_key)
            dossier.pdf_r2_key = r2_key if settings.storage_backend == "r2" else local_pdf
            pdf_path = pdf_url
        except Exception as e:
            print(f"PDF failed: {e}")

        job.progress = 100
        job.status = "done"
        job.provider = provider
        job.result = {"dossier_id": dossier.id, "pdf_url": pdf_path, "quality": result.get("quality")}
        job.dossier_id = dossier.id
        db.commit()
    except Exception as e:
        try:
            job.status = "failed"
            job.error = str(e)[:500]
            db.commit()
        except Exception:
            pass
        raise
    finally:
        db.close()
