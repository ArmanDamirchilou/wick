from pathlib import Path
from typing import NamedTuple

from .embeddings import Embedder, SentenceTransformerEmbedder
from .ingest import chunk_text, extract_text
from .llm import REFUSAL, LocalLLM
from .store import VectorStore


class Answer(NamedTuple):
    text: str
    sources: list[str]


class OfflineAssistant:
    def __init__(
        self,
        model_path: Path,
        embedder: Embedder | None = None,
        embed_model: str = "all-MiniLM-L6-v2",
        min_relevance: float = 0.2,
    ):
        # LLM first: its instant missing-file check beats a slow embedder load.
        self.llm = LocalLLM(model_path)
        self.embedder = embedder or SentenceTransformerEmbedder(embed_model)
        self.min_relevance = min_relevance
        self.store: VectorStore | None = None
        self.passages = 0

    def load_pdf(self, pdf_path: Path) -> None:
        self.load_text(extract_text(pdf_path))

    def load_text(self, text: str) -> None:
        chunks = chunk_text(text)
        vectors = self.embedder.embed(chunks)
        self.store = VectorStore(dim=vectors.shape[1])
        self.store.add(vectors, chunks)
        self.passages = len(chunks)

    def ask(self, question: str) -> Answer:
        """Answer from the loaded document, or refuse. Sources are the passages actually used."""
        if self.store is None:
            raise RuntimeError("Load a PDF before asking a question.")
        query_vector = self.embedder.embed([question])[0]
        context = self.store.search(query_vector, min_score=self.min_relevance)
        # Nothing cleared the bar — refuse rather than let the model answer from training data.
        if not context:
            return Answer(REFUSAL, [])
        return Answer(self.llm.answer(question, context), context)
