from typing import Tuple
from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument
import markdown
from bs4 import BeautifulSoup


def extract_text(path: str | Path) -> Tuple[str, str]:
    """Return (text, mime) from supported files.

    Supports: .pdf, .docx, .txt, .md
    """
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(p), "application/pdf"
    if suffix == ".docx":
        return extract_docx(p), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if suffix in {".txt", ""}:
        return p.read_text(encoding="utf-8", errors="ignore"), "text/plain"
    if suffix == ".md":
        return extract_md(p), "text/markdown"
    raise ValueError(f"Unsupported file type: {suffix}")


def extract_pdf(p: Path) -> str:
    reader = PdfReader(str(p))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n\n".join(filter(None, parts))


def extract_docx(p: Path) -> str:
    doc = DocxDocument(str(p))
    paras = [para.text.strip() for para in doc.paragraphs]
    return "\n\n".join([t for t in paras if t])


def extract_md(p: Path) -> str:
    html = markdown.markdown(p.read_text(encoding="utf-8", errors="ignore"))
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n")
