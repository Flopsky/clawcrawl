"""Load and render step prompts from ``prompts/<step>/*.md``."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


@lru_cache
def load_prompt(step: str, name: str) -> str:
    """Return the contents of ``prompts/<step>/<name>.md``."""
    path = PROMPTS_DIR / step / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Missing prompt: {step}/{name}.md")
    return path.read_text(encoding="utf-8").strip()


def render_prompt(step: str, name: str, **variables: str) -> str:
    """Load a prompt template and substitute ``{placeholders}``."""
    template = load_prompt(step, name)
    if not variables:
        return template
    return template.format(**variables)
