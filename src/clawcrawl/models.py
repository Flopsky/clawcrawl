"""API and LLM structured output models."""

from pydantic import BaseModel, Field, HttpUrl


class ImageRef(BaseModel):
    """A single image reference found in markdown."""

    url: str = Field(..., description="Absolute image URL")
    alt: str | None = Field(None, description="Alt text if present")
    source: str = Field(
        "markdown",
        description="How it appeared: markdown, html, or bare_url",
    )


class MarkdownImageLinks(BaseModel):
    """LLM output: all image URLs in the page markdown."""

    images: list[ImageRef] = Field(default_factory=list)


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


class CrawlResponse(BaseModel):
    """Successful crawl result."""

    url: str
    markdown: str
    images: list[ImageDescription]
    metadata: dict = Field(default_factory=dict)