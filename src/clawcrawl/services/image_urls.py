"""Dedupe image refs after URL sanitization."""

from __future__ import annotations

import logging

from clawcrawl.models import ImageRef
from clawcrawl.url_sanitize import sanitize_image_url

logger = logging.getLogger(__name__)


def normalize_image_ref(ref: ImageRef) -> ImageRef | None:
    """Return ref with cleaned URL, or None if URL is invalid."""
    clean = sanitize_image_url(ref.url)
    if not clean:
        logger.info("Drop invalid image ref url=%r", ref.url[:120])
        return None
    if clean == ref.url:
        return ref
    return ref.model_copy(update={"url": clean})


def dedupe_image_refs(refs: list[ImageRef]) -> list[ImageRef]:
    """Sanitize URLs and dedupe by canonical URL."""
    seen: set[str] = set()
    out: list[ImageRef] = []
    for ref in refs:
        normalized = normalize_image_ref(ref)
        if normalized is None:
            continue
        if normalized.url in seen:
            continue
        seen.add(normalized.url)
        out.append(normalized)
    return out
