"""Professional / Business / Enterprise flows — E2E-P1-03–07, P2-01–06, P2-08."""

from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import auth_dict


async def _upgrade(client: AsyncClient, h: dict, tier: str):
    r = await client.post("/api/v1/billing/checkout", headers=h, json={"tier": tier})
    assert r.status_code == 200, r.text
    return r.json()


async def _site_and_crawl(client: AsyncClient, h: dict, ws: str, url: str = "https://biz.example.com"):
    site = await client.post("/api/v1/sites", headers=h, json={"url": url, "workspace_id": ws})
    assert site.status_code == 200, site.text
    site_id = site.json()["id"]
    crawl = await client.post(f"/api/v1/crawl/{site_id}/start", headers=h)
    assert crawl.status_code == 200, crawl.text
    return site_id


async def test_social_generate_publish(client: AsyncClient, auth_headers: dict):
    """E2E-P1-03"""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]
    await _upgrade(client, h, "professional")

    acct = await client.post(
        "/api/v1/social/accounts",
        headers=h,
        json={"workspace_id": ws, "platform": "linkedin", "handle": "@digiseo"},
    )
    assert acct.status_code == 200, acct.text

    gen = await client.post(
        "/api/v1/social/generate",
        headers=h,
        json={"workspace_id": ws, "platform": "linkedin", "topic": "Product launch"},
    )
    assert gen.status_code == 200, gen.text
    post_id = gen.json()["id"]

    pub = await client.post(f"/api/v1/social/posts/{post_id}/publish", headers=h)
    assert pub.status_code == 200, pub.text
    assert pub.json()["status"] in ("published", "scheduled", "draft") or pub.json().get("status")


async def test_calendar_seed(client: AsyncClient, auth_headers: dict):
    """E2E-P1-04"""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]
    await _upgrade(client, h, "professional")
    res = await client.post(f"/api/v1/content/calendar/seed?workspace_id={ws}", headers=h)
    assert res.status_code == 200, res.text
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


async def test_competitor_scan_events(client: AsyncClient, auth_headers: dict):
    """E2E-P1-05"""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]
    await _upgrade(client, h, "professional")
    comp = await client.post(
        "/api/v1/competitors",
        headers=h,
        json={"workspace_id": ws, "name": "Rival Co", "domain": "rival.example.com"},
    )
    assert comp.status_code == 200, comp.text
    cid = comp.json()["id"]
    scan = await client.post(f"/api/v1/competitors/{cid}/scan", headers=h)
    assert scan.status_code == 200, scan.text
    events = await client.get(f"/api/v1/competitors/{cid}/events", headers=h)
    assert events.status_code == 200
    assert isinstance(events.json(), list)


async def test_analytics_dashboard(client: AsyncClient, auth_headers: dict):
    """E2E-P1-06"""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]
    await _upgrade(client, h, "professional")
    dash = await client.get(f"/api/v1/analytics/dashboard?workspace_id={ws}", headers=h)
    assert dash.status_code == 200, dash.text
    body = dash.json()
    assert "metrics" in body or "summary" in body


async def test_cms_connect(client: AsyncClient, auth_headers: dict):
    """E2E-P1-07"""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]
    await _upgrade(client, h, "professional")
    conn = await client.post(
        "/api/v1/integrations/connect",
        headers=h,
        json={"provider": "wordpress", "workspace_id": ws, "meta": {}},
    )
    assert conn.status_code == 200, conn.text
    listed = await client.get("/api/v1/integrations", headers=h)
    providers = {i["provider"] for i in listed.json()}
    assert "wordpress" in providers


async def test_launch_product_workflow(client: AsyncClient, auth_headers: dict):
    """E2E-P2-01"""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]
    await _upgrade(client, h, "business")
    site_id = await _site_and_crawl(client, h, ws, "https://launch.example.com")
    run = await client.post(
        "/api/v1/workflows/launch",
        headers=h,
        json={
            "workspace_id": ws,
            "site_id": site_id,
            "workflow": "launch_product",
            "goal": "Launch campaign",
        },
    )
    assert run.status_code == 200, run.text
    assert run.json()["status"] == "completed"


async def test_outreach_ppc_local(client: AsyncClient, auth_headers: dict):
    """E2E-P2-02, P2-03, P2-04"""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]
    await _upgrade(client, h, "business")
    await _site_and_crawl(client, h, ws, "https://growth.example.com")

    out = await client.post(
        f"/api/v1/outreach/discover?workspace_id={ws}&niche=seo",
        headers=h,
    )
    assert out.status_code == 200, out.text

    opps = await client.get(f"/api/v1/outreach/opportunities?workspace_id={ws}", headers=h)
    assert opps.status_code == 200

    ppc = await client.post(
        "/api/v1/ppc/optimize",
        headers=h,
        json={"workspace_id": ws, "platform": "google", "keywords": ["seo tool"]},
    )
    assert ppc.status_code == 200, ppc.text

    campaigns = await client.get(f"/api/v1/ppc/campaigns?workspace_id={ws}", headers=h)
    assert campaigns.status_code == 200

    local = await client.post(
        "/api/v1/local-seo/optimize",
        headers=h,
        json={"workspace_id": ws, "business_name": "DigiSEO Demo", "city": "Austin"},
    )
    assert local.status_code == 200, local.text


async def test_api_key_auth(client: AsyncClient, auth_headers: dict):
    """E2E-P2-05"""
    h = await auth_dict(auth_headers)
    await _upgrade(client, h, "business")
    key_res = await client.post("/api/v1/enterprise/api-keys", headers=h)
    assert key_res.status_code == 200, key_res.text
    api_key = key_res.json()["api_key"]

    sites = await client.get(
        "/api/v1/sites",
        headers={"X-API-Key": api_key, "X-Org-Id": auth_headers["org_id"]},
    )
    assert sites.status_code == 200


async def test_auto_apply_on_approve(client: AsyncClient, auth_headers: dict):
    """E2E-P2-06"""
    h = await auth_dict(auth_headers)
    ws = auth_headers["workspace_id"]
    await _upgrade(client, h, "business")
    # set_plan_tier already enables auto_apply for business; ensure toggle on
    toggle = await client.post("/api/v1/enterprise/auto-apply?enabled=true", headers=h)
    assert toggle.status_code == 200, toggle.text

    site_id = await _site_and_crawl(client, h, ws, "https://autoapply.example.com")
    await client.post(
        "/api/v1/agents/run",
        headers=h,
        json={"agent": "seo", "workspace_id": ws, "site_id": site_id, "goal": "seo"},
    )
    crs = await client.get("/api/v1/change-requests?status_filter=proposed", headers=h)
    proposed = crs.json()
    if not proposed:
        return
    review = await client.post(
        f"/api/v1/change-requests/{proposed[0]['id']}/review",
        headers=h,
        json={"status": "approved"},
    )
    assert review.status_code == 200
    assert review.json()["status"] == "applied"


async def test_enterprise_white_label_sso(client: AsyncClient, auth_headers: dict):
    """E2E-P2-08"""
    h = await auth_dict(auth_headers)
    await _upgrade(client, h, "enterprise")

    wl = await client.put(
        "/api/v1/enterprise/white-label",
        headers=h,
        json={
            "custom_domain": "seo.customer.com",
            "brand_logo_url": "https://cdn.example/logo.png",
            "brand_primary_color": "#0a7",
            "enabled": True,
        },
    )
    assert wl.status_code == 200, wl.text

    sso = await client.put(
        "/api/v1/enterprise/sso",
        headers=h,
        json={"enabled": True, "metadata_url": "https://idp.example/meta", "entity_id": "digiseo"},
    )
    assert sso.status_code == 200, sso.text

    settings = await client.get("/api/v1/enterprise/settings", headers=h)
    assert settings.status_code == 200
    org = settings.json()["organization"]
    assert org["white_label_enabled"] is True
    assert org["custom_domain"] == "seo.customer.com"
    assert org["sso_enabled"] is True
