from pathlib import Path

import numpy as np
import pytest

from wick import pipeline
from wick.llm import REFUSAL
from wick.pipeline import OfflineAssistant
from wick.store import VectorStore


class _FakeEmbedder:
    """Returns one fixed vector, so tests control the retrieval score directly."""

    def __init__(self, query_vector):
        self._vec = np.asarray(query_vector, dtype="float32")

    def embed(self, texts):
        return np.array([self._vec for _ in texts], dtype="float32")


class _StubLLM:
    def answer(self, question, context):
        return "answered from: " + " | ".join(context)


def _assistant(monkeypatch, query_vector, min_relevance=0.5):
    monkeypatch.setattr(pipeline, "LocalLLM", lambda *a, **k: _StubLLM())
    assistant = OfflineAssistant(
        Path("unused.gguf"), embedder=_FakeEmbedder(query_vector), min_relevance=min_relevance
    )
    assistant.store = VectorStore(dim=3)
    assistant.store.add(np.array([[1, 0, 0]], dtype="float32"), ["the north star"])
    return assistant


def test_ask_before_loading_pdf_raises(monkeypatch):
    monkeypatch.setattr(pipeline, "LocalLLM", lambda *a, **k: _StubLLM())
    assistant = OfflineAssistant(Path("unused.gguf"), embedder=_FakeEmbedder([1, 0, 0]))
    with pytest.raises(RuntimeError):
        assistant.ask("anything")


def test_ask_refuses_when_nothing_clears_the_bar(monkeypatch):
    assistant = _assistant(monkeypatch, query_vector=[0, 1, 0])  # orthogonal → score 0
    answer = assistant.ask("something unrelated")

    assert answer.text == REFUSAL
    assert answer.sources == []


def test_ask_answers_when_a_chunk_is_relevant(monkeypatch):
    assistant = _assistant(monkeypatch, query_vector=[1, 0, 0])  # score 1
    answer = assistant.ask("about the north star")

    assert "the north star" in answer.text
    assert answer.sources == ["the north star"]


def test_load_text_counts_the_passages_it_indexed(monkeypatch):
    monkeypatch.setattr(pipeline, "LocalLLM", lambda *a, **k: _StubLLM())
    assistant = OfflineAssistant(Path("unused.gguf"), embedder=_FakeEmbedder([1, 0, 0]))
    assistant.load_text("word " * 600)  # 3000 chars → more than one chunk

    assert assistant.passages > 1
    assert assistant.passages == len(assistant.store.chunks)
