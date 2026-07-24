# DigiSEO AI

Enterprise multi-agent marketing platform for SEO, AEO, content, social, PPC, and analytics.

## Stack

- **Frontend:** Next.js 15, React, Tailwind CSS
- **API:** FastAPI (Python)
- **Workers:** ARQ/async polling worker
- **Data:** PostgreSQL, Redis, Qdrant
- **Orchestration:** LangGraph agent fleet

## Deploy on Railway

**Separate project:** DigiSEO lives on its own GitHub repo and Railway project (not digicane-systems).

| Resource | URL |
|----------|-----|
| GitHub | https://github.com/varundigicane/digiseo-ai |
| Railway project | `digiseo-ai` |
| API | https://api-production-4a88.up.railway.app |
| Web | https://web-production-faa9d.up.railway.app |

See **[docs/deploy/RAILWAY.md](docs/deploy/RAILWAY.md)** for full multi-service setup (`api` + `web` + Postgres). Root directories: `apps/api`, `apps/web`.

## Quick start

### 1. Infrastructure

```bash
cp .env.example .env
docker compose -f infra/docker/docker-compose.yml up -d postgres redis qdrant
```

### 2. API

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy ..\..\.env .env   # or: cp ../../.env .env
# Defaults: MOCK_LLM=true, MOCK_CRAWL=true, SQLite DB
uvicorn app.main:app --reload --port 8000
```

For Postgres/Redis/Qdrant instead of SQLite, start Docker services and set `DATABASE_URL` in `.env` to the Postgres URL from `.env.example`.

### 3. Web

```bash
npm install
npm run dev:web
```

Open http://localhost:3000

### 4. Worker (optional)

```bash
cd apps/worker
set PYTHONPATH=..\api
python -m worker.main
```

## Plans

| Plan | Price | Credits |
|------|-------|---------|
| Starter | $49/mo | 500 |
| Professional | $149/mo | 2,000 |
| Business | $399/mo | 8,000 |
| Enterprise | Custom | 50,000+ |

## Agents

1. Website SEO · 2. AEO · 3. Content · 4. Social · 5. Competitor · 6. Keywords · 7. Backlink · 8. PPC · 9. Analytics · 10. Local SEO

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/README.md](docs/README.md) | Documentation index |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | End-user guide |
| [docs/functional/FUNCTIONAL_SPEC.md](docs/functional/FUNCTIONAL_SPEC.md) | Functional spec & use cases |
| [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) | System architecture |
| [docs/architecture/DIAGRAMS.md](docs/architecture/DIAGRAMS.md) | Mermaid diagram pack |
| [docs/agents/README.md](docs/agents/README.md) | Agent catalog |
| [docs/deploy/RAILWAY.md](docs/deploy/RAILWAY.md) | Railway deploy |
| [docs/testing/E2E_TEST_PLAN.md](docs/testing/E2E_TEST_PLAN.md) | E2E test cases |

## Tests

```bash
# API (pytest) — uses isolated SQLite + MOCK_LLM/MOCK_CRAWL
cd apps/api
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests -q
# or from root: npm run test:api
```

## License

Proprietary — Digicane Systems
