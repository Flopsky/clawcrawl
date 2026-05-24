"""clawcrawl — multi-modal URL crawler."""

from clawcrawl.api import crawl, crawl_sync
from clawcrawl.config import Settings, get_settings
from clawcrawl.models import (
    CrawlRequest,
    CrawlResponse,
    ImageDescription,
    ImageRef,
    MarkdownImageLinks,
)
from clawcrawl.pipeline import run_crawl

__all__ = [
    "CrawlRequest",
    "CrawlResponse",
    "ImageDescription",
    "ImageRef",
    "MarkdownImageLinks",
    "Settings",
    "crawl",
    "crawl_sync",
    "get_settings",
    "run_crawl",
]

__version__ = "0.1.0"
