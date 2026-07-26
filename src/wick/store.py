import faiss
import numpy as np


class VectorStore:
    def __init__(self, dim: int):
        # Inner product on normalized vectors == cosine similarity, and it's the fastest FAISS index
        self.index = faiss.IndexFlatIP(dim)
        self.chunks: list[str] = []

    def add(self, vectors: np.ndarray, chunks: list[str]) -> None:
        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self, query_vector: np.ndarray, k: int = 4) -> list[str]:
        if not self.chunks:
            return []
        _, idx = self.index.search(query_vector.reshape(1, -1), min(k, len(self.chunks)))
        return [self.chunks[i] for i in idx[0] if i != -1]
