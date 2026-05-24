#!/usr/bin/env python3
"""POST a URL to clawcrawl and save the returned markdown."""

import os
import re
import sys
from pathlib import Path

import httpx

BASE_URL = os.environ.get("CLAWCRAWL_BASE_URL", "http://127.0.0.1:9000")
OUT_DIR = Path("output")


def slug_from_url(url: str) -> str:
    host = re.sub(r"^https?://", "", url).split("/")[0]
    return re.sub(r"[^\w.-]+", "_", host)[:80] or "page"


def main() -> None:
    url = (sys.argv[1] if len(sys.argv) > 1 else input("URL: ")).strip()
    if not url:
        sys.exit("URL required")

    with httpx.Client(timeout=300.0) as client:
        r = client.post(f"{BASE_URL}/v1/crawl", json={"url": url})
        r.raise_for_status()
        data = r.json()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{slug_from_url(url)}.md"
    out_path.write_text(data["markdown"], encoding="utf-8")
    print(
        f"Wrote {out_path} ({len(data['markdown'])} chars, "
        f"{len(data.get('images', []))} images)"
    )


if __name__ == "__main__":
    main()