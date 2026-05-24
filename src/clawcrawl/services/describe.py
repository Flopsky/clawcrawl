"""Describe images with a multimodal Instructor call."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

import httpx
from instructor.processing.multimodal import Image

from clawcrawl.config import Settings
from clawcrawl.llm.client import OPENROUTER_EXTRA
from clawcrawl.models import ImageDescription, ImageRef
from clawcrawl.services.image_filter import filter_describable_refs
from clawcrawl.services.image_urls import dedupe_image_refs
from clawcrawl.url_sanitize import sanitize_image_url
from clawcrawl.prompts import load_prompt, render_prompt
from clawcrawl.telemetry.langfuse import llm_generation, pipeline_span
from clawcrawl.telemetry.llm_obs import complete_llm_generation

logger = logging.getLogger(__name__)

OnDescribeStarted = Callable[[int], Awaitable[None]]
OnDescribeProgress = Callable[[int, int, str, bool], Awaitable[None]]


async def _fetch_image(url: str, max_bytes: int, timeout: float) -> None:
    logger.info("Start _fetch_image url=%s", url)
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as http:
            async with http.stream("GET", url) as resp:
                resp.raise_for_status()
                size = 0
                async for chunk in resp.aiter_bytes():
                    size += len(chunk)
                    if size > max_bytes:
                        raise ValueError(f"Image too large: {url}")
        logger.info("End _fetch_image url=%s", url)
    except Exception:
        logger.exception("End _fetch_image (failed) url=%s", url)
        raise


def _description_ok(desc: ImageDescription) -> bool:
    try:
        payload = json.loads(desc.description)
        return payload.get("_meta", {}).get("type") != "error"
    except json.JSONDecodeError:
        return True


async def describe_one(
    client,
    ref: ImageRef,
    *,
    max_bytes: int,
    timeout: float,
    settings: Settings,
) -> ImageDescription:
    """Download-check then vision-describe a single image."""
    logger.info("Start describe_one url=%s", ref.url)
    span = None
    desc: ImageDescription
    try:
        with pipeline_span(
            "describe_one", settings=settings, input=ref.model_dump()
        ) as span:
            await _fetch_image(ref.url, max_bytes, timeout)
            messages = [
                {
                    "role": "system",
                    "content": load_prompt("describe_one", "system"),
                },
                {
                    "role": "user",
                    "content": [
                        render_prompt(
                            "describe_one", "user", image_url=ref.url
                        ),
                        Image.from_url(ref.url),
                    ],
                },
            ]
            with llm_generation(
                "describe_one.llm",
                settings=settings,
                model=settings.vision_model,
                messages=messages,
            ) as gen:
                desc, raw = await client.create_with_completion(
                    messages=messages,
                    response_model=ImageDescription,
                    extra_body=OPENROUTER_EXTRA,
                )
                complete_llm_generation(
                    gen,
                    output=desc.model_dump(),
                    raw_response=raw,
                )
            if not desc.url:
                desc = desc.model_copy(update={"url": ref.url})
            if span is not None:
                span.update(output=desc.model_dump())
    except Exception:
        logger.exception("End describe_one (failed) url=%s", ref.url)
        raise
    else:
        logger.info("End describe_one url=%s", ref.url)
        return desc


async def describe_all(
    client,
    refs: list[ImageRef],
    *,
    max_bytes: int,
    timeout: float,
    concurrency: int,
    settings: Settings,
    on_started: OnDescribeStarted | None = None,
    on_progress: OnDescribeProgress | None = None,
) -> list[ImageDescription]:
    """Describe images with bounded concurrency."""
    refs = dedupe_image_refs(filter_describable_refs(refs))
    logger.info(
        "Start describe_all count=%d concurrency=%d",
        len(refs),
        concurrency,
    )
    sem = asyncio.Semaphore(concurrency)

    async def run(ref: ImageRef) -> ImageDescription:
        async with sem:
            try:
                return await describe_one(
                    client,
                    ref,
                    max_bytes=max_bytes,
                    timeout=timeout,
                    settings=settings,
                )
            except Exception as exc:
                logger.warning(
                    "describe_one fallback url=%s error=%s", ref.url, exc
                )
                return ImageDescription(
                    url=ref.url,
                    description=json.dumps(
                        {
                            "_meta": {"type": "error"},
                            "data": {"message": str(exc)},
                        },
                        ensure_ascii=False,
                    ),
                )

    span = None
    results: list[ImageDescription] = []
    total = len(refs)
    try:
        with pipeline_span(
            "describe_all",
            settings=settings,
            input={"count": total, "concurrency": concurrency},
        ) as span:
            if on_started is not None:
                await on_started(total)

            if on_progress is None:
                results = await asyncio.gather(*[run(r) for r in refs])
            else:
                by_url: dict[str, ImageDescription] = {}
                tasks = [asyncio.create_task(run(r)) for r in refs]
                completed = 0
                for task in asyncio.as_completed(tasks):
                    desc = await task
                    completed += 1
                    key = sanitize_image_url(desc.url) or desc.url
                    by_url[key] = (
                        desc
                        if desc.url == key
                        else desc.model_copy(update={"url": key})
                    )
                    await on_progress(
                        completed,
                        total,
                        key,
                        _description_ok(desc),
                    )
                results = []
                for r in refs:
                    key = r.url
                    if key in by_url:
                        results.append(by_url[key])
                    else:
                        logger.warning(
                            "describe_all missing result for url=%s", r.url
                        )

            if span is not None:
                span.update(output={"count": len(results)})
    except Exception:
        logger.exception("End describe_all (failed)")
        raise
    else:
        logger.info("End describe_all count=%d", len(results))
        return results
