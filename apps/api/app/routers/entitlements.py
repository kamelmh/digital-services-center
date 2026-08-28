"""Entitlement middleware — free 1/mo, starter 10, pro/business fair-use."""
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.config import settings
from .billing import PLANS
from .billing import _get_db as _get_db_billing
from ..core.tenant import get_current_tenant_id, require_tenant_user


def require_entitlement(min_plan: str = "free"):
    """Dependency that checks quota and plan tier. Use as Depends(require_entitlement('pro'))."""
    order = {"free": 0, "starter": 1, "pro": 2, "business": 3}

    def _check(
        tenant_id: str = Depends(get_current_tenant_id),
        db: Session = Depends(_get_db_billing),
    ):
        user = require_tenant_user(db, tenant_id)
        user_rank = order.get(user.subscription, 0)
        required_rank = order.get(min_plan, 0)
        if user_rank < required_rank:
            raise HTTPException(status_code=402, detail=f"Plan {user.subscription} insufficient — requires {min_plan}")

        # Quota check (monthly)
        if user.subscription in PLANS:
            quota = PLANS[user.subscription]["quota"]
            # Count jobs created this month
            from ..models.job import Job
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            count = db.query(func.count(Job.id)).filter(Job.tenant_id == user.id, Job.created_at >= month_start).scalar() or 0
            if count >= quota:
                raise HTTPException(status_code=429, detail=f"Quota exceeded: {quota} docs/month for {user.subscription}. Upgrade at /pricing")
        return user

    return _check
