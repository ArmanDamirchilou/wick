import pytest
from pypdf import PdfWriter

from wick.ingest import chunk_text, extract_text


def test_chunk_text_splits_long_input():
    text = "a" * 2000
    chunks = chunk_text(text, chunk_size=800, overlap=100)
    assert len(chunks) > 1
    assert all(len(c) <= 800 for c in chunks)


def test_chunk_text_drops_empty_pieces():
    assert chunk_text("   ") == []


def test_extract_text_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_text(tmp_path / "nope.pdf")


def test_extract_text_rejects_non_pdf(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"this is plainly not a pdf")
    with pytest.raises(ValueError):
        extract_text(bad)


def test_extract_text_rejects_pdf_with_no_text(tmp_path):
    blank = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(blank, "wb") as f:
        writer.write(f)

    with pytest.raises(ValueError, match="extractable text"):
        extract_text(blank)
