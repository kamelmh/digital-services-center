"""Billing — Chargily/Stripe-ready plans + mock checkout + webhook.

Offline: all ops are local SQLite (users.subscription).  No external call
is required to test.  Wire to a real gateway by replacing
_create_gateway_session().

Plans mirror pricing_calculator PACKAGES but are billing-oriented.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from auth import UserOut, get_current_user, get_current_user_optional

# ── Plans (single source; can be moved to DB later) ─────────────────────────

PLANS = {
    "free":      {"name_fr": "Gratuit",         "name_ar": "مجاني",   "price_dzd": 0,      "features": ["1 dossier / mois", "Guides fiscaux", "Support communautaire"]},
    "starter":   {"name_fr": "Starter",         "name_ar": "بداية",   "price_dzd": 2_900,  "features": ["10 dossiers / mois", "7 formulaires DGI", "Export PDF"]},
    "pro":       {"name_fr": "Pro",             "name_ar": "احترافي", "price_dzd": 5_900,  "features": ["Illimité", "Tous les générateurs", "Batch 10", "Support prioritaire"]},
    "business":  {"name_fr": "Business",        "name_ar": "أعمال",   "price_dzd": 12_900, "features": ["Pro + API", "Whitelabel PDF", "Onboarding"]},
}

PLAN_ORDER = ["free", "starter", "pro", "business"]

GATEWAY = os.getenv("DSC_BILLING_GATEWAY", "mock")  # mock | chargily | stripe
WEBHOOK_SECRET = os.getenv("DSC_BILLING_WEBHOOK_SECRET", "")

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: str = Field(..., description="starter | pro | business")
    billing_cycle: str = Field("monthly", description="monthly | yearly")


class CheckoutResponse(BaseModel):
    plan: str
    price_dzd: int
    gateway: str
    payment_url: str
    checkout_id: str
    note: str


class WebhookRequest(BaseModel):
    checkout_id: str
    status: str  # paid | failed | cancelled
    plan: Optional[str] = None
    user_id: Optional[int] = None
    # Real gateways send a signature header; we check it when not mock.
    signature: Optional[str] = None


# ── Helpers ──────────────────────────────────────────────────────────────────

def _create_gateway_session(plan: str, user: UserOut, billing_cycle: str) -> dict:
    """Create a checkout session. Replace with real Chargily/Stripe call."""
    checkout_id = f"chk_{uuid.uuid4().hex[:12]}"
    price = PLANS[plan]["price_dzd"]
    if billing_cycle == "yearly":
        price = int(price * 10)  # 2 months free
    if GATEWAY == "mock":
        # No external call — return a mock URL that the frontend can
        # treat as "redirect to payment".  Webhook will confirm.
        payment_url = f"/billing/mock-pay?checkout_id={checkout_id}&plan={plan}"
        note = "mock gateway — call POST /billing/webhook with {checkout_id, status:'paid'} to activate"
    elif GATEWAY == "chargily":
        # Real Chargily Pay: POST https://pay.chargily.dz/test/api/v2/checkouts
        # with API key from DSC_CHARGILY_KEY.  Left as stub for wiring.
        payment_url = f"https://pay.chargily.dz/checkout/{checkout_id} (stub — wire DSC_CHARGILY_KEY)"
        note = "chargily gateway stub — set DSC_CHARGILY_KEY and implement"
    elif GATEWAY == "stripe":
        payment_url = f"https://checkout.stripe.com/pay/{checkout_id} (stub — wire STRIPE_SECRET_KEY)"
        note = "stripe gateway stub — set STRIPE_SECRET_KEY and implement"
    else:
        payment_url = f"/billing/mock-pay?checkout_id={checkout_id}&plan={plan}"
        note = f"unknown gateway '{GATEWAY}', fell back to mock"
    return {"checkout_id": checkout_id, "payment_url": payment_url, "price_dzd": price, "note": note}


def _activate_subscription(user_id: int, plan: str, months: int = 1):
    until = (datetime.now(timezone.utc) + timedelta(days=30 * months)).isoformat()
    from dsc_utils import get_db
    conn = get_db()
    conn.execute(
        "UPDATE users SET subscription=?, subscription_until=? WHERE id=?",
        (plan, until, user_id),
    )
    conn.commit()
    conn.close()
    return until


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/plans")
def list_plans():
    """List all billing plans (public)."""
    return {
        k: {"key": k, **v}
        for k, v in PLANS.items()
    }


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(req: CheckoutRequest, user: UserOut = Depends(get_current_user)):
    """Create a checkout session for the authenticated user."""
    plan = req.plan.lower().strip()
    if plan not in PLANS or plan == "free":
        raise HTTPException(400, f"Unknown plan '{req.plan}'. Choose from {', '.join(PLAN_ORDER[1:])}")
    if req.billing_cycle not in ("monthly", "yearly"):
        raise HTTPException(400, "billing_cycle must be monthly or yearly")
    sess = _create_gateway_session(plan, user, req.billing_cycle)
    return CheckoutResponse(
        plan=plan,
        price_dzd=sess["price_dzd"],
        gateway=GATEWAY,
        payment_url=sess["payment_url"],
        checkout_id=sess["checkout_id"],
        note=sess["note"],
    )


@router.post("/webhook")
def billing_webhook(req: WebhookRequest, request: Request):
    """Gateway webhook — confirm payment and activate subscription.

    Mock: POST {"checkout_id":"...", "status":"paid", "plan":"pro", "user_id":1}
    Real: Chargily/Stripe will POST with a signature header — verify
    against DSC_BILLING_WEBHOOK_SECRET when not mock.
    """
    if GATEWAY != "mock" and WEBHOOK_SECRET:
        sig = request.headers.get("X-Chargily-Signature") or request.headers.get("Stripe-Signature") or req.signature or ""
        if sig != WEBHOOK_SECRET:
            raise HTTPException(401, "Invalid webhook signature")
    if req.status != "paid":
        return {"ok": True, "action": "ignored", "status": req.status}
    if not req.user_id or not req.plan:
        raise HTTPException(400, "paid webhook requires user_id and plan")
    if req.plan not in PLANS:
        raise HTTPException(400, f"Unknown plan '{req.plan}'")
    from auth import get_user_by_id
    if not get_user_by_id(req.user_id):
        raise HTTPException(404, "User not found")
    until = _activate_subscription(req.user_id, req.plan)
    return {"ok": True, "action": "activated", "plan": req.plan, "until": until}


@router.get("/me")
def my_subscription(user: UserOut = Depends(get_current_user)):
    """Current user's subscription (requires auth)."""
    return {"user_id": user.id, "email": user.email, "subscription": user.subscription, "until": user.subscription_until, "gateway": GATEWAY}


@router.get("/mock-pay")
def mock_pay(checkout_id: str, plan: str):
    """Mock payment page — for local testing without a gateway."""
    if plan not in PLANS:
        raise HTTPException(400, "Unknown plan")
    return {
        "message": "Mock payment page — in production this would be Chargily/Stripe.",
        "checkout_id": checkout_id,
        "plan": plan,
        "price_dzd": PLANS[plan]["price_dzd"],
        "next": f"POST /billing/webhook with {{checkout_id, status:'paid', plan, user_id}} to activate",
    }
