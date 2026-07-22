"""E2E-NF-01, E2E-P0-12/13/14, E2E-NF-04 — health + starter happy path."""

from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import auth_dict, unique_email


async def test_health(client: AsyncClient):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


async def test_sites_unauthenticated(client: AsyncClient):
    """E2E-P0-12"""
    res = await client.get("/api/v1/sites")
    assert res.status_code == 401


async def test_wrong_org_id_forbidden(client: AsyncClient, auth_headers: dict):
    """E2E-P0-13"""
    h = await auth_dict(auth_headers)
    h["X-Org-Id"] = "00000000-0000-0000-0000-000000000099"
    res = await client.get("/api/v1/sites", headers=h)
    assert res.status_code in (400, 403)


async def test_p0_api_happy_path(client: AsyncClient, auth_headers: dict):
    """E2E-P0-14 — signup → site → crawl → seo → change-requests → review."""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]

    me = await client.get("/api/v1/auth/me", headers=h)
    assert me.status_code == 200
    assert me.json()["subscription"]["tier"] == "starter"
    credits_before = me.json()["subscription"]["credits_balance"]
    assert credits_before >= 500

    site_res = await client.post(
        "/api/v1/sites",
        headers=h,
        json={"url": "https://example.com", "workspace_id": ws},
    )
    assert site_res.status_code == 200, site_res.text
    site_id = site_res.json()["id"]

    crawl = await client.post(f"/api/v1/crawl/{site_id}/start", headers=h)
    assert crawl.status_code == 200, crawl.text
    assert crawl.json()["pages_crawled"] >= 1

    seo = await client.post(
        "/api/v1/agents/run",
        headers=h,
        json={
            "agent": "seo",
            "workspace_id": ws,
            "site_id": site_id,
            "goal": "seo audit",
        },
    )
    assert seo.status_code == 200, seo.text
    assert seo.json()["status"] == "completed"

    issues = await client.get(f"/api/v1/crawl/{site_id}/issues", headers=h)
    assert issues.status_code == 200
    assert isinstance(issues.json(), list)

    aeo = await client.post(
        "/api/v1/agents/run",
        headers=h,
        json={"agent": "aeo", "workspace_id": ws, "site_id": site_id, "goal": "aeo"},
    )
    assert aeo.status_code == 200
    assert aeo.json()["status"] == "completed"

    kw = await client.post(
        "/api/v1/agents/run",
        headers=h,
        json={"agent": "keyword", "workspace_id": ws, "site_id": site_id, "goal": "kw"},
    )
    assert kw.status_code == 200
    assert kw.json()["status"] == "completed"

    content = await client.post(
        "/api/v1/content/generate",
        headers=h,
        json={
            "workspace_id": ws,
            "site_id": site_id,
            "content_type": "blog",
            "topic": "AI SEO for startups",
            "keywords": ["seo", "aeo"],
            "tone": "professional",
        },
    )
    assert content.status_code == 200, content.text
    assert content.json()["title"] or content.json().get("body_markdown")

    crs = await client.get("/api/v1/change-requests?status_filter=proposed", headers=h)
    assert crs.status_code == 200
    proposed = crs.json()
    if proposed:
        review = await client.post(
            f"/api/v1/change-requests/{proposed[0]['id']}/review",
            headers=h,
            json={"status": "approved"},
        )
        assert review.status_code == 200
        assert review.json()["status"] in ("approved", "applied")

    me2 = await client.get("/api/v1/auth/me", headers=h)
    assert me2.json()["subscription"]["credits_balance"] < credits_before


async def test_org_isolation(client: AsyncClient, auth_headers: dict):
    """E2E-NF-04"""
    h_a = await auth_dict(auth_headers)
    site = await client.post(
        "/api/v1/sites",
        headers=h_a,
        json={"url": "https://org-a.example", "workspace_id": auth_headers["workspace_id"]},
    )
    assert site.status_code == 200
    site_id_a = site.json()["id"]

    email_b = unique_email("orgb")
    signup_b = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email_b,
            "password": "password123",
            "full_name": "Org B",
            "organization_name": f"Company B {email_b}",
            "workspace_name": "Default",
        },
    )
    assert signup_b.status_code == 200
    data_b = signup_b.json()
    h_b = {
        "Authorization": f"Bearer {data_b['access_token']}",
        "X-Org-Id": data_b["org_id"],
        "X-Workspace-Id": data_b["workspace_id"],
    }

    sites_b = await client.get("/api/v1/sites", headers=h_b)
    assert sites_b.status_code == 200
    ids = {s["id"] for s in sites_b.json()}
    assert site_id_a not in ids

    other = await client.get(f"/api/v1/sites/{site_id_a}", headers=h_b)
    assert other.status_code == 404
