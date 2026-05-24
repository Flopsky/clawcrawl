"""Tests for image URL sanitization."""

import pytest

from clawcrawl.models import ImageRef, MarkdownImageLinks
from clawcrawl.services.image_urls import dedupe_image_refs
from clawcrawl.url_sanitize import sanitize_image_url


@pytest.mark.parametrize(
    "raw,expected",
    [
        (
            "https://example.com/a.png?w=90&fm=webp', alt: ",
            "https://example.com/a.png?w=90&fm=webp",
        ),
        (
            "https://i.vimeocdn.com/video/x-d?mw=80&q=85', alt: ",
            "https://i.vimeocdn.com/video/x-d?mw=80&q=85",
        ),
        (
            "  https://cdn.test/icon.svg?q=1  ",
            "https://cdn.test/icon.svg?q=1",
        ),
    ],
)
def test_sanitize_strips_garbage(raw: str, expected: str):
    assert sanitize_image_url(raw) == expected


def test_dedupe_collapses_malformed_and_clean_duplicate():
    refs = [
        ImageRef(
            url="https://i.vimeocdn.com/video/x-d?mw=80&q=85', alt: ",
            source="markdown",
        ),
        ImageRef(url="https://i.vimeocdn.com/video/x-d?mw=80&q=85", source="markdown"),
    ]
    out = dedupe_image_refs(refs)
    assert len(out) == 1
    assert out[0].url == "https://i.vimeocdn.com/video/x-d?mw=80&q=85"


def test_markdown_image_links_skips_invalid_strings():
    parsed = MarkdownImageLinks.model_validate(
        {
            "images": [
                "not a url",
                "https://example.com/ok.png', alt: ",
            ]
        }
    )
    assert len(parsed.images) == 1
    assert parsed.images[0].url == "https://example.com/ok.png"
