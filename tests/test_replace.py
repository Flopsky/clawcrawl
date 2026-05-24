import pytest

from clawcrawl.config import Settings
from clawcrawl.models import ImageDescription
from clawcrawl.services.replace import replace_images_in_markdown


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    monkeypatch.setenv("CLAWCRAWL_LANGFUSE_ENABLED", "false")
    return Settings()


def test_replace_markdown_image(settings):
    md = "Hello ![alt](https://example.com/a.png) world"
    desc = ImageDescription(
        url="https://example.com/a.png",
        description='{"_meta":{"type":"photo"},"data":"A red circle"}',
    )
    out = replace_images_in_markdown(md, [desc], settings)
    assert "image-desc:" in out
    assert "*[Image:" in out
    assert "red circle" in out
    assert "a.png)" not in out