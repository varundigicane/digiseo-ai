from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    org_id: str
    workspace_id: Optional[str] = None


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    organization_name: str
    workspace_name: str = "Default"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str

    model_config = {"from_attributes": True}


class OrganizationOut(BaseModel):
    id: str
    name: str
    slug: str
    white_label_enabled: bool = False
    custom_domain: Optional[str] = None
    brand_logo_url: Optional[str] = None
    brand_primary_color: Optional[str] = None
    sso_enabled: bool = False

    model_config = {"from_attributes": True}


class WorkspaceOut(BaseModel):
    id: str
    organization_id: str
    name: str
    slug: str
    brand_voice: str = ""
    industry: str = ""

    model_config = {"from_attributes": True}


class WorkspaceCreate(BaseModel):
    name: str
    brand_voice: str = ""
    industry: str = ""


class SubscriptionOut(BaseModel):
    id: str
    tier: str
    status: str
    credits_balance: int
    auto_apply_enabled: bool
    limits: dict[str, Any] = {}

    model_config = {"from_attributes": True}


class SiteCreate(BaseModel):
    url: str
    workspace_id: str


class SiteOut(BaseModel):
    id: str
    workspace_id: str
    organization_id: str
    url: str
    domain: str
    gsc_property: Optional[str] = None
    last_crawled_at: Optional[datetime] = None
    seo_score: Optional[float] = None
    aeo_score: Optional[float] = None

    model_config = {"from_attributes": True}


class CrawlOut(BaseModel):
    id: str
    site_id: str
    status: str
    pages_found: int
    pages_crawled: int
    error: Optional[str] = None

    model_config = {"from_attributes": True}


class IssueOut(BaseModel):
    id: str
    site_id: str
    category: str
    severity: str
    code: str
    title: str
    description: str
    recommendation: str
    resolved: bool

    model_config = {"from_attributes": True}


class ChangeRequestOut(BaseModel):
    id: str
    agent: str
    change_type: str
    title: str
    payload: dict[str, Any]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangeRequestReview(BaseModel):
    status: str = Field(pattern="^(approved|rejected)$")


class AgentRunRequest(BaseModel):
    agent: str
    workspace_id: str
    site_id: Optional[str] = None
    goal: str = ""
    input_payload: dict[str, Any] = {}


class AgentRunOut(BaseModel):
    id: str
    agent: str
    goal: str
    status: str
    credits_used: int
    output_payload: dict[str, Any] = {}
    error: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentGenerateRequest(BaseModel):
    workspace_id: str
    site_id: Optional[str] = None
    content_type: str = "blog"
    topic: str
    keywords: list[str] = []
    tone: str = "professional"


class ContentPieceOut(BaseModel):
    id: str
    content_type: str
    title: str
    body_markdown: str
    status: str
    target_keywords: list[Any] = []
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    aeo_faq: list[Any] = []

    model_config = {"from_attributes": True}


class SocialPostCreate(BaseModel):
    workspace_id: str
    platform: str
    topic: str
    tone: str = "engaging"


class SocialPostOut(BaseModel):
    id: str
    platform: str
    body: str
    hashtags: list[Any] = []
    script: Optional[str] = None
    status: str
    scheduled_at: Optional[datetime] = None
    metrics: dict[str, Any] = {}

    model_config = {"from_attributes": True}


class CompetitorCreate(BaseModel):
    workspace_id: str
    name: str
    domain: str


class CompetitorOut(BaseModel):
    id: str
    name: str
    domain: str
    last_checked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CheckoutRequest(BaseModel):
    tier: str = Field(pattern="^(starter|professional|business|enterprise)$")
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CreditPackPurchase(BaseModel):
    credits: int = Field(ge=100, le=100000)


class WorkflowLaunchRequest(BaseModel):
    workspace_id: str
    site_id: Optional[str] = None
    workflow: str = "launch_product"
    goal: str
    input_payload: dict[str, Any] = {}


class DashboardOut(BaseModel):
    seo_score: Optional[float] = None
    aeo_score: Optional[float] = None
    credits_balance: int = 0
    open_issues: int = 0
    pending_approvals: int = 0
    recent_runs: list[AgentRunOut] = []
    metrics: dict[str, Any] = {}

