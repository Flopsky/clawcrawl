"""FastAPI application."""

import logging

from fastapi import FastAPI, HTTPException

from clawcrawl.api import crawl
from clawcrawl.config import get_settings
from clawcrawl.log import setup_logging
from clawcrawl.models import CrawlRequest, CrawlResponse

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="clawcrawl", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    logger.info("Start health")
    logger.info("End health")
    return {"status": "ok"}


@app.post("/v1/crawl", response_model=CrawlResponse)
async def crawl_endpoint(body: CrawlRequest) -> CrawlResponse:
    """Crawl URL and return markdown with image descriptions inlined."""
    settings = get_settings()
    try:
        return await crawl(str(body.url), settings=settings)
    except ValueError as exc:
        logger.exception("End crawl (failed) url=%s", body.url)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("End crawl (failed) url=%s", body.url)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
