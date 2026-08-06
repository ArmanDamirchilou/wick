from pathlib import Path

from .embeddings import Embedder, SentenceTransformerEmbedder
from .ingest import chunk_text, extract_text
from .llm import LocalLLM
from .store import VectorStore


class OfflineAssistant:
    def __init__(
        self,
        model_path: Path,
        embedder: Embedder | None = None,
        embed_model: str = "all-MiniLM-L6-v2",
        min_relevance: float = 0.2,
    ):
        # LLM first: its missing-file check is instant, so a bad --model path
        # fails before the embedder spends time loading.
        self.llm = LocalLLM(model_path)
        self.embedder = embedder or SentenceTransformerEmbedder(embed_model)
        self.min_relevance = min_relevance
        self.store: VectorStore | None = None

    def load_pdf(self, pdf_path: Path) -> None:
        chunks = chunk_text(extract_text(pdf_path))
        vectors = self.embedder.embed(chunks)
        self.store = VectorStore(dim=vectors.shape[1])
        self.store.add(vectors, chunks)

    def ask(self, question: str) -> str:
        if self.store is None:
            raise RuntimeError("Load a PDF before asking a question.")
        query_vector = self.embedder.embed([question])[0]
        context = self.store.search(query_vector, min_score=self.min_relevance)
        # Nothing cleared the relevance bar — refuse instead of letting a weak
        # model answer from its own training data.
        if not context:
            return LocalLLM.REFUSAL
        return self.llm.answer(question, context)
