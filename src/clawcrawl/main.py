"""FastAPI application."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from clawcrawl.api import crawl
from clawcrawl.config import Settings, get_settings, resolve_settings
from clawcrawl.events import CrawlEvent
from clawcrawl.log import setup_logging
from clawcrawl.models import CrawlRequest, CrawlResponse

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="clawcrawl", version="0.1.0")

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _settings_for_request(body: CrawlRequest) -> Settings:
    return resolve_settings(
        text_model=body.text_model,
        vision_model=body.vision_model,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    logger.info("Start health")
    logger.info("End health")
    return {"status": "ok"}


@app.get("/v1/models")
async def list_models(
    output_modalities: str = Query(default="text"),
) -> dict[str, Any]:
    """Proxy OpenRouter model list (API key stays server-side)."""
    settings = get_settings()
    url = f"{settings.openrouter_base_url.rstrip('/')}/models"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                url,
                params={"output_modalities": output_modalities},
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                },
            )
            resp.raise_for_status()
            payload = resp.json()
    except httpx.HTTPError as exc:
        logger.exception("OpenRouter models fetch failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    data = payload.get("data", [])
    slim = []
    for item in data:
        arch = item.get("architecture") or {}
        slim.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "architecture": {
                    "input_modalities": arch.get("input_modalities"),
                    "output_modalities": arch.get("output_modalities"),
                },
            }
        )
    return {"data": slim}


@app.post("/v1/crawl", response_model=CrawlResponse)
async def crawl_endpoint(body: CrawlRequest) -> CrawlResponse:
    """Crawl URL and return markdown with image descriptions inlined."""
    settings = _settings_for_request(body)
    try:
        return await crawl(str(body.url), settings=settings)
    except ValueError as exc:
        logger.exception("End crawl (failed) url=%s", body.url)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("End crawl (failed) url=%s", body.url)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


async def _crawl_event_stream(body: CrawlRequest) -> AsyncIterator[str]:
    """Yield SSE frames for each crawl progress event."""
    settings = _settings_for_request(body)
    queue: asyncio.Queue[CrawlEvent | None] = asyncio.Queue()

    async def on_event(event: CrawlEvent) -> None:
        await queue.put(event)

    async def run_crawl_task() -> None:
        try:
            await crawl(str(body.url), settings=settings, on_event=on_event)
        except Exception:
            logger.exception("Stream crawl failed url=%s", body.url)
        finally:
            await queue.put(None)

    task = asyncio.create_task(run_crawl_task())
    try:
        while True:
            event = await queue.get()
            if event is None:
                break
            payload = json.dumps(event.model_dump(), default=str)
            yield f"data: {payload}\n\n"
    finally:
        await task


@app.post("/v1/crawl/stream")
async def crawl_stream_endpoint(body: CrawlRequest) -> StreamingResponse:
    """Stream crawl progress as Server-Sent Events."""
    return StreamingResponse(
        _crawl_event_stream(body),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
