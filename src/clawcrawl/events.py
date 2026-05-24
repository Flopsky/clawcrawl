"""Crawl progress events for streaming clients."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

from clawcrawl.models import CrawlResponse

CrawlEventType = Literal[
    "crawl_started",
    "scrape_started",
    "scrape_done",
    "extract_started",
    "extract_done",
    "describe_started",
    "describe_progress",
    "replace_started",
    "replace_done",
    "crawl_done",
    "crawl_error",
]

EventCallback = Callable[["CrawlEvent"], Awaitable[None] | None]


class CrawlEvent(BaseModel):
    """A single progress event emitted during a crawl."""

    type: CrawlEventType
    data: dict[str, Any] = Field(default_factory=dict)


async def emit(
    callback: EventCallback | None,
    event_type: CrawlEventType,
    **data: Any,
) -> None:
    """Invoke the event callback if present."""
    if callback is None:
        return
    event = CrawlEvent(type=event_type, data=data)
    result = callback(event)
    if result is not None:
        await result


def crawl_done_event(response: CrawlResponse) -> CrawlEvent:
    """Build the terminal success event."""
    return CrawlEvent(
        type="crawl_done",
        data={"result": response.model_dump()},
    )


def crawl_error_event(step: str, message: str) -> CrawlEvent:
    """Build the terminal failure event."""
    return CrawlEvent(type="crawl_error", data={"step": step, "message": message})
