from typing import Protocol

import numpy as np


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray: ...


class SentenceTransformerEmbedder:
    """Local sentence-transformers model, loaded from cache — see wick.models.download."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        SentenceTransformer = _import_sentence_transformers()
        try:
            self.model = SentenceTransformer(model_name)
        except OSError as e:
            raise FileNotFoundError(
                f"Retrieval model '{model_name}' isn't downloaded yet.\n"
                f"Run 'wick --download-model --embed-model {model_name}' once, "
                "then every run after that is offline."
            ) from e

    def embed(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def _import_sentence_transformers():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise RuntimeError(
            "Retrieval needs sentence-transformers, which isn't installed.\n"
            'Install it with: pip install "wick-offline[embeddings]"'
        ) from e
    return SentenceTransformer
