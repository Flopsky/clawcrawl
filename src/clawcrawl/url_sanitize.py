"""Sanitize image URLs parsed from markdown or LLM output."""

from __future__ import annotations

import re
from urllib.parse import urlparse

_GARBAGE_SUFFIX = re.compile(r"['\"]?\s*,\s*alt\s*:.*$", re.IGNORECASE)
_HTTP_URL = re.compile(r"https?://[^\s'\"<>\]]+", re.IGNORECASE)


def sanitize_image_url(raw: str) -> str | None:
    """Extract a valid http(s) URL from messy LLM or markdown text."""
    if not raw or not isinstance(raw, str):
        return None

    s = raw.strip().strip("'\"")
    s = _GARBAGE_SUFFIX.sub("", s).strip().strip("'\"")

    match = _HTTP_URL.search(s)
    if match:
        s = match.group(0)

    s = s.rstrip("',\"")
    if not s:
        return None

    parsed = urlparse(s)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return s
