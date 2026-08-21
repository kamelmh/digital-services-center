"""Dossiers router — POST /v1/dossiers/feasibility (queued) + GET /jobs/{id}."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.config import settings
from .entitlements import require_entitlement

router = APIRouter(prefix="/v1/dossiers", tags=["dossiers"])


class FeasibilityRequest(BaseModel):
    business_type: str  # e.g. "centre_services_num"
    location: str
    wilaya: str
    investment: int
    business_name: str | None = None


def _get_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from ..models.base import Base

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_current_user_optional():
    # Reuse existing auth.py logic if available; fallback to anonymous when AUTH_REQUIRED=0
    try:
        from auth import get_current_user_optional as _orig

        return _orig
    except Exception:
        return lambda: None


@router.post("/feasibility", status_code=202, dependencies=[Depends(require_entitlement("free"))])
def create_feasibility(req: FeasibilityRequest, db: Session = Depends(_get_db)):
    """Enqueue feasibility generation. Returns job_id for polling."""
    # Entitlement enforced via dependencies — free 1/mo, starter 10, pro/business fair-use

    from ..models.job import Job
    from ..models.user import User

    # For SaaS, resolve tenant from JWT; for local dev without auth, use first user or create ephemeral
    tenant_id = "00000000-0000-0000-0000-000000000000"
    try:
        # Try to get real user if auth is available
        from auth import get_current_user_optional
        from fastapi import Request

        # This router is called without Request injection, so we keep ephemeral tenant for MVP
        pass
    except Exception:
        pass

    # Ensure ephemeral tenant exists for local/dev (default free, upgrade via billing)
    if tenant_id == "00000000-0000-0000-0000-000000000000":
        anon = db.get(User, tenant_id)
        if not anon:
            from auth import hash_password

            anon = User(
                id=tenant_id,
                email="anon@local",
                name="Local Dev",
                password_hash=hash_password("local-dev-not-used"),
                subscription="free",
            )
            db.add(anon)
            db.commit()

    job = Job(tenant_id=tenant_id, type="feasibility", status="queued", progress=0)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue RQ if Redis available, else run inline (sync fallback for local dev without Redis)
    try:
        import redis
        from rq import Queue

        q = Queue(settings.rq_queue_name, connection=redis.from_url(settings.redis_url))
        q.enqueue(
            "apps.api.app.workers.jobs.job_generate_feasibility",
            job.id,
            req.business_type,
            req.location,
            req.wilaya,
            req.investment,
            job_timeout=300,
        )
    except Exception as e:
        # Fallback: generate inline (blocks, but works without Redis — useful for tests)
        try:
            from ..workers.jobs import job_generate_feasibility

            job_generate_feasibility(job.id, req.business_type, req.location, req.wilaya, req.investment)
            db.refresh(job)
        except Exception as ie:
            job.status = "failed"
            job.error = str(ie)[:500]
            db.commit()
            raise HTTPException(status_code=500, detail=f"Enqueue + inline fallback failed: {e} / {ie}")

    return {"job_id": job.id, "status": job.status, "message": "Queued — poll GET /v1/jobs/{job_id}"}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(_get_db)):
    from ..models.job import Job

    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "type": job.type,
        "status": job.status,
        "progress": job.progress,
        "provider": job.provider,
        "result": job.result,
        "error": job.error,
        "dossier_id": job.dossier_id,
    }
