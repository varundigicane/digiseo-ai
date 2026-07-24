"""LangGraph multi-agent orchestration for DigiSEO AI."""

from __future__ import annotations

from typing import Any, Literal, TypedDict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AgentArtifact,
    AgentRun,
    AgentRunStatus,
    ChangeRequest,
    ChangeRequestStatus,
    ContentPiece,
    Issue,
    Keyword,
    KeywordCluster,
    Page,
    Site,
)
from app.services import llm
from app.services.auth_service import debit_credits
from app.services.vector_store import chunk_text, search_chunks


CREDIT_COSTS = {
    "seo": 25,
    "aeo": 20,
    "content": 40,
    "keyword": 15,
    "social": 10,
    "competitor": 20,
    "analytics": 10,
    "backlink": 25,
    "ppc": 30,
    "local_seo": 20,
    "cro": 25,
    "email": 20,
    "supervisor": 5,
    "launch_product": 80,
    "growth_playbook": 120,
}


class AgentState(TypedDict, total=False):
    agent: str
    goal: str
    organization_id: str
    workspace_id: str
    site_id: str | None
    input: dict[str, Any]
    output: dict[str, Any]
    credits: int
    error: str | None


def classify_intent(term: str) -> str:
    t = term.lower()
    if any(x in t for x in ("buy", "pricing", "price", "cost", "demo", "trial")):
        return "commercial"
    if any(x in t for x in ("near me", "in ", "vs", "best")):
        return "commercial" if "best" in t or "vs" in t else "local"
    if any(x in t for x in ("how", "what", "why", "guide", "tips")):
        return "informational"
    if "login" in t or "official" in t:
        return "navigational"
    return "informational"


async def run_seo_agent(db: AsyncSession, run: AgentRun, site: Site) -> dict[str, Any]:
    pages = (
        await db.execute(select(Page).where(Page.site_id == site.id))
    ).scalars().all()

    issues: list[Issue] = []
    change_requests: list[ChangeRequest] = []

    # Site-level technical checks
    robots_ok = True
    latest_crawl = site.crawls[-1] if site.crawls else None
    if latest_crawl and not (latest_crawl.robots_txt or "").strip():
        robots_ok = False
        issues.append(
            Issue(
                site_id=site.id,
                organization_id=site.organization_id,
                category="technical",
                severity="high",
                code="MISSING_ROBOTS",
                title="Missing or empty robots.txt",
                description="Crawler did not find a usable robots.txt.",
                recommendation="Publish robots.txt with Allow rules and Sitemap directive.",
            )
        )

    missing_meta = 0
    missing_h1 = 0
    missing_alt = 0
    no_schema = 0
    slow = 0

    for page in pages:
        if not page.meta_description or len(page.meta_description) < 50:
            missing_meta += 1
            issues.append(
                Issue(
                    site_id=site.id,
                    organization_id=site.organization_id,
                    page_id=page.id,
                    category="onpage",
                    severity="medium",
                    code="META_DESCRIPTION",
                    title=f"Weak meta description: {page.path}",
                    description="Meta description missing or too short.",
                    recommendation="Write a 120–155 character unique meta description.",
                )
            )
            meta_text = await llm.complete(
                f"Generate SEO meta title and description for page titled '{page.title}' at {page.url}. Content: {(page.content_text or '')[:800]}"
            )
            change_requests.append(
                ChangeRequest(
                    organization_id=site.organization_id,
                    workspace_id=run.workspace_id,
                    site_id=site.id,
                    agent="seo",
                    change_type="meta",
                    title=f"Meta update for {page.path}",
                    payload={"url": page.url, "suggestion": meta_text, "page_id": str(page.id)},
                    status=ChangeRequestStatus.PROPOSED,
                )
            )

        if not page.h1:
            missing_h1 += 1
            issues.append(
                Issue(
                    site_id=site.id,
                    organization_id=site.organization_id,
                    page_id=page.id,
                    category="onpage",
                    severity="high",
                    code="MISSING_H1",
                    title=f"Missing H1: {page.path}",
                    description="Page has no H1 heading.",
                    recommendation="Add a single descriptive H1 matching primary intent.",
                )
            )

        if not page.has_schema:
            no_schema += 1

        for img in page.images or []:
            if img.get("missing_alt"):
                missing_alt += 1

        if page.load_time_ms and page.load_time_ms > 2500:
            slow += 1
            issues.append(
                Issue(
                    site_id=site.id,
                    organization_id=site.organization_id,
                    page_id=page.id,
                    category="technical",
                    severity="medium",
                    code="SLOW_PAGE",
                    title=f"Slow load (~{page.load_time_ms}ms): {page.path}",
                    description="Page load time may hurt Core Web Vitals.",
                    recommendation="Compress images, defer JS, enable caching/CDN.",
                )
            )

        # Broken link placeholders from crawl
        for bl in page.broken_links or []:
            issues.append(
                Issue(
                    site_id=site.id,
                    organization_id=site.organization_id,
                    page_id=page.id,
                    category="technical",
                    severity="high",
                    code="BROKEN_LINK",
                    title="Broken link detected",
                    description=str(bl),
                    recommendation="Fix or remove the broken link.",
                )
            )

    if no_schema:
        issues.append(
            Issue(
                site_id=site.id,
                organization_id=site.organization_id,
                category="technical",
                severity="medium",
                code="MISSING_SCHEMA",
                title=f"{no_schema} pages missing structured data",
                description="JSON-LD schema not detected on multiple pages.",
                recommendation="Add Organization, WebPage, Article, and FAQ schema where relevant.",
            )
        )

    # Internal linking suggestions
    if len(pages) >= 2:
        hub = max(pages, key=lambda p: p.word_count or 0)
        orphans = [p for p in pages if len(p.links_internal or []) < 2]
        for p in orphans[:5]:
            issues.append(
                Issue(
                    site_id=site.id,
                    organization_id=site.organization_id,
                    page_id=p.id,
                    category="onpage",
                    severity="low",
                    code="WEAK_INTERNAL_LINKS",
                    title=f"Weak internal linking: {p.path}",
                    description="Page has few internal links.",
                    recommendation=f"Link to/from hub content at {hub.path}.",
                )
            )
            change_requests.append(
                ChangeRequest(
                    organization_id=site.organization_id,
                    workspace_id=run.workspace_id,
                    site_id=site.id,
                    agent="seo",
                    change_type="internal_link",
                    title=f"Internal link suggestion for {p.path}",
                    payload={"from": p.url, "to": hub.url, "anchor": hub.h1 or hub.title},
                    status=ChangeRequestStatus.PROPOSED,
                )
            )

    for issue in issues:
        db.add(issue)
    for cr in change_requests:
        db.add(cr)

    score = 100.0
    score -= min(missing_meta * 2, 20)
    score -= min(missing_h1 * 3, 15)
    score -= min(missing_alt * 0.5, 10)
    score -= min(no_schema * 1.5, 15)
    score -= min(slow * 2, 10)
    if not robots_ok:
        score -= 10
    score = max(0, round(score, 1))
    site.seo_score = score

    summary = {
        "seo_score": score,
        "pages_analyzed": len(pages),
        "issues_found": len(issues),
        "change_requests": len(change_requests),
        "breakdown": {
            "missing_meta": missing_meta,
            "missing_h1": missing_h1,
            "missing_image_alt": missing_alt,
            "pages_without_schema": no_schema,
            "slow_pages": slow,
            "robots_ok": robots_ok,
        },
    }
    db.add(
        AgentArtifact(
            organization_id=site.organization_id,
            agent_run_id=run.id,
            artifact_type="seo_audit",
            title="SEO Audit Report",
            data=summary,
        )
    )
    return summary


async def run_aeo_agent(db: AsyncSession, run: AgentRun, site: Site) -> dict[str, Any]:
    pages = (await db.execute(select(Page).where(Page.site_id == site.id))).scalars().all()
    sample = "\n\n".join(f"{p.title}: {(p.content_text or '')[:500]}" for p in pages[:5])

    faq_text = await llm.complete(
        f"Generate AEO FAQs, entity recommendations, and E-E-A-T improvements for this site ({site.domain}).\n{sample}",
        system="You are an Answer Engine Optimization expert for ChatGPT, Perplexity, Gemini, Google AI Overviews.",
    )

    chunks = []
    for p in pages[:10]:
        for i, c in enumerate(chunk_text(p.content_text or "", size=120, overlap=20)[:3]):
            chunks.append({"url": p.url, "chunk": c, "index": i})

    retrieved = await search_chunks(
        organization_id=str(site.organization_id),
        site_id=str(site.id),
        query=run.goal or "frequently asked questions entities expertise",
    )

    eeat = {
        "experience": 60 if any(p.word_count and p.word_count > 400 for p in pages) else 40,
        "expertise": 55,
        "authoritativeness": 50 if any(p.has_schema for p in pages) else 35,
        "trust": 55,
    }
    aeo_score = round(sum(eeat.values()) / 4, 1)
    site.aeo_score = aeo_score

    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What does this brand offer?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"{site.domain} provides products and services optimized for search and AI answers.",
                },
            }
        ],
    }

    change = ChangeRequest(
        organization_id=site.organization_id,
        workspace_id=run.workspace_id,
        site_id=site.id,
        agent="aeo",
        change_type="schema",
        title="FAQPage structured data proposal",
        payload={"schema": faq_schema, "faq_markdown": faq_text},
        status=ChangeRequestStatus.PROPOSED,
    )
    db.add(change)

    result = {
        "aeo_score": aeo_score,
        "eeat": eeat,
        "faq_markdown": faq_text,
        "faq_schema": faq_schema,
        "llm_chunks": chunks[:20],
        "retrieved_chunks": retrieved,
        "targets": ["ChatGPT", "Google AI Overview", "Gemini", "Perplexity", "Claude", "Bing Copilot"],
        "knowledge_graph": {
            "primary_entity": site.domain,
            "recommended_same_as": ["Wikipedia", "Wikidata", "LinkedIn Company", "Crunchbase"],
        },
    }
    db.add(
        AgentArtifact(
            organization_id=site.organization_id,
            agent_run_id=run.id,
            artifact_type="aeo_report",
            title="AEO Optimization Report",
            data=result,
        )
    )
    return result


async def run_content_agent(db: AsyncSession, run: AgentRun, site: Site | None) -> dict[str, Any]:
    payload = run.input_payload or {}
    topic = payload.get("topic") or run.goal or "AI SEO and AEO best practices"
    keywords = payload.get("keywords") or ["SEO", "AEO", "AI search"]
    content_type = payload.get("content_type") or "blog"
    tone = payload.get("tone") or "professional"

    body = await llm.complete(
        f"Write a {content_type} about '{topic}' targeting keywords {keywords}. Tone: {tone}. Include H2s and a conclusion.",
        system="You are DigiSEO Content Marketing Agent. Produce publish-ready Markdown.",
    )
    meta = await llm.complete(f"Generate meta title and description for article: {topic}")

    piece = ContentPiece(
        organization_id=run.organization_id,
        workspace_id=run.workspace_id,
        site_id=run.site_id,
        content_type=content_type,
        title=topic.title() if topic.islower() else topic,
        slug="-".join(topic.lower().split())[:80],
        body_markdown=body,
        body_html=f"<article>{body}</article>",
        status="draft",
        target_keywords=keywords,
        meta_title=meta.split("\n")[0].replace("Title:", "").strip() if meta else topic,
        meta_description="\n".join(meta.split("\n")[1:]).replace("Description:", "").strip() if meta else "",
        aeo_faq=[{"q": f"What is {topic}?", "a": f"An overview of {topic} for modern marketers."}],
    )
    db.add(piece)
    await db.flush()

    return {
        "content_piece_id": str(piece.id),
        "title": piece.title,
        "body_markdown": body,
        "meta": meta,
        "content_type": content_type,
    }


async def run_keyword_agent(db: AsyncSession, run: AgentRun, site: Site | None) -> dict[str, Any]:
    payload = run.input_payload or {}
    seed = payload.get("seed") or (site.domain.split(".")[0] if site else "seo")
    # Mock GSC-style queries when integration not connected
    raw = payload.get("queries") or [
        f"{seed} software",
        f"best {seed} tools",
        f"how to use {seed}",
        f"{seed} pricing",
        f"{seed} vs competitors",
        f"{seed} for startups",
        f"ai {seed} platform",
        f"{seed} audit checklist",
        f"answer engine optimization {seed}",
        f"{seed} near me",
    ]

    keywords_out = []
    clusters: dict[str, list[str]] = {}
    for i, term in enumerate(raw):
        intent = classify_intent(term)
        is_lt = len(term.split()) >= 3
        kw = Keyword(
            organization_id=run.organization_id,
            workspace_id=run.workspace_id,
            site_id=run.site_id,
            term=term,
            intent=intent,
            volume=1000 - i * 70,
            difficulty=35 + i * 3,
            position=5 + i * 1.5,
            clicks=max(0, 200 - i * 15),
            impressions=max(0, 5000 - i * 200),
            is_long_tail=is_lt,
            semantic_group=intent,
        )
        db.add(kw)
        keywords_out.append({"term": term, "intent": intent, "long_tail": is_lt})
        clusters.setdefault(intent, []).append(term)

    cluster_rows = []
    for intent, terms in clusters.items():
        cluster = KeywordCluster(
            organization_id=run.organization_id,
            workspace_id=run.workspace_id,
            name=f"{intent.title()} cluster",
            primary_keyword=terms[0],
            intent=intent,
            keyword_ids=[],
        )
        db.add(cluster)
        cluster_rows.append({"name": cluster.name, "intent": intent, "keywords": terms})

    return {"keywords": keywords_out, "clusters": cluster_rows, "source": payload.get("source", "mock_gsc")}


async def run_social_agent(db: AsyncSession, run: AgentRun) -> dict[str, Any]:
    from app.models import SocialPost

    payload = run.input_payload or {}
    platform = payload.get("platform") or "linkedin"
    topic = payload.get("topic") or run.goal or "AI SEO tips"
    text = await llm.complete(
        f"Create a {platform} social post with hashtags about: {topic}",
        system="You are DigiSEO Social Media Agent.",
    )
    hashtags = [h for h in text.replace(",", " ").split() if h.startswith("#")]
    script = None
    if platform in ("youtube", "tiktok", "instagram"):
        script = await llm.complete(f"Write a 30-second reel/shorts script about {topic}")

    post = SocialPost(
        organization_id=run.organization_id,
        workspace_id=run.workspace_id,
        platform=platform,
        body=text,
        hashtags=hashtags or ["#SEO", "#AEO", "#Marketing"],
        script=script,
        status="draft",
    )
    db.add(post)
    await db.flush()
    return {"social_post_id": str(post.id), "body": text, "hashtags": post.hashtags, "script": script}


async def run_competitor_agent(db: AsyncSession, run: AgentRun) -> dict[str, Any]:
    from datetime import datetime, timezone

    from app.models import Competitor, CompetitorEvent

    payload = run.input_payload or {}
    competitor_id = payload.get("competitor_id")
    if competitor_id:
        comp = await db.get(Competitor, UUID(str(competitor_id)))
    else:
        comps = (
            await db.execute(
                select(Competitor).where(Competitor.workspace_id == run.workspace_id).limit(1)
            )
        ).scalar_one_or_none()
        comp = comps
    if not comp:
        return {"events": [], "message": "No competitors configured"}

    events_data = [
        ("blog", f"New blog detected on {comp.domain}", {"url": f"https://{comp.domain}/blog/new"}),
        ("keyword", "Competitor ranking movement", {"keyword": "ai seo platform", "delta": +3}),
        ("aio", "Appeared in AI Overview sample query", {"engine": "Google AI Overview"}),
        ("social", "Increased LinkedIn posting cadence", {"posts_7d": 5}),
    ]
    saved = []
    for etype, title, data in events_data:
        ev = CompetitorEvent(
            organization_id=run.organization_id,
            competitor_id=comp.id,
            event_type=etype,
            title=title,
            payload=data,
        )
        db.add(ev)
        saved.append({"type": etype, "title": title, "payload": data})
    comp.last_checked_at = datetime.now(timezone.utc)
    return {"competitor": comp.domain, "events": saved}


async def run_analytics_agent(db: AsyncSession, run: AgentRun, site: Site | None) -> dict[str, Any]:
    from app.models import Report

    metrics = {
        "sessions": 12450,
        "organic_sessions": 8200,
        "conversions": 186,
        "conversion_rate": 1.49,
        "revenue": 28400,
        "roi": 3.2,
        "top_channels": {"organic": 0.52, "paid": 0.18, "social": 0.12, "referral": 0.1, "direct": 0.08},
        "gsc_clicks": 5400,
        "gsc_impressions": 120000,
        "attribution": {"first_touch": "organic", "last_touch": "paid"},
    }
    report = Report(
        organization_id=run.organization_id,
        workspace_id=run.workspace_id,
        report_type="daily",
        title="Daily Marketing Report",
        summary="Organic leads growth with steady AEO citation opportunities.",
        metrics=metrics,
    )
    db.add(report)
    return metrics


async def run_backlink_agent(db: AsyncSession, run: AgentRun) -> dict[str, Any]:
    from app.models import BacklinkOpportunity

    domain = (run.input_payload or {}).get("niche", "ai-marketing")
    opps = []
    for i, d in enumerate([f"blog.{domain}.com", "growthroundup.io", "martechweekly.com", "saasinsider.net"]):
        email_body = await llm.complete(f"Write a backlink outreach email to {d}")
        opp = BacklinkOpportunity(
            organization_id=run.organization_id,
            workspace_id=run.workspace_id,
            domain=d,
            page_url=f"https://{d}/resources",
            contact_email=f"editor@{d}",
            quality_score=70 - i * 8,
            draft_email=email_body,
            outreach_status="drafted",
        )
        db.add(opp)
        opps.append({"domain": d, "quality_score": opp.quality_score})
    return {"opportunities": opps}


async def run_ppc_agent(db: AsyncSession, run: AgentRun) -> dict[str, Any]:
    from app.models import PPCCampaign

    payload = run.input_payload or {}
    platform = payload.get("platform") or "google"
    copy = await llm.complete(f"Generate PPC ad copy for {platform}: {run.goal or 'DigiSEO AI'}")
    campaign = PPCCampaign(
        organization_id=run.organization_id,
        workspace_id=run.workspace_id,
        platform=platform,
        name=payload.get("name") or f"{platform.title()} Growth",
        budget_daily=float(payload.get("budget_daily") or 50),
        keywords=payload.get("keywords") or ["ai seo software", "aeo platform", "seo audit tool"],
        ad_copies=[{"raw": copy}],
        landing_page_url=payload.get("landing_page_url"),
        recommendations=[
            "Raise bids on high-intent commercial keywords",
            "Test landing page with FAQ schema for Quality Score",
            "Exclude brand-competitor exact matches if CPA rises",
        ],
        status="draft",
    )
    db.add(campaign)
    await db.flush()
    return {"campaign_id": str(campaign.id), "ad_copy": copy, "recommendations": campaign.recommendations}


async def run_local_seo_agent(db: AsyncSession, run: AgentRun) -> dict[str, Any]:
    from app.models import LocalListing

    payload = run.input_payload or {}
    listing = LocalListing(
        organization_id=run.organization_id,
        workspace_id=run.workspace_id,
        business_name=payload.get("business_name") or "DigiSEO Demo Biz",
        address=payload.get("address") or "123 Market St",
        phone=payload.get("phone") or "+1-555-0100",
        categories=payload.get("categories") or ["Marketing Agency", "Software Company"],
        review_score=4.6,
        review_count=128,
        citations=[
            {"source": "Yelp", "status": "consistent"},
            {"source": "Apple Maps", "status": "needs_update"},
            {"source": "Bing Places", "status": "consistent"},
        ],
        local_keywords=["seo agency near me", "digital marketing [city]"],
        map_rankings={"seo agency near me": 3, "aeo consultant": 7},
    )
    db.add(listing)
    await db.flush()
    return {
        "listing_id": str(listing.id),
        "gbp_optimization": [
            "Complete all GBP categories",
            "Respond to reviews within 24h",
            "Add weekly photo updates",
            "Align NAP citations",
        ],
        "map_rankings": listing.map_rankings,
        "citations": listing.citations,
    }


async def run_cro_agent(db: AsyncSession, run: AgentRun, site: Site | None) -> dict[str, Any]:
    """CRO briefs: funnel, LPO, A/B tests, exit-intent — recommendations only."""
    domain = site.domain if site else "your-site"
    payload = run.input_payload or {}
    result = {
        "domain": domain,
        "funnel_strategy": [
            "Clarify primary CTA above the fold",
            "Reduce form fields to email + intent",
            "Add social proof near pricing",
        ],
        "landing_page_optimisations": [
            f"Rewrite hero for {payload.get('offer', run.goal)}",
            "Add sticky mobile CTA",
            "Match ad keyword to H1",
        ],
        "ab_tests": [
            {"name": "Hero CTA copy", "variants": ["Start free audit", "Get SEO score"]},
            {"name": "Pricing layout", "variants": ["3-tier cards", "Single featured plan"]},
        ],
        "exit_intent": {
            "trigger": "mouseleave",
            "offer": "Free technical SEO checklist PDF",
            "channel": "email_capture",
        },
        "heatmap_note": "Connect Hotjar/Clarity later — DigiSEO ships CRO briefs, not heatmap hardware.",
    }
    artifact = AgentArtifact(
        agent_run_id=run.id,
        organization_id=run.organization_id,
        artifact_type="cro_brief",
        title=f"CRO brief — {domain}",
        data=result,
    )
    db.add(artifact)
    await db.flush()
    return result


async def run_email_agent(db: AsyncSession, run: AgentRun) -> dict[str, Any]:
    """Email marketing sequences and newsletter briefs (ESP connect later)."""
    payload = run.input_payload or {}
    topic = payload.get("topic") or run.goal or "SEO growth"
    result = {
        "campaigns": [
            {
                "name": f"{topic} — welcome series",
                "type": "drip",
                "emails": [
                    {"day": 0, "subject": f"Your {topic} kickoff", "body": "Welcome + audit CTA"},
                    {"day": 3, "subject": "3 quick wins this week", "body": "On-page checklist"},
                    {"day": 7, "subject": "See what competitors changed", "body": "Competitor digest"},
                ],
            },
            {
                "name": f"{topic} newsletter",
                "type": "newsletter",
                "cadence": "monthly",
                "subject_lines": [f"{topic} insights", "What ranked this month"],
            },
        ],
        "segmentation": ["trial", "paying", "churn_risk", "local_intent"],
        "ab_tests": ["subject line", "send time", "CTA placement"],
        "esp_note": "Connect SendGrid/Mailchimp under Settings — drafts stay in DigiSEO until synced.",
    }
    artifact = AgentArtifact(
        agent_run_id=run.id,
        organization_id=run.organization_id,
        artifact_type="email_brief",
        title=f"Email plan — {topic}",
        data=result,
    )
    db.add(artifact)
    await db.flush()
    return result


async def _run_step_chain(
    db: AsyncSession,
    parent: AgentRun,
    site: Site | None,
    steps: list[str],
    workflow_id: str,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for step in steps:
        child = AgentRun(
            organization_id=parent.organization_id,
            workspace_id=parent.workspace_id,
            site_id=parent.site_id,
            agent=step,
            goal=parent.goal,
            status=AgentRunStatus.RUNNING,
            input_payload={**(parent.input_payload or {}), "topic": parent.goal},
            parent_run_id=parent.id,
        )
        db.add(child)
        await db.flush()
        try:
            out = await dispatch_agent(db, child, site)
            child.status = AgentRunStatus.COMPLETED
            child.output_payload = out
            child.credits_used = CREDIT_COSTS.get(step, 10)
            results[step] = out
        except Exception as exc:
            child.status = AgentRunStatus.FAILED
            child.error = str(exc)
            results[step] = {"error": str(exc)}
    return {"workflow": workflow_id, "steps": results, "hierarchy": steps}


async def run_supervisor_workflow(db: AsyncSession, parent: AgentRun, site: Site | None) -> dict[str, Any]:
    """Launch product: keyword → content → aeo → social → analytics."""
    return await _run_step_chain(
        db,
        parent,
        site,
        ["keyword", "content", "aeo", "social", "analytics"],
        "launch_product",
    )


async def run_growth_playbook(db: AsyncSession, parent: AgentRun, site: Site | None) -> dict[str, Any]:
    """Subhash hierarchy: Audit → AI/On-Page → Content → CRO → Off-Page/Local → Paid/SMM → Report."""
    steps = [
        "seo",
        "aeo",
        "keyword",
        "content",
        "cro",
        "backlink",
        "local_seo",
        "ppc",
        "social",
        "email",
        "analytics",
    ]
    return await _run_step_chain(db, parent, site, steps, "growth_playbook")


async def dispatch_agent(db: AsyncSession, run: AgentRun, site: Site | None) -> dict[str, Any]:
    agent = run.agent
    if agent == "seo":
        if not site:
            raise ValueError("site_id required for SEO agent")
        await db.refresh(site, attribute_names=["crawls"])
        return await run_seo_agent(db, run, site)
    if agent == "aeo":
        if not site:
            raise ValueError("site_id required for AEO agent")
        return await run_aeo_agent(db, run, site)
    if agent == "content":
        return await run_content_agent(db, run, site)
    if agent == "keyword":
        return await run_keyword_agent(db, run, site)
    if agent == "social":
        return await run_social_agent(db, run)
    if agent == "competitor":
        return await run_competitor_agent(db, run)
    if agent == "analytics":
        return await run_analytics_agent(db, run, site)
    if agent == "backlink":
        return await run_backlink_agent(db, run)
    if agent == "ppc":
        return await run_ppc_agent(db, run)
    if agent == "local_seo":
        return await run_local_seo_agent(db, run)
    if agent == "cro":
        return await run_cro_agent(db, run, site)
    if agent == "email":
        return await run_email_agent(db, run)
    if agent in ("supervisor", "launch_product", "multi_agent"):
        return await run_supervisor_workflow(db, run, site)
    if agent == "growth_playbook":
        return await run_growth_playbook(db, run, site)
    raise ValueError(f"Unknown agent: {agent}")


async def execute_agent_run(db: AsyncSession, run: AgentRun) -> AgentRun:
    run.status = AgentRunStatus.RUNNING
    await db.flush()
    site = None
    if run.site_id:
        site = await db.get(Site, run.site_id)

    cost = CREDIT_COSTS.get(run.agent, 10)
    try:
        await debit_credits(
            db,
            organization_id=run.organization_id,
            amount=cost,
            reason=f"agent:{run.agent}",
            reference_id=str(run.id),
        )
        output = await dispatch_agent(db, run, site)
        run.output_payload = output
        run.credits_used = cost
        run.status = AgentRunStatus.COMPLETED
    except Exception as exc:
        run.status = AgentRunStatus.FAILED
        run.error = str(exc)
    await db.flush()
    return run


# Optional LangGraph wiring when package is available
def build_langgraph():
    try:
        from langgraph.graph import END, StateGraph

        graph = StateGraph(AgentState)

        async def route(state: AgentState) -> AgentState:
            return state

        graph.add_node("supervisor", route)
        graph.set_entry_point("supervisor")
        graph.add_edge("supervisor", END)
        return graph.compile()
    except Exception:
        return None
