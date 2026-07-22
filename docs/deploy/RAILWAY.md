# DigiSEO AI — Railway deployment

Deploy as **three services** (plus Postgres) from the same GitHub repo.

## Architecture on Railway

| Service | Root Directory | Notes |
|---------|----------------|-------|
| `api` | `apps/api` | FastAPI, Dockerfile |
| `web` | `apps/web` | Next.js standalone, Dockerfile |
| `worker` (optional) | `/` (repo root) | Dockerfile `apps/worker/Dockerfile` |
| Postgres | Railway plugin | Provides `DATABASE_URL` |
| Redis (optional) | Railway plugin | Provides `REDIS_URL` |

Qdrant is optional — the API soft-fails indexing when `QDRANT_URL` is unreachable.

---

## 1. Create project

1. Push this repo to GitHub.
2. [Railway](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Add a **PostgreSQL** plugin to the project.

---

## 2. API service

1. **New Service** → same repo.
2. Settings:
   - **Root Directory:** `apps/api`
   - **Builder:** Dockerfile (`Dockerfile`)
3. **Variables** (Settings → Variables):

| Variable | Value |
|----------|--------|
| `APP_ENV` | `production` |
| `SECRET_KEY` | long random string |
| `WEB_URL` | `https://<your-web>.up.railway.app` (update after web is live) |
| `API_URL` | `https://<your-api>.up.railway.app` |
| `CORS_ORIGINS` | same as `WEB_URL` (add custom domains later) |
| `MOCK_LLM` | `true` initially, or `false` + LLM keys |
| `MOCK_CRAWL` | `true` for demo, `false` for live crawls |
| `DATABASE_URL` | **Reference** from Postgres (`${{Postgres.DATABASE_URL}}`) |

Optional: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `REDIS_URL`, Stripe keys, Google OAuth.

4. **Networking:** Generate a public domain for the API.
5. Health check path: `/health` (already in `railway.toml`).

The API rewrites Railway’s `postgresql://…` URL to `postgresql+asyncpg://…` and enables TLS automatically.

---

## 3. Web service

1. **New Service** → same repo.
2. Settings:
   - **Root Directory:** `apps/web`
   - **Builder:** Dockerfile
3. **Variables:**

| Variable | Value |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | `https://<your-api>.up.railway.app` |
| `NEXT_PUBLIC_APP_URL` | `https://<your-web>.up.railway.app` |

Important: `NEXT_PUBLIC_*` are baked in at **build** time. Set them before the first successful build (or **Redeploy** after changing).

In Railway Docker builds, also set these as **Build Arguments** / service variables so the Dockerfile `ARG`s receive them:

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_APP_URL`

4. Generate a public domain for the web service.
5. Update the API’s `WEB_URL` + `CORS_ORIGINS` to the web domain, then redeploy API.

---

## 4. Worker (optional)

1. New service from repo root.
2. Dockerfile path: `apps/worker/Dockerfile`
3. Share the same `DATABASE_URL` (and Redis) as the API.
4. No public domain needed.

---

## 5. Post-deploy checklist

1. Open `https://<api>/health` → `{"status":"ok",...}`
2. Open the web URL → signup → connect a site → run SEO audit
3. Set a strong `SECRET_KEY` (never use the example)
4. Turn `MOCK_LLM=false` when real keys are configured
5. Point a custom domain at `web` and add it to `CORS_ORIGINS`

---

## Local Docker smoke test (optional)

```bash
# From repo root — API
docker build -t digiseo-api ./apps/api
docker run --rm -p 8000:8000 -e SECRET_KEY=test -e MOCK_LLM=true digiseo-api

# Web (pass public URLs for build)
docker build -t digiseo-web \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  --build-arg NEXT_PUBLIC_APP_URL=http://localhost:3000 \
  ./apps/web
docker run --rm -p 3000:3000 digiseo-web
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| CORS errors in browser | Set `WEB_URL` / `CORS_ORIGINS` to exact web origin (https, no trailing slash) |
| Web calls localhost API | Rebuild web after setting `NEXT_PUBLIC_API_URL` |
| DB connection failed | Ensure Postgres is linked; check `DATABASE_URL` reference |
| Blank Next page | Confirm standalone build; check Railway deploy logs |
| Cold start timeouts | Raise healthcheck timeout; keep `/health` lightweight |
