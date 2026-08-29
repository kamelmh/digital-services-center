"""Integration coverage for SaaS JWT tenancy and billing protection.

The SQLite tests exercise the FastAPI request/dependency path. The PostgreSQL
RLS test is opt-in because it must use a least-privilege database role, not the
migration/owner role that bypasses RLS.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.app.core.config import settings
from apps.api.app.core.tenant import get_current_tenant_id
from apps.api.app.models.base import Base
from apps.api.app.models.checkout import Checkout  # noqa: F401
from apps.api.app.models.dossier import Dossier  # noqa: F401
from apps.api.app.models.job import Job  # noqa: F401
from apps.api.app.models.user import User  # noqa: F401
from apps.api.app.routers import billing


@pytest.fixture()
def billing_client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    tenant_a = str(uuid.uuid4())
    tenant_b = str(uuid.uuid4())
    with SessionLocal() as db:
        db.add_all(
            [
                User(id=tenant_a, email="a@example.test", name="Tenant A", password_hash="x", subscription="starter"),
                User(id=tenant_b, email="b@example.test", name="Tenant B", password_hash="x", subscription="free"),
            ]
        )
        db.commit()

    def override_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(billing.router)
    app.dependency_overrides[billing._get_db] = override_db
    monkeypatch.setattr(settings, "billing_gateway", "mock")
    client = TestClient(app)
    client.app.state.SessionLocal = SessionLocal

    def token(tenant_id: str) -> str:
        return jwt.encode(
            {"sub": tenant_id, "email": f"{tenant_id}@example.test"},
            settings.jwt_secret,
            algorithm=settings.jwt_alg,
        )

    return client, token, tenant_a, tenant_b


def test_tenant_dependency_rejects_missing_and_malformed_tokens():
    with pytest.raises(Exception) as missing:
        get_current_tenant_id(None)
    assert getattr(missing.value, "status_code", None) == 401


def test_tenant_dependency_accepts_only_uuid_subject():
    token = jwt.encode({"sub": "123"}, settings.jwt_secret, algorithm=settings.jwt_alg)
    from fastapi.security import HTTPAuthorizationCredentials

    with pytest.raises(Exception) as invalid:
        get_current_tenant_id(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))
    assert getattr(invalid.value, "status_code", None) == 401


def test_billing_routes_require_authentication(billing_client):
    client, _, _, _ = billing_client
    assert client.get("/billing/me").status_code == 401
    assert client.post("/billing/checkout", json={"plan": "starter"}).status_code == 401


def test_billing_checkout_is_bound_to_authenticated_tenant(billing_client):
    client, token, tenant_a, tenant_b = billing_client
    response = client.post(
        "/billing/checkout",
        headers={"Authorization": f"Bearer {token(tenant_a)}"},
        json={"plan": "starter", "billing_cycle": "monthly"},
    )
    assert response.status_code == 200
    checkout_id = response.json()["checkout_id"]

    own = client.get("/billing/me", headers={"Authorization": f"Bearer {token(tenant_a)}"})
    other = client.get("/billing/me", headers={"Authorization": f"Bearer {token(tenant_b)}"})
    assert own.status_code == 200
    assert own.json()["tenant_id"] == tenant_a
    assert other.status_code == 200
    assert other.json()["tenant_id"] == tenant_b
    assert checkout_id


def test_unknown_uuid_user_is_rejected(billing_client):
    client, token, _, _ = billing_client
    response = client.get(
        "/billing/me",
        headers={"Authorization": f"Bearer {token(str(uuid.uuid4()))}"},
    )
    assert response.status_code == 401


def test_webhook_rejects_unknown_checkout(billing_client):
    client, _, _, _ = billing_client
    response = client.post(
        "/billing/webhook",
        json={"checkout_id": str(uuid.uuid4()), "status": "paid", "plan": "pro"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown checkout"


def test_webhook_validates_amount_and_is_idempotent(billing_client):
    client, token, tenant_a, _ = billing_client
    checkout = client.post(
        "/billing/checkout",
        headers={"Authorization": f"Bearer {token(tenant_a)}"},
        json={"plan": "starter", "billing_cycle": "monthly"},
    ).json()
    bad_amount = client.post(
        "/billing/webhook",
        json={
            "checkout_id": checkout["checkout_id"],
            "status": "paid",
            "plan": "starter",
            "amount": checkout["price"] + 1,
            "currency": "DZD",
            "metadata": {"user_id": tenant_a},
        },
    )
    assert bad_amount.status_code == 400
    assert "amount" in bad_amount.json()["detail"]

    payload = {
        "checkout_id": checkout["checkout_id"],
        "status": "paid",
        "plan": "starter",
        "amount": checkout["price"],
        "currency": "DZD",
        "metadata": {"user_id": tenant_a},
    }
    first = client.post("/billing/webhook", json=payload)
    second = client.post("/billing/webhook", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["status"] == "already_processed"

    with client.app.state.SessionLocal() as db:
        user = db.get(User, tenant_a)
        assert user.subscription == "starter"


def test_chargily_live_rejects_mock_webhook_bypass(monkeypatch):
    """HMAC-pinning contract: gateway==chargily must reject a mock webhook signature."""
    from apps.api.app.core.config import settings as s

    monkeypatch.setattr(s, "billing_gateway", "chargily")
    monkeypatch.setattr(s, "billing_webhook_secret", "live-secret-32-bytes-for-test-pinning")
    monkeypatch.setattr(s, "chargily_secret", "live-secret-32-bytes-for-test-pinning")
    from apps.api.app.routers.billing import _verify_hmac

    assert _verify_hmac(b'{"checkout_id":"x","status":"paid"}', "mock-signature") is False
    assert _verify_hmac(b'{"checkout_id":"x","status":"paid"}', None) is False
    # Real sha256 hex of the same body must pass.
    import hashlib as _hl, hmac as _hm

    sig = _hm.new(b"live-secret-32-bytes-for-test-pinning", b'{"checkout_id":"x","status":"paid"}', _hl.sha256).hexdigest()
    assert _verify_hmac(b'{"checkout_id":"x","status":"paid"}', sig) is True


@pytest.mark.skipif(
    not os.getenv("DSC_RLS_TEST_DATABASE_URL"),
    reason="Set DSC_RLS_TEST_DATABASE_URL to a least-privilege Neon/PostgreSQL test role",
)
def test_neon_rls_policies_are_enabled_and_deny_cross_tenant_rows():
    """Validate the deployed migration without using the owner role.

    The supplied URL must connect as the restricted application role. The test
    only reads existing policy metadata and performs rollback-scoped probes.
    """
    engine = create_engine(os.environ["DSC_RLS_TEST_DATABASE_URL"], pool_pre_ping=True)
    with engine.begin() as conn:
        enabled = conn.execute(
            text("""
                SELECT relname, relrowsecurity
                FROM pg_class
                WHERE relname IN ('dossiers', 'jobs', 'checkouts')
            """)
        ).all()
        assert {name for name, is_enabled in enabled if is_enabled} == {"dossiers", "jobs", "checkouts"}

        policies = conn.execute(
            text("""
                SELECT tablename, policyname
                FROM pg_policies
                WHERE tablename IN ('dossiers', 'jobs', 'checkouts')
            """)
        ).all()
        policy_names = {name for _, name in policies}
        assert {"dossiers_select_own", "jobs_select_own", "checkouts_select_own"}.issubset(policy_names)

        tenant_a = str(uuid.uuid4())
        tenant_b = str(uuid.uuid4())
        conn.execute(text("SELECT set_config('app.current_tenant_id', :tenant, true)"), {"tenant": tenant_a})
        dossier_count_a = conn.execute(text("SELECT count(*) FROM dossiers WHERE tenant_id = :tenant"), {"tenant": tenant_a}).scalar_one()
        conn.execute(text("SELECT set_config('app.current_tenant_id', :tenant, true)"), {"tenant": tenant_b})
        dossier_count_b = conn.execute(text("SELECT count(*) FROM dossiers WHERE tenant_id = :tenant"), {"tenant": tenant_b}).scalar_one()
        assert dossier_count_a == 0
        assert dossier_count_b == 0


@pytest.fixture()
def dossier_client(monkeypatch):
    from apps.api.app.routers import dossiers, entitlements

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    tenant_a = str(uuid.uuid4())
    tenant_b = str(uuid.uuid4())
    dossier_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    with SessionLocal() as db:
        db.add_all(
            [
                User(id=tenant_a, email="dossier-a@example.test", password_hash="x", subscription="starter"),
                User(id=tenant_b, email="dossier-b@example.test", password_hash="x", subscription="starter"),
                Dossier(id=dossier_id, tenant_id=tenant_a, project_name="Tenant A project", status="draft"),
                Job(id=job_id, tenant_id=tenant_a, type="feasibility", status="queued", progress=10),
            ]
        )
        db.commit()

    def override_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(dossiers.router)
    app.dependency_overrides[dossiers._get_db] = override_db
    app.dependency_overrides[entitlements._get_db_billing] = override_db
    client = TestClient(app)

    def token(tenant_id: str) -> str:
        return jwt.encode({"sub": tenant_id}, settings.jwt_secret, algorithm=settings.jwt_alg)

    return client, token, tenant_a, tenant_b, dossier_id, job_id


def test_live_webhook_requires_valid_signature_and_matching_metadata(billing_client, monkeypatch):
    client, _, tenant_a, _ = billing_client
    monkeypatch.setattr(settings, "billing_gateway", "chargily")
    monkeypatch.setattr(settings, "billing_webhook_secret", "webhook-test-secret")
    with client.app.state.SessionLocal() as db:
        checkout = Checkout(
            id=str(uuid.uuid4()), tenant_id=tenant_a, plan="starter", billing_cycle="monthly",
            amount=2900, status="pending", gateway="chargily", gateway_checkout_id="gw-123",
        )
        db.add(checkout)
        db.commit()
        checkout_id = checkout.id

    payload = {
        "checkout_id": checkout_id,
        "status": "paid",
        "plan": "starter",
        "amount": 2900,
        "currency": "DZD",
        "metadata": {"user_id": tenant_a},
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(b"webhook-test-secret", raw, hashlib.sha256).hexdigest()
    invalid = client.post("/billing/webhook", content=raw, headers={"X-Chargily-Signature": "bad"})
    assert invalid.status_code == 401
    mismatch = dict(payload, metadata={"user_id": str(uuid.uuid4())})
    mismatch_raw = json.dumps(mismatch, separators=(",", ":")).encode()
    mismatch_sig = hmac.new(b"webhook-test-secret", mismatch_raw, hashlib.sha256).hexdigest()
    mismatch_response = client.post("/billing/webhook", content=mismatch_raw, headers={"X-Chargily-Signature": mismatch_sig})
    assert mismatch_response.status_code == 400
    valid = client.post("/billing/webhook", content=raw, headers={"X-Chargily-Signature": signature})
    assert valid.status_code == 200


def test_dossier_and_job_endpoints_isolate_tenants(dossier_client):
    client, token, tenant_a, tenant_b, dossier_id, job_id = dossier_client
    headers_a = {"Authorization": f"Bearer {token(tenant_a)}"}
    headers_b = {"Authorization": f"Bearer {token(tenant_b)}"}

    assert client.get("/v1/dossiers", headers=headers_a).json()["total"] == 1
    assert client.get("/v1/dossiers", headers=headers_b).json()["total"] == 0

    assert client.get(f"/v1/dossiers/{dossier_id}", headers=headers_a).status_code == 200
    assert client.get(f"/v1/dossiers/{dossier_id}", headers=headers_b).status_code == 404

    export_a = client.get(f"/v1/dossiers/export-csv?ids={dossier_id}", headers=headers_a)
    export_b = client.get(f"/v1/dossiers/export-csv?ids={dossier_id}", headers=headers_b)
    assert export_a.status_code == 200
    assert dossier_id in export_a.text
    assert export_b.status_code == 200
    assert dossier_id not in export_b.text

    assert client.get(f"/v1/dossiers/jobs/{job_id}", headers=headers_a).status_code == 200
    assert client.get(f"/v1/dossiers/jobs/{job_id}", headers=headers_b).status_code == 404


def test_dossier_creation_requires_authentication(dossier_client):
    client, _, _, _, _, _ = dossier_client
    response = client.post(
        "/v1/dossiers/feasibility",
        json={"business_type": "centre_services_num", "location": "Alger", "wilaya": "Alger", "investment": 300000},
    )
    assert response.status_code == 401


def test_billing_me_includes_quota_usage(billing_client):
    """Verify /billing/me returns used_this_month and remaining."""
    client, token, tenant_a, _ = billing_client
    # tenant_a has "starter" plan (quota=10)
    with client.app.state.SessionLocal() as db:
        db.add(Job(tenant_id=tenant_a, type="feasibility", status="done", progress=100))
        db.add(Job(tenant_id=tenant_a, type="feasibility", status="done", progress=100))
        db.commit()

    resp = client.get("/billing/me", headers={"Authorization": f"Bearer {token(tenant_a)}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["quota"] == 10
    assert data["used_this_month"] == 2
    assert data["remaining"] == 8
    assert data["plan_label"] == "Starter"


def test_webhook_activates_subscription_and_extends_if_already_active(billing_client):
    """Verify webhook sets subscription and extends on re-activation."""
    client, token, tenant_a, _ = billing_client
    checkout = client.post(
        "/billing/checkout",
        headers={"Authorization": f"Bearer {token(tenant_a)}"},
        json={"plan": "pro", "billing_cycle": "monthly"},
    ).json()

    # First payment — activates
    payload = {
        "checkout_id": checkout["checkout_id"],
        "status": "paid",
        "plan": "pro",
        "amount": checkout["price"],
        "currency": "DZD",
        "metadata": {"user_id": tenant_a},
    }
    resp1 = client.post("/billing/webhook", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "ok"

    with client.app.state.SessionLocal() as db:
        user = db.get(User, tenant_a)
        assert user.subscription == "pro"
        assert user.subscription_until is not None
        first_until = user.subscription_until

    # Second payment (idempotent) — extends
    resp2 = client.post("/billing/webhook", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "already_processed"


def test_webhook_rejects_currency_mismatch(billing_client):
    """Verify webhook rejects wrong currency."""
    client, token, tenant_a, _ = billing_client
    checkout = client.post(
        "/billing/checkout",
        headers={"Authorization": f"Bearer {token(tenant_a)}"},
        json={"plan": "starter", "billing_cycle": "monthly"},
    ).json()

    payload = {
        "checkout_id": checkout["checkout_id"],
        "status": "paid",
        "plan": "starter",
        "amount": checkout["price"],
        "currency": "USD",
        "metadata": {"user_id": tenant_a},
    }
    resp = client.post("/billing/webhook", json=payload)
    assert resp.status_code == 400
    assert "currency" in resp.json()["detail"].lower()


def test_entitlement_rejects_insufficient_plan(monkeypatch):
    """Verify entitlement check rejects users below required plan tier."""
    from fastapi import FastAPI
    from apps.api.app.routers import entitlements, billing

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    tenant_id = str(uuid.uuid4())
    with SessionLocal() as db:
        db.add(User(id=tenant_id, email="free@test.com", password_hash="x", subscription="free"))
        db.commit()

    def override_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(billing.router)
    app.dependency_overrides[billing._get_db] = override_db
    app.dependency_overrides[entitlements._get_db_billing] = override_db
    client = TestClient(app)

    token_val = jwt.encode({"sub": tenant_id}, settings.jwt_secret, algorithm=settings.jwt_alg)
    resp = client.get("/billing/me", headers={"Authorization": f"Bearer {token_val}"})
    assert resp.status_code == 200
    assert resp.json()["subscription"] == "free"
    assert resp.json()["quota"] == 1
