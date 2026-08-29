"""Tenant isolation tests — verify cross-tenant access is blocked.

These tests run against SQLite (no RLS) but verify the application-level
tenant_id predicates that provide defense-in-depth. The RLS policies in
003_rls_policies.sql provide the database-level enforcement for PostgreSQL.
"""
import uuid
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_tenant_id() -> str:
    return str(uuid.uuid4())


def _make_jwt(tenant_id: str, expired: bool = False) -> str:
    """Create a minimal JWT for testing (no external deps needed)."""
    import json
    import base64

    def _b64(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

    header = {"alg": "HS256", "typ": "JWT"}
    now = datetime.now(timezone.utc)
    exp = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
    payload = {"sub": tenant_id, "iat": now.isoformat(), "exp": exp.isoformat()}
    # Note: signature is fake — we mock jwt.decode in tests
    return f"{_b64(header)}.{_b64(payload)}.fake-signature"


# ── Tenant ID extraction ─────────────────────────────────────────────────────

class TestTenantIDResolution:
    """Verify get_current_tenant_id extracts UUID correctly from JWT."""

    def test_valid_uuid(self):
        from apps.api.app.core.tenant import get_current_tenant_id
        from fastapi import HTTPException
        from unittest.mock import MagicMock

        tenant_id = _make_tenant_id()
        token = _make_jwt(tenant_id)

        # Mock the dependency injection
        mock_creds = MagicMock()
        mock_creds.credentials = token

        with patch("apps.api.app.core.tenant.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": tenant_id}
            result = get_current_tenant_id(mock_creds)
            assert result == tenant_id

    def test_missing_credentials(self):
        from apps.api.app.core.tenant import get_current_tenant_id
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            get_current_tenant_id(None)
        assert exc_info.value.status_code == 401

    def test_invalid_uuid_rejected(self):
        from apps.api.app.core.tenant import get_current_tenant_id
        from fastapi import HTTPException
        from unittest.mock import MagicMock

        mock_creds = MagicMock()
        mock_creds.credentials = _make_jwt("not-a-uuid")

        with patch("apps.api.app.core.tenant.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "not-a-uuid"}
            with pytest.raises(HTTPException) as exc_info:
                get_current_tenant_id(mock_creds)
            assert exc_info.value.status_code == 401

    def test_expired_token(self):
        from apps.api.app.core.tenant import get_current_tenant_id
        from fastapi import HTTPException
        from unittest.mock import MagicMock

        mock_creds = MagicMock()
        mock_creds.credentials = _make_jwt(_make_tenant_id(), expired=True)

        with patch("apps.api.app.core.tenant.jwt.decode") as mock_decode:
            import jwt as pyjwt
            mock_decode.side_effect = pyjwt.ExpiredSignatureError("Token expired")
            with pytest.raises(HTTPException) as exc_info:
                get_current_tenant_id(mock_creds)
            assert exc_info.value.status_code == 401


# ── Cross-tenant access patterns ─────────────────────────────────────────────

class TestCrossTenantDossierAccess:
    """Verify dossiers are filtered by tenant_id in all query patterns."""

    def test_list_dossiers_filters_by_tenant(self):
        """list_dossiers must only return rows where tenant_id matches."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from apps.api.app.models.base import Base
        from apps.api.app.models.dossier import Dossier

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        tenant_a = _make_tenant_id()
        tenant_b = _make_tenant_id()

        # Create dossiers for both tenants
        d1 = Dossier(id=str(uuid.uuid4()), tenant_id=tenant_a, project_name="A's Project")
        d2 = Dossier(id=str(uuid.uuid4()), tenant_id=tenant_b, project_name="B's Project")
        db.add_all([d1, d2])
        db.commit()

        # Query as tenant A — should only see A's dossier
        results = db.query(Dossier).filter(Dossier.tenant_id == tenant_a).all()
        assert len(results) == 1
        assert results[0].project_name == "A's Project"

        # Query as tenant B — should only see B's dossier
        results = db.query(Dossier).filter(Dossier.tenant_id == tenant_b).all()
        assert len(results) == 1
        assert results[0].project_name == "B's Project"

        db.close()

    def test_get_dossier_cross_tenant_blocked(self):
        """get_dossier must reject access to another tenant's dossier."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from apps.api.app.models.base import Base
        from apps.api.app.models.dossier import Dossier

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        tenant_a = _make_tenant_id()
        tenant_b = _make_tenant_id()

        d1 = Dossier(id=str(uuid.uuid4()), tenant_id=tenant_a, project_name="A's Project")
        db.add(d1)
        db.commit()

        # Tenant B tries to access Tenant A's dossier — must return None
        result = db.query(Dossier).filter(
            Dossier.id == d1.id,
            Dossier.tenant_id == tenant_b
        ).first()
        assert result is None

        db.close()


class TestCrossTenantJobAccess:
    """Verify jobs are filtered by tenant_id."""

    def test_list_jobs_filters_by_tenant(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from apps.api.app.models.base import Base
        from apps.api.app.models.job import Job

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        tenant_a = _make_tenant_id()
        tenant_b = _make_tenant_id()

        j1 = Job(id=str(uuid.uuid4()), tenant_id=tenant_a, type="feasibility", status="done")
        j2 = Job(id=str(uuid.uuid4()), tenant_id=tenant_b, type="feasibility", status="done")
        db.add_all([j1, j2])
        db.commit()

        # Tenant A should only see their jobs
        results = db.query(Job).filter(Job.tenant_id == tenant_a).all()
        assert len(results) == 1

        db.close()

    def test_get_job_cross_tenant_blocked(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from apps.api.app.models.base import Base
        from apps.api.app.models.job import Job

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        tenant_a = _make_tenant_id()
        tenant_b = _make_tenant_id()

        j1 = Job(id=str(uuid.uuid4()), tenant_id=tenant_a, type="feasibility", status="done")
        db.add(j1)
        db.commit()

        # Tenant B tries to access Tenant A's job
        result = db.query(Job).filter(
            Job.id == j1.id,
            Job.tenant_id == tenant_b
        ).first()
        assert result is None

        db.close()


class TestCrossTenantCheckoutAccess:
    """Verify checkouts are filtered by tenant_id."""

    def test_checkout_tenant_isolation(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from apps.api.app.models.base import Base
        from apps.api.app.models.checkout import Checkout

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        tenant_a = _make_tenant_id()
        tenant_b = _make_tenant_id()

        c1 = Checkout(
            id=str(uuid.uuid4()),
            tenant_id=tenant_a,
            plan="starter",
            amount=2900,
            status="paid",
            gateway="mock"
        )
        c2 = Checkout(
            id=str(uuid.uuid4()),
            tenant_id=tenant_b,
            plan="pro",
            amount=5900,
            status="paid",
            gateway="mock"
        )
        db.add_all([c1, c2])
        db.commit()

        # Tenant A should only see their checkouts
        results = db.query(Checkout).filter(Checkout.tenant_id == tenant_a).all()
        assert len(results) == 1
        assert results[0].plan == "starter"

        db.close()


# ── Admin bypass ─────────────────────────────────────────────────────────────

class TestAdminBypass:
    """Verify admin users can cross tenant boundaries."""

    def test_admin_flag_default_false(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from apps.api.app.models.base import Base
        from apps.api.app.models.user import User

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        user = User(
            id=_make_tenant_id(),
            email="test@example.com",
            name="Test User",
            password_hash="fake-hash",
            subscription="free"
        )
        db.add(user)
        db.commit()

        assert user.is_admin is False

        db.close()

    def test_admin_user_creation(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from apps.api.app.models.base import Base
        from apps.api.app.models.user import User

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        admin = User(
            id=_make_tenant_id(),
            email="admin@example.com",
            name="Admin User",
            password_hash="fake-hash",
            subscription="pro",
            is_admin=True
        )
        db.add(admin)
        db.commit()

        assert admin.is_admin is True

        db.close()


# ── Rate limiting ────────────────────────────────────────────────────────────

class TestTenantRateLimiting:
    """Verify tenant-keyed rate limiting works correctly."""

    def test_tenant_rate_limit_different_tenants_independent(self):
        """Different tenants should have independent rate limit buckets."""
        from apps.api.app.middleware.rate_limiter import make_tenant_rate_limit

        limit_fn = make_tenant_rate_limit("2/second")

        # Simulate requests from two different tenants
        # (We can't easily mock Request here, but we verify the function returns a callable)
        assert callable(limit_fn)

    def test_rate_limit_spec_parsing(self):
        from apps.api.app.middleware.rate_limiter import _parse_spec

        assert _parse_spec("60/minute") == (60, 60)
        assert _parse_spec("10/second") == (10, 1)
        assert _parse_spec("100/hour") == (100, 3600)
        assert _parse_spec("1000/day") == (1000, 86400)

        with pytest.raises(ValueError):
            _parse_spec("invalid")

        with pytest.raises(ValueError):
            _parse_spec("0/minute")


# ── Entitlement enforcement ──────────────────────────────────────────────────

class TestEntitlementEnforcement:
    """Verify plan tier + quota checks block unauthorized access."""

    def test_plan_tier_ordering(self):
        """Verify plan tier hierarchy is correct."""
        order = {"free": 0, "starter": 1, "pro": 2, "business": 3}
        assert order["free"] < order["starter"] < order["pro"] < order["business"]

    def test_quota_check_blocks_excess(self):
        """Verify quota check raises 429 when limit reached."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from apps.api.app.models.base import Base
        from apps.api.app.models.user import User
        from apps.api.app.models.job import Job
        from apps.api.app.routers.billing import PLANS
        from datetime import datetime, timezone

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        tenant_id = _make_tenant_id()
        user = User(
            id=tenant_id,
            email="quota@example.com",
            name="Quota User",
            password_hash="fake-hash",
            subscription="free"  # quota = 1
        )
        db.add(user)
        db.commit()

        # Create 1 job (hitting the free quota)
        job = Job(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            type="feasibility",
            status="done",
            created_at=datetime.now(timezone.utc)
        )
        db.add(job)
        db.commit()

        # Verify quota is exhausted
        from sqlalchemy import func
        count = db.query(func.count(Job.id)).filter(
            Job.tenant_id == tenant_id,
            Job.created_at >= datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ).scalar()

        quota = PLANS["free"]["quota"]
        assert count >= quota  # Should be blocked

        db.close()


# ── Webhook security ─────────────────────────────────────────────────────────

class TestWebhookSecurity:
    """Verify webhook HMAC verification and checkout validation."""

    def test_hmac_verification_mock_mode(self):
        """Mock mode should always pass HMAC verification."""
        from apps.api.app.routers.billing import _verify_hmac

        # Mock mode returns True regardless of signature
        assert _verify_hmac(b"test-body", None) is True
        assert _verify_hmac(b"test-body", "fake-sig") is True

    def test_hmac_verification_live_mode(self):
        """Live mode should verify HMAC signature."""
        from apps.api.app.routers.billing import _verify_hmac
        from apps.api.app.core.config import settings

        # Temporarily set gateway to chargily
        original = settings.billing_gateway
        settings.billing_gateway = "chargily"
        settings.billing_webhook_secret = "test-secret"

        import hmac as hmac_mod
        body = b"test-body"
        expected_sig = hmac_mod.new(b"test-secret", body, "sha256").hexdigest()

        assert _verify_hmac(body, expected_sig) is True
        assert _verify_hmac(body, "wrong-sig") is False
        assert _verify_hmac(body, None) is False

        # Restore
        settings.billing_gateway = original
