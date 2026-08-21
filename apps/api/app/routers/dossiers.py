"""Dossiers router — POST /v1/dossiers/feasibility (queued) + GET /jobs/{id}."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
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


@router.get("")
def list_dossiers(
    q: str | None = None,
    wilaya: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(_get_db),
):
    """List dossiers for current tenant (RLS) with search/filter/pagination."""
    from ..models.dossier import Dossier

    tenant_id = "00000000-0000-0000-0000-000000000000"
    query = db.query(Dossier).filter(Dossier.tenant_id == tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter((Dossier.project_name.ilike(like)) | (Dossier.beneficiary_name.ilike(like)) | (Dossier.activity_type.ilike(like)))
    if wilaya:
        query = query.filter(Dossier.wilaya == wilaya)
    if status:
        query = query.filter(Dossier.status == status)
    total = query.count()
    rows = query.order_by(Dossier.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "dossiers": [
            {
                "id": r.id,
                "project_name": r.project_name,
                "beneficiary_name": r.beneficiary_name,
                "wilaya": r.wilaya,
                "activity_type": r.activity_type,
                "total_cost": r.total_cost,
                "status": r.status,
                "pdf_r2_key": r.pdf_r2_key,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "tenant_id": r.tenant_id,  # exposed for RLS verification in admin
            }
            for r in rows
        ],
    }


@router.get("/{dossier_id}")
def get_dossier(dossier_id: str, db: Session = Depends(_get_db)):
    from ..models.dossier import Dossier

    tenant_id = "00000000-0000-0000-0000-000000000000"
    row = db.get(Dossier, dossier_id)
    if not row or row.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return {
        "id": row.id,
        "project_name": row.project_name,
        "beneficiary_name": row.beneficiary_name,
        "wilaya": row.wilaya,
        "activity_type": row.activity_type,
        "total_cost": row.total_cost,
        "status": row.status,
        "content": row.content,
        "pdf_r2_key": row.pdf_r2_key,
        "data_json": row.data_json,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


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


@router.get("/export-csv", response_class=Response)
def export_csv(ids: str = "", db: Session = Depends(_get_db)):
    """Export selected dossiers as CSV. Use ?ids=id1,id2,…"""
    from ..models.dossier import Dossier
    from fastapi.responses import Response

    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    if not id_list:
        raise HTTPException(status_code=400, detail="Parameter ?ids=id1,id2 required")
    tenant_id = "00000000-0000-0000-0000-000000000000"
    query = db.query(Dossier).filter(Dossier.tenant_id == tenant_id).filter(Dossier.id.in_(id_list))
    rows = query.all()
    lines = ["id,project_name,beneficiary_name,total_cost,status,created_at"]
    for r in rows:
        lines.append(
            f"{r.id},{r.project_name or ''},{r.beneficiary_name or ''},{r.total_cost or 0},{r.status or ''},{r.created_at.isoformat() if r.created_at else ''}"
        )
    csv_content = "\n".join(lines)
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="dossiers-{Date.now()}.csv"'})
