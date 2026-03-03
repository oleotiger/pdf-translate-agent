from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .downloader import download_pdf_from_input
from .exporter import markdown_to_pdf, render_markdown_with_images, save_markdown
from .llm_factory import LLMConfig, build_chat_model
from .translator import parse_pdf_to_sections, summarize_translation, translate_sections


@dataclass
class SessionPaperRecord:
    title: str
    source_pdf: Path
    translated_markdown: Path
    translated_pdf: Path | None
    summary: str


class PaperTranslateAgent:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.download_dir = workspace / "downloads"
        self.output_dir = workspace / "outputs"
        self.records: list[SessionPaperRecord] = []

    def _resolve_pdf(self, pdf_file: str | None, link_or_title: str | None) -> tuple[Path, str]:
        if pdf_file:
            pdf_path = Path(pdf_file)
            return pdf_path, pdf_path.stem
        if link_or_title:
            return download_pdf_from_input(link_or_title, self.download_dir)
        raise ValueError("请上传 PDF，或提供论文标题/链接。")

    def run(
        self,
        llm_config: LLMConfig,
        pdf_file: str | None,
        link_or_title: str | None,
        output_format: str,
    ) -> SessionPaperRecord:
        llm = build_chat_model(llm_config)
        pdf_path, paper_title = self._resolve_pdf(pdf_file, link_or_title)

        paper_slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in paper_title)[:100]
        assets_dir = self.output_dir / paper_slug / "assets"
        parse_result = parse_pdf_to_sections(pdf_path, assets_dir)
        translated_sections = translate_sections(llm, parse_result.title, parse_result.sections)
        markdown_text = render_markdown_with_images(translated_sections, parse_result.image_paths)

        md_file = self.output_dir / paper_slug / f"{paper_slug}_translated.md"
        save_markdown(markdown_text, md_file)

        pdf_out: Path | None = None
        if output_format in {"pdf", "both"}:
            pdf_out = self.output_dir / paper_slug / f"{paper_slug}_translated.pdf"
            markdown_to_pdf(markdown_text, pdf_out)

        summary = summarize_translation(llm, markdown_text)
        record = SessionPaperRecord(
            title=parse_result.title,
            source_pdf=pdf_path,
            translated_markdown=md_file,
            translated_pdf=pdf_out,
            summary=summary,
        )
        self.records.append(record)
        return record
