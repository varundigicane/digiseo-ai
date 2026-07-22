from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.plans import PlanTier, get_limits, has_feature
from app.core.security import as_uuid, decode_token
from app.models import Membership, Organization, Subscription, User

security = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user: User
    organization: Organization
    membership: Membership
    subscription: Subscription
    workspace_id: Optional[str] = None

    @property
    def org_id(self) -> str:
        return str(self.organization.id)

    @property
    def tier(self) -> PlanTier:
        return PlanTier(self.subscription.tier.value)

    def require_feature(self, feature: str) -> None:
        if not has_feature(self.tier, feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature}' not available on {self.tier.value} plan",
            )

    def require_role(self, *roles: str) -> None:
        if self.membership.role.value == "owner":
            return
        if self.membership.role.value not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")


async def get_current_auth(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    x_org_id: Annotated[Optional[str], Header(alias="X-Org-Id")] = None,
    x_workspace_id: Annotated[Optional[str], Header(alias="X-Workspace-Id")] = None,
    x_api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None,
) -> AuthContext:
    # API key path (Phase 3)
    if x_api_key and not credentials:
        from hashlib import sha256

        key_hash = sha256(x_api_key.encode()).hexdigest()
        result = await db.execute(
            select(Organization)
            .options(selectinload(Organization.subscription))
            .where(Organization.api_key_hash == key_hash)
        )
        org = result.scalar_one_or_none()
        if not org or not org.subscription:
            raise HTTPException(401, "Invalid API key")
        # Synthetic owner membership for API
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.user))
            .where(Membership.organization_id == org.id)
            .limit(1)
        )
        membership = result.scalar_one_or_none()
        if not membership:
            raise HTTPException(401, "Invalid API key")
        return AuthContext(
            user=membership.user,
            organization=org,
            membership=membership,
            subscription=org.subscription,
            workspace_id=as_uuid(x_workspace_id),
        )

    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token") from None

    user_id = as_uuid(payload.get("sub"))
    if not user_id:
        raise HTTPException(401, "Invalid token subject")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(401, "User inactive or missing")

    org_id = as_uuid(x_org_id or payload.get("org_id"))
    if not org_id:
        raise HTTPException(400, "Organization context required (X-Org-Id)")

    result = await db.execute(
        select(Membership)
        .options(
            selectinload(Membership.organization).selectinload(Organization.subscription),
        )
        .where(Membership.user_id == user.id, Membership.organization_id == org_id)
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(403, "Not a member of this organization")

    org = membership.organization
    sub = org.subscription
    if not sub:
        raise HTTPException(400, "Organization has no subscription")

    return AuthContext(
        user=user,
        organization=org,
        membership=membership,
        subscription=sub,
        workspace_id=as_uuid(x_workspace_id or payload.get("workspace_id")),
    )


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentAuth = Annotated[AuthContext, Depends(get_current_auth)]


def plan_limits(auth: AuthContext) -> dict:
    return get_limits(auth.tier)
