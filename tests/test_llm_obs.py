from types import SimpleNamespace

from clawcrawl.telemetry.llm_obs import (
    complete_llm_generation,
    messages_for_langfuse,
    usage_and_cost_from_response,
)


def test_messages_for_langfuse_system_and_user():
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"},
    ]
    out = messages_for_langfuse(messages)
    assert out[0] == {"role": "system", "content": "You are helpful."}
    assert out[1] == {"role": "user", "content": "Hello"}


def test_messages_for_langfuse_image_url():
    image = SimpleNamespace(source="https://example.com/a.png")
    messages = [
        {
            "role": "user",
            "content": ["describe", image],
        },
    ]
    out = messages_for_langfuse(messages)
    assert out[0]["content"][1] == {
        "type": "image_url",
        "image_url": {"url": "https://example.com/a.png"},
    }


def test_usage_and_cost_from_response():
    raw = SimpleNamespace(
        usage=SimpleNamespace(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            cost=0.0025,
            model_dump=lambda **_: {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
                "cost": 0.0025,
            },
        )
    )
    usage, cost = usage_and_cost_from_response(raw)
    assert usage == {"input": 10, "output": 5, "total": 15}
    assert cost == {"total": 0.0025}


def test_complete_llm_generation_noop_when_disabled():
    complete_llm_generation(None, output={"ok": True}, raw_response=None)
