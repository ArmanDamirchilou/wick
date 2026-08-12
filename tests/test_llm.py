import builtins

import pytest

from wick import llm


def _hide(monkeypatch, missing: str) -> None:
    real = builtins.__import__

    def fake(name, *args, **kwargs):
        if name == missing:
            raise ImportError(f"No module named {missing!r}")
        return real(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake)


def test_a_missing_runtime_names_the_install_command(monkeypatch):
    _hide(monkeypatch, "llama_cpp")

    with pytest.raises(RuntimeError, match="pip install llama-cpp-python"):
        llm._import_llama_cpp()


def test_a_missing_retrieval_backend_names_the_extra(monkeypatch):
    _hide(monkeypatch, "sentence_transformers")
    from wick import embeddings

    with pytest.raises(RuntimeError, match=r"wick-offline\[embeddings\]"):
        embeddings._import_sentence_transformers()
