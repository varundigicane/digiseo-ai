"""Pytest fixtures — isolated SQLite + mock LLM/crawl."""

from __future__ import annotations

import os
import sys
import time
import uuid
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

TEST_DB = API_ROOT / "test_digiseo.db"
if TEST_DB.exists():
    try:
        TEST_DB.unlink()
    except OSError:
        pass

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB.as_posix()}"
os.environ["DATABASE_URL_SYNC"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["MOCK_LLM"] = "true"
os.environ["MOCK_CRAWL"] = "true"
os.environ["STRIPE_SECRET_KEY"] = ""
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-e2e"

from app.core.config import get_settings  # noqa: E402
import app.core.config as config_mod  # noqa: E402

get_settings.cache_clear()
config_mod.settings = get_settings()

from app.core import database as db_mod  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

db_mod.engine = create_async_engine(
    config_mod.settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db_mod.AsyncSessionLocal = async_sessionmaker(
    db_mod.engine, expire_on_commit=False, class_=AsyncSession
)

from app.core.database import init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
async def client():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def unique_email(prefix: str = "e2e") -> str:
    return f"{prefix}+{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Signup a fresh starter org and return auth headers + ids."""
    email = unique_email()
    password = "password123"
    res = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "password": password,
            "full_name": "E2E Tester",
            "organization_name": f"Org {email}",
            "workspace_name": "Default",
        },
    )
    assert res.status_code == 200, res.text
    data = res.json()
    headers = {
        "Authorization": f"Bearer {data['access_token']}",
        "X-Org-Id": data["org_id"],
        "X-Workspace-Id": data["workspace_id"],
    }
    return {
        **headers,
        "email": email,
        "password": password,
        "org_id": data["org_id"],
        "workspace_id": data["workspace_id"],
        "access_token": data["access_token"],
    }


async def auth_dict(headers: dict) -> dict[str, str]:
    return {
        "Authorization": headers["Authorization"],
        "X-Org-Id": headers["X-Org-Id"],
        "X-Workspace-Id": headers["X-Workspace-Id"],
    }
