"""Tests for Pydantic model coercion."""

import pytest

from clawcrawl.models import ImageRef, MarkdownImageLinks


def test_markdown_image_links_coerces_url_strings():
    payload = {
        "images": [
            "https://example.com/a.png",
            {"url": "https://example.com/b.jpg", "alt": "B"},
        ],
    }
    parsed = MarkdownImageLinks.model_validate(payload)
    assert len(parsed.images) == 2
    assert parsed.images[0] == ImageRef(
        url="https://example.com/a.png", alt=None, source="markdown"
    )
    assert parsed.images[1].url == "https://example.com/b.jpg"
    assert parsed.images[1].alt == "B"


def test_markdown_image_links_empty():
    assert MarkdownImageLinks.model_validate({"images": []}).images == []


def test_markdown_image_links_invalid_raises():
    with pytest.raises(ValueError):
        MarkdownImageLinks.model_validate({"images": [123]})
