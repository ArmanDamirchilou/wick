from pathlib import Path

from .embeddings import SentenceTransformerEmbedder
from .ingest import chunk_text, extract_text
from .llm import LocalLLM
from .store import VectorStore


class OfflineAssistant:
    def __init__(self, model_path: Path, embedder: SentenceTransformerEmbedder | None = None):
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.llm = LocalLLM(model_path)
        self.store: VectorStore | None = None

    def load_pdf(self, pdf_path: Path) -> None:
        chunks = chunk_text(extract_text(pdf_path))
        vectors = self.embedder.embed(chunks)
        self.store = VectorStore(dim=vectors.shape[1])
        self.store.add(vectors, chunks)

    def ask(self, question: str) -> str:
        if self.store is None:
            raise RuntimeError("Load a PDF before asking questions")
        query_vector = self.embedder.embed([question])[0]
        context = self.store.search(query_vector)
        return self.llm.answer(question, context)
