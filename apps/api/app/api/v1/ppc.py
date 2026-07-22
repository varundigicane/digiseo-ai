from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.models import AgentRun, AgentRunStatus, PPCCampaign

router = APIRouter()


class PPCCreate(BaseModel):
    workspace_id: str
    platform: str = "google"
    name: str | None = None
    budget_daily: float = 50
    keywords: list[str] = []
    landing_page_url: str | None = None
    goal: str = "Lead gen for DigiSEO AI"


@router.post("/optimize")
async def optimize(body: PPCCreate, auth: CurrentAuth, db: DbSession):
    auth.require_feature("ppc")
    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        agent="ppc",
        goal=body.goal,
        status=AgentRunStatus.QUEUED,
        input_payload=body.model_dump(),
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run.output_payload


@router.get("/campaigns")
async def list_campaigns(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("ppc")
    result = await db.execute(
        select(PPCCampaign).where(
            PPCCampaign.organization_id == auth.org_id,
            PPCCampaign.workspace_id == workspace_id,
        )
    )
    return [
        {
            "id": str(c.id),
            "platform": c.platform,
            "name": c.name,
            "budget_daily": c.budget_daily,
            "status": c.status,
            "keywords": c.keywords,
            "ad_copies": c.ad_copies,
            "recommendations": c.recommendations,
            "landing_page_url": c.landing_page_url,
        }
        for c in result.scalars().all()
    ]


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, auth: CurrentAuth, db: DbSession):
    auth.require_feature("ppc")
    c = await db.get(PPCCampaign, campaign_id)
    if not c or c.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    return c
