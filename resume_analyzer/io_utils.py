"""Document loading utilities — supports PDF, DOCX, and TXT."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentInput:
    text: str
    source: str  # filename or "pasted"


def load_document(path: Path) -> DocumentInput:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return DocumentInput(text=_read_pdf(path), source=path.name)
    elif suffix == ".docx":
        return DocumentInput(text=_read_docx(path), source=path.name)
    else:
        return DocumentInput(text=path.read_text(encoding="utf-8", errors="ignore"), source=path.name)


def load_from_bytes(data: bytes, filename: str) -> DocumentInput:
    suffix = Path(filename).suffix.lower()
    tmp = Path(f"._tmp_resume{suffix}")
    tmp.write_bytes(data)
    try:
        return load_document(tmp)
    finally:
        tmp.unlink(missing_ok=True)


def _read_pdf(path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)
    except ImportError:
        pass
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        raise RuntimeError("Install pdfplumber or pypdf to read PDF files:\n  pip install pdfplumber")


def _read_docx(path: Path) -> str:
    try:
        import docx2txt
        return docx2txt.process(str(path))
    except ImportError:
        pass
    try:
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        raise RuntimeError("Install python-docx or docx2txt to read DOCX files:\n  pip install python-docx")
