"""Replace image URLs in markdown with description blocks."""

import json
import logging
import re

from clawcrawl.config import Settings
from clawcrawl.models import ImageDescription
from clawcrawl.telemetry.langfuse import pipeline_span

logger = logging.getLogger(__name__)

_MD_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_HTML_IMG = re.compile(
    r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
    re.IGNORECASE,
)


def _block(desc: ImageDescription) -> str:
    logger.info("Start _block url=%s", desc.url)
    payload = desc.model_dump()
    compact = json.dumps(payload, ensure_ascii=False)
    short = desc.description.replace("\n", " ").strip()[:500]
    block = f"<!-- image-desc:{compact} -->\n*[Image: {short}]*"
    logger.info("End _block url=%s", desc.url)
    return block


def replace_images_in_markdown(
    markdown: str,
    descriptions: list[ImageDescription],
    settings: Settings,
) -> str:
    """Substitute image references with structured description blocks."""
    logger.info(
        "Start replace_images_in_markdown descriptions=%d",
        len(descriptions),
    )
    with pipeline_span(
        "replace_images_in_markdown",
        settings=settings,
        input={
            "markdown_len": len(markdown),
            "descriptions": len(descriptions),
        },
    ) as span:
        by_url = {d.url: d for d in descriptions}
        urls = sorted(by_url.keys(), key=len, reverse=True)
        out = markdown
        for url in urls:
            desc = by_url[url]
            block = _block(desc)

            def md_sub(m: re.Match) -> str:
                if m.group(2).strip() == url:
                    return block
                return m.group(0)

            out = _MD_IMG.sub(md_sub, out)

            def html_sub(m: re.Match) -> str:
                if m.group(1).strip() == url:
                    return block
                return m.group(0)

            out = _HTML_IMG.sub(html_sub, out)
        if span is not None:
            span.update(output={"markdown_len": len(out)})
    logger.info("End replace_images_in_markdown len=%d", len(out))
    return out