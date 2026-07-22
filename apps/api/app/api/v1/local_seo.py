from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.agents.orchestrator import execute_agent_run
from app.api.deps import CurrentAuth, DbSession
from app.models import AgentRun, AgentRunStatus, LocalListing

router = APIRouter()


class LocalSetup(BaseModel):
    workspace_id: str
    business_name: str
    address: str = ""
    phone: str = ""
    categories: list[str] = []


@router.post("/optimize")
async def optimize_local(body: LocalSetup, auth: CurrentAuth, db: DbSession):
    auth.require_feature("local_seo")
    run = AgentRun(
        organization_id=auth.org_id,
        workspace_id=body.workspace_id,
        agent="local_seo",
        goal=f"Optimize GBP for {body.business_name}",
        status=AgentRunStatus.QUEUED,
        input_payload=body.model_dump(),
    )
    db.add(run)
    await db.flush()
    run = await execute_agent_run(db, run)
    return run.output_payload


@router.get("/listings")
async def list_listings(auth: CurrentAuth, db: DbSession, workspace_id: str):
    auth.require_feature("local_seo")
    result = await db.execute(
        select(LocalListing).where(
            LocalListing.organization_id == auth.org_id,
            LocalListing.workspace_id == workspace_id,
        )
    )
    return [
        {
            "id": str(l.id),
            "business_name": l.business_name,
            "address": l.address,
            "review_score": l.review_score,
            "review_count": l.review_count,
            "citations": l.citations,
            "local_keywords": l.local_keywords,
            "map_rankings": l.map_rankings,
        }
        for l in result.scalars().all()
    ]


@router.get("/listings/{listing_id}/reviews")
async def monitor_reviews(listing_id: str, auth: CurrentAuth, db: DbSession):
    auth.require_feature("local_seo")
    listing = await db.get(LocalListing, listing_id)
    if not listing or listing.organization_id != auth.org_id:
        raise HTTPException(404, "Not found")
    return {
        "listing_id": listing_id,
        "review_score": listing.review_score,
        "review_count": listing.review_count,
        "recent_reviews": [
            {"author": "Alex", "rating": 5, "text": "Great service and clear communication."},
            {"author": "Sam", "rating": 4, "text": "Solid results on local search."},
        ],
        "alerts": ["1 review awaiting response (>24h)"],
    }
