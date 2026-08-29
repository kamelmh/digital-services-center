"""Billing router — Chargily Pay live (BaridiMob/CIB/Dahabiya) + mock + entitlements."""
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.config import settings
from ..middleware.rate_limiter import make_rate_limit
from ..core.tenant import get_current_tenant_id, require_tenant_user

# Rate limits (dependency-based; slowapi decorators break include_router on FastAPI >= 0.141)
_rl_checkout = make_rate_limit("10/minute")   # checkout creation is expensive + abuse-prone
_rl_webhook = make_rate_limit("60/minute")
_rl_me = make_rate_limit("60/minute")

router = APIRouter(prefix="/billing", tags=["billing"])


# ── Plans (single source, mirrors billing.py:24 but with DB enforcement) ──
PLANS = {
    "free": {"price": 0, "quota": 1, "label": "Free"},
    "starter": {"price": 2900, "quota": 10, "label": "Starter"},
    "pro": {"price": 5900, "quota": 100, "label": "Pro"},  # fair-use 100
    "business": {"price": 12900, "quota": 300, "label": "Business"},
}


class CheckoutRequest(BaseModel):
    plan: str  # starter|pro|business
    billing_cycle: str = "monthly"  # monthly|yearly (yearly = 10×)


class CheckoutResponse(BaseModel):
    plan: str
    price: int
    gateway: str
    payment_url: str
    checkout_id: str
    note: str | None = None


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


def _price_for(plan: str, cycle: str) -> int:
    base = PLANS[plan]["price"]
    if cycle == "yearly":
        return base * 10  # 2 months free
    return base


def _get_or_create_anon_user(db: Session):
    from ..models.user import User
    from auth import hash_password

    anon_id = "00000000-0000-0000-0000-000000000000"
    u = db.get(User, anon_id)
    if not u:
        u = User(id=anon_id, email="anon@local", name="Local Dev", password_hash=hash_password("local-dev-not-used"), subscription="free")
        db.add(u)
        db.commit()
        db.refresh(u)
    return u


def _create_chargily_checkout(amount: int, checkout_id: str, user_id: str, plan: str) -> tuple[str, str]:
    """Call Chargily API live, return (gateway_checkout_id, checkout_url). Falls back to mock on any error."""
    if settings.billing_gateway != "chargily" or not settings.chargily_key:
        # Mock
        gw_id = f"chk_{uuid.uuid4().hex[:12]}"
        url = f"{settings.frontend_url}/billing/mock-pay?checkout_id={checkout_id}"
        return gw_id, url

    import requests

    # Chargily Pay v2: https://pay.chargily.dz/test/api/v2/checkouts (test) / https://pay.chargily.dz/api/v2/checkouts (live)
    endpoint = "https://pay.chargily.dz/api/v2/checkouts"
    if settings.chargily_key.startswith("test_"):
        endpoint = "https://pay.chargily.dz/test/api/v2/checkouts"

    payload = {
        "amount": amount,
        "currency": "DZD",
        "success_url": f"{settings.frontend_url}/billing/success?checkout_id={checkout_id}",
        "failure_url": f"{settings.frontend_url}/billing/failure?checkout_id={checkout_id}",
        "webhook_endpoint": settings.webhook_url or f"{settings.frontend_url}/billing/webhook",
        "metadata": {"checkout_id": checkout_id, "user_id": user_id, "plan": plan},
        "description": f"DSC {plan} — {amount} DZD",
    }
    headers = {"Authorization": f"Bearer {settings.chargily_key}", "Content-Type": "application/json"}
    try:
        r = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Chargily returns {id, checkout_url}
        gw_id = data.get("id") or data.get("checkout_id") or f"chk_{uuid.uuid4().hex[:12]}"
        url = data.get("checkout_url") or data.get("url") or f"{settings.frontend_url}/billing/mock-pay?checkout_id={checkout_id}"
        return gw_id, url
    except Exception as e:
        print(f"Chargily call failed, falling back to mock: {e}")
        gw_id = f"chk_{uuid.uuid4().hex[:12]}"
        url = f"{settings.frontend_url}/billing/mock-pay?checkout_id={checkout_id}"
        return gw_id, url


@router.get("/plans")
def list_plans():
    return {k: {"price": v["price"], "quota": v["quota"], "label": v["label"]} for k, v in PLANS.items()}


@router.post("/checkout", response_model=CheckoutResponse, dependencies=[Depends(_rl_checkout)])
def create_checkout(
    req: CheckoutRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(_get_db),
):
    if req.plan not in PLANS or req.plan == "free":
        raise HTTPException(status_code=400, detail="Invalid plan — choose starter|pro|business")
    if req.billing_cycle not in ("monthly", "yearly"):
        raise HTTPException(status_code=400, detail="Invalid billing_cycle")

    user = require_tenant_user(db, tenant_id)

    amount = _price_for(req.plan, req.billing_cycle)
    checkout_id = str(uuid.uuid4())
    gw_id, payment_url = _create_chargily_checkout(amount, checkout_id, tenant_id, req.plan)

    from ..models.checkout import Checkout

    row = Checkout(
        id=checkout_id,
        tenant_id=tenant_id,
        plan=req.plan,
        billing_cycle=req.billing_cycle,
        amount=amount,
        status="pending",
        gateway=settings.billing_gateway,
        gateway_checkout_id=gw_id,
    )
    db.add(row)
    db.commit()

    return CheckoutResponse(
        plan=req.plan,
        price=amount,
        gateway=settings.billing_gateway,
        payment_url=payment_url,
        checkout_id=checkout_id,
        note="Mock payment — no Chargily key set" if settings.billing_gateway == "mock" else None,
    )


def _verify_hmac(raw_body: bytes, signature: str | None) -> bool:
    if settings.billing_gateway == "mock":
        return True  # mock bypass
    secret = settings.billing_webhook_secret or settings.chargily_secret
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _activate_subscription(db: Session, tenant_id: str, plan: str, months: int = 1):
    from ..models.user import User

    user = db.get(User, tenant_id)
    if not user:
        return
    now = datetime.now(timezone.utc)
    # Extend if still active, else from now (prevents overlap loss)
    base = user.subscription_until if user.subscription_until and user.subscription_until > now else now
    user.subscription = plan
    user.subscription_until = base + timedelta(days=30 * months)
    db.commit()


@router.post("/webhook", dependencies=[Depends(_rl_webhook)])
async def webhook(
    request: Request,
    x_chargily_signature: str | None = Header(default=None),
    x_stripe_signature: str | None = Header(default=None),
    db: Session = Depends(_get_db),
):
    raw = await request.body()
    # Verify HMAC (Chargily: X-Chargily-Signature, Stripe: X-Stripe-Signature)
    sig = x_chargily_signature or x_stripe_signature
    if not _verify_hmac(raw, sig):
        # In mock mode we allow, in live we would 401
        if settings.billing_gateway != "mock":
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        data = await request.json()
    except Exception:
        data = {}

    # Chargily payload: {id, status, metadata: {checkout_id, user_id, plan}} or flat
    checkout_id = (data.get("metadata") or {}).get("checkout_id") or data.get("checkout_id") or data.get("id")
    status = data.get("status") or data.get("event") or "paid"
    plan = (data.get("metadata") or {}).get("plan") or data.get("plan")
    user_id = (data.get("metadata") or {}).get("user_id") or data.get("user_id") or data.get("tenant_id")

    # Normalize status
    paid_statuses = {"paid", "success", "completed", "succeeded"}
    if status not in paid_statuses:
        return {"status": "ignored", "reason": f"status {status} not in paid"}

    if not checkout_id:
        raise HTTPException(status_code=400, detail="Missing checkout_id in webhook")

    from ..models.checkout import Checkout

    # A webhook may only settle a checkout created by this application. Never
    # trust webhook metadata to create a new tenant/plan/amount record.
    row = db.get(Checkout, checkout_id)
    if not row:
        row = db.query(Checkout).filter(Checkout.gateway_checkout_id == checkout_id).first()
    if not row:
        raise HTTPException(status_code=400, detail="Unknown checkout")

    # Validate fields supplied by the gateway against the original checkout.
    metadata = data.get("metadata") or {}
    payload_currency = data.get("currency") or data.get("currency_code")
    if payload_currency and str(payload_currency).upper() != "DZD":
        raise HTTPException(status_code=400, detail="Unsupported checkout currency")
    if plan and plan != row.plan:
        raise HTTPException(status_code=400, detail="Webhook plan does not match checkout")
    payload_amount = data.get("amount")
    if payload_amount is not None:
        try:
            if int(payload_amount) != row.amount:
                raise HTTPException(status_code=400, detail="Webhook amount does not match checkout")
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid webhook amount") from exc
    metadata_tenant = metadata.get("user_id") or metadata.get("tenant_id")
    if metadata_tenant and str(metadata_tenant) != row.tenant_id:
        raise HTTPException(status_code=400, detail="Webhook tenant does not match checkout")

    if row.status == "paid":
        return {"status": "already_processed", "checkout_id": row.id}

    row.status = "paid"
    db.commit()

    # Activate subscription — yearly = 12 months
    months = 12 if row.billing_cycle == "yearly" else 1
    _activate_subscription(db, row.tenant_id, row.plan, months=months)

    return {"status": "ok", "checkout_id": row.id, "plan": row.plan}


@router.get("/me", dependencies=[Depends(_rl_me)])
def billing_me(
    tenant_id: str = Depends(get_current_tenant_id),
    db: Session = Depends(_get_db),
):
    user = require_tenant_user(db, tenant_id)
    plan_info = PLANS.get(user.subscription, PLANS["free"])
    quota = plan_info["quota"]

    # Count jobs this month
    from ..models.job import Job
    from sqlalchemy import func

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    used = db.query(func.count(Job.id)).filter(
        Job.tenant_id == user.id,
        Job.created_at >= month_start,
    ).scalar() or 0

    return {
        "tenant_id": user.id,
        "subscription": user.subscription,
        "until": user.subscription_until,
        "plan_label": plan_info["label"],
        "quota": quota,
        "used_this_month": used,
        "remaining": max(0, quota - used),
    }


@router.get("/mock-pay")
def mock_pay(checkout_id: str):
    return {"message": "Mock payment page — in prod this redirects to pay.chargily.dz", "checkout_id": checkout_id, "note": "Call POST /billing/webhook with {checkout_id, status: 'paid'} to simulate success"}
