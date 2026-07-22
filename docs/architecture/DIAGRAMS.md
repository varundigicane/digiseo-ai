# DigiSEO AI — Diagram Pack

All diagrams use Mermaid. Render in GitHub, VS Code Mermaid preview, or Notion.

---

## 1. System context (C4 level 1)

```mermaid
C4Context
  title DigiSEO AI System Context
  Person(marketer, "Marketer", "SMB / startup growth owner")
  Person(admin, "Org Admin", "Billing & integrations")
  System(digiseo, "DigiSEO AI", "Multi-agent SEO/AEO/marketing SaaS")
  System_Ext(gsc, "Google Search Console")
  System_Ext(ga4, "Google Analytics 4")
  System_Ext(cms, "WordPress / Shopify")
  System_Ext(social, "Social Networks")
  System_Ext(llm, "LLM Providers")
  System_Ext(stripe, "Stripe")

  Rel(marketer, digiseo, "Runs audits, content, social")
  Rel(admin, digiseo, "Plans, keys, SSO")
  Rel(digiseo, gsc, "Queries / properties")
  Rel(digiseo, ga4, "Metrics")
  Rel(digiseo, cms, "Publish approved content")
  Rel(digiseo, social, "Schedule / publish")
  Rel(digiseo, llm, "Generate / score")
  Rel(digiseo, stripe, "Subscriptions / credits")
```

> If C4 Mermaid is unsupported in your viewer, use §2 instead.

---

## 2. Container diagram

```mermaid
flowchart TB
  subgraph clients [Clients]
    Browser[Browser]
  end

  subgraph product [DigiSEO_Product]
    Web[apps_web_Nextjs]
    API[apps_api_FastAPI]
    Worker[apps_worker]
    SDK[packages_agent_sdk]
  end

  subgraph data [Data_Plane]
    PG[(PostgreSQL)]
    Redis[(Redis)]
    QD[(Qdrant)]
  end

  subgraph external [External]
    LLM[OpenAI_Anthropic]
    Google[GSC_GA4_GBP]
    CMS[WordPress_Shopify]
    Social[LinkedIn_X_Meta]
    Stripe[Stripe]
  end

  Browser --> Web
  Web -->|REST_JWT| API
  API --> PG
  API --> Redis
  API --> QD
  API --> LLM
  API --> Google
  API --> CMS
  API --> Social
  API --> Stripe
  Worker --> PG
  Worker --> Redis
  Worker --> LLM
  API -.-> SDK
  Worker -.-> SDK
```

---

## 3. Functional capability map

```mermaid
mindmap
  root((DigiSEO_AI))
    Acquisition
      Signup_Login
      Org_Workspace
      Plans_Credits
    Site_Intelligence
      Crawl
      SEO_Audit
      AEO_Report
      Keywords
    Creation
      Content_Studio
      Calendar
      Social_Posts
    Growth
      Competitors
      Backlinks
      PPC
      Local_SEO
    Measurement
      Analytics
      Attribution
    Governance
      Approvals
      Auto_Apply
      API_Keys
      White_Label
```

---

## 4. User journey — first week

```mermaid
journey
  title First week with DigiSEO AI
  section Day 1
    Sign up: 5: User
    Connect site crawl: 4: User, System
    Run SEO and AEO: 5: User, System
  section Day 2-3
    Review Approvals: 4: User
    Generate blog: 5: User, System
  section Day 4-5
    Keyword clusters: 4: User, System
    Social draft batch: 4: User, System
  section Day 6-7
    Competitor scan: 3: User, System
    Check Analytics: 4: User
    Upgrade if needed: 3: User
```

---

## 5. Auth & tenancy sequence

```mermaid
sequenceDiagram
  participant U as User
  participant W as Web
  participant A as API
  participant DB as DB

  U->>W: POST signup
  W->>A: /auth/signup
  A->>DB: Create user org membership workspace subscription
  A-->>W: tokens + org_id
  W->>W: Store JWT + org in localStorage
  U->>W: Open SEO page
  W->>A: GET /sites + X-Org-Id
  A->>A: Resolve membership
  A->>DB: Query sites for org
  A-->>W: Sites list
```

---

## 6. Agent run state machine

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> running: worker_or_inline
  running --> completed: success
  running --> failed: error
  completed --> [*]
  failed --> [*]
```

---

## 7. Approval & publish flow

```mermaid
sequenceDiagram
  participant Ag as Agent
  participant DB as DB
  participant U as Reviewer
  participant CMS as CMS_Connector

  Ag->>DB: Insert change_request proposed
  U->>DB: Approve
  alt auto_apply_enabled
    DB->>CMS: Apply payload
    CMS-->>DB: applied
  else manual apply
    U->>DB: Apply
    DB->>CMS: Apply payload
  end
```

---

## 8. Billing & credits

```mermaid
flowchart LR
  Signup[Signup] --> Starter[Starter_500_credits]
  Starter --> Usage[Agent_Runs_Debit]
  Usage --> Check{Credits_GT_0}
  Check -->|yes| Run[Execute_Agent]
  Check -->|no| Block[402_or_upgrade_prompt]
  Block --> Upgrade[Stripe_Checkout]
  Upgrade --> Plan[New_Plan_Quota]
  Plan --> Run
  Upgrade --> Pack[Credit_Pack]
  Pack --> Run
```

---

## 9. Feature gating by plan

```mermaid
flowchart TB
  Req[API_Request] --> Auth[JWT_Valid]
  Auth --> Org[Load_Subscription]
  Org --> Feat{Feature_in_plan?}
  Feat -->|no| Deny[403_Feature_Locked]
  Feat -->|yes| Cred{Credits_enough?}
  Cred -->|no| Pay[Upgrade_Credits]
  Cred -->|yes| OK[Handler]
```

---

## 10. Data model (core entities)

```mermaid
erDiagram
  users ||--o{ memberships : has
  organizations ||--o{ memberships : has
  organizations ||--|| subscriptions : has
  organizations ||--o{ workspaces : owns
  workspaces ||--o{ sites : has
  sites ||--o{ crawls : has
  sites ||--o{ pages : has
  sites ||--o{ issues : has
  organizations ||--o{ agent_runs : runs
  organizations ||--o{ change_requests : reviews
  organizations ||--o{ content_pieces : creates
  organizations ||--o{ social_posts : creates
  organizations ||--o{ competitors : watches
  organizations ||--o{ credit_ledger : tracks
  organizations ||--o{ integrations : connects
```

---

## 11. Multi-agent launch_product orchestration

```mermaid
flowchart LR
  Start([Start]) --> KW[keyword]
  KW --> CT[content]
  CT --> AE[aeo]
  AE --> SO[social]
  SO --> AN[analytics]
  AN --> End([Done_artifacts])
```

---

## 12. Component view — API modules

```mermaid
flowchart TB
  Main[main.py] --> Router[api_v1_router]
  Router --> AuthR[auth]
  Router --> OrgR[orgs]
  Router --> SiteR[sites]
  Router --> AgentR[agents]
  Router --> ContR[content]
  Router --> SocR[social]
  Router --> CompR[competitors]
  Router --> AnalR[analytics]
  Router --> ApprR[approvals]
  Router --> BillR[billing]
  Router --> IntR[integrations]
  Router --> SettR[settings]
  AgentR --> Orch[orchestrator]
  Orch --> Spec[specialist_agents]
```

---

## 13. Deployment topology

```mermaid
flowchart LR
  Users((Users))
  Users --> WebURL[web_production_faa9d]
  Users --> ApiURL[api_production_4a88]
  WebURL -->|NEXT_PUBLIC_API_URL| ApiURL
  ApiURL --> PG[(Railway_Postgres)]
  GH[GitHub_main] -->|auto_deploy| WebURL
  GH -->|auto_deploy| ApiURL
```

---

## 14. Local development topology

```mermaid
flowchart LR
  Dev[Developer]
  Dev --> WebLocal[localhost_3000]
  Dev --> ApiLocal[localhost_8000]
  WebLocal --> ApiLocal
  ApiLocal --> SQLite[(SQLite_dev.db)]
  ApiLocal --> MockLLM[MOCK_LLM]
  ApiLocal --> MockCrawl[MOCK_CRAWL]
```

---

## 15. Threat / trust boundaries (simplified)

```mermaid
flowchart TB
  subgraph public [Public_Internet]
    Browser
  end
  subgraph app [Trusted_App_Boundary]
    Web
    API
  end
  subgraph secrets [Secret_Store]
    Env[Env_Vars_KMS]
  end
  subgraph third [Third_Party]
    LLM
    Google
    Stripe
  end

  Browser -->|HTTPS_JWT| Web
  Browser -->|HTTPS_JWT| API
  API --> Env
  API -->|TLS| third
```
