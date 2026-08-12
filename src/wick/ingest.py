from pathlib import Path

import pypdf
from pypdf.errors import PdfReadError


def extract_text(pdf_path: str | Path) -> str:
    # Callers hand us whatever their framework gave them; a plain string is fine.
    pdf_path = Path(pdf_path)
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
    """Split into overlapping chunks that begin and end on whole words."""
    # Without this the loop never advances and the caller hangs instead of failing.
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size})")
    chunks: list[str] = []
    current: list[str] = []
    length = 0
    for word in text.split():
        for piece in _fit(word, chunk_size):
            if current and length + len(piece) + 1 > chunk_size:
                chunks.append(" ".join(current))
                current, length = _carry_over(current, overlap)
                # A piece as long as a whole chunk can't share one with the carried tail.
                if length + len(piece) + 1 > chunk_size:
                    current, length = [], 0
            current.append(piece)
            length += len(piece) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks


def _fit(word: str, limit: int) -> list[str]:
    # A "word" longer than a whole chunk — a URL, a run of table punctuation — still has to fit.
    if len(word) <= limit:
        return [word]
    return [word[i : i + limit] for i in range(0, len(word), limit)]


def _carry_over(words: list[str], overlap: int) -> tuple[list[str], int]:
    # Repeating the tail of a chunk keeps an idea from being cut in half at the boundary.
    carried: list[str] = []
    length = 0
    for word in reversed(words):
        if length + len(word) + 1 > overlap:
            break
        carried.insert(0, word)
        length += len(word) + 1
    return carried, length
