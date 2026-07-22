"""LLM router with mock mode for local development."""

from __future__ import annotations

from typing import Any

from app.core.config import settings


async def complete(
    prompt: str,
    *,
    system: str = "You are DigiSEO AI, an expert digital marketing assistant.",
    model_hint: str = "auto",
    max_tokens: int = 1200,
) -> str:
    if settings.MOCK_LLM or not (settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY):
        return _mock_complete(prompt, system=system)

    if settings.OPENAI_API_KEY and model_hint in ("auto", "openai", "gpt"):
        try:
            import httpx

            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": max_tokens,
                    },
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    if settings.ANTHROPIC_API_KEY and model_hint in ("auto", "claude", "anthropic"):
        try:
            import httpx

            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": settings.ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-sonnet-4-20250514",
                        "max_tokens": max_tokens,
                        "system": system,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["content"][0]["text"]
        except Exception:
            pass

    return _mock_complete(prompt, system=system)


def _mock_complete(prompt: str, *, system: str) -> str:
    lower = prompt.lower()
    if "faq" in lower or "aeo" in lower:
        return """## FAQs
1. What is DigiSEO AI?
DigiSEO AI is an enterprise multi-agent platform for SEO, AEO, and digital marketing.

2. How does Answer Engine Optimization work?
AEO structures content so AI search engines can cite clear, authoritative answers.

3. Which AI search engines should I optimize for?
ChatGPT, Google AI Overviews, Gemini, Perplexity, Claude, and Bing Copilot.

## JSON-LD
```json
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[]}
```
"""
    if "blog" in lower or "write" in lower or "article" in lower:
        return """# How to Win SEO and AEO in 2026

Search is shifting from ten blue links to AI answers. Brands that structure expertise, entities, and citeable facts win visibility across Google and generative engines.

## Why AEO Matters
Answer engines reward clear Q&A, schema, and E-E-A-T signals.

## Action Plan
1. Audit technical SEO and Core Web Vitals
2. Add FAQ and HowTo schema
3. Publish entity-rich pillar content
4. Monitor citations and refine chunks for LLMs

## Conclusion
Treat DigiSEO AI as your always-on marketing team for continuous improvement.
"""
    if "meta" in lower or "title" in lower:
        return (
            "Title: DigiSEO AI | AI SEO & AEO Platform for Growing Brands\n"
            "Description: Automate website audits, answer-engine optimization, "
            "and content with DigiSEO AI's multi-agent marketing team."
        )
    if "hashtag" in lower or "social" in lower or "linkedin" in lower:
        return (
            "Post: AI is rewriting search. Here's how our team uses DigiSEO AI "
            "to stay visible in ChatGPT, Perplexity, and Google AI Overviews.\n\n"
            "Hashtags: #SEO #AEO #DigitalMarketing #AI #ContentMarketing"
        )
    if "outreach" in lower or "backlink" in lower:
        return (
            "Subject: Collaboration idea for your readers\n\nHi {{name}},\n"
            "I enjoyed your recent piece and thought our research on AI search "
            "visibility could add value for your audience.\nBest,\nDigiSEO AI"
        )
    if "ad copy" in lower or "ppc" in lower:
        return (
            "Headline: Grow Organic + AI Search Visibility\n"
            "Description: DigiSEO AI audits, optimizes, and publishes — so your team ships faster.\n"
            "CTA: Start free trial"
        )
    return f"[DigiSEO mock response]\nSystem: {system[:80]}\nPrompt summary: {prompt[:400]}"


async def complete_json(prompt: str, **kwargs: Any) -> dict[str, Any]:
    text = await complete(prompt, **kwargs)
    return {"text": text}
