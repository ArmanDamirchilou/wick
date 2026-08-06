from pathlib import Path

import pypdf
from pypdf.errors import PdfReadError


def extract_text(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except PdfReadError as e:
        raise ValueError(f"Could not read PDF (corrupt or not a PDF): {pdf_path}") from e
    if not text.strip():
        raise ValueError(
            f"No extractable text in {pdf_path} — it looks like a scanned or "
            "image-only PDF, which needs OCR (not supported yet)."
        )
    return text


def chunk_text(text: str, *, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    # Overlap keeps an idea from getting cut in half right at a chunk boundary
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]
