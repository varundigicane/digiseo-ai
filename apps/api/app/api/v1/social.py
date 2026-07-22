from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.core.plans import get_limits
from app.models import AgentRun, AgentRunStatus, SocialAccount, SocialPost, Workspace
from app.schemas import SocialPostCreate, SocialPostOut

router = APIRouter()


class ConnectSocial(BaseModel):
    workspace_id: str
    platform: str
    handle: str


class ScheduleBody(BaseModel):
    scheduled_at: datetime


class ReplyBody(BaseModel):
    comment_id: str
    reply: str


@router.get("/accounts")
async def list_accounts(auth: CurrentAuth, db: DbSession, workspace_id: str | None = None):
    auth.require_feature("social")
    q = select(SocialAccount).where(SocialAccount.organization_id == auth.org_id)
    if workspace_id:
        q = q.where(SocialAccount.workspace_id == workspace_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/accounts")
async def connect_account(body: ConnectSocial, auth: CurrentAuth, db: DbSession):
    auth.require_feature("social")
    limits = get_limits(auth.tier)
    existing = await db.execute(
        select(SocialAccount).where(SocialAccount.organization_id == auth.org_id, SocialAccount.is_active.is_(True))
    )
    if len(existing.scalars().all()) >= limits["social_channels"]:
        raise HTTPException(403, "Social channel limit reached")
    ws = await db.get(Workspace, body.workspace_id)
    if not ws or ws.organization_id != auth.org_id:
        raise HTTPException(404, "Workspace not found")
    acct = SocialAccount(
        organization_id=auth.org_id,
        workspace_id=ws.id,
        platform=body.platform.lower(),
        handle=body.handle,
        access_token_enc="enc:mock",
        meta={"mock": True},
    )
    db.add(acct)
    await db.flush()
    return {"id": str(acct.id), "platform": acct.platform, "handle": acct.handle}


@router.post("/generate", response_model=SocialPostOut)
async def generate_post(body: SocialPostCreate, auth: CurrentAuth, db: DbSession):
    auth.require_feature("social")
    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        agent="social",
        goal=body.topic,
        status=AgentRunStatus.QUEUED,
        input_payload={"platform": body.platform, "topic": body.topic, "tone": body.tone},
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    post_id = run.output_payload.get("social_post_id")
    post = await db.get(SocialPost, post_id)
    return post


@router.get("/posts", response_model=list[SocialPostOut])
async def list_posts(auth: CurrentAuth, db: DbSession, workspace_id: str | None = None):
    auth.require_feature("social")
    q = select(SocialPost).where(SocialPost.organization_id == auth.org_id)
    if workspace_id:
        q = q.where(SocialPost.workspace_id == workspace_id)
    result = await db.execute(q.order_by(SocialPost.created_at.desc()).limit(50))
    return result.scalars().all()


@router.post("/posts/{post_id}/schedule", response_model=SocialPostOut)
async def schedule_post(post_id: str, body: ScheduleBody, auth: CurrentAuth, db: DbSession):
    auth.require_feature("social")
    post = await db.get(SocialPost, post_id)
    if not post or post.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    post.scheduled_at = body.scheduled_at
    post.status = "scheduled"
    await db.flush()
    return post


@router.post("/posts/{post_id}/publish", response_model=SocialPostOut)
async def publish_post(post_id: str, auth: CurrentAuth, db: DbSession):
    auth.require_feature("social")
    post = await db.get(SocialPost, post_id)
    if not post or post.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    post.status = "published"
    post.published_at = datetime.now(timezone.utc)
    post.metrics = {"likes": 0, "comments": 0, "shares": 0, "impressions": 0}
    await db.flush()
    return post


@router.post("/reply")
async def reply_comment(body: ReplyBody, auth: CurrentAuth):
    auth.require_feature("social")
    # Human-in-the-loop: return draft for approval rather than sending
    return {
        "status": "proposed",
        "comment_id": body.comment_id,
        "reply": body.reply,
        "message": "Reply queued for approval before send",
    }


@router.get("/analytics")
async def social_analytics(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("social")
    result = await db.execute(
        select(SocialPost).where(
            SocialPost.organization_id == auth.org_id,
            SocialPost.workspace_id == workspace_id,
            SocialPost.status == "published",
        )
    )
    posts = result.scalars().all()
    return {
        "published": len(posts),
        "platforms": list({p.platform for p in posts}),
        "totals": {
            "likes": sum((p.metrics or {}).get("likes", 0) for p in posts),
            "comments": sum((p.metrics or {}).get("comments", 0) for p in posts),
        },
    }
