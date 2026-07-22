from fastapi import APIRouter, HTTPException

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.models import AgentRun, AgentRunStatus, Workspace
from app.schemas import AgentRunOut, WorkflowLaunchRequest

router = APIRouter()


@router.post("/launch", response_model=AgentRunOut)
async def launch_workflow(body: WorkflowLaunchRequest, auth: CurrentAuth, db: DbSession):
    auth.require_feature("multi_agent")
    ws = await db.get(Workspace, body.workspace_id)
    if not ws or ws.organization_id != auth.org_id:
        raise HTTPException(404, "Workspace not found")

    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        site_id=body.site_id,
        agent=body.workflow if body.workflow != "launch_product" else "launch_product",
        goal=body.goal,
        status=AgentRunStatus.QUEUED,
        input_payload=body.input_payload,
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run


@router.get("/templates")
async def workflow_templates(auth: CurrentAuth):
    auth.require_feature("multi_agent")
    return [
        {
            "id": "launch_product",
            "name": "Launch Product",
            "steps": ["keyword", "content", "aeo", "social", "analytics"],
            "description": "Research keywords, draft content, optimize for answer engines, socialize, and report.",
        },
        {
            "id": "seo_refresh",
            "name": "SEO Refresh",
            "steps": ["seo", "aeo", "content"],
            "description": "Full site audit, AEO upgrades, and content fixes.",
        },
    ]
