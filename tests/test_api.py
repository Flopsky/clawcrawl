import pytest

from clawcrawl import crawl, crawl_sync
from clawcrawl.config import Settings
from clawcrawl.models import CrawlResponse


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setenv("CLAWCRAWL_LANGFUSE_ENABLED", "false")
    return Settings()


@pytest.mark.asyncio
async def test_crawl_delegates_to_pipeline(settings, monkeypatch):
    expected = CrawlResponse(
        url="https://example.com",
        markdown="# hi",
        images=[],
        metadata={},
    )

    async def fake_run(
        url: str, s: Settings, *, on_event=None
    ) -> CrawlResponse:
        assert url == "https://example.com"
        assert s is settings
        return expected

    monkeypatch.setattr("clawcrawl.api.run_crawl", fake_run)
    result = await crawl("https://example.com", settings=settings)
    assert result is expected


def test_crawl_sync_delegates(settings, monkeypatch):
    expected = CrawlResponse(
        url="https://example.com",
        markdown="# hi",
        images=[],
        metadata={},
    )

    async def fake_crawl(url: str, *, settings: Settings | None = None):
        return expected

    monkeypatch.setattr("clawcrawl.api.crawl", fake_crawl)
    result = crawl_sync("https://example.com", settings=settings)
    assert result is expected
