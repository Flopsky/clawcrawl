"""Tests for settings resolution and models proxy."""

from __future__ import annotations

import pytest

from clawcrawl.config import resolve_settings
from clawcrawl.models import CrawlRequest


@pytest.fixture
def settings_env(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setenv("CLAWCRAWL_LANGFUSE_ENABLED", "false")
    monkeypatch.setenv(
        "CLAWCRAWL_TEXT_MODEL", "openrouter/google/gemini-2.0-flash-lite-001"
    )
    monkeypatch.setenv("CLAWCRAWL_VISION_MODEL", "openrouter/google/gemma-3-27b-it")


def test_resolve_settings_no_overrides(settings_env):
    base = resolve_settings()
    assert base.text_model == "openrouter/google/gemini-2.0-flash-lite-001"
    assert base.vision_model == "openrouter/google/gemma-3-27b-it"


def test_resolve_settings_with_overrides(settings_env):
    resolved = resolve_settings(
        text_model="openrouter/anthropic/claude-3.5-haiku",
        vision_model="openrouter/google/gemma-3-27b-it:free",
    )
    assert resolved.text_model == "openrouter/anthropic/claude-3.5-haiku"
    assert resolved.vision_model == "openrouter/google/gemma-3-27b-it:free"
    assert resolved.firecrawl_api_key


def test_crawl_request_accepts_models(settings_env):
    body = CrawlRequest(
        url="https://example.com",
        text_model="custom/text",
        vision_model="custom/vision",
    )
    resolved = resolve_settings(
        text_model=body.text_model,
        vision_model=body.vision_model,
    )
    assert resolved.text_model == "custom/text"
    assert resolved.vision_model == "custom/vision"


@pytest.mark.asyncio
async def test_list_models_proxy(settings_env, monkeypatch):
    from fastapi.testclient import TestClient

    from clawcrawl.main import app

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "data": [
                    {
                        "id": "google/gemini-2.0-flash-lite-001",
                        "name": "Gemini Flash Lite",
                        "description": "Fast text",
                        "architecture": {
                            "input_modalities": ["text"],
                            "output_modalities": ["text"],
                        },
                    }
                ]
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url, params=None, headers=None):
            assert "models" in url
            assert params == {"output_modalities": "text"}
            assert headers["Authorization"].startswith("Bearer ")
            return FakeResponse()

    monkeypatch.setattr("clawcrawl.main.httpx.AsyncClient", FakeClient)

    client = TestClient(app)
    resp = client.get("/v1/models", params={"output_modalities": "text"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == "google/gemini-2.0-flash-lite-001"
