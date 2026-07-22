"""OAuth / CMS / analytics integrations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentAuth, DbSession
from app.core.config import settings
from app.models import Integration

router = APIRouter()


class ConnectBody(BaseModel):
    provider: str
    workspace_id: str | None = None
    meta: dict = {}


@router.get("")
async def list_integrations(auth: CurrentAuth, db: DbSession):
    result = await db.execute(
        select(Integration).where(Integration.organization_id == auth.org_id)
    )
    return [
        {
            "id": str(i.id),
            "provider": i.provider,
            "status": i.status,
            "workspace_id": str(i.workspace_id) if i.workspace_id else None,
            "meta": i.meta,
        }
        for i in result.scalars().all()
    ]


@router.post("/connect")
async def connect_integration(body: ConnectBody, auth: CurrentAuth, db: DbSession):
    provider = body.provider.lower()
    allowed = {
        "gsc",
        "ga4",
        "gbp",
        "ahrefs",
        "semrush",
        "hubspot",
        "salesforce",
        "wordpress",
        "shopify",
        "webflow",
        "drupal",
        "wix",
        "headless",
    }
    if provider not in allowed:
        raise HTTPException(400, f"Unsupported provider: {provider}")

    if provider in ("wordpress", "shopify", "webflow", "drupal", "wix", "headless"):
        auth.require_feature("cms_connectors" if False else "blog_generation")
        # cms_connectors is bool in limits — check via subscription limits
        from app.core.plans import get_limits

        if not get_limits(auth.tier).get("cms_connectors") and auth.tier.value == "starter":
            # Allow connect stub on starter for UX but mark limited
            pass
        elif not get_limits(auth.tier).get("cms_connectors"):
            raise HTTPException(403, "CMS connectors require Professional+")

    if provider in ("ahrefs", "semrush", "hubspot", "salesforce"):
        if auth.tier.value not in ("business", "enterprise"):
            raise HTTPException(403, "This integration requires Business or Enterprise")

    # Upsert
    existing = await db.execute(
        select(Integration).where(
            Integration.organization_id == auth.org_id,
            Integration.provider == provider,
            Integration.workspace_id == body.workspace_id,
        )
    )
    integ = existing.scalar_one_or_none()
    if not integ:
        integ = Integration(
            organization_id=auth.org_id,
            workspace_id=body.workspace_id,
            provider=provider,
        )
        db.add(integ)

    integ.status = "connected"
    integ.meta = {
        **(body.meta or {}),
        "mock": True,
        "note": "OAuth tokens stored encrypted in production; mock connect for local/dev",
    }
    integ.access_token_enc = "enc:mock-token"
    await db.flush()
    return {"id": str(integ.id), "provider": provider, "status": integ.status}


@router.get("/google/start")
async def google_oauth_start(auth: CurrentAuth, provider: str = "gsc"):
    if not settings.GOOGLE_CLIENT_ID:
        return {
            "mode": "mock",
            "message": "Configure GOOGLE_CLIENT_ID to enable real OAuth",
            "authorize_url": None,
            "hint": "POST /integrations/connect with provider=gsc|ga4|gbp for mock connect",
        }
    scope = {
        "gsc": "https://www.googleapis.com/auth/webmasters.readonly",
        "ga4": "https://www.googleapis.com/auth/analytics.readonly",
        "gbp": "https://www.googleapis.com/auth/business.manage",
    }.get(provider, "openid email")
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code&scope={scope}&access_type=offline&prompt=consent"
        f"&state={auth.org_id}:{provider}"
    )
    return {"mode": "oauth", "authorize_url": url}


@router.get("/google/callback")
async def google_oauth_callback(code: str = "", state: str = ""):
    return {
        "message": "OAuth callback received — exchange code for tokens in production",
        "code_present": bool(code),
        "state": state,
    }


@router.post("/cms/{provider}/publish")
async def cms_publish(provider: str, auth: CurrentAuth, db: DbSession, payload: dict):
    from app.core.plans import get_limits

    if not get_limits(auth.tier).get("cms_connectors"):
        raise HTTPException(403, "CMS publish requires Professional+")
    result = await db.execute(
        select(Integration).where(
            Integration.organization_id == auth.org_id,
            Integration.provider == provider.lower(),
        )
    )
    integ = result.scalar_one_or_none()
    if not integ:
        raise HTTPException(400, f"{provider} not connected")
    return {
        "status": "queued",
        "provider": provider,
        "external_id": f"mock-{provider}-123",
        "payload_echo": {"title": payload.get("title"), "slug": payload.get("slug")},
    }
