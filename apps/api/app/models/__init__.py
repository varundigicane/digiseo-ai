"""SQLAlchemy models for DigiSEO AI."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base

# Use JSONB on Postgres, JSON elsewhere (e.g. SQLite)
JSONType = JSON().with_variant(JSONB(), "postgresql")


def uuid_pk():
    return mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Role(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class PlanTier(str, enum.Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class ChangeRequestStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"


class AgentRunStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = uuid_pk()
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    memberships: Mapped[list[Membership]] = relationship(back_populates="user")


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[str] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    # White-label (Phase 3)
    white_label_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    custom_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    brand_logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    brand_primary_color: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    sso_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    sso_metadata: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    memberships: Mapped[list[Membership]] = relationship(back_populates="organization")
    workspaces: Mapped[list[Workspace]] = relationship(back_populates="organization")
    subscription: Mapped[Optional[Subscription]] = relationship(
        back_populates="organization", uselist=False
    )


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "organization_id", name="uq_membership"),)

    id: Mapped[str] = uuid_pk()
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=Role.OWNER)

    user: Mapped[User] = relationship(back_populates="memberships")
    organization: Mapped[Organization] = relationship(back_populates="memberships")


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, index=True
    )
    tier: Mapped[PlanTier] = mapped_column(Enum(PlanTier, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=PlanTier.STARTER)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="trialing")
    credits_balance: Mapped[int] = mapped_column(Integer, default=500)
    credits_reset_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    auto_apply_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = relationship(back_populates="subscription")


class CreditLedger(Base, TimestampMixin):
    __tablename__ = "credit_ledger"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    delta: Mapped[int] = mapped_column(Integer)
    balance_after: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(255))
    reference_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)


class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100))
    brand_voice: Mapped[str] = mapped_column(Text, default="")
    industry: Mapped[str] = mapped_column(String(128), default="")

    organization: Mapped[Organization] = relationship(back_populates="workspaces")
    sites: Mapped[list[Site]] = relationship(back_populates="workspace")


class Site(Base, TimestampMixin):
    __tablename__ = "sites"

    id: Mapped[str] = uuid_pk()
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    url: Mapped[str] = mapped_column(String(512))
    domain: Mapped[str] = mapped_column(String(255), index=True)
    gsc_property: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    last_crawled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    seo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    aeo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    workspace: Mapped[Workspace] = relationship(back_populates="sites")
    crawls: Mapped[list[Crawl]] = relationship(back_populates="site")
    pages: Mapped[list[Page]] = relationship(back_populates="site")


class Crawl(Base, TimestampMixin):
    __tablename__ = "crawls"

    id: Mapped[str] = uuid_pk()
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(64), default="queued")
    pages_found: Mapped[int] = mapped_column(Integer, default=0)
    pages_crawled: Mapped[int] = mapped_column(Integer, default=0)
    robots_txt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sitemap_urls: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    site: Mapped[Site] = relationship(back_populates="crawls")


class Page(Base, TimestampMixin):
    __tablename__ = "pages"

    id: Mapped[str] = uuid_pk()
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    url: Mapped[str] = mapped_column(String(1024))
    path: Mapped[str] = mapped_column(String(1024), default="/")
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    h1: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    canonical: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    has_schema: Mapped[bool] = mapped_column(Boolean, default=False)
    schema_types: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    images: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    links_internal: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    links_external: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    broken_links: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    load_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    crawl_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    site: Mapped[Site] = relationship(back_populates="pages")


class Issue(Base, TimestampMixin):
    __tablename__ = "issues"

    id: Mapped[str] = uuid_pk()
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    page_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    category: Mapped[str] = mapped_column(String(64))  # technical, onpage, aeo, content, local
    severity: Mapped[str] = mapped_column(String(32))  # critical, high, medium, low
    code: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text, default="")
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)


class ChangeRequest(Base, TimestampMixin):
    __tablename__ = "change_requests"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    site_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    agent: Mapped[str] = mapped_column(String(64))
    change_type: Mapped[str] = mapped_column(String(64))  # meta, schema, cms, social_reply, etc.
    title: Mapped[str] = mapped_column(String(255))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    status: Mapped[ChangeRequestStatus] = mapped_column(
        Enum(ChangeRequestStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=ChangeRequestStatus.PROPOSED
    )
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Keyword(Base, TimestampMixin):
    __tablename__ = "keywords"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    site_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    term: Mapped[str] = mapped_column(String(255), index=True)
    cluster_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    intent: Mapped[str] = mapped_column(String(64), default="informational")
    volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    is_long_tail: Mapped[bool] = mapped_column(Boolean, default=False)
    semantic_group: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)


class KeywordCluster(Base, TimestampMixin):
    __tablename__ = "keyword_clusters"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    name: Mapped[str] = mapped_column(String(255))
    primary_keyword: Mapped[str] = mapped_column(String(255))
    intent: Mapped[str] = mapped_column(String(64), default="informational")
    keyword_ids: Mapped[list[Any]] = mapped_column(JSONType, default=list)


class ContentPiece(Base, TimestampMixin):
    __tablename__ = "content_pieces"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    site_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    content_type: Mapped[str] = mapped_column(String(64))  # blog, landing, case_study, whitepaper, pr, newsletter
    title: Mapped[str] = mapped_column(String(512))
    slug: Mapped[str] = mapped_column(String(512), default="")
    body_markdown: Mapped[str] = mapped_column(Text, default="")
    body_html: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(64), default="draft")
    target_keywords: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    aeo_faq: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ContentCalendarItem(Base, TimestampMixin):
    __tablename__ = "content_calendar_items"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    content_piece_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(512))
    channel: Mapped[str] = mapped_column(String(64), default="blog")
    planned_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(64), default="planned")
    notes: Mapped[str] = mapped_column(Text, default="")


class SocialAccount(Base, TimestampMixin):
    __tablename__ = "social_accounts"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    platform: Mapped[str] = mapped_column(String(64))  # linkedin, x, facebook, instagram, threads, youtube, tiktok
    handle: Mapped[str] = mapped_column(String(255))
    access_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SocialPost(Base, TimestampMixin):
    __tablename__ = "social_posts"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    social_account_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    platform: Mapped[str] = mapped_column(String(64))
    body: Mapped[str] = mapped_column(Text)
    hashtags: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    media_urls: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    script: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # reels/shorts
    status: Mapped[str] = mapped_column(String(64), default="draft")
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)


class Competitor(Base, TimestampMixin):
    __tablename__ = "competitors"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(255), index=True)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class CompetitorEvent(Base, TimestampMixin):
    __tablename__ = "competitor_events"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    competitor_id: Mapped[str] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(64))  # blog, keyword, backlink, ad, social, site_change, aio
    title: Mapped[str] = mapped_column(String(512))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Integration(Base, TimestampMixin):
    __tablename__ = "integrations"
    __table_args__ = (
        UniqueConstraint("organization_id", "provider", "workspace_id", name="uq_integration"),
    )

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    provider: Mapped[str] = mapped_column(String(64))  # gsc, ga4, gbp, ahrefs, semrush, hubspot, salesforce, wordpress, shopify
    access_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scopes: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    status: Mapped[str] = mapped_column(String(64), default="connected")


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    site_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    agent: Mapped[str] = mapped_column(String(64))
    goal: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[AgentRunStatus] = mapped_column(Enum(AgentRunStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=AgentRunStatus.QUEUED)
    credits_used: Mapped[int] = mapped_column(Integer, default=0)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_run_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class AgentArtifact(Base, TimestampMixin):
    __tablename__ = "agent_artifacts"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    agent_run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"))
    artifact_type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    data: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    report_type: Mapped[str] = mapped_column(String(64))  # daily, seo_audit, aeo, roi
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class BacklinkOpportunity(Base, TimestampMixin):
    __tablename__ = "backlink_opportunities"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    domain: Mapped[str] = mapped_column(String(255))
    page_url: Mapped[str] = mapped_column(String(1024))
    contact_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    outreach_status: Mapped[str] = mapped_column(String(64), default="identified")
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    draft_email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PPCCampaign(Base, TimestampMixin):
    __tablename__ = "ppc_campaigns"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    platform: Mapped[str] = mapped_column(String(64))  # google, meta, linkedin
    name: Mapped[str] = mapped_column(String(255))
    budget_daily: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(64), default="draft")
    keywords: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    ad_copies: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    landing_page_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    recommendations: Mapped[list[Any]] = mapped_column(JSONType, default=list)


class LocalListing(Base, TimestampMixin):
    __tablename__ = "local_listings"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    workspace_id: Mapped[str] = mapped_column(String(36), index=True)
    business_name: Mapped[str] = mapped_column(String(255))
    gbp_place_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    categories: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    review_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    citations: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    local_keywords: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    map_rankings: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = uuid_pk()
    organization_id: Mapped[str] = mapped_column(String(36), index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(128))
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
