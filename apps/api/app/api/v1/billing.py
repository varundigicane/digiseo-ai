from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from app.api.deps import CurrentAuth, DbSession
from app.core.config import settings
from app.core.plans import PlanTier, get_limits
from app.models import CreditLedger, PlanTier as ModelPlanTier
from app.schemas import CheckoutRequest, CreditPackPurchase, SubscriptionOut
from app.services import auth_service

router = APIRouter()


@router.get("/subscription", response_model=SubscriptionOut)
async def get_subscription(auth: CurrentAuth):
    return SubscriptionOut(
        id=auth.subscription.id,
        tier=auth.subscription.tier.value,
        status=auth.subscription.status,
        credits_balance=auth.subscription.credits_balance,
        auto_apply_enabled=auth.subscription.auto_apply_enabled,
        limits=get_limits(auth.tier),
    )


@router.get("/credits")
async def credit_history(auth: CurrentAuth, db: DbSession):
    result = await db.execute(
        select(CreditLedger)
        .where(CreditLedger.organization_id == auth.org_id)
        .order_by(CreditLedger.created_at.desc())
        .limit(50)
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "delta": r.delta,
            "balance_after": r.balance_after,
            "reason": r.reason,
            "created_at": r.created_at,
        }
        for r in rows
    ]


@router.post("/checkout")
async def checkout(body: CheckoutRequest, auth: CurrentAuth, db: DbSession):
    """Create Stripe Checkout session or mock upgrade in development."""
    tier = PlanTier(body.tier)
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY.startswith("sk_test_xxx"):
        sub = await auth_service.set_plan_tier(db, auth.org_id, ModelPlanTier(tier.value))
        return {
            "mode": "mock",
            "message": f"Upgraded to {tier.value} (dev mock — configure Stripe for production)",
            "tier": tier.value,
            "credits_balance": sub.credits_balance,
        }

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    price_map = {
        PlanTier.STARTER: settings.STRIPE_PRICE_STARTER,
        PlanTier.PROFESSIONAL: settings.STRIPE_PRICE_PROFESSIONAL,
        PlanTier.BUSINESS: settings.STRIPE_PRICE_BUSINESS,
    }
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_map[tier], "quantity": 1}],
        success_url=body.success_url or f"{settings.WEB_URL}/app/billing?success=1",
        cancel_url=body.cancel_url or f"{settings.WEB_URL}/app/billing?canceled=1",
        customer_email=auth.user.email,
        metadata={"organization_id": str(auth.org_id), "tier": tier.value},
    )
    return {"mode": "stripe", "checkout_url": session.url, "session_id": session.id}


@router.post("/credits/purchase")
async def purchase_credits(body: CreditPackPurchase, auth: CurrentAuth, db: DbSession):
    # Mock credit pack purchase
    balance = await auth_service.credit_credits(
        db,
        organization_id=auth.org_id,
        amount=body.credits,
        reason="credit_pack_purchase",
    )
    return {"credits_added": body.credits, "balance": balance}


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: DbSession):
    payload = await request.body()
    if not settings.STRIPE_WEBHOOK_SECRET or settings.STRIPE_WEBHOOK_SECRET.startswith("whsec_xxx"):
        return {"received": True, "mode": "mock"}

    import stripe

    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        meta = session.get("metadata") or {}
        org_id = meta.get("organization_id")
        tier = meta.get("tier")
        if org_id and tier:
            await auth_service.set_plan_tier(db, org_id, PlanTier(tier))
    return {"received": True}
