# PDF Translate Agent（本地 Windows 部署）

一个基于 **LangChain + Gradio** 的轻量级论文下载与翻译 AI Agent。

## 设计选择（轻量、易部署）

- **Agent 编排**：LangChain（只用 ChatPrompt + Runnable，避免过重依赖）。
- **图形界面**：Gradio（纯 Python，部署简单，浏览器即可使用）。
- **PDF 解析**：PyMuPDF（提取页面文本和插图）。
- **格式导出**：Markdown + xhtml2pdf。
- **状态存储**：仅内存（`PaperTranslateAgent.records`），不使用数据库。

## 功能覆盖

1. 支持 Gemini / OpenAI / OpenAI 兼容本地模型（如 vLLM、LM Studio、Ollama 网关）。
2. 输入支持：
   - 直接上传 PDF；
   - 输入论文标题（默认走 arXiv 搜索并下载）；
   - 输入论文链接（支持直接 PDF 链接，arXiv abs/pdf 链接自动归一化下载）。
3. 翻译输出：
   - Markdown；
   - PDF；
   - 或两者都输出。
4. 自动生成论文总结（研究问题、方法、结果、局限、复现建议）。
5. 会话内记录译文路径和标题，不持久化到数据库。

## 快速启动（Windows）

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -U pip
pip install -e .
python -m pdf_translate_agent.app
```

打开浏览器访问 `http://127.0.0.1:7860`。

## Prompt 设计说明

本项目内置两个 prompt：

- `TRANSLATION_PROMPT`：强调忠实翻译、术语一致、保留公式结构、Markdown 层级。
- `SUMMARY_PROMPT`：结构化总结（问题/方法/结果/局限/复现）。

设计原则参考了开源社区常见学术翻译 agent 实践：
- “忠实性优先于润色”；
- “结构化输出便于检索与二次编辑”；
- “总结固定模板降低幻觉”。

你可以在 `src/pdf_translate_agent/translator.py` 中进一步定制。

## 目录结构

```text
src/pdf_translate_agent/
  app.py          # Gradio UI
  agent.py        # 主流程编排
  downloader.py   # 标题/链接下载论文
  llm_factory.py  # Gemini/OpenAI/本地模型适配
  translator.py   # PDF 解析、翻译和总结
  exporter.py     # markdown/pdf 导出
```

## 注意事项

- 标题下载当前优先 arXiv，如需扩展可加入 Crossref/Semantic Scholar。
- PDF 到 Markdown 的“版式一致”是近似实现（按页分节 + 插图保留）。
- 大论文建议选择高上下文窗口模型（如 Gemini 1.5 Pro 或 GPT-4.1）。
