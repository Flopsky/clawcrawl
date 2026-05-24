"""Langfuse helpers for LLM generations (prompts, tokens, cost)."""

from __future__ import annotations

from typing import Any

from clawcrawl.telemetry.serialize import safe_json


def messages_for_langfuse(messages: list[Any]) -> list[dict[str, Any]]:
    """Serialize chat messages for Langfuse (text + image URLs, no binary)."""
    out: list[dict[str, Any]] = []
    for msg in messages:
        if not isinstance(msg, dict):
            out.append({"role": "user", "content": str(msg)})
            continue
        role = str(msg.get("role", "user"))
        content = msg.get("content")
        if isinstance(content, list):
            parts: list[Any] = []
            for part in content:
                if isinstance(part, str):
                    parts.append({"type": "text", "text": part})
                elif isinstance(part, dict):
                    parts.append(part)
                elif hasattr(part, "source"):
                    parts.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": str(part.source)},
                        }
                    )
                else:
                    parts.append({"type": "text", "text": str(part)})
            out.append({"role": role, "content": parts})
        else:
            out.append({"role": role, "content": content})
    return out


def usage_and_cost_from_response(
    raw_response: Any,
) -> tuple[dict[str, int] | None, dict[str, float] | None]:
    """Map OpenAI/OpenRouter completion usage to Langfuse usage_details / cost_details."""
    if raw_response is None:
        return None, None
    usage = getattr(raw_response, "usage", None)
    if usage is None:
        return None, None

    if hasattr(usage, "model_dump"):
        data: dict[str, Any] = usage.model_dump(exclude_none=True)
    elif isinstance(usage, dict):
        data = usage
    else:
        data = {k: v for k, v in usage.__dict__.items() if v is not None}

    usage_details: dict[str, int] = {}
    if (prompt := data.get("prompt_tokens")) is not None:
        usage_details["input"] = int(prompt)
    if (completion := data.get("completion_tokens")) is not None:
        usage_details["output"] = int(completion)
    if (total := data.get("total_tokens")) is not None:
        usage_details["total"] = int(total)

    cost_details: dict[str, float] | None = None
    if (cost := data.get("cost")) is not None:
        cost_details = {"total": float(cost)}
    cost_breakdown = data.get("cost_details")
    if isinstance(cost_breakdown, dict):
        merged = cost_details or {}
        for key, value in cost_breakdown.items():
            if value is not None:
                merged[str(key)] = float(value)
        cost_details = merged or None

    return (usage_details or None), cost_details


def complete_llm_generation(
    gen: Any,
    *,
    output: Any,
    raw_response: Any = None,
) -> None:
    """Attach structured output, token usage, and cost to a Langfuse generation."""
    if gen is None:
        return
    usage_details, cost_details = usage_and_cost_from_response(raw_response)
    kwargs: dict[str, Any] = {"output": safe_json(output)}
    if usage_details:
        kwargs["usage_details"] = usage_details
    if cost_details:
        kwargs["cost_details"] = cost_details
    gen.update(**kwargs)
