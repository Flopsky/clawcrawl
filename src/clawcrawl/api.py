"""Public library API for running crawls outside FastAPI."""

from __future__ import annotations

import asyncio
import logging

from langfuse import get_client, propagate_attributes

from clawcrawl.config import Settings, get_settings
from clawcrawl.models import CrawlResponse
from clawcrawl.pipeline import run_crawl
from clawcrawl.telemetry.langfuse import flush_langfuse, tracing_enabled

logger = logging.getLogger(__name__)


async def crawl(url: str, *, settings: Settings | None = None) -> CrawlResponse:
    """Crawl a URL and return markdown with image descriptions inlined.

    Loads settings from the environment and ``.env`` when ``settings`` is omitted.
    """
    settings = settings or get_settings()
    logger.info("Start crawl url=%s", url)
    result: CrawlResponse | None = None
    try:
        if tracing_enabled(settings):
            langfuse = get_client()
            with propagate_attributes(trace_name="clawcrawl.crawl"):
                with langfuse.start_as_current_observation(
                    as_type="span",
                    name="crawl",
                    input={"url": url},
                ) as root:
                    result = await run_crawl(url, settings)
                    root.update(
                        output={
                            "url": result.url,
                            "images": len(result.images),
                        }
                    )
        else:
            result = await run_crawl(url, settings)
    finally:
        if tracing_enabled(settings):
            flush_langfuse()
    logger.info("End crawl url=%s", url)
    assert result is not None
    return result


def crawl_sync(url: str, *, settings: Settings | None = None) -> CrawlResponse:
    """Synchronous wrapper around :func:`crawl` for scripts and notebooks."""
    return asyncio.run(crawl(url, settings=settings))
