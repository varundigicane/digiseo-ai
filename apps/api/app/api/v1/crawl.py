from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentAuth, DbSession
from app.models import Crawl, Issue, Page, Site
from app.schemas import CrawlOut, IssueOut
from app.services.crawler import run_crawl

router = APIRouter()


@router.post("/{site_id}/start", response_model=CrawlOut)
async def start_crawl(site_id: str, auth: CurrentAuth, db: DbSession):
    site = await db.get(Site, site_id)
    if not site or site.organization_id != auth.org_id:
        raise HTTPException(404, "Site not found")

    crawl = Crawl(site_id=site.id, organization_id=auth.org_id, status="queued")
    db.add(crawl)
    await db.flush()
    crawl = await run_crawl(db, site, crawl)
    return crawl


@router.get("/{site_id}/latest", response_model=CrawlOut | None)
async def latest_crawl(site_id: str, auth: CurrentAuth, db: DbSession):
    site = await db.get(Site, site_id)
    if not site or site.organization_id != auth.org_id:
        raise HTTPException(404, "Site not found")
    result = await db.execute(
        select(Crawl).where(Crawl.site_id == site.id).order_by(Crawl.created_at.desc()).limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/{site_id}/pages")
async def list_pages(site_id: str, auth: CurrentAuth, db: DbSession):
    site = await db.get(Site, site_id)
    if not site or site.organization_id != auth.org_id:
        raise HTTPException(404, "Site not found")
    result = await db.execute(select(Page).where(Page.site_id == site.id))
    pages = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "url": p.url,
            "path": p.path,
            "title": p.title,
            "status_code": p.status_code,
            "word_count": p.word_count,
            "has_schema": p.has_schema,
            "seo_hints": {
                "meta_description": p.meta_description,
                "h1": p.h1,
            },
        }
        for p in pages
    ]


@router.get("/{site_id}/issues", response_model=list[IssueOut])
async def list_issues(site_id: str, auth: CurrentAuth, db: DbSession):
    site = await db.get(Site, site_id)
    if not site or site.organization_id != auth.org_id:
        raise HTTPException(404, "Site not found")
    result = await db.execute(
        select(Issue).where(Issue.site_id == site.id).order_by(Issue.created_at.desc())
    )
    return result.scalars().all()
