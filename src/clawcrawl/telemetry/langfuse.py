"""Langfuse spans (functions) and generations (LLM calls)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from langfuse import get_client

from clawcrawl.config import Settings
from clawcrawl.telemetry.llm_obs import messages_for_langfuse
from clawcrawl.telemetry.serialize import safe_json


def _lf():
    return get_client()


def tracing_enabled(settings: Settings) -> bool:
    return (
        settings.langfuse_enabled
        and bool(settings.langfuse_public_key)
        and bool(settings.langfuse_secret_key)
    )


@contextmanager
def pipeline_span(
    name: str,
    *,
    settings: Settings,
    input: Any = None,
    metadata: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """One span per function; no-op if Langfuse disabled."""
    if not tracing_enabled(settings):
        yield None
        return
    langfuse = _lf()
    with langfuse.start_as_current_observation(
        as_type="span",
        name=name,
        metadata=metadata or {},
    ) as span:
        if input is not None:
            span.update(input=safe_json(input))
        try:
            yield span
        except Exception as exc:
            span.update(output={"error": str(exc)})
            raise


@contextmanager
def llm_generation(
    name: str,
    *,
    settings: Settings,
    model: str,
    messages: list[Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Nested generation under current span (same function, multiple allowed)."""
    if not tracing_enabled(settings):
        yield None
        return
    langfuse = _lf()
    with langfuse.start_as_current_observation(
        as_type="generation",
        name=name,
        model=model,
        metadata=metadata or {},
    ) as gen:
        if messages is not None:
            gen.update(input=safe_json(messages_for_langfuse(messages)))
        try:
            yield gen
        except Exception as exc:
            gen.update(output={"error": str(exc)})
            raise


def flush_langfuse() -> None:
    _lf().flush()