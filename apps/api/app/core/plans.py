"""Plan limits and feature flags by subscription tier."""

from enum import Enum
from typing import Any


class PlanTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


PLAN_LIMITS: dict[PlanTier, dict[str, Any]] = {
    PlanTier.STARTER: {
        "price_usd": 49,
        "monthly_credits": 500,
        "workspaces": 1,
        "sites": 1,
        "audits_per_month": 5,
        "social_channels": 0,
        "competitors": 0,
        "cms_connectors": False,
        "auto_apply": False,
        "api_access": False,
        "white_label": False,
        "sso": False,
        "features": ["seo_audit", "aeo", "blog_generation", "gsc"],
    },
    PlanTier.PROFESSIONAL: {
        "price_usd": 149,
        "monthly_credits": 2000,
        "workspaces": 3,
        "sites": 5,
        "audits_per_month": 30,
        "social_channels": 4,
        "competitors": 5,
        "cms_connectors": True,
        "auto_apply": False,
        "api_access": False,
        "white_label": False,
        "sso": False,
        "features": [
            "seo_audit",
            "aeo",
            "blog_generation",
            "gsc",
            "social",
            "content_calendar",
            "analytics",
            "competitor",
            "trends",
        ],
    },
    PlanTier.BUSINESS: {
        "price_usd": 399,
        "monthly_credits": 8000,
        "workspaces": 10,
        "sites": 25,
        "audits_per_month": 100,
        "social_channels": 12,
        "competitors": 25,
        "cms_connectors": True,
        "auto_apply": True,
        "api_access": True,
        "white_label": False,
        "sso": False,
        "features": [
            "seo_audit",
            "aeo",
            "blog_generation",
            "gsc",
            "social",
            "content_calendar",
            "analytics",
            "competitor",
            "trends",
            "backlink",
            "ppc",
            "local_seo",
            "multi_agent",
            "auto_apply",
        ],
    },
    PlanTier.ENTERPRISE: {
        "price_usd": None,
        "monthly_credits": 50000,
        "workspaces": 100,
        "sites": 500,
        "audits_per_month": 1000,
        "social_channels": 100,
        "competitors": 100,
        "cms_connectors": True,
        "auto_apply": True,
        "api_access": True,
        "white_label": True,
        "sso": True,
        "features": ["*"],
    },
}


def has_feature(tier: PlanTier | str, feature: str) -> bool:
    t = PlanTier(tier) if isinstance(tier, str) else tier
    limits = PLAN_LIMITS[t]
    feats = limits["features"]
    return "*" in feats or feature in feats


def get_limits(tier: PlanTier | str) -> dict[str, Any]:
    t = PlanTier(tier) if isinstance(tier, str) else tier
    return PLAN_LIMITS[t]
