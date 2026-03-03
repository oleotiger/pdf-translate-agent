from __future__ import annotations

from pathlib import Path

def render_markdown_with_images(translated_sections: list[str], image_paths: list[Path]) -> str:
    content = ["# 论文中文翻译\n"]
    content.extend(translated_sections)

    if image_paths:
        content.append("\n## 原论文插图\n")
        for image in image_paths:
            content.append(f"![{image.name}]({image.as_posix()})")
    return "\n\n".join(content)


def save_markdown(markdown_text: str, output_file: Path) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown_text, encoding="utf-8")
    return output_file


def markdown_to_pdf(markdown_text: str, output_file: Path) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    import markdown
    from xhtml2pdf import pisa

    html = markdown.markdown(markdown_text)
    with output_file.open("wb") as f:
        pisa.CreatePDF(html, dest=f)
    return output_file
