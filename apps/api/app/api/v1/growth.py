from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.models import AgentRun, AgentRunStatus

router = APIRouter()


class CroRequest(BaseModel):
    workspace_id: str
    site_id: str | None = None
    offer: str = "primary conversion"
    goal: str = "Improve conversion rate"


class EmailRequest(BaseModel):
    workspace_id: str
    topic: str = "SEO growth"
    goal: str = "Email nurture plan"


@router.post("/cro")
async def cro_optimize(body: CroRequest, auth: CurrentAuth, db: DbSession):
    auth.require_feature("cro")
    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        site_id=body.site_id,
        agent="cro",
        goal=body.goal,
        status=AgentRunStatus.QUEUED,
        input_payload={"offer": body.offer},
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run.output_payload


@router.post("/email")
async def email_plan(body: EmailRequest, auth: CurrentAuth, db: DbSession):
    auth.require_feature("email")
    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        agent="email",
        goal=body.goal,
        status=AgentRunStatus.QUEUED,
        input_payload={"topic": body.topic},
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run.output_payload
