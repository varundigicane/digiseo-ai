# DigiSEO AI

Enterprise multi-agent marketing platform for SEO, AEO, content, social, PPC, and analytics.

## Stack

- **Frontend:** Next.js 15, React, Tailwind CSS
- **API:** FastAPI (Python)
- **Workers:** ARQ/async polling worker
- **Data:** PostgreSQL, Redis, Qdrant
- **Orchestration:** LangGraph agent fleet

## Deploy on Railway

See **[docs/deploy/RAILWAY.md](docs/deploy/RAILWAY.md)** for a full multi-service setup (`api` + `web` + Postgres).

Quick outline:

1. Push to GitHub → New Railway project
2. Add **PostgreSQL** plugin
3. Service **api** — Root Directory `apps/api` (Dockerfile)
4. Service **web** — Root Directory `apps/web` (Dockerfile)
5. Set `DATABASE_URL` on api from Postgres; set `NEXT_PUBLIC_API_URL` / `WEB_URL` / `CORS_ORIGINS` to your Railway domains

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

## License

Proprietary — Digicane Systems
