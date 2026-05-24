"""Extract image URLs from markdown using Instructor."""

import logging
import re

from clawcrawl.config import Settings
from clawcrawl.llm.client import OPENROUTER_EXTRA
from clawcrawl.prompts import load_prompt, render_prompt
from clawcrawl.models import ImageRef, MarkdownImageLinks
from clawcrawl.telemetry.langfuse import llm_generation, pipeline_span
from clawcrawl.telemetry.llm_obs import complete_llm_generation

logger = logging.getLogger(__name__)

_MD_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_HTML_IMG = re.compile(
    r'<img[^>]+src=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def _regex_refs(markdown: str) -> list[ImageRef]:
    logger.info("Start _regex_refs")
    refs: list[ImageRef] = []
    for alt, url in _MD_IMG.findall(markdown):
        refs.append(ImageRef(url=url.strip(), alt=alt or None, source="markdown"))
    for url in _HTML_IMG.findall(markdown):
        refs.append(ImageRef(url=url.strip(), source="html"))
    logger.info("End _regex_refs count=%d", len(refs))
    return refs


def _dedupe(refs: list[ImageRef]) -> list[ImageRef]:
    logger.info("Start _dedupe")
    seen: set[str] = set()
    out: list[ImageRef] = []
    for r in refs:
        if r.url not in seen:
            seen.add(r.url)
            out.append(r)
    logger.info("End _dedupe count=%d", len(out))
    return out


async def extract_image_links(
    client,
    markdown: str,
    *,
    max_images: int,
    settings: Settings,
) -> list[ImageRef]:
    """Use LLM plus regex hints to list image URLs in markdown."""
    logger.info("Start extract_image_links max_images=%d", max_images)
    span = None
    out: list[ImageRef] = []
    try:
        with pipeline_span(
            "extract_image_links",
            settings=settings,
            input={"max_images": max_images, "markdown_len": len(markdown)},
        ) as span:
            hints = _dedupe(_regex_refs(markdown))
            hint_block = (
                "\n".join(f"- {h.url}" for h in hints[: max_images * 2]) or "(none)"
            )
            messages = [
                {
                    "role": "system",
                    "content": load_prompt("extract_image_links", "system"),
                },
                {
                    "role": "user",
                    "content": render_prompt(
                        "extract_image_links",
                        "user",
                        hint_block=hint_block,
                        markdown=markdown[:120000],
                    ),
                },
            ]
            with llm_generation(
                "extract_image_links.llm",
                settings=settings,
                model=settings.text_model,
                messages=messages,
            ) as gen:
                result, raw = await client.create_with_completion(
                    messages=messages,
                    response_model=MarkdownImageLinks,
                    extra_body=OPENROUTER_EXTRA,
                )
                complete_llm_generation(
                    gen,
                    output=result.model_dump(),
                    raw_response=raw,
                )
            merged = _dedupe(list(result.images) + hints)
            out = merged[:max_images]
            if span is not None:
                span.update(
                    output={"count": len(out), "urls": [r.url for r in out]}
                )
    except Exception:
        logger.exception("End extract_image_links (failed)")
        raise
    else:
        logger.info("End extract_image_links count=%d", len(out))
        return out