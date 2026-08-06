import numpy as np

from wick.store import VectorStore


def test_search_returns_closest_chunk():
    store = VectorStore(dim=3)
    vectors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype="float32")
    store.add(vectors, ["north", "east", "up"])

    result = store.search(np.array([0.9, 0.1, 0], dtype="float32"), k=1)

    assert result == ["north"]


def test_search_on_empty_store_returns_nothing():
    store = VectorStore(dim=3)
    assert store.search(np.zeros(3, dtype="float32")) == []


def test_search_drops_chunks_below_min_score():
    store = VectorStore(dim=3)
    store.add(np.array([[1, 0, 0], [0, 1, 0]], dtype="float32"), ["north", "east"])

    # Query scores 0.9 against north, 0.1 against east; the bar keeps only north.
    result = store.search(np.array([0.9, 0.1, 0], dtype="float32"), min_score=0.5)

    assert result == ["north"]


def test_search_returns_nothing_when_all_below_min_score():
    store = VectorStore(dim=3)
    store.add(np.array([[1, 0, 0]], dtype="float32"), ["north"])

    assert store.search(np.array([0, 1, 0], dtype="float32"), min_score=0.5) == []
