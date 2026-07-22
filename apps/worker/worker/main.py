"""Background worker — processes queued agent runs via Redis/ARQ when available."""

from __future__ import annotations

import asyncio
import logging
import os
import sys

# Ensure API package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("digiseo.worker")


async def process_pending_runs() -> int:
    from sqlalchemy import select

    from app.agents.orchestrator import execute_agent_run
    from app.core.database import AsyncSessionLocal
    from app.models import AgentRun, AgentRunStatus

    processed = 0
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AgentRun)
            .where(AgentRun.status == AgentRunStatus.QUEUED)
            .order_by(AgentRun.created_at)
            .limit(5)
        )
        runs = result.scalars().all()
        for run in runs:
            logger.info("Processing agent run %s (%s)", run.id, run.agent)
            await execute_agent_run(db, run)
            processed += 1
        await db.commit()
    return processed


async def loop(poll_seconds: float = 5.0):
    logger.info("DigiSEO worker started")
    while True:
        try:
            n = await process_pending_runs()
            if n:
                logger.info("Processed %s runs", n)
        except Exception:
            logger.exception("Worker loop error")
        await asyncio.sleep(poll_seconds)


def main():
    asyncio.run(loop())


if __name__ == "__main__":
    main()
