# Architecture

DigiSEO AI is a multi-tenant SaaS with:

- Next.js app (marketing + authenticated product)
- FastAPI gateway with JWT org/workspace context
- LangGraph-oriented agent orchestrator (`apps/api/app/agents`)
- Async crawl + Qdrant chunk index
- Stripe subscriptions + credit ledger
- Human-in-the-loop `change_requests`
- Phase 3 enterprise: API keys, white-label, SSO stubs, audit logs

Local default DB is SQLite (`sqlite+aiosqlite`). For production, set `DATABASE_URL` to Postgres and run `infra/docker/docker-compose.yml`.

## Docs in this folder

| File | Contents |
|------|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full architecture narrative + key Mermaid views |
| [DIAGRAMS.md](DIAGRAMS.md) | Complete diagram pack (15 diagrams) |

Also see:

- [../USER_GUIDE.md](../USER_GUIDE.md)
- [../functional/FUNCTIONAL_SPEC.md](../functional/FUNCTIONAL_SPEC.md)
- [../README.md](../README.md) — documentation index
