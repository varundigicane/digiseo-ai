from fastapi import APIRouter

from app.api.v1 import (
    agents,
    analytics,
    auth,
    billing,
    change_requests,
    competitors,
    content,
    crawl,
    enterprise,
    growth,
    integrations,
    local_seo,
    outreach,
    ppc,
    sites,
    social,
    workflows,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(crawl.router, prefix="/crawl", tags=["crawl"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(change_requests.router, prefix="/change-requests", tags=["approvals"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
api_router.include_router(ppc.router, prefix="/ppc", tags=["ppc"])
api_router.include_router(local_seo.router, prefix="/local-seo", tags=["local-seo"])
api_router.include_router(growth.router, prefix="/growth", tags=["growth"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(enterprise.router, prefix="/enterprise", tags=["enterprise"])
