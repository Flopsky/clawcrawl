"""API and LLM structured output models."""

from typing import Any, Self, Union

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from clawcrawl.url_sanitize import sanitize_image_url


class ImageRef(BaseModel):
    """A single image reference found in markdown."""

    url: str = Field(..., description="Absolute image URL")
    alt: str | None = Field(None, description="Alt text if present")
    source: str = Field(
        "markdown",
        description="How it appeared: markdown, html, or bare_url",
    )

    @field_validator("url", mode="before")
    @classmethod
    def clean_url(cls, value: object) -> str:
        """Strip garbage suffixes some models append to URL strings."""
        if not isinstance(value, str):
            raise TypeError("url must be a string")
        cleaned = sanitize_image_url(value)
        if not cleaned:
            raise ValueError(f"Invalid image URL: {value!r}")
        return cleaned


class MarkdownImageLinks(BaseModel):
    """LLM output: all image URLs in the page markdown."""

    # Union keeps JSON schema compatible with models that return URL strings.
    images: list[Union[str, ImageRef]] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_images(self) -> Self:
        """Normalize to list[ImageRef] for downstream pipeline code."""
        refs: list[ImageRef] = []
        for item in self.images:
            try:
                if isinstance(item, str):
                    refs.append(ImageRef(url=item, alt=None, source="markdown"))
                elif isinstance(item, ImageRef):
                    refs.append(item)
                elif isinstance(item, dict):
                    refs.append(ImageRef.model_validate(item))
            except ValueError:
                continue
        return self.model_copy(update={"images": refs})


class ImageDescription(BaseModel):
    """Vision extraction for one image (JSON-encoded content as text)."""

    url: str = Field(..., description="Image URL")
    description: str = Field(
        ...,
        description=(
            "JSON text with `_meta` and `data` keys encoding the full image "
            "content per the system prompt. No markdown fences or commentary."
        ),
    )


class CrawlRequest(BaseModel):
    """POST /v1/crawl body."""

    url: HttpUrl
    text_model: str | None = Field(
        None,
        description="Override CLAWCRAWL_TEXT_MODEL for image URL extraction",
    )
    vision_model: str | None = Field(
        None,
        description="Override CLAWCRAWL_VISION_MODEL for image description",
    )


class CrawlResponse(BaseModel):
    """Successful crawl result."""

    url: str
    markdown: str
    images: list[ImageDescription]
    metadata: dict = Field(default_factory=dict)
