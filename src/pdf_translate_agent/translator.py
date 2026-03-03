from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

TRANSLATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
你是学术翻译助手。目标：把英文论文准确翻译为中文 Markdown。
要求：
1) 严格保持原文技术含义，不要扩写，不要省略重要公式含义。
2) 保留原有层次结构，用 Markdown 标题、列表、表格表达。
3) 专业术语第一次出现时可保留英文括注。
4) 数学公式与符号原样保留。
5) 仅输出翻译结果，不要解释过程。
""".strip(),
        ),
        (
            "human",
            "原文片段（来自论文 {title} 的第 {chunk_index}/{chunk_total} 段）:\n\n{text}",
        ),
    ]
)

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
你是科研论文总结助手。请输出结构化总结：
- 研究问题
- 核心方法
- 关键实验与结果
- 局限性
- 可复现建议
要求：准确、简洁、避免虚构。
""".strip(),
        ),
        ("human", "请基于以下翻译内容总结论文：\n\n{text}"),
    ]
)


@dataclass
class PaperParseResult:
    title: str
    sections: list[str]
    image_paths: list[Path]


def parse_pdf_to_sections(pdf_path: Path, assets_dir: Path) -> PaperParseResult:
    assets_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    sections: list[str] = []
    image_paths: list[Path] = []

    title = pdf_path.stem
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text").strip()
        if text:
            sections.append(f"## Page {page_idx + 1}\n\n{text}")

        for img_idx, image in enumerate(page.get_images(full=True)):
            xref = image[0]
            base = doc.extract_image(xref)
            ext = base.get("ext", "png")
            image_name = f"page_{page_idx + 1}_img_{img_idx + 1}.{ext}"
            path = assets_dir / image_name
            path.write_bytes(base["image"])
            image_paths.append(path)

    doc.close()
    return PaperParseResult(title=title, sections=sections, image_paths=image_paths)


def translate_sections(
    llm: BaseChatModel,
    title: str,
    sections: list[str],
) -> list[str]:
    chain = TRANSLATION_PROMPT | llm
    total = len(sections)
    translated: list[str] = []
    for idx, text in enumerate(sections, start=1):
        response = chain.invoke(
            {
                "title": title,
                "chunk_index": idx,
                "chunk_total": total,
                "text": text,
            }
        )
        translated.append(response.content)
    return translated


def summarize_translation(llm: BaseChatModel, translated_markdown: str) -> str:
    chain = SUMMARY_PROMPT | llm
    response = chain.invoke({"text": translated_markdown[:20000]})
    return response.content
