# Testing

| Doc | Description |
|-----|-------------|
| [E2E_TEST_PLAN.md](E2E_TEST_PLAN.md) | P0–P2 + NF case catalog (manual / API coverage) |

## Quick start

```bash
# From repo root — API contract/gates (isolated SQLite)
npm run test:api
```

UI flows are covered manually against the plan in `E2E_TEST_PLAN.md` (Playwright was removed from `apps/web`).
