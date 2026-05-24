"""Application settings loaded from environment."""

import logging
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Runtime configuration for clawcrawl."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    firecrawl_api_key: str
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    text_model: str = Field(
        default="openrouter/google/gemini-2.0-flash-lite-001",
        validation_alias="CLAWCRAWL_TEXT_MODEL",
    )
    vision_model: str = Field(
        default="openrouter/google/gemma-3-27b-it",
        validation_alias="CLAWCRAWL_VISION_MODEL",
    )
    max_images: int = Field(default=30, validation_alias="CLAWCRAWL_MAX_IMAGES")
    image_max_bytes: int = Field(
        default=5_242_880,
        validation_alias="CLAWCRAWL_IMAGE_MAX_BYTES",
    )
    request_timeout_s: float = Field(
        default=120.0,
        validation_alias="CLAWCRAWL_REQUEST_TIMEOUT_S",
    )
    describe_concurrency: int = Field(
        default=5,
        validation_alias="CLAWCRAWL_DESCRIBE_CONCURRENCY",
    )
    langfuse_enabled: bool = Field(
        default=True,
        validation_alias="CLAWCRAWL_LANGFUSE_ENABLED",
    )
    langfuse_public_key: str | None = Field(
        default=None,
        validation_alias="LANGFUSE_PUBLIC_KEY",
    )
    langfuse_secret_key: str | None = Field(
        default=None,
        validation_alias="LANGFUSE_SECRET_KEY",
    )
    langfuse_base_url: str = Field(
        default="https://cloud.langfuse.com",
        validation_alias="LANGFUSE_BASE_URL",
    )


def sync_langfuse_env(settings: Settings) -> None:
    """Expose Langfuse credentials to the SDK (reads os.environ, not Settings)."""
    if settings.langfuse_public_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
    if settings.langfuse_secret_key:
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
    os.environ["LANGFUSE_BASE_URL"] = settings.langfuse_base_url


def get_settings() -> Settings:
    """Return settings instance."""
    logger.info("Start get_settings")
    settings = Settings()
    sync_langfuse_env(settings)
    logger.info("End get_settings")
    return settings