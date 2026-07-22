"""DigiSEO agent SDK — contracts shared across agents and MCP adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable


class AgentName(str, Enum):
    SEO = "seo"
    AEO = "aeo"
    CONTENT = "content"
    SOCIAL = "social"
    COMPETITOR = "competitor"
    KEYWORD = "keyword"
    BACKLINK = "backlink"
    PPC = "ppc"
    ANALYTICS = "analytics"
    LOCAL_SEO = "local_seo"
    SUPERVISOR = "supervisor"


@dataclass
class AgentContract:
    name: AgentName
    description: str
    credit_cost: int
    required_feature: str
    requires_approval: bool = True
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


AGENT_CATALOG: dict[str, AgentContract] = {
    "seo": AgentContract(
        AgentName.SEO,
        "Website technical and on-page SEO audit",
        25,
        "seo_audit",
        inputs=["site_id"],
        outputs=["seo_audit", "issues", "change_requests"],
    ),
    "aeo": AgentContract(
        AgentName.AEO,
        "Answer Engine Optimization for AI search",
        20,
        "aeo",
        inputs=["site_id"],
        outputs=["aeo_report", "faq_schema", "llm_chunks"],
    ),
    "content": AgentContract(
        AgentName.CONTENT,
        "Content marketing generation",
        40,
        "blog_generation",
        inputs=["topic", "keywords"],
        outputs=["content_piece"],
    ),
    "social": AgentContract(
        AgentName.SOCIAL,
        "Social media content and scheduling",
        10,
        "social",
        inputs=["platform", "topic"],
        outputs=["social_post"],
    ),
    "competitor": AgentContract(
        AgentName.COMPETITOR,
        "Competitor intelligence scanning",
        20,
        "competitor",
        inputs=["competitor_id"],
        outputs=["competitor_events"],
    ),
    "keyword": AgentContract(
        AgentName.KEYWORD,
        "Keyword research and clustering",
        15,
        "gsc",
        inputs=["seed", "queries"],
        outputs=["keywords", "clusters"],
    ),
    "backlink": AgentContract(
        AgentName.BACKLINK,
        "Backlink outreach opportunities",
        25,
        "backlink",
        inputs=["niche"],
        outputs=["opportunities"],
    ),
    "ppc": AgentContract(
        AgentName.PPC,
        "PPC campaign optimization",
        30,
        "ppc",
        inputs=["platform", "budget_daily"],
        outputs=["campaign"],
    ),
    "analytics": AgentContract(
        AgentName.ANALYTICS,
        "Marketing analytics and ROI reporting",
        10,
        "analytics",
        requires_approval=False,
        inputs=["workspace_id"],
        outputs=["report"],
    ),
    "local_seo": AgentContract(
        AgentName.LOCAL_SEO,
        "Local SEO and GBP optimization",
        20,
        "local_seo",
        inputs=["business_name"],
        outputs=["listing"],
    ),
}


ToolHandler = Callable[..., Awaitable[Any]]


@dataclass
class MCPTool:
    name: str
    description: str
    handler: ToolHandler | None = None


def default_mcp_tools() -> list[MCPTool]:
    return [
        MCPTool("crawl_site", "Crawl a website and extract SEO signals"),
        MCPTool("search_chunks", "Semantic search over indexed page chunks"),
        MCPTool("gsc_queries", "Fetch Google Search Console queries"),
        MCPTool("publish_cms", "Publish content to connected CMS"),
        MCPTool("schedule_social", "Schedule a social post"),
    ]
