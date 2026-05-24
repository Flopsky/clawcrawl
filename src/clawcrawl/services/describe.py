"""Describe images with a multimodal Instructor call."""

import asyncio
import json
import logging

import httpx
from instructor.processing.multimodal import Image

from clawcrawl.config import Settings
from clawcrawl.llm.client import OPENROUTER_EXTRA
from clawcrawl.prompts import load_prompt, render_prompt
from clawcrawl.models import ImageDescription, ImageRef
from clawcrawl.telemetry.langfuse import llm_generation, pipeline_span
from clawcrawl.telemetry.llm_obs import complete_llm_generation

logger = logging.getLogger(__name__)


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
) -> list[ImageDescription]:
    """Describe images with bounded concurrency."""
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
    try:
        with pipeline_span(
            "describe_all",
            settings=settings,
            input={"count": len(refs), "concurrency": concurrency},
        ) as span:
            results = await asyncio.gather(*[run(r) for r in refs])
            if span is not None:
                span.update(output={"count": len(results)})
    except Exception:
        logger.exception("End describe_all (failed)")
        raise
    else:
        logger.info("End describe_all count=%d", len(results))
        return results