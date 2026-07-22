from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.core.plans import get_limits
from app.models import AgentRun, AgentRunStatus, Competitor, CompetitorEvent, Workspace
from app.schemas import CompetitorCreate, CompetitorOut

router = APIRouter()


@router.get("", response_model=list[CompetitorOut])
async def list_competitors(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("competitor")
    result = await db.execute(
        select(Competitor).where(
            Competitor.organization_id == auth.org_id,
            Competitor.workspace_id == workspace_id,
        )
    )
    return result.scalars().all()


@router.post("", response_model=CompetitorOut)
async def add_competitor(body: CompetitorCreate, auth: CurrentAuth, db: DbSession):
    auth.require_feature("competitor")
    limits = get_limits(auth.tier)
    existing = await db.execute(
        select(Competitor).where(
            Competitor.organization_id == auth.org_id,
            Competitor.workspace_id == body.workspace_id,
        )
    )
    if len(existing.scalars().all()) >= limits["competitors"]:
        raise HTTPException(403, "Competitor limit reached")
    ws = await db.get(Workspace, body.workspace_id)
    if not ws or ws.organization_id != auth.org_id:
        raise HTTPException(404, "Workspace not found")
    domain = body.domain.lower().removeprefix("https://").removeprefix("http://").split("/")[0]
    comp = Competitor(
        organization_id=auth.org_id,
        workspace_id=ws.id,
        name=body.name,
        domain=domain,
    )
    db.add(comp)
    await db.flush()
    return comp


@router.post("/{competitor_id}/scan")
async def scan_competitor(competitor_id: str, auth: CurrentAuth, db: DbSession):
    auth.require_feature("competitor")
    comp = await db.get(Competitor, competitor_id)
    if not comp or comp.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=comp.workspace_id,
        agent="competitor",
        goal=f"Scan {comp.domain}",
        status=AgentRunStatus.QUEUED,
        input_payload={"competitor_id": str(comp.id)},
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run.output_payload


@router.get("/{competitor_id}/events")
async def competitor_events(competitor_id: str, auth: CurrentAuth, db: DbSession):
    auth.require_feature("competitor")
    result = await db.execute(
        select(CompetitorEvent)
        .where(
            CompetitorEvent.organization_id == auth.org_id,
            CompetitorEvent.competitor_id == competitor_id,
        )
        .order_by(CompetitorEvent.detected_at.desc())
    )
    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "title": e.title,
            "payload": e.payload,
            "detected_at": e.detected_at,
        }
        for e in result.scalars().all()
    ]
