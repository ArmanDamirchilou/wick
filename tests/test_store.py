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
