"""Enterprise: white-label, API keys, SSO stubs, audit logs."""

from __future__ import annotations

import secrets
from hashlib import sha256

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentAuth, DbSession
from app.core.plans import get_limits
from app.models import AuditLog

router = APIRouter()


class WhiteLabelUpdate(BaseModel):
    custom_domain: str | None = None
    brand_logo_url: str | None = None
    brand_primary_color: str | None = None
    enabled: bool = True


class SSOConfig(BaseModel):
    enabled: bool = True
    metadata_url: str | None = None
    entity_id: str | None = None


@router.get("/settings")
async def enterprise_settings(auth: CurrentAuth):
    limits = get_limits(auth.tier)
    return {
        "tier": auth.tier.value,
        "white_label": limits.get("white_label"),
        "api_access": limits.get("api_access"),
        "sso": limits.get("sso"),
        "organization": {
            "white_label_enabled": auth.organization.white_label_enabled,
            "custom_domain": auth.organization.custom_domain,
            "brand_logo_url": auth.organization.brand_logo_url,
            "brand_primary_color": auth.organization.brand_primary_color,
            "sso_enabled": auth.organization.sso_enabled,
            "has_api_key": bool(auth.organization.api_key_hash),
        },
    }


@router.put("/white-label")
async def update_white_label(body: WhiteLabelUpdate, auth: CurrentAuth, db: DbSession):
    if not get_limits(auth.tier).get("white_label"):
        raise HTTPException(403, "White-label requires Enterprise")
    auth.require_role("owner", "admin")
    org = auth.organization
    org.white_label_enabled = body.enabled
    org.custom_domain = body.custom_domain
    org.brand_logo_url = body.brand_logo_url
    org.brand_primary_color = body.brand_primary_color
    db.add(
        AuditLog(
            organization_id=auth.org_id,
            user_id=auth.user.id,
            action="white_label.update",
            resource_type="organization",
            resource_id=str(org.id),
            meta=body.model_dump(),
        )
    )
    await db.flush()
    return {"ok": True}


@router.post("/api-keys")
async def create_api_key(auth: CurrentAuth, db: DbSession):
    if not get_limits(auth.tier).get("api_access"):
        raise HTTPException(403, "API access requires Business or Enterprise")
    auth.require_role("owner", "admin")
    raw = f"dseo_{secrets.token_urlsafe(32)}"
    auth.organization.api_key_hash = sha256(raw.encode()).hexdigest()
    db.add(
        AuditLog(
            organization_id=auth.org_id,
            user_id=auth.user.id,
            action="api_key.create",
            resource_type="organization",
            resource_id=str(auth.org_id),
            meta={},
        )
    )
    await db.flush()
    return {"api_key": raw, "warning": "Store this key securely — it will not be shown again"}


@router.put("/sso")
async def configure_sso(body: SSOConfig, auth: CurrentAuth, db: DbSession):
    if not get_limits(auth.tier).get("sso"):
        raise HTTPException(403, "SSO requires Enterprise")
    auth.require_role("owner", "admin")
    auth.organization.sso_enabled = body.enabled
    auth.organization.sso_metadata = {
        "metadata_url": body.metadata_url,
        "entity_id": body.entity_id,
    }
    db.add(
        AuditLog(
            organization_id=auth.org_id,
            user_id=auth.user.id,
            action="sso.configure",
            resource_type="organization",
            resource_id=str(auth.org_id),
            meta=body.model_dump(),
        )
    )
    await db.flush()
    return {"ok": True, "sso_enabled": body.enabled}


@router.get("/audit-logs")
async def audit_logs(auth: CurrentAuth, db: DbSession):
    if auth.tier.value not in ("business", "enterprise"):
        raise HTTPException(403, "Audit logs require Business+")
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.organization_id == auth.org_id)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
    )
    return [
        {
            "id": str(a.id),
            "action": a.action,
            "resource_type": a.resource_type,
            "resource_id": a.resource_id,
            "meta": a.meta,
            "created_at": a.created_at,
        }
        for a in result.scalars().all()
    ]


@router.post("/auto-apply")
async def toggle_auto_apply(auth: CurrentAuth, db: DbSession, enabled: bool = True):
    auth.require_feature("auto_apply")
    auth.require_role("owner", "admin")
    auth.subscription.auto_apply_enabled = enabled
    await db.flush()
    return {"auto_apply_enabled": enabled}
