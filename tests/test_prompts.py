import pytest

from clawcrawl.prompts import load_prompt, render_prompt


def test_load_extract_image_links_system():
    text = load_prompt("extract_image_links", "system")
    assert "image URL" in text
    assert "dedupe" in text


def test_render_extract_image_links_user():
    text = render_prompt(
        "extract_image_links",
        "user",
        hint_block="- https://example.com/a.png",
        markdown="# Hello",
    )
    assert "https://example.com/a.png" in text
    assert "# Hello" in text


def test_load_describe_one_system():
    text = load_prompt("describe_one", "system")
    assert "Visual Data Architect" in text
    assert "`description`" in text


def test_missing_prompt_raises():
    with pytest.raises(FileNotFoundError, match="missing_step/nope"):
        load_prompt("missing_step", "nope")
