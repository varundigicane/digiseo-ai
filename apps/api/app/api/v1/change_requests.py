from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentAuth, DbSession
from app.models import ChangeRequest, ChangeRequestStatus
from app.schemas import ChangeRequestOut, ChangeRequestReview

router = APIRouter()


@router.get("", response_model=list[ChangeRequestOut])
async def list_change_requests(
    auth: CurrentAuth,
    db: DbSession,
    status_filter: str | None = None,
):
    q = select(ChangeRequest).where(ChangeRequest.organization_id == auth.org_id)
    if status_filter:
        q = q.where(ChangeRequest.status == status_filter)
    result = await db.execute(q.order_by(ChangeRequest.created_at.desc()).limit(100))
    return result.scalars().all()


@router.post("/{change_id}/review", response_model=ChangeRequestOut)
async def review_change(change_id: str, body: ChangeRequestReview, auth: CurrentAuth, db: DbSession):
    auth.require_role("owner", "admin", "editor")
    cr = await db.get(ChangeRequest, change_id)
    if not cr or cr.organization_id != auth.org_id:
        raise HTTPException(404, "Change request not found")
    if cr.status != ChangeRequestStatus.PROPOSED:
        raise HTTPException(400, "Change request already reviewed")

    cr.status = ChangeRequestStatus.APPROVED if body.status == "approved" else ChangeRequestStatus.REJECTED
    cr.reviewed_by = auth.user.id
    cr.reviewed_at = datetime.now(timezone.utc)

    # Phase 3 auto-apply path
    if (
        cr.status == ChangeRequestStatus.APPROVED
        and auth.subscription.auto_apply_enabled
        and auth.tier.value in ("business", "enterprise")
    ):
        cr.status = ChangeRequestStatus.APPLIED
        cr.payload = {**(cr.payload or {}), "applied_at": datetime.now(timezone.utc).isoformat(), "auto": True}

    await db.flush()
    return cr


@router.post("/{change_id}/apply", response_model=ChangeRequestOut)
async def apply_change(change_id: str, auth: CurrentAuth, db: DbSession):
    """Explicit apply after approval (CMS write stub)."""
    auth.require_feature("auto_apply")
    cr = await db.get(ChangeRequest, change_id)
    if not cr or cr.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    if cr.status not in (ChangeRequestStatus.APPROVED, ChangeRequestStatus.APPLIED):
        raise HTTPException(400, "Must be approved first")
    cr.status = ChangeRequestStatus.APPLIED
    cr.payload = {
        **(cr.payload or {}),
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "cms": "stub",
    }
    await db.flush()
    return cr
