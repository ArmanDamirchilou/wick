from pathlib import Path

import pypdf


def extract_text(pdf_path: Path) -> str:
    reader = pypdf.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str, *, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    # Overlap keeps an idea from getting cut in half right at a chunk boundary
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]
