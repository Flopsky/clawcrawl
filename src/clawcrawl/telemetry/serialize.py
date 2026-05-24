"""JSON-safe serialization for Langfuse payloads."""

from __future__ import annotations

import json
from typing import Any


def safe_json(value: Any, *, max_str: int = 8000) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        return value if len(value) <= max_str else value[:max_str] + "…"
    if hasattr(value, "model_dump"):
        return safe_json(value.model_dump(), max_str=max_str)
    if isinstance(value, list):
        return [safe_json(v, max_str=max_str) for v in value[:200]]
    if isinstance(value, dict):
        out = {}
        for k, v in list(value.items())[:100]:
            out[str(k)] = safe_json(v, max_str=max_str)
        return out
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)[:max_str]
