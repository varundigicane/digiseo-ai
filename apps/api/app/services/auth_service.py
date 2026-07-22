from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.plans import PlanTier as PlanTierLimits
from app.core.plans import get_limits
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Membership, Organization, PlanTier, Role, Subscription, User, Workspace


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:80] or "org"


async def signup(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    full_name: str,
    organization_name: str,
    workspace_name: str,
) -> tuple[User, Organization, Workspace, str]:
    existing = await db.execute(select(User).where(User.email == email.lower()))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=email.lower(),
        full_name=full_name,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.flush()

    base_slug = slugify(organization_name)
    slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
    org = Organization(name=organization_name, slug=slug)
    db.add(org)
    await db.flush()

    membership = Membership(user_id=user.id, organization_id=org.id, role=Role.OWNER)
    db.add(membership)

    limits = get_limits(PlanTierLimits.STARTER)
    sub = Subscription(
        organization_id=org.id,
        tier=PlanTier.STARTER,
        status="trialing",
        credits_balance=limits["monthly_credits"],
    )
    db.add(sub)

    ws = Workspace(
        organization_id=org.id,
        name=workspace_name,
        slug=slugify(workspace_name),
    )
    db.add(ws)
    await db.flush()

    token = create_access_token(
        str(user.id),
        org_id=str(org.id),
        workspace_id=str(ws.id),
        role=Role.OWNER.value,
    )
    return user, org, ws, token


async def login(db: AsyncSession, *, email: str, password: str) -> tuple[User, Organization, Workspace | None, str]:
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    result = await db.execute(
        select(Membership)
        .options(
            selectinload(Membership.organization).selectinload(Organization.workspaces),
            selectinload(Membership.organization).selectinload(Organization.subscription),
        )
        .where(Membership.user_id == user.id)
        .limit(1)
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise ValueError("No organization")

    org = membership.organization
    workspace = org.workspaces[0] if org.workspaces else None
    token = create_access_token(
        str(user.id),
        org_id=str(org.id),
        workspace_id=str(workspace.id) if workspace else None,
        role=membership.role.value,
    )
    return user, org, workspace, token


async def debit_credits(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    amount: int,
    reason: str,
    reference_id: str | None = None,
) -> int:
    from app.models import CreditLedger

    result = await db.execute(
        select(Subscription).where(Subscription.organization_id == organization_id).with_for_update()
    )
    sub = result.scalar_one()
    if sub.credits_balance < amount:
        raise ValueError("Insufficient credits")
    sub.credits_balance -= amount
    ledger = CreditLedger(
        organization_id=organization_id,
        delta=-amount,
        balance_after=sub.credits_balance,
        reason=reason,
        reference_id=reference_id,
    )
    db.add(ledger)
    return sub.credits_balance


async def credit_credits(
    db: AsyncSession,
    *,
    organization_id: uuid.UUID,
    amount: int,
    reason: str,
    reference_id: str | None = None,
) -> int:
    from app.models import CreditLedger

    result = await db.execute(
        select(Subscription).where(Subscription.organization_id == organization_id).with_for_update()
    )
    sub = result.scalar_one()
    sub.credits_balance += amount
    ledger = CreditLedger(
        organization_id=organization_id,
        delta=amount,
        balance_after=sub.credits_balance,
        reason=reason,
        reference_id=reference_id,
    )
    db.add(ledger)
    return sub.credits_balance


async def set_plan_tier(
    db: AsyncSession, organization_id: uuid.UUID, tier: PlanTier | PlanTierLimits | str
) -> Subscription:
    result = await db.execute(select(Subscription).where(Subscription.organization_id == organization_id))
    sub = result.scalar_one()
    tier_value = tier.value if hasattr(tier, "value") else str(tier)
    model_tier = PlanTier(tier_value)
    limits = get_limits(tier_value)
    sub.tier = model_tier
    sub.status = "active"
    sub.credits_balance = limits["monthly_credits"]
    sub.auto_apply_enabled = bool(limits.get("auto_apply"))
    sub.credits_reset_at = datetime.now(timezone.utc)
    await db.flush()
    return sub
