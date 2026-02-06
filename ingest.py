# python/app/ingest.py
import httpx
import feedparser
import asyncio
import logging
from typing import List

logger = logging.getLogger("horaculo.ingest")

NEWSAPI_URL = "https://newsapi.org/v2/everything"

# ======================================================
# FETCHERS
# ======================================================
async def _fetch_newsapi_async(client, query, api_key, page_size):
    params = {
        "q": query,
        "language": "en",
        "pageSize": page_size,
        "sortBy": "publishedAt"
    }
    headers = {"Authorization": api_key}

    try:
        resp = await client.get(NEWSAPI_URL, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "source": a["source"]["name"] or "unknown",
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "text": f"{a.get('title','')} . {a.get('description','')}",
                "url": a.get("url", ""),
                "publishedAt": a.get("publishedAt")
            }
            for a in data.get("articles", [])
        ]
    except Exception as e:
        logger.warning(f"NewsAPI falhou: {e}")
        return []


async def _fetch_rss_async(client, url, limit):
    try:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

        return [
            {
                "source": feed.feed.get("title", "rss"),
                "title": e.get("title", ""),
                "description": e.get("summary", ""),
                "text": f"{e.get('title','')} . {e.get('summary','')}",
                "url": e.get("link", ""),
                "publishedAt": e.get("published")
            }
            for e in feed.entries[:limit]
        ]
    except Exception as e:
        logger.warning(f"RSS falhou ({url}): {e}")
        return []


# ======================================================
# CONFIDENCE HEURISTIC (SIMPLES E EFICAZ)
# ======================================================
def estimate_confidence(results: List[dict]) -> float:
    if not results:
        return 0.0

    trusted_sources = {"reuters", "bloomberg"}
    hits = sum(
        1 for r in results
        if any(src in r["source"].lower() for src in trusted_sources)
    )

    return min(1.0, hits / max(1, len(results)))


# ======================================================
# INGESTÃO EM TIERS (FAIL-FAST)
# ======================================================
async def fetch_all_sources(query, api_key):
    tier1_rss = [
        "https://www.reuters.com/rssFeed/businessNews",
        "https://feeds.bloomberg.com/markets/news.rss"
    ]

    tier2_rss = [
        # exemplos
        "https://finance.yahoo.com/rss",
        "https://www.investing.com/rss/news.rss"
    ]

    async with httpx.AsyncClient() as client:

        # -------------------------
        # TIER 1
        # -------------------------
        tier1_tasks = []

        if api_key:
            tier1_tasks.append(
                asyncio.create_task(
                    _fetch_newsapi_async(client, query, api_key, 30)
                )
            )

        for url in tier1_rss:
            tier1_tasks.append(
                asyncio.create_task(
                    _fetch_rss_async(client, url, 10)
                )
            )

        done, pending = await asyncio.wait(
            tier1_tasks,
            timeout=2,
            return_when=asyncio.FIRST_COMPLETED
        )

        tier1_results = []
        for task in done:
            tier1_results.extend(task.result())

        confidence = estimate_confidence(tier1_results)

        if tier1_results and confidence >= 0.9:
            # FAIL-FAST: cancela o resto
            for task in pending:
                task.cancel()

            logger.info("Tier 1 suficiente. Abortando Tier 2.")
            return tier1_results

        # -------------------------
        # TIER 2
        # -------------------------
        logger.info("Tier 1 insuficiente. Ativando Tier 2.")

        tier2_tasks = [
            asyncio.create_task(_fetch_rss_async(client, url, 10))
            for url in tier2_rss
        ]

        tier2_results = []
        if tier2_tasks:
            results = await asyncio.gather(*tier2_tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, list):
                    tier2_results.extend(r)

        return tier1_results + tier2_results


# ======================================================
# SYNC ENTRYPOINT (CELERY / FASTAPI)
# ======================================================
def fetch_data_entrypoint(query, api_key):
    try:
        return asyncio.run(fetch_all_sources(query, api_key))
    except Exception as e:
        logger.error(f"Falha crítica no ingest: {e}")
        return []
