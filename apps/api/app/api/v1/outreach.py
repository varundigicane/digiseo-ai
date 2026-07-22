from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.models import AgentRun, AgentRunStatus, BacklinkOpportunity

router = APIRouter()


class TrackResponse(BaseModel):
    response_notes: str
    outreach_status: str = "replied"


@router.post("/discover")
async def discover(auth: CurrentAuth, db: DbSession, workspace_id: str, niche: str = "ai-marketing"):
    auth.require_feature("backlink")
    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=workspace_id,
        agent="backlink",
        goal=f"Find backlinks in {niche}",
        status=AgentRunStatus.QUEUED,
        input_payload={"niche": niche},
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run.output_payload


@router.get("/opportunities")
async def list_opportunities(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("backlink")
    result = await db.execute(
        select(BacklinkOpportunity).where(
            BacklinkOpportunity.organization_id == auth.org_id,
            BacklinkOpportunity.workspace_id == workspace_id,
        )
    )
    return [
        {
            "id": str(o.id),
            "domain": o.domain,
            "page_url": o.page_url,
            "contact_email": o.contact_email,
            "outreach_status": o.outreach_status,
            "quality_score": o.quality_score,
            "draft_email": o.draft_email,
        }
        for o in result.scalars().all()
    ]


@router.post("/opportunities/{opp_id}/send")
async def send_outreach(opp_id: str, auth: CurrentAuth, db: DbSession):
    auth.require_feature("backlink")
    opp = await db.get(BacklinkOpportunity, opp_id)
    if not opp or opp.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    opp.outreach_status = "sent"
    await db.flush()
    return {"status": "sent", "id": str(opp.id), "note": "Email send is stubbed; integrate ESP in production"}


@router.post("/opportunities/{opp_id}/response")
async def track_response(opp_id: str, body: TrackResponse, auth: CurrentAuth, db: DbSession):
    auth.require_feature("backlink")
    opp = await db.get(BacklinkOpportunity, opp_id)
    if not opp or opp.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    opp.outreach_status = body.outreach_status
    opp.response_notes = body.response_notes
    await db.flush()
    return {"id": str(opp.id), "outreach_status": opp.outreach_status}
