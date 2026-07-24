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

    workflow = body.workflow
    agent = {
        "launch_product": "launch_product",
        "growth_playbook": "growth_playbook",
        "seo_refresh": "launch_product",
    }.get(workflow, workflow)

    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        site_id=body.site_id,
        agent=agent,
        goal=body.goal,
        status=AgentRunStatus.QUEUED,
        input_payload={**(body.input_payload or {}), "workflow": workflow},
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
            "id": "growth_playbook",
            "name": "Growth Playbook",
            "steps": [
                "seo",
                "aeo",
                "keyword",
                "content",
                "cro",
                "backlink",
                "local_seo",
                "ppc",
                "social",
                "email",
                "analytics",
            ],
            "description": (
                "Hierarchy playbook: Strategy/Audit → AI SEO & On-Page → Content → CRO → "
                "Off-Page & Local → Paid & SMM & Email → Reporting."
            ),
        },
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
