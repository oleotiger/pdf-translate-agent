from pathlib import Path

from pdf_translate_agent.downloader import ARXIV_ID_PATTERN
from pdf_translate_agent.exporter import render_markdown_with_images


def test_arxiv_pattern_matches_abs_and_pdf_links():
    assert ARXIV_ID_PATTERN.search("https://arxiv.org/abs/2401.01234")
    assert ARXIV_ID_PATTERN.search("https://arxiv.org/pdf/2401.01234v2")


def test_render_markdown_with_images(tmp_path: Path):
    image = tmp_path / "img.png"
    image.write_bytes(b"fake")
    text = render_markdown_with_images(["## Page 1\n\nHello"], [image])
    assert "论文中文翻译" in text
    assert "img.png" in text
