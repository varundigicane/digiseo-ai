from fastapi import APIRouter
from sqlalchemy import select

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.models import AgentRun, AgentRunStatus, Report

router = APIRouter()


@router.get("/dashboard")
async def analytics_dashboard(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("analytics")
    result = await db.execute(
        select(Report)
        .where(Report.organization_id == auth.org_id, Report.workspace_id == workspace_id)
        .order_by(Report.created_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    if not latest:
        # Generate on demand
        run = AgentRun(
            organization_id=auth.org_id,
            workspace_id=workspace_id,
            agent="analytics",
            goal="Daily dashboard",
            status=AgentRunStatus.QUEUED,
        )
        db.add(run)
        await db.flush()
        run = await execute_agent_run(db, run)
        return {"metrics": run.output_payload, "generated": True}
    return {
        "report_id": str(latest.id),
        "title": latest.title,
        "summary": latest.summary,
        "metrics": latest.metrics,
        "generated": False,
    }


@router.post("/daily-report")
async def generate_daily(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("analytics")
    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=workspace_id,
        agent="analytics",
        goal="Generate daily report",
        status=AgentRunStatus.QUEUED,
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run.output_payload


@router.get("/reports")
async def list_reports(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("analytics")
    result = await db.execute(
        select(Report)
        .where(Report.organization_id == auth.org_id, Report.workspace_id == workspace_id)
        .order_by(Report.created_at.desc())
        .limit(30)
    )
    return [
        {
            "id": str(r.id),
            "type": r.report_type,
            "title": r.title,
            "summary": r.summary,
            "metrics": r.metrics,
            "created_at": r.created_at,
        }
        for r in result.scalars().all()
    ]
