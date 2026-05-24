"""End-to-end crawl pipeline."""

import logging

from clawcrawl.config import Settings
from clawcrawl.llm.client import build_text_client, build_vision_client
from clawcrawl.models import CrawlResponse, ImageDescription
from clawcrawl.services.describe import describe_all
from clawcrawl.services.image_links import extract_image_links
from clawcrawl.services.replace import replace_images_in_markdown
from clawcrawl.services.scrape import scrape_markdown
from clawcrawl.telemetry.langfuse import pipeline_span

logger = logging.getLogger(__name__)


async def run_crawl(url: str, settings: Settings) -> CrawlResponse:
    """Scrape, extract images, describe, and rewrite markdown."""
    logger.info("Start run_crawl url=%s", url)
    span = None
    try:
        with pipeline_span("run_crawl", settings=settings, input={"url": url}) as span:
            markdown, metadata = scrape_markdown(url, settings)
            text_client = build_text_client(settings)
            vision_client = build_vision_client(settings)

            refs = await extract_image_links(
                text_client,
                markdown,
                max_images=settings.max_images,
                settings=settings,
            )
            descriptions: list[ImageDescription] = []
            if refs:
                descriptions = await describe_all(
                    vision_client,
                    refs,
                    max_bytes=settings.image_max_bytes,
                    timeout=settings.request_timeout_s,
                    concurrency=settings.describe_concurrency,
                    settings=settings,
                )
            final_md = replace_images_in_markdown(
                markdown, descriptions, settings
            )
            resp = CrawlResponse(
                url=url,
                markdown=final_md,
                images=descriptions,
                metadata=metadata,
            )
            if span is not None:
                span.update(
                    output={
                        "url": url,
                        "markdown_len": len(final_md),
                        "images": len(descriptions),
                    }
                )
    except Exception:
        logger.exception("End run_crawl (failed) url=%s", url)
        raise
    else:
        logger.info("End run_crawl url=%s images=%d", url, len(resp.images))
        return resp