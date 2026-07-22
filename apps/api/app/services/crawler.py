"""Website crawler: robots.txt, sitemap, on-page extraction, Qdrant indexing."""

from __future__ import annotations

import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Crawl, Page, Site
from app.services.vector_store import index_page_chunks


USER_AGENT = "DigiSEOBot/0.1 (+https://digiseo.ai)"


def extract_domain(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = parsed.netloc or parsed.path
    return host.lower().removeprefix("www.")


async def fetch_text(client: httpx.AsyncClient, url: str) -> tuple[int, str, float]:
    start = time.perf_counter()
    resp = await client.get(url, follow_redirects=True, timeout=20.0)
    elapsed = (time.perf_counter() - start) * 1000
    return resp.status_code, resp.text, elapsed


def parse_robots(robots_txt: str) -> dict[str, Any]:
    sitemaps: list[str] = []
    disallows: list[str] = []
    for line in robots_txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lower = line.lower()
        if lower.startswith("sitemap:"):
            sitemaps.append(line.split(":", 1)[1].strip())
        elif lower.startswith("disallow:"):
            disallows.append(line.split(":", 1)[1].strip())
    return {"sitemaps": sitemaps, "disallows": disallows}


def parse_sitemap(xml: str) -> list[str]:
    # Lightweight sitemap URL extraction
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml, flags=re.I)


def extract_page(url: str, html: str, status_code: int, load_time_ms: float, domain: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    title = (soup.title.string or "").strip() if soup.title else None
    meta_desc = None
    md = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if md and md.get("content"):
        meta_desc = md["content"].strip()
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else None
    canonical = None
    can = soup.find("link", rel=lambda v: v and "canonical" in str(v).lower())
    if can and can.get("href"):
        canonical = can["href"]

    # Schema
    schema_types: list[str] = []
    for script in soup.find_all("script", type="application/ld+json"):
        text = script.string or ""
        for match in re.findall(r'"@type"\s*:\s*"([^"]+)"', text):
            schema_types.append(match)

    images = []
    for img in soup.find_all("img")[:50]:
        images.append(
            {
                "src": img.get("src"),
                "alt": img.get("alt") or "",
                "missing_alt": not bool(img.get("alt")),
            }
        )

    links_internal: list[str] = []
    links_external: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        absolute = urljoin(url, href)
        host = urlparse(absolute).netloc.lower().removeprefix("www.")
        if host == domain or host.endswith("." + domain):
            links_internal.append(absolute)
        else:
            links_external.append(absolute)

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)

    path = urlparse(url).path or "/"
    return {
        "url": url,
        "path": path,
        "status_code": status_code,
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "canonical": canonical,
        "word_count": len(text.split()),
        "has_schema": bool(schema_types),
        "schema_types": list(dict.fromkeys(schema_types)),
        "images": images,
        "links_internal": list(dict.fromkeys(links_internal))[:200],
        "links_external": list(dict.fromkeys(links_external))[:100],
        "broken_links": [],
        "content_text": text[:50000],
        "content_html": html[:100000],
        "load_time_ms": int(load_time_ms),
    }


async def mock_pages(site_url: str, domain: str) -> list[dict[str, Any]]:
    base = site_url.rstrip("/")
    samples = [
        ("/", f"{domain} — Home", "Welcome to our platform. We help businesses grow with SEO and content."),
        ("/about", "About Us", "Our team has years of experience in digital marketing and AI."),
        ("/blog/seo-tips", "SEO Tips for 2026", "Learn how to optimize Core Web Vitals, schema, and on-page SEO."),
        ("/pricing", "Pricing", "Starter, Professional, and Business plans for growing teams."),
        ("/contact", "Contact", "Get in touch with our team for a demo."),
    ]
    pages = []
    for path, title, body in samples:
        html = f"""<!DOCTYPE html><html><head><title>{title}</title>
        <meta name="description" content="{body[:140]}"/>
        <script type="application/ld+json">{{"@type":"Organization","name":"{domain}"}}</script>
        </head><body><h1>{title}</h1><p>{body}</p>
        <a href="/">Home</a><a href="/about">About</a><a href="/blog/seo-tips">Blog</a>
        <img src="/logo.png" alt="Logo"/><img src="/hero.jpg"/>
        </body></html>"""
        pages.append(extract_page(f"{base}{path}", html, 200, 320.0, domain))
    return pages


async def run_crawl(db: AsyncSession, site: Site, crawl: Crawl, max_pages: int = 30) -> Crawl:
    crawl.status = "running"
    await db.flush()

    domain = site.domain
    base = site.url if "://" in site.url else f"https://{site.url}"

    try:
        if settings.MOCK_CRAWL:
            robots_txt = "User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml\n"
            sitemap_urls = [f"{base.rstrip('/')}/sitemap.xml"]
            pages_data = await mock_pages(base, domain)
        else:
            async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
                robots_txt = ""
                try:
                    code, robots_txt, _ = await fetch_text(client, urljoin(base, "/robots.txt"))
                    if code >= 400:
                        robots_txt = ""
                except Exception:
                    robots_txt = ""

                robots = parse_robots(robots_txt)
                sitemap_urls = robots.get("sitemaps") or [urljoin(base, "/sitemap.xml")]
                urls: list[str] = [base]
                for sm in sitemap_urls[:3]:
                    try:
                        code, xml, _ = await fetch_text(client, sm)
                        if code < 400:
                            urls.extend(parse_sitemap(xml))
                    except Exception:
                        continue
                # Deduplicate same-domain
                seen: set[str] = set()
                filtered: list[str] = []
                for u in urls:
                    host = urlparse(u).netloc.lower().removeprefix("www.")
                    if host != domain and not host.endswith("." + domain):
                        continue
                    if u not in seen:
                        seen.add(u)
                        filtered.append(u)
                filtered = filtered[:max_pages]
                crawl.pages_found = len(filtered)
                crawl.robots_txt = robots_txt
                crawl.sitemap_urls = sitemap_urls

                pages_data = []
                for u in filtered:
                    try:
                        code, html, ms = await fetch_text(client, u)
                        pages_data.append(extract_page(u, html, code, ms, domain))
                    except Exception as exc:
                        pages_data.append(
                            {
                                "url": u,
                                "path": urlparse(u).path or "/",
                                "status_code": 0,
                                "title": None,
                                "meta_description": None,
                                "h1": None,
                                "canonical": None,
                                "word_count": 0,
                                "has_schema": False,
                                "schema_types": [],
                                "images": [],
                                "links_internal": [],
                                "links_external": [],
                                "broken_links": [str(exc)],
                                "content_text": "",
                                "content_html": "",
                                "load_time_ms": None,
                            }
                        )

        if settings.MOCK_CRAWL:
            crawl.pages_found = len(pages_data)
            crawl.robots_txt = robots_txt
            crawl.sitemap_urls = sitemap_urls

        # Clear old pages for site (simple strategy for MVP)
        existing = await db.execute(select(Page).where(Page.site_id == site.id))
        for old in existing.scalars().all():
            await db.delete(old)
        await db.flush()

        for pdata in pages_data:
            page = Page(
                site_id=site.id,
                organization_id=site.organization_id,
                crawl_id=crawl.id,
                **pdata,
            )
            db.add(page)
            await db.flush()
            await index_page_chunks(
                organization_id=str(site.organization_id),
                site_id=str(site.id),
                page_id=str(page.id),
                url=page.url,
                text=page.content_text or "",
            )

        crawl.pages_crawled = len(pages_data)
        crawl.status = "completed"
        site.last_crawled_at = datetime.now(timezone.utc)
        await db.flush()
        return crawl
    except Exception as exc:
        crawl.status = "failed"
        crawl.error = str(exc)
        await db.flush()
        return crawl
