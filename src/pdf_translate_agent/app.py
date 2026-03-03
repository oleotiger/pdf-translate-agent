from __future__ import annotations

from pathlib import Path

import gradio as gr

from .agent import PaperTranslateAgent
from .llm_factory import LLMConfig

WORKSPACE = Path("./runtime")
WORKSPACE.mkdir(parents=True, exist_ok=True)
AGENT = PaperTranslateAgent(WORKSPACE)

MODEL_HINTS = {
    "gemini": "例如: gemini-2.0-flash-exp / gemini-1.5-pro",
    "openai": "例如: gpt-4o-mini / gpt-4.1",
    "local_openai_compatible": "例如: Qwen/Qwen2.5-7B-Instruct",
}


def run_agent(
    provider,
    model,
    api_key,
    base_url,
    temperature,
    disable_ssl_verify,
    pdf_file,
    link_or_title,
    output_format,
):
    cfg = LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url or None,
        temperature=temperature,
        verify_ssl=not disable_ssl_verify,
    )

    record = AGENT.run(
        llm_config=cfg,
        pdf_file=pdf_file,
        link_or_title=link_or_title,
        output_format=output_format,
    )

    markdown_text = record.translated_markdown.read_text(encoding="utf-8")
    translated_pdf_path = str(record.translated_pdf) if record.translated_pdf else "未生成 PDF"

    history = "\n".join(
        f"- {idx + 1}. {item.title} | MD: {item.translated_markdown}"
        for idx, item in enumerate(AGENT.records)
    )

    return (
        record.title,
        str(record.source_pdf),
        str(record.translated_markdown),
        translated_pdf_path,
        markdown_text,
        record.summary,
        history,
    )


def update_model_hint(provider):
    return gr.update(info=MODEL_HINTS.get(provider, ""))


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="论文下载翻译 Agent") as demo:
        gr.Markdown("# 论文下载与翻译 Agent（本地内存会话版）")

        with gr.Row():
            provider = gr.Dropdown(
                label="模型提供方",
                choices=["gemini", "openai", "local_openai_compatible"],
                value="gemini",
            )
            model = gr.Textbox(label="模型名称", value="gemini-2.0-flash-exp", info=MODEL_HINTS["gemini"])
            temperature = gr.Slider(label="Temperature", minimum=0.0, maximum=1.0, value=0.1, step=0.05)

        api_key = gr.Textbox(label="API Key", type="password")
        base_url = gr.Textbox(label="Base URL（本地模型或代理服务可填）", placeholder="http://localhost:8000/v1")
        disable_ssl_verify = gr.Checkbox(
            label="禁用 SSL 证书校验（不安全，仅用于排障）",
            value=False,
        )

        with gr.Row():
            pdf_file = gr.File(label="上传论文 PDF（可选）", file_types=[".pdf"], type="filepath")
            link_or_title = gr.Textbox(label="论文标题或链接（可选）")

        output_format = gr.Radio(label="输出格式", choices=["markdown", "pdf", "both"], value="both")

        run_btn = gr.Button("开始下载+翻译")

        with gr.Tab("结果"):
            paper_title = gr.Textbox(label="论文标题")
            source_pdf = gr.Textbox(label="源 PDF 路径")
            md_path = gr.Textbox(label="翻译 Markdown 路径")
            pdf_path = gr.Textbox(label="翻译 PDF 路径")
            md_preview = gr.Markdown(label="Markdown 预览")
            summary = gr.Markdown(label="论文总结")

        with gr.Tab("会话内记录"):
            history = gr.Markdown()

        provider.change(update_model_hint, inputs=[provider], outputs=[model])
        run_btn.click(
            run_agent,
            inputs=[
                provider,
                model,
                api_key,
                base_url,
                temperature,
                disable_ssl_verify,
                pdf_file,
                link_or_title,
                output_format,
            ],
            outputs=[paper_title, source_pdf, md_path, pdf_path, md_preview, summary, history],
        )

    return demo


def main() -> None:
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
