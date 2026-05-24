"""Tests for crawl progress events."""

from __future__ import annotations

import json

import pytest

from clawcrawl.config import Settings
from clawcrawl.models import CrawlResponse, ImageDescription, ImageRef
from clawcrawl.pipeline import run_crawl


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setenv("CLAWCRAWL_LANGFUSE_ENABLED", "false")
    return Settings()


@pytest.mark.asyncio
async def test_run_crawl_emits_ordered_events(settings, monkeypatch):
    refs = [
        ImageRef(url="https://example.com/a.png", alt="a"),
        ImageRef(url="https://example.com/b.png", alt="b"),
    ]
    descriptions = [
        ImageDescription(url=r.url, description='{"_meta":{"type":"photo"}}')
        for r in refs
    ]

    monkeypatch.setattr(
        "clawcrawl.pipeline.scrape_markdown",
        lambda url, s: ("# page", {"title": "T"}),
    )
    monkeypatch.setattr(
        "clawcrawl.pipeline.build_text_client",
        lambda s: object(),
    )
    monkeypatch.setattr(
        "clawcrawl.pipeline.build_vision_client",
        lambda s: object(),
    )

    async def fake_extract(*_args, **_kwargs):
        return refs

    monkeypatch.setattr(
        "clawcrawl.pipeline.extract_image_links",
        fake_extract,
    )

    progress_calls: list[tuple[int, int]] = []

    async def fake_describe_all(*_args, on_started=None, on_progress=None, **_kw):
        if on_started:
            await on_started(len(refs))
        for i, desc in enumerate(descriptions, start=1):
            if on_progress:
                await on_progress(i, len(refs), desc.url, True)
        return descriptions

    monkeypatch.setattr(
        "clawcrawl.pipeline.describe_all",
        fake_describe_all,
    )
    monkeypatch.setattr(
        "clawcrawl.pipeline.replace_images_in_markdown",
        lambda md, descs, s: "# done",
    )

    events: list[str] = []

    async def on_event(event):
        events.append(event.type)

    result = await run_crawl(
        "https://example.com",
        settings,
        on_event=on_event,
    )

    assert result.markdown == "# done"
    assert events == [
        "crawl_started",
        "scrape_started",
        "scrape_done",
        "extract_started",
        "extract_done",
        "describe_started",
        "describe_progress",
        "describe_progress",
        "replace_started",
        "replace_done",
        "crawl_done",
    ]


@pytest.mark.asyncio
async def test_run_crawl_emits_error_event(settings, monkeypatch):
    def fail_scrape(url, s):
        raise ValueError("scrape failed")

    monkeypatch.setattr("clawcrawl.pipeline.scrape_markdown", fail_scrape)

    errors: list[dict] = []

    async def on_event(event):
        if event.type == "crawl_error":
            errors.append(event.data)

    with pytest.raises(ValueError, match="scrape failed"):
        await run_crawl(
            "https://example.com",
            settings,
            on_event=on_event,
        )

    assert errors == [{"step": "scrape", "message": "scrape failed"}]
