# clawcrawl

Multi-modal crawler: given a URL, fetch page markdown (Firecrawl), find images, describe them with a vision LLM (OpenRouter via Instructor), and return markdown with structured image descriptions inlined.

## How it works

1. **Scrape** — Firecrawl returns page markdown and metadata.
2. **Extract** — Regex hints plus a text LLM list image URLs (deduped, capped).
3. **Describe** — Vision LLM describes each image (bounded concurrency; per-image failures become fallback text).
4. **Replace** — Image references become `<!-- image-desc:{json} -->` plus `*[Image: …]*`.

Optional **Langfuse** tracing: one span per pipeline step, one generation per LLM call.

## Requirements

- Python 3.11+
- [Firecrawl](https://firecrawl.dev) API key
- [OpenRouter](https://openrouter.ai) API key
- Optional: [Langfuse](https://langfuse.com) keys for observability

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env: FIRECRAWL_API_KEY, OPENROUTER_API_KEY
```

## Configuration

Settings are read from the process environment and from a `.env` file in the project root (via Pydantic Settings). Langfuse keys in `.env` are copied into `os.environ` on each `get_settings()` call so the Langfuse SDK can see them.

| Variable | Description |
|----------|-------------|
| `FIRECRAWL_API_KEY` | Required |
| `OPENROUTER_API_KEY` | Required |
| `CLAWCRAWL_TEXT_MODEL` | Image URL extraction (default: `openrouter/google/gemini-2.0-flash-lite-001`). OpenRouter IDs like `google/gemma-…` are auto-prefixed with `openrouter/`. |
| `CLAWCRAWL_VISION_MODEL` | Image description (default: `openrouter/google/gemma-3-27b-it`). Same `openrouter/` prefix rule. |
| `CLAWCRAWL_MAX_IMAGES` | Max images per crawl (default: `30`) |
| `CLAWCRAWL_IMAGE_MAX_BYTES` | Max download size per image (default: `5242880`) |
| `CLAWCRAWL_REQUEST_TIMEOUT_S` | HTTP timeout for image fetch (default: `120`) |
| `CLAWCRAWL_DESCRIBE_CONCURRENCY` | Parallel vision calls (default: `5`) |
| `LANGFUSE_SECRET_KEY` | Optional; Langfuse project secret |
| `LANGFUSE_PUBLIC_KEY` | Optional; Langfuse public key |
| `LANGFUSE_BASE_URL` | Langfuse host (default: `https://cloud.langfuse.com`) |
| `CLAWCRAWL_LANGFUSE_ENABLED` | Enable tracing (default: `true`; set `false` for tests) |

## Use as a Python library

Install the package (`pip install -e .`), configure `.env` (or export the same variables), then call the crawler from your code. No HTTP server required.

**Async** (recommended):

```python
import asyncio

from clawcrawl import crawl

async def main() -> None:
    result = await crawl("https://example.com")
    print(result.markdown)
    for image in result.images:
        print(image.url, image.description[:200])

asyncio.run(main())
```

**Sync** (scripts, notebooks):

```python
from clawcrawl import crawl_sync

result = crawl_sync("https://example.com")
print(result.markdown)
```

**Custom settings** (skip `.env` or override values):

```python
from clawcrawl import Settings, crawl_sync

settings = Settings(
    firecrawl_api_key="fc-...",
    openrouter_api_key="sk-or-...",
    max_images=10,
    langfuse_enabled=False,
)
result = crawl_sync("https://example.com", settings=settings)
```

### Return value

`crawl` / `crawl_sync` return a `CrawlResponse` (`pydantic` model):

| Field | Description |
|-------|-------------|
| `url` | Crawled URL |
| `markdown` | Page markdown with image blocks inlined |
| `images` | List of `ImageDescription` (`url`, `description`) |
| `metadata` | Firecrawl metadata dict |

Lower-level access: `run_crawl(url, settings)` runs the pipeline without the top-level Langfuse “crawl” span (still traces per-step if Langfuse is enabled).

```python
from clawcrawl import get_settings, run_crawl

result = await run_crawl("https://example.com", get_settings())
```

## Run the API

The HTTP service is a thin wrapper around `clawcrawl.crawl`:

```bash
uvicorn clawcrawl.main:app --reload --app-dir src
```

- `GET /health` — liveness
- `POST /v1/crawl` — body: `{"url": "https://example.com"}`

Response includes `markdown`, `images` (structured descriptions), and `metadata` from Firecrawl.

## Quick test client

With the server running:

```bash
pip install httpx
python easy_test.py "https://example.com"
```

Writes `output/<host>.md`. Override API base with `CLAWCRAWL_BASE_URL` (default `http://127.0.0.1:8000`).

## Tests

```bash
pytest -q
```

Unit tests disable Langfuse and use dummy API keys via env fixtures.

## Langfuse trace tree

When tracing is enabled, a typical crawl looks like:

`crawl` → `run_crawl` → `scrape_markdown` | `extract_image_links` + `extract_image_links.llm` | `describe_all` → `describe_one` + `describe_one.llm` (×N) | `replace_images_in_markdown`

LLM generations record system/user prompts in **input**, structured output in **output**, token counts (`input` / `output` / `total`), and OpenRouter **cost** when returned on the completion.

## Project layout

```
src/clawcrawl/
  __init__.py      # Public exports: crawl, crawl_sync, models, settings
  api.py           # Library entrypoint (crawl / crawl_sync)
  main.py          # FastAPI app
  pipeline.py      # Orchestration
  config.py        # Settings from .env
  prompts/         # LLM prompts: <step>/system.md, user.md
  services/        # scrape, image_links, describe, replace
  llm/             # Instructor + OpenRouter clients
  telemetry/       # Langfuse helpers
easy_test.py       # POST URL → output/*.md
tests/
```

### Prompts

Each pipeline step that calls an LLM has a folder under `src/clawcrawl/prompts/` named after the step (e.g. `extract_image_links`, `describe_one`). Edit `system.md` and `user.md` there; `user.md` may use `{placeholders}` filled in by the service code.

## License

See repository for license terms if applicable.