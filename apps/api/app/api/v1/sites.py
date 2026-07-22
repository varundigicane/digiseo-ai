from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentAuth, DbSession
from app.core.plans import get_limits
from app.models import Site, Workspace
from app.schemas import DashboardOut, SiteCreate, SiteOut
from app.services.crawler import extract_domain

router = APIRouter()


@router.get("", response_model=list[SiteOut])
async def list_sites(auth: CurrentAuth, db: DbSession, workspace_id: str | None = None):
    q = select(Site).where(Site.organization_id == auth.org_id)
    if workspace_id:
        q = q.where(Site.workspace_id == workspace_id)
    result = await db.execute(q.order_by(Site.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=SiteOut)
async def create_site(body: SiteCreate, auth: CurrentAuth, db: DbSession):
    ws = await db.get(Workspace, body.workspace_id)
    if not ws or ws.organization_id != auth.org_id:
        raise HTTPException(404, "Workspace not found")
    limits = get_limits(auth.tier)
    existing = await db.execute(select(Site).where(Site.organization_id == auth.org_id))
    if len(existing.scalars().all()) >= limits["sites"]:
        raise HTTPException(403, "Site limit reached for your plan")

    url = body.url.strip()
    if not url.startswith("http"):
        url = f"https://{url}"
    site = Site(
        workspace_id=ws.id,
        organization_id=auth.org_id,
        url=url,
        domain=extract_domain(url),
    )
    db.add(site)
    await db.flush()
    return site


@router.get("/{site_id}", response_model=SiteOut)
async def get_site(site_id: str, auth: CurrentAuth, db: DbSession):
    site = await db.get(Site, site_id)
    if not site or site.organization_id != auth.org_id:
        raise HTTPException(404, "Site not found")
    return site


@router.get("/{site_id}/dashboard", response_model=DashboardOut)
async def site_dashboard(site_id: str, auth: CurrentAuth, db: DbSession):
    from app.models import AgentRun, ChangeRequest, ChangeRequestStatus, Issue

    site = await db.get(Site, site_id)
    if not site or site.organization_id != auth.org_id:
        raise HTTPException(404, "Site not found")

    issues = await db.execute(
        select(Issue).where(Issue.site_id == site.id, Issue.resolved.is_(False))
    )
    pending = await db.execute(
        select(ChangeRequest).where(
            ChangeRequest.organization_id == auth.org_id,
            ChangeRequest.status == ChangeRequestStatus.PROPOSED,
        )
    )
    runs = await db.execute(
        select(AgentRun)
        .where(AgentRun.organization_id == auth.org_id, AgentRun.site_id == site.id)
        .order_by(AgentRun.created_at.desc())
        .limit(5)
    )
    return DashboardOut(
        seo_score=site.seo_score,
        aeo_score=site.aeo_score,
        credits_balance=auth.subscription.credits_balance,
        open_issues=len(issues.scalars().all()),
        pending_approvals=len(pending.scalars().all()),
        recent_runs=list(runs.scalars().all()),
        metrics={"domain": site.domain},
    )
