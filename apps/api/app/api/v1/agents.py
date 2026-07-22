from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.models import AgentRun, AgentRunStatus, Site, Workspace
from app.schemas import AgentRunOut, AgentRunRequest

router = APIRouter()


@router.post("/run", response_model=AgentRunOut)
async def run_agent(body: AgentRunRequest, auth: CurrentAuth, db: DbSession):
    feature_map = {
        "seo": "seo_audit",
        "aeo": "aeo",
        "content": "blog_generation",
        "keyword": "gsc",
        "social": "social",
        "competitor": "competitor",
        "analytics": "analytics",
        "backlink": "backlink",
        "ppc": "ppc",
        "local_seo": "local_seo",
        "supervisor": "multi_agent",
        "launch_product": "multi_agent",
        "multi_agent": "multi_agent",
    }
    feat = feature_map.get(body.agent, body.agent)
    auth.require_feature(feat)

    ws = await db.get(Workspace, body.workspace_id)
    if not ws or ws.organization_id != auth.org_id:
        raise HTTPException(404, "Workspace not found")

    if body.site_id:
        site = await db.get(Site, body.site_id)
        if not site or site.organization_id != auth.org_id:
            raise HTTPException(404, "Site not found")

    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        site_id=body.site_id,
        agent=body.agent,
        goal=body.goal,
        status=AgentRunStatus.QUEUED,
        input_payload=body.input_payload,
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run


@router.get("", response_model=list[AgentRunOut])
async def list_runs(auth: CurrentAuth, db: DbSession, workspace_id: str | None = None):
    q = select(AgentRun).where(AgentRun.organization_id == auth.org_id)
    if workspace_id:
        q = q.where(AgentRun.workspace_id == workspace_id)
    result = await db.execute(q.order_by(AgentRun.created_at.desc()).limit(50))
    return result.scalars().all()


@router.get("/{run_id}", response_model=AgentRunOut)
async def get_run(run_id: str, auth: CurrentAuth, db: DbSession):
    run = await db.get(AgentRun, run_id)
    if not run or run.organization_id != auth.org_id:
        raise HTTPException(404, "Run not found")
    return run
