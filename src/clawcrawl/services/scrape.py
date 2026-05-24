"""Firecrawl markdown scrape."""

import logging

from firecrawl import Firecrawl

from clawcrawl.config import Settings
from clawcrawl.telemetry.langfuse import pipeline_span

logger = logging.getLogger(__name__)


def scrape_markdown(url: str, settings: Settings) -> tuple[str, dict]:
    """Fetch page markdown via Firecrawl."""
    logger.info("Start scrape_markdown url=%s", url)
    span = None
    try:
        with pipeline_span(
            "scrape_markdown", settings=settings, input={"url": url}
        ) as span:
            client = Firecrawl(api_key=settings.firecrawl_api_key)
            doc = client.scrape(url, formats=["markdown"])
            md = getattr(doc, "markdown", None) or (
                doc.get("markdown") if isinstance(doc, dict) else ""
            )
            if not md:
                raise ValueError("Firecrawl returned no markdown")
            meta = {}
            if hasattr(doc, "metadata"):
                meta = doc.metadata or {}
            elif isinstance(doc, dict):
                meta = doc.get("metadata") or {}
            result = (md, dict(meta) if meta else {})
    except Exception:
        logger.exception("End scrape_markdown (failed) url=%s", url)
        raise
    else:
        if span is not None:
            span.update(
                output={
                    "markdown_len": len(result[0]),
                    "metadata_keys": list(result[1].keys()),
                }
            )
        logger.info("End scrape_markdown url=%s len=%d", url, len(result[0]))
        return result