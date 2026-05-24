import os

from clawcrawl.config import Settings, sync_langfuse_env


def test_sync_langfuse_env(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    settings = Settings(
        firecrawl_api_key="fc",
        openrouter_api_key="or",
        langfuse_public_key="pk-test",
        langfuse_secret_key="sk-test",
        langfuse_base_url="https://langfuse.example",
    )
    sync_langfuse_env(settings)
    assert os.environ["LANGFUSE_PUBLIC_KEY"] == "pk-test"
    assert os.environ["LANGFUSE_SECRET_KEY"] == "sk-test"
    assert os.environ["LANGFUSE_BASE_URL"] == "https://langfuse.example"
