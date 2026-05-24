"""Tests for SSE crawl stream endpoint."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from clawcrawl.main import app
from clawcrawl.models import CrawlResponse


@pytest.fixture
def settings_env(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setenv("CLAWCRAWL_LANGFUSE_ENABLED", "false")


@pytest.fixture
def client(settings_env):
    return TestClient(app)


def test_crawl_stream_first_event(client, monkeypatch):
    expected = CrawlResponse(
        url="https://example.com",
        markdown="# hi",
        images=[],
        metadata={},
    )
    events_seen: list[str] = []
    captured: dict = {}

    async def fake_crawl(url, *, settings=None, on_event=None):
        captured["text_model"] = settings.text_model if settings else None
        if on_event is not None:
            from clawcrawl.events import crawl_done_event, emit

            await emit(on_event, "crawl_started", url=url)
            await on_event(crawl_done_event(expected))
        return expected

    monkeypatch.setattr("clawcrawl.main.crawl", fake_crawl)

    with client.stream(
        "POST",
        "/v1/crawl/stream",
        json={
            "url": "https://example.com",
            "text_model": "openrouter/custom/text",
        },
    ) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        first_line = next(response.iter_lines())
        assert first_line.startswith("data: ")
        payload = json.loads(first_line.removeprefix("data: "))
        events_seen.append(payload["type"])

    assert events_seen[0] == "crawl_started"
    assert captured["text_model"] == "openrouter/custom/text"
