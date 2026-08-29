"""Authenticated tenant resolution for the SaaS API.

JWTs used by the SaaS API must carry the UUID of the row in the SQLAlchemy
``users`` table as their ``sub`` claim. Legacy offline auth uses a separate
SQLite schema and integer IDs; it must not be used for SaaS tenant routing.
"""
from __future__ import annotations

import uuid

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings

_bearer = HTTPBearer(auto_error=False)


def get_current_tenant_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """Return the authenticated SaaS tenant UUID from a bearer JWT."""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg],
        )
        subject = str(payload["sub"])
        tenant_id = str(uuid.UUID(subject))
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired") from exc
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    return tenant_id


def set_tenant_context(db: Session, tenant_id: str) -> None:
    """Set the PostgreSQL transaction-local tenant context used by RLS.

    SQLite has no session GUC, so this is intentionally a no-op there. The
    explicit ``tenant_id`` predicates in every route remain mandatory defense
    in depth for both databases.
    """
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
            {"tenant_id": tenant_id},
        )


def require_tenant_user(db: Session, tenant_id: str):
    """Load the authenticated SaaS user or return a consistent 401."""
    from ..models.user import User

    set_tenant_context(db, tenant_id)
    user = db.get(User, tenant_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(db: Session, tenant_id: str):
    """Load the authenticated user and verify they are an admin.

    Admins can cross tenant boundaries for support operations.
    Non-admins get 403 Forbidden.
    """
    user = require_tenant_user(db, tenant_id)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
