from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.models import AgentRun, AgentRunStatus, ContentCalendarItem, ContentPiece, Workspace
from app.schemas import ContentGenerateRequest, ContentPieceOut

router = APIRouter()


@router.get("", response_model=list[ContentPieceOut])
async def list_content(auth: CurrentAuth, db: DbSession, workspace_id: str | None = None):
    q = select(ContentPiece).where(ContentPiece.organization_id == auth.org_id)
    if workspace_id:
        q = q.where(ContentPiece.workspace_id == workspace_id)
    result = await db.execute(q.order_by(ContentPiece.created_at.desc()).limit(50))
    return result.scalars().all()


@router.post("/generate", response_model=ContentPieceOut)
async def generate_content(body: ContentGenerateRequest, auth: CurrentAuth, db: DbSession):
    auth.require_feature("blog_generation")
    ws = await db.get(Workspace, body.workspace_id)
    if not ws or ws.organization_id != auth.org_id:
        raise HTTPException(404, "Workspace not found")

    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        site_id=body.site_id,
        agent="content",
        goal=body.topic,
        status=AgentRunStatus.QUEUED,
        input_payload={
            "topic": body.topic,
            "keywords": body.keywords,
            "content_type": body.content_type,
            "tone": body.tone,
        },
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    if run.status != AgentRunStatus.COMPLETED:
        raise HTTPException(500, run.error or "Content generation failed")
    piece_id = run.output_payload.get("content_piece_id")
    piece = await db.get(ContentPiece, piece_id)
    return piece


@router.get("/calendar")
async def get_calendar(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("content_calendar")
    result = await db.execute(
        select(ContentCalendarItem)
        .where(
            ContentCalendarItem.organization_id == auth.org_id,
            ContentCalendarItem.workspace_id == workspace_id,
        )
        .order_by(ContentCalendarItem.planned_date)
    )
    return result.scalars().all()


@router.post("/calendar/seed")
async def seed_calendar(auth: CurrentAuth, db: DbSession, workspace_id: str, weeks: int = 4):
    auth.require_feature("content_calendar")
    ws = await db.get(Workspace, workspace_id)
    if not ws or ws.organization_id != auth.org_id:
        raise HTTPException(404, "Workspace not found")
    now = datetime.now(timezone.utc)
    items = []
    topics = [
        ("blog", "SEO audit checklist"),
        ("landing", "Product landing page refresh"),
        ("newsletter", "Monthly growth newsletter"),
        ("case_study", "Customer success story"),
        ("social", "Thought leadership thread"),
    ]
    for i in range(weeks * 2):
        ctype, title = topics[i % len(topics)]
        item = ContentCalendarItem(
            organization_id=auth.org_id,
            workspace_id=ws.id,
            title=title,
            channel=ctype,
            planned_date=now + timedelta(days=i * 3),
            status="planned",
            notes="Auto-generated calendar item",
        )
        db.add(item)
        items.append(item)
    await db.flush()
    return [{"id": str(i.id), "title": i.title, "planned_date": i.planned_date, "channel": i.channel} for i in items]


@router.get("/{content_id}", response_model=ContentPieceOut)
async def get_content(content_id: str, auth: CurrentAuth, db: DbSession):
    piece = await db.get(ContentPiece, content_id)
    if not piece or piece.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    return piece
