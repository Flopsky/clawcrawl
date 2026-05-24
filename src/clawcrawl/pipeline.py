"""End-to-end crawl pipeline."""

from __future__ import annotations

import asyncio
import logging

from clawcrawl.config import Settings
from clawcrawl.events import EventCallback, crawl_done_event, crawl_error_event, emit
from clawcrawl.llm.client import build_text_client, build_vision_client
from clawcrawl.models import CrawlResponse, ImageDescription
from clawcrawl.services.describe import describe_all
from clawcrawl.services.image_links import extract_image_links
from clawcrawl.services.replace import replace_images_in_markdown
from clawcrawl.services.scrape import scrape_markdown
from clawcrawl.telemetry.langfuse import pipeline_span

logger = logging.getLogger(__name__)


async def run_crawl(
    url: str,
    settings: Settings,
    *,
    on_event: EventCallback | None = None,
) -> CrawlResponse:
    """Scrape, extract images, describe, and rewrite markdown."""
    logger.info("Start run_crawl url=%s", url)
    span = None
    step = "crawl"
    try:
        await emit(on_event, "crawl_started", url=url)
        with pipeline_span("run_crawl", settings=settings, input={"url": url}) as span:
            step = "scrape"
            await emit(on_event, "scrape_started", url=url)
            if on_event is not None:
                markdown, metadata = await asyncio.to_thread(
                    scrape_markdown, url, settings
                )
            else:
                markdown, metadata = scrape_markdown(url, settings)
            await emit(
                on_event,
                "scrape_done",
                markdown_len=len(markdown),
                metadata_keys=list(metadata.keys()) if metadata else [],
            )

            text_client = build_text_client(settings)
            vision_client = build_vision_client(settings)

            step = "extract"
            await emit(on_event, "extract_started")
            refs = await extract_image_links(
                text_client,
                markdown,
                max_images=settings.max_images,
                settings=settings,
            )
            urls = [r.url for r in refs]
            await emit(
                on_event,
                "extract_done",
                count=len(refs),
                urls=urls[:20],
            )

            descriptions: list[ImageDescription] = []
            if refs:
                step = "describe"

                async def on_describe_progress(
                    index: int, total: int, image_url: str, ok: bool
                ) -> None:
                    await emit(
                        on_event,
                        "describe_progress",
                        index=index,
                        total=total,
                        url=image_url,
                        ok=ok,
                    )

                async def _describe_started(total: int) -> None:
                    await emit(on_event, "describe_started", total=total)

                descriptions = await describe_all(
                    vision_client,
                    refs,
                    max_bytes=settings.image_max_bytes,
                    timeout=settings.request_timeout_s,
                    concurrency=settings.describe_concurrency,
                    settings=settings,
                    on_started=_describe_started,
                    on_progress=on_describe_progress,
                )

            step = "replace"
            await emit(on_event, "replace_started")
            final_md = replace_images_in_markdown(
                markdown, descriptions, settings
            )
            await emit(
                on_event,
                "replace_done",
                markdown_len=len(final_md),
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
    except Exception as exc:
        logger.exception("End run_crawl (failed) url=%s", url)
        if on_event is not None:
            result = on_event(crawl_error_event(step, str(exc)))
            if result is not None:
                await result
        raise
    else:
        logger.info("End run_crawl url=%s images=%d", url, len(resp.images))
        if on_event is not None:
            result = on_event(crawl_done_event(resp))
            if result is not None:
                await result
        return resp
