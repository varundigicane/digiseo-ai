# DigiSEO AI — User Guide

**Product:** DigiSEO AI  
**Audience:** SMB / startup marketers, founders, agency operators  
**Live app:** https://web-production-faa9d.up.railway.app  
**API:** https://api-production-4a88.up.railway.app  

---

## 1. What DigiSEO AI does

DigiSEO AI is a self-serve multi-agent marketing platform. Instead of one chatbot, you get a team of specialists that:

1. Audit and improve **website SEO**
2. Optimize for **answer engines** (ChatGPT, Google AI Overviews, Perplexity, Gemini, Claude, Bing Copilot)
3. Generate **content** (blogs, landing pages, and more)
4. Run **social**, **competitor**, **keyword**, **backlink**, **PPC**, **analytics**, and **local SEO** workflows (by plan)

Every outbound change (meta tags, schema, social replies, CMS publishes) goes through **human approval** unless Business+ auto-apply is enabled.

---

## 2. Plans at a glance

| Plan | Price | Monthly credits | Best for |
|------|-------|-----------------|----------|
| Starter | $49/mo | 500 | SEO + AEO audits, blogs, GSC |
| Professional | $149/mo | 2,000 | Social, calendar, analytics, competitors |
| Business | $399/mo | 8,000 | Multi-agent workflows, PPC, outreach, API |
| Enterprise | Custom | 50,000+ | White-label, SSO, high limits |

Upgrade anytime under **Billing**. Credit packs can be purchased as add-ons.

---

## 3. Getting started (first 15 minutes)

### Step 1 — Create an account

1. Open the web app → **Start free** / **Sign up**
2. Enter name, email, password, company, and workspace name
3. You land on the **Campaign board** with a Starter trial and credits

### Step 2 — Connect your website

1. Go to **Onboarding**
2. Enter your site URL (e.g. `https://example.com`)
3. Click **Connect & crawl**
4. DigiSEO fetches robots.txt / sitemap signals, crawls pages, and indexes content chunks for AEO

### Step 3 — Run SEO + AEO

1. Open **SEO / AEO**
2. Select your site
3. Click **Run seo**, then **Run aeo**, then **Run keyword**
4. Review scores, issues, and proposed fixes

### Step 4 — Generate content

1. Open **Content**
2. Choose type (blog, landing, case study, etc.), topic, and keywords
3. Click **Generate**
4. Edit the draft; export Markdown/HTML as needed

### Step 5 — Approve changes

1. Open **Approvals**
2. Review proposed meta/schema/internal-link changes
3. **Approve** or **Reject** each item

---

## 4. App navigation

| Nav item | Purpose |
|----------|---------|
| Overview | Campaign board — sites, scores, credits |
| Onboarding | Connect site + crawl + GSC mock/connect |
| SEO / AEO | Technical/on-page audit + answer-engine report |
| Content | Content studio + calendar (Pro+) |
| Social | Posts, hashtags, scripts, publish (Pro+) |
| Competitors | Watchlist + scan events (Pro+) |
| Analytics | GA4/GSC-style dashboard (Pro+) |
| Approvals | Human-in-the-loop change requests |
| Workflows | Multi-agent “Launch product” (Business+) |
| Billing | Plans, credits, upgrades |
| Settings | Integrations, API key, white-label, SSO |

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
