"""Qdrant vector store for page chunks (LLM / AEO retrieval)."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from app.core.config import settings

_client = None
_collection_ready = False


def _get_client():
    global _client
    if _client is None:
        try:
            from qdrant_client import QdrantClient

            _client = QdrantClient(url=settings.QDRANT_URL, timeout=5)
        except Exception:
            _client = False
    return _client if _client is not False else None


def _hash_embed(text: str, dims: int = 64) -> list[float]:
    """Deterministic bag-of-hashes embedding for offline/dev without OpenAI."""
    vec = [0.0] * dims
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    if not tokens:
        return vec
    for tok in tokens:
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % dims] += 1.0
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    i = 0
    step = max(size - overlap, 1)
    while i < len(words):
        chunk = " ".join(words[i : i + size])
        chunks.append(chunk)
        i += step
    return chunks[:40]


def ensure_collection(dims: int = 64) -> bool:
    global _collection_ready
    client = _get_client()
    if not client:
        return False
    if _collection_ready:
        return True
    try:
        from qdrant_client.http import models as qm

        names = [c.name for c in client.get_collections().collections]
        if settings.QDRANT_COLLECTION not in names:
            client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=qm.VectorParams(size=dims, distance=qm.Distance.COSINE),
            )
        _collection_ready = True
        return True
    except Exception:
        return False


async def index_page_chunks(
    *,
    organization_id: str,
    site_id: str,
    page_id: str,
    url: str,
    text: str,
) -> int:
    client = _get_client()
    chunks = chunk_text(text)
    if not client or not ensure_collection():
        return len(chunks)

    from qdrant_client.http import models as qm

    points = []
    for i, chunk in enumerate(chunks):
        pid = abs(hash(f"{page_id}:{i}")) % (2**63)
        points.append(
            qm.PointStruct(
                id=pid,
                vector=_hash_embed(chunk),
                payload={
                    "organization_id": organization_id,
                    "site_id": site_id,
                    "page_id": page_id,
                    "url": url,
                    "chunk_index": i,
                    "text": chunk[:2000],
                },
            )
        )
    if points:
        try:
            client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
        except Exception:
            return 0
    return len(points)


async def search_chunks(
    *,
    organization_id: str,
    site_id: str | None,
    query: str,
    limit: int = 8,
) -> list[dict[str, Any]]:
    client = _get_client()
    if not client or not ensure_collection():
        return []
    from qdrant_client.http import models as qm

    must = [qm.FieldCondition(key="organization_id", match=qm.MatchValue(value=organization_id))]
    if site_id:
        must.append(qm.FieldCondition(key="site_id", match=qm.MatchValue(value=site_id)))
    try:
        hits = client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=_hash_embed(query),
            query_filter=qm.Filter(must=must),
            limit=limit,
        )
        return [{"score": h.score, **(h.payload or {})} for h in hits]
    except Exception:
        return []
