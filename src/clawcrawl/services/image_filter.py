"""Filter image URLs that should not be sent to the vision model."""

from __future__ import annotations

import logging
from urllib.parse import unquote, urlparse

from clawcrawl.models import ImageRef

logger = logging.getLogger(__name__)


def is_vector_image_url(url: str) -> bool:
    """Return True when the URL points at SVG/vector artwork."""
    raw = url.strip()
    if not raw:
        return False

    lower = raw.lower()
    if lower.startswith("data:image/svg"):
        return True

    path = unquote(urlparse(raw).path).lower()
    return path.endswith(".svg") or path.endswith(".svgz")


def should_describe_image_url(url: str) -> bool:
    """Return False for SVG URLs we keep unchanged in markdown."""
    return not is_vector_image_url(url)


def filter_describable_refs(refs: list[ImageRef]) -> list[ImageRef]:
    """Drop vector/SVG references before the describe step."""
    kept: list[ImageRef] = []
    skipped = 0
    for ref in refs:
        if should_describe_image_url(ref.url):
            kept.append(ref)
        else:
            skipped += 1
            logger.info("Skip vector image url=%s", ref.url)
    if skipped:
        logger.info("filter_describable_refs skipped=%d kept=%d", skipped, len(kept))
    return kept
