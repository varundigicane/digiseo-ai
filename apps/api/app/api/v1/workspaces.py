from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentAuth, DbSession
from app.core.plans import get_limits
from app.models import Workspace
from app.schemas import WorkspaceCreate, WorkspaceOut
from app.services.auth_service import slugify

router = APIRouter()


@router.get("", response_model=list[WorkspaceOut])
async def list_workspaces(auth: CurrentAuth, db: DbSession):
    result = await db.execute(
        select(Workspace).where(Workspace.organization_id == auth.org_id).order_by(Workspace.created_at)
    )
    return result.scalars().all()


@router.post("", response_model=WorkspaceOut)
async def create_workspace(body: WorkspaceCreate, auth: CurrentAuth, db: DbSession):
    limits = get_limits(auth.tier)
    existing = await db.execute(select(Workspace).where(Workspace.organization_id == auth.org_id))
    count = len(existing.scalars().all())
    if count >= limits["workspaces"]:
        raise HTTPException(403, f"Workspace limit reached for {auth.tier.value} plan")
    ws = Workspace(
        organization_id=auth.org_id,
        name=body.name,
        slug=slugify(body.name),
        brand_voice=body.brand_voice,
        industry=body.industry,
    )
    db.add(ws)
    await db.flush()
    return ws
