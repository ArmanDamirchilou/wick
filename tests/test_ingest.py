from wick.ingest import chunk_text


def test_chunk_text_splits_long_input():
    text = "a" * 2000
    chunks = chunk_text(text, chunk_size=800, overlap=100)
    assert len(chunks) > 1
    assert all(len(c) <= 800 for c in chunks)


def test_chunk_text_drops_empty_pieces():
    assert chunk_text("   ") == []
