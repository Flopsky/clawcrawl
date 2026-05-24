"""Tests for SVG / vector image filtering."""

import pytest

from clawcrawl.models import ImageRef
from clawcrawl.services.image_filter import (
    filter_describable_refs,
    is_vector_image_url,
    should_describe_image_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://cdn.example.com/Light_Mode.svg?w=3840&q=90",
        "https://example.com/icon.SVG",
        "https://example.com/assets/logo.svgz",
        "data:image/svg+xml;base64,PHN2Zy8+",
    ],
)
def test_vector_urls_detected(url: str):
    assert is_vector_image_url(url)
    assert not should_describe_image_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://images.ctfassets.net/foo/1_1.png?w=3840&q=90&fm=webp",
        "https://example.com/photo.jpg",
        "https://i.vimeocdn.com/video/2159667619-d?mw=80&q=85",
    ],
)
def test_raster_urls_kept(url: str):
    assert not is_vector_image_url(url)
    assert should_describe_image_url(url)


def test_filter_describable_refs():
    refs = [
        ImageRef(url="https://a.com/x.svg", source="markdown"),
        ImageRef(url="https://a.com/y.png", source="markdown"),
    ]
    out = filter_describable_refs(refs)
    assert len(out) == 1
    assert out[0].url == "https://a.com/y.png"
