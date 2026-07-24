# DigiSEO AI — User Guide

**Product:** DigiSEO AI  
**Audience:** SMB / startup marketers, founders, agency operators  
**Live app:** https://web-production-faa9d.up.railway.app  
**API:** https://api-production-4a88.up.railway.app  

---

## 1. What DigiSEO AI does

DigiSEO AI is an **AI Growth OS** for SMBs and agencies. Work follows a delivery hierarchy:

1. **Strategy & Audit** — site crawl, technical audit, keywords, competitors, persona  
2. **AI SEO + On-Page** — AEO/GEO/SGE readiness and on-page checklist  
3. **Content** — writing specialist for blogs, landing pages, and more  
4. **CRO** — funnel and landing briefs, A/B plans (Professional+)  
5. **Off-Page + Local** — backlinks/outreach and GBP (Business+)  
6. **Paid + SMM + Email** — Google/Meta ads drafts, social, email plans (by plan)  
7. **Reporting** — dashboard and strategy notes  

Keywords, competitors, backlinks, and analytics are **capabilities inside these pillars**, not separate products.  
Web design & hosting are **partner-only** (export brief from Settings).

Every outbound change goes through **human approval** unless Business+ auto-apply is enabled.

---

## 2. Plans at a glance

| Plan | Price | Monthly credits | Best for |
|------|-------|-----------------|----------|
| Starter | $49/mo | 500 | Strategy, AI SEO, On-Page, blogs |
| Professional | $149/mo | 2,000 | CRO, SMM, reporting, competitors |
| Business | $399/mo | 8,000 | Off-Page, Local, Paid, Email, Growth Playbook |
| Enterprise | Custom | 50,000+ | White-label agency mode, SSO |

Upgrade anytime under **Billing**. Credit packs can be purchased as add-ons.

---

## 3. Getting started (first 15 minutes)

### Step 1 — Create an account

1. Open the web app → **Start free** / **Sign up**
2. Enter name, email, password, company, and workspace name
3. You land on the **Campaign board** with a Starter trial and credits

### Step 2 — Strategy & Audit

1. Go to **Strategy & Audit**
2. Enter your site URL → **Connect & crawl**
3. Optionally run keyword clustering and add competitors (Pro+)

### Step 3 — AI SEO + On-Page

1. Open **AI SEO** → Run AEO / GEO  
2. Open **On-Page SEO** → Run on-page audit  
3. Review scores and proposed fixes

### Step 4 — Generate content

1. Open **Content Studio**
2. Choose type, topic, and keywords → **Generate**

### Step 5 — Approve changes

1. Open **Approvals**
2. **Approve** or **Reject** each item

---

## 4. App navigation

| Nav item | Purpose |
|----------|---------|
| Overview | Campaign board + hierarchy shortcuts |
| Strategy & Audit | Crawl, keywords, competitors, persona |
| AI SEO | AEO/GEO, clusters, AI competitor intel |
| On-Page SEO | Meta, schema, CWV, links, FAQ, E-E-A-T checklist |
| Content Studio | Writing specialist + calendar (Pro+) |
| CRO | Funnel / LPO / A/B briefs (Pro+) |
| Off-Page SEO | Backlinks & outreach (Business+) |
| Local SEO | GBP / citations / reviews (Business+) |
| Paid Media | Google + Meta + LinkedIn drafts (Business+) |
| Social (SMM) | Posts & publish (Pro+) |
| Email | Campaigns & drips (Business+) |
| Reporting | Dashboard + strategy notes (Pro+) |
| Growth Playbook | Full hierarchy orchestration (Business+) |
| Approvals | Human-in-the-loop change requests |
| Billing | Plans, credits, upgrades |
| Settings | Integrations, partner web-design brief, enterprise |

---

## 5. Feature walkthroughs

### 5.1 Website SEO Agent

**Runs:** Technical + on-page checklist after a crawl.

**You get:**
- SEO score
- Issues by severity (robots, meta, H1, schema, slow pages, broken links, weak internal links)
- Proposed meta title/description and internal link suggestions in Approvals

**Tips:** Crawl before every major SEO run. Fix critical/high issues first.

### 5.2 AEO (Answer Engine Optimization) Agent

**Runs:** FAQ generation, FAQ/JSON-LD proposals, E-E-A-T checklist, LLM content chunks, citation readiness.

**Targets:** ChatGPT, Google AI Overview, Gemini, Perplexity, Claude, Bing Copilot.

**Tips:** Approve FAQ schema proposals, then publish on high-intent pages.

### 5.3 Content Marketing Agent

**Starter:** Blog drafts.  
**Pro+:** Landing pages, case studies, whitepapers, newsletters, content calendar seed.

**Tips:** Pass 3–5 target keywords. Keep brand voice updated on the workspace.

### 5.4 Keyword Research Agent

Uses GSC-style query data (live OAuth when configured; mock clustering in demo).

**Outputs:** Clusters by intent (informational, commercial, navigational, local), long-tail flags, volumes/positions.

### 5.5 Social Media Agent (Professional+)

Platforms: LinkedIn, X, Facebook, Instagram, Threads, YouTube, TikTok (scripts where publish APIs are limited).

**Flow:** Generate → review → schedule/publish → analytics.

Comment/DM replies are drafted for approval (not auto-sent on Starter/Pro without policy).

### 5.6 Competitor Intelligence (Professional+)

Add competitor domains → **Scan** → review events (new blogs, keyword moves, AI Overview mentions, social cadence).

### 5.7 Analytics (Professional+)

Unified dashboard metrics: sessions, organic, conversions, revenue/ROI, GSC clicks/impressions, channel mix, attribution stubs.

Connect GA4 / GSC under **Settings → Integrations**.

### 5.8 Workflows (Business+)

**Launch product** orchestrates: keyword → content → AEO → social → analytics in one run.

Also available from Workflows: backlink discover, PPC optimize, local SEO optimize.

### 5.9 Backlink, PPC, Local SEO (Business+)

| Agent | What you do |
|-------|-------------|
| Backlink | Discover opportunities, draft outreach emails, track replies |
| PPC | Generate Google/Meta/LinkedIn campaign drafts, budgets, ad copy |
| Local SEO | GBP-style listing optimization, citations, map rankings, reviews |

### 5.10 Enterprise controls (Business / Enterprise)

Under **Settings**:
- Create API key (`X-API-Key` header)
- Enable auto-apply for approved CMS changes (Business+)
- White-label domain/logo/color (Enterprise)
- SSO metadata (Enterprise)
- Connect CMS (WordPress/Shopify) and SEO tools (Ahrefs/SEMrush) where plan allows

---

## 6. Credits & billing

- Each agent run spends credits (e.g. SEO ~25, content ~40, launch workflow ~80)
- Insufficient credits → upgrade plan or buy a credit pack on **Billing**
- Stripe Checkout is used in production; local/dev may mock upgrades

---

## 7. Approvals & safety

```
proposed → approved | rejected → applied
```

- **proposed:** Agent suggestion waiting for you
- **approved:** Ready to apply (or auto-applied on Business+ with auto-apply on)
- **rejected:** Discarded
- **applied:** Written / queued to CMS (stub until connector live)

Never enable auto-apply without reviewing Approvals for a week first.

---

## 8. Integrations checklist

| Integration | Where | Notes |
|-------------|-------|-------|
| Google Search Console | Onboarding / Settings | OAuth when `GOOGLE_CLIENT_*` set |
| GA4 | Settings | Analytics dashboard |
| GBP | Settings | Local SEO |
| WordPress / Shopify | Settings | CMS publish (Pro+) |
| Ahrefs / SEMrush / HubSpot / Salesforce | Settings | Business+ |

---

## 9. Typical weekly routine

1. **Monday:** Crawl + SEO/AEO run; clear Approvals  
2. **Tue–Wed:** Generate 1–2 content pieces from keyword clusters  
3. **Thursday:** Social batch + schedule  
4. **Friday:** Competitor scan + Analytics daily report  
5. **Monthly:** Workflows → Launch product for a campaign theme  

---

## 10. Troubleshooting

| Symptom | Fix |
|---------|-----|
| Empty SEO score | Complete Onboarding crawl first |
| Feature blocked | Upgrade plan (see Billing limits) |
| CORS / API errors in browser | Confirm `NEXT_PUBLIC_API_URL` matches live API |
| Credits exhausted | Buy pack or upgrade |
| Integration connect fails | Check provider keys / OAuth env vars |

---

## 11. Support & docs

- Architecture: [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md)  
- Diagrams: [architecture/DIAGRAMS.md](architecture/DIAGRAMS.md)  
- Functional overview: [functional/FUNCTIONAL_SPEC.md](functional/FUNCTIONAL_SPEC.md)  
- Agents: [agents/README.md](agents/README.md)  
- Railway deploy: [deploy/RAILWAY.md](deploy/RAILWAY.md)  

Digicane Systems · DigiSEO AI
