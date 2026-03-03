from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

ARXIV_ID_PATTERN = re.compile(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)")


def _safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:120]


def download_pdf_from_url(url: str, output_dir: Path) -> tuple[Path, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    if not filename.endswith(".pdf"):
        filename = f"{filename or 'paper'}.pdf"

    target = output_dir / filename
    import requests

    with requests.get(url, timeout=60, stream=True) as resp:
        resp.raise_for_status()
        with target.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return target, target.stem


def download_pdf_from_title(title: str, output_dir: Path) -> tuple[Path, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    import arxiv

    search = arxiv.Search(query=title, max_results=1, sort_by=arxiv.SortCriterion.Relevance)
    results = list(search.results())
    if not results:
        raise ValueError("No paper found on arXiv for this title.")

    paper = results[0]
    base_name = _safe_filename(paper.title)
    target = output_dir / f"{base_name}.pdf"
    paper.download_pdf(filename=str(target))
    return target, paper.title


def download_pdf_from_input(link_or_title: str, output_dir: Path) -> tuple[Path, str]:
    candidate = link_or_title.strip()
    if candidate.startswith("http://") or candidate.startswith("https://"):
        arxiv_match = ARXIV_ID_PATTERN.search(candidate)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
            normalized = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            return download_pdf_from_url(normalized, output_dir)
        return download_pdf_from_url(candidate, output_dir)
    return download_pdf_from_title(candidate, output_dir)
