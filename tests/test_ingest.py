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


def test_chunk_text_rejects_an_overlap_that_would_never_advance():
    with pytest.raises(ValueError, match="must be smaller"):
        chunk_text("a" * 2000, chunk_size=100, overlap=100)


def test_chunks_begin_and_end_on_whole_words():
    words = [f"word{n}" for n in range(400)]
    chunks = chunk_text(" ".join(words), chunk_size=200, overlap=40)

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.split()[0] in words
        assert chunk.split()[-1] in words


def test_consecutive_chunks_overlap():
    chunks = chunk_text(" ".join(f"word{n}" for n in range(400)), chunk_size=200, overlap=40)
    tail = chunks[0].split()[-1]

    assert tail in chunks[1].split()


def test_a_word_longer_than_a_chunk_is_still_split():
    chunks = chunk_text("short " + "x" * 500, chunk_size=200, overlap=40)

    assert all(len(chunk) <= 200 for chunk in chunks)
    assert "".join(chunks).count("x") >= 500


def test_extract_text_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_text(tmp_path / "nope.pdf")


def test_extract_text_accepts_a_plain_string_path(tmp_path):
    # Web frameworks hand over an upload as a string, not a Path.
    with pytest.raises(FileNotFoundError):
        extract_text(str(tmp_path / "nope.pdf"))


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
