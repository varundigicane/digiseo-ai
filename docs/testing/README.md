# Testing

| Doc | Description |
|-----|-------------|
| [E2E_TEST_PLAN.md](E2E_TEST_PLAN.md) | Full P0–P2 + NF case catalog and how to run |

## Quick start

```bash
# From repo root — API contract/gates (isolated SQLite)
npm run test:api

# UI E2E — start API on :8000 first (MOCK_LLM/MOCK_CRAWL), then:
# Playwright serves DigiSEO on :3010
npm run test:e2e
```
