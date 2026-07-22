# DigiSEO AI — End-to-End Test Plan

**Stack:** Playwright (UI) · pytest + httpx (API) · local mock mode (`MOCK_LLM=true`, `MOCK_CRAWL=true`)  
**Targets:** Web `http://localhost:3000` · API `http://localhost:8000`  
**Traceability:** Use cases in [../functional/FUNCTIONAL_SPEC.md](../functional/FUNCTIONAL_SPEC.md)

---

## How to run

```bash
# API tests (isolated SQLite test DB)
cd apps/api
pip install -r requirements.txt -r requirements-dev.txt
# Prefer project venv if present:
# .venv\Scripts\python.exe -m pytest tests -q
python -m pytest tests -q

# UI E2E — Playwright starts DigiSEO web on :3010 (avoids clashing with other apps on :3000)
# Terminal 1: API with mock mode + CORS for :3010
cd apps/api
set MOCK_LLM=true
set MOCK_CRAWL=true
set CORS_ORIGINS=http://127.0.0.1:3010,http://localhost:3010
uvicorn app.main:app --port 8000
# Terminal 2:
cd apps/web
npx playwright install chromium
npx playwright test
```

From monorepo root: `npm run test:api` · `npm run test:e2e`

---

## Preconditions

| Check | Expect |
|-------|--------|
| `GET /health` | `{ "status": "ok" }` |
| Web `/` | 200 |
| Session key | `localStorage.digiseo_session` |
| Auth headers | `Authorization`, `X-Org-Id`, `X-Workspace-Id` |
| Plans | [`apps/api/app/core/plans.py`](../../apps/api/app/core/plans.py) |

---

## P0 — Critical path (UC-01–07)

| ID | Type | UC | Steps | Expected | Automation |
|----|------|-----|-------|----------|------------|
| E2E-P0-01 | UI | UC-01 | Landing → Signup | `/app`; sidebar starter; credits ~500 | `e2e/auth.spec.ts` |
| E2E-P0-02 | UI | UC-01 | Sign out → Login | `/app`; session restored | `e2e/auth.spec.ts` |
| E2E-P0-03 | UI | — | Invalid login | Stay `/login`; error; no session | `e2e/auth.spec.ts` |
| E2E-P0-04 | UI | — | `/app` without session | Redirect `/login` | `e2e/auth.spec.ts` |
| E2E-P0-05 | UI+API | UC-02 | Onboarding connect & crawl | Crawl completed; pages/issues | `e2e/critical-path.spec.ts`, API happy path |
| E2E-P0-06 | UI+API | UC-03 | Run SEO | Completed; score/issues; credits −~25 | critical-path + API |
| E2E-P0-07 | UI+API | UC-04 | Run AEO | Completed; credits −~20 | critical-path + API |
| E2E-P0-08 | UI+API | UC-08 | Run keyword | Clusters; credits −~15 | API |
| E2E-P0-09 | UI+API | UC-05 | Generate blog | Draft listed | critical-path + API |
| E2E-P0-10 | UI+API | UC-06 | Approve change request | `approved` (or `applied` if auto) | critical-path + API |
| E2E-P0-11 | UI | UC-07 | Billing + mock upgrade | Starter shown; upgrade to professional | `e2e/plan-gates.spec.ts` |
| E2E-P0-12 | API | — | `GET /sites` no auth | 401 | `tests/test_p0_happy_path.py` |
| E2E-P0-13 | API | — | Wrong `X-Org-Id` | 403 | `tests/test_p0_happy_path.py` |
| E2E-P0-14 | API | UC-01–06 | signup→site→crawl→seo→review | Full API chain | `tests/test_p0_happy_path.py` |

**Golden UI journey:** signup → onboarding crawl → SEO + AEO → content generate → approvals approve → billing credits &lt; 500.

---

## P1 — Professional+ (UC-08–13)

| ID | Type | Steps | Expected | Automation |
|----|------|-------|----------|------------|
| E2E-P1-01 | UI+API | Starter hits social/competitor APIs | 403 feature locked | `tests/test_plan_gates.py`, `e2e/plan-gates.spec.ts` |
| E2E-P1-02 | API | Mock checkout → professional | Tier + 2000 credits | `tests/test_plan_gates.py` |
| E2E-P1-03 | UI+API | Social generate → publish | Posts published | `e2e/plan-gates.spec.ts`, API |
| E2E-P1-04 | API | Calendar seed | Items returned | `tests/test_p1_p2.py` |
| E2E-P1-05 | API | Competitor add → scan → events | Events non-empty | `tests/test_p1_p2.py` |
| E2E-P1-06 | API | Analytics dashboard | Report/metrics | `tests/test_p1_p2.py` |
| E2E-P1-07 | API | Connect CMS WordPress | Integration connected | `tests/test_p1_p2.py` |
| E2E-P1-08 | API | 6th site on Pro (limit 5) | 403 site limit | `tests/test_plan_gates.py` |
| E2E-P1-09 | API | 6th competitor (limit 5) | 403 competitor limit | `tests/test_plan_gates.py` |

---

## P2 — Business / Enterprise (UC-14–20)

| ID | Type | Steps | Expected | Automation |
|----|------|-------|----------|------------|
| E2E-P2-01 | API | Business + `launch_product` | Workflow completed | `tests/test_p1_p2.py` |
| E2E-P2-02 | API | Outreach discover | Opportunities | `tests/test_p1_p2.py` |
| E2E-P2-03 | API | PPC optimize | Campaign | `tests/test_p1_p2.py` |
| E2E-P2-04 | API | Local SEO optimize | Listing/result | `tests/test_p1_p2.py` |
| E2E-P2-05 | API | Create API key; `X-API-Key` only | `GET /sites` 200 | `tests/test_p1_p2.py` |
| E2E-P2-06 | API | Auto-apply on; approve CR | Status `applied` | `tests/test_p1_p2.py` |
| E2E-P2-07 | API | Starter `/workflows/launch` | 403 | `tests/test_plan_gates.py` |
| E2E-P2-08 | API | Enterprise white-label + SSO | Persisted settings | `tests/test_p1_p2.py` |
| E2E-P2-09 | API | Credits = 0 → agent run | Run `failed` / insufficient | `tests/test_plan_gates.py` |

---

## Cross-cutting (NF)

| ID | Case | Expected | Automation |
|----|------|----------|------------|
| E2E-NF-01 | Health API + web | 200 | API + Playwright |
| E2E-NF-02 | CORS signup from UI | No CORS error | Playwright critical path |
| E2E-NF-03 | Persistence (same DB) | Login after restart | Manual / optional |
| E2E-NF-04 | Org isolation | Org A ≠ Org B sites | `tests/test_p0_happy_path.py` |
| E2E-NF-05 | Viewer cannot review CR | 403 | `tests/test_plan_gates.py` |
| E2E-NF-06 | Prod health smoke | Read-only Railway | Optional; not in default suite |

---

## Out of scope

Real Stripe Checkout, live Google OAuth, live HTTP crawl, paid LLM calls, visual regression, load tests, destructive writes against Railway production.

---

## API route map (for assertions)

| Flow | Routes |
|------|--------|
| Auth | `POST /auth/signup`, `/auth/login`, `GET /auth/me` |
| Site/crawl | `POST /sites`, `POST /crawl/{id}/start`, `GET /crawl/{id}/issues` |
| Agents | `POST /agents/run` |
| Content | `POST /content/generate`, `GET /content` |
| Approvals | `GET /change-requests`, `POST /change-requests/{id}/review` |
| Billing | `GET /billing/subscription`, `POST /billing/checkout` |
| Pro+ | `/social/*`, `/competitors/*`, `/analytics/*`, `/content/calendar/seed` |
| Business+ | `/workflows/launch`, `/outreach/*`, `/ppc/*`, `/local-seo/*`, `/enterprise/*` |
