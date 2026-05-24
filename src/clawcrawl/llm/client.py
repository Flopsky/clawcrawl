"""Instructor clients routed through OpenRouter."""

import logging
import os

import instructor

from clawcrawl.config import Settings

logger = logging.getLogger(__name__)

OPENROUTER_EXTRA = {"provider": {"require_parameters": True}}


def openrouter_model_id(model: str) -> str:
    """Ensure Instructor routes via OpenRouter, not a native provider SDK."""
    if model.startswith("openrouter/"):
        return model
    return f"openrouter/{model}"


def build_text_client(settings: Settings, *, async_client: bool = True):
    """Text-only structured extractions."""
    model = openrouter_model_id(settings.text_model)
    logger.info("Start build_text_client model=%s", model)
    os.environ.setdefault("OPENAI_API_KEY", settings.openrouter_api_key)
    client = instructor.from_provider(
        model,
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        async_client=async_client,
    )
    logger.info("End build_text_client")
    return client


def build_vision_client(settings: Settings, *, async_client: bool = True):
    """Multimodal structured extractions."""
    model = openrouter_model_id(settings.vision_model)
    logger.info("Start build_vision_client model=%s", model)
    os.environ.setdefault("OPENAI_API_KEY", settings.openrouter_api_key)
    client = instructor.from_provider(
        model,
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        async_client=async_client,
    )
    logger.info("End build_vision_client")
    return client