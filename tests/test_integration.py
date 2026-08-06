import os
from pathlib import Path

import pytest

from wick.llm import REFUSAL
from wick.pipeline import OfflineAssistant

MODEL_ENV = "WICK_TEST_MODEL"
SAMPLE_PDF = Path(__file__).parent / "fixtures" / "sample.pdf"


@pytest.fixture(scope="module")
def assistant():
    model = os.environ.get(MODEL_ENV)
    if not model or not Path(model).exists():
        pytest.skip(f"set {MODEL_ENV} to a local GGUF path to run integration tests")
    loaded = OfflineAssistant(model_path=Path(model))
    loaded.load_pdf(SAMPLE_PDF)
    return loaded


@pytest.mark.integration
def test_answers_a_question_from_the_document(assistant):
    answer = assistant.ask("How much power does the primary generator produce?")
    assert "3.5" in answer


@pytest.mark.integration
def test_refuses_a_question_the_document_cannot_answer(assistant):
    assert assistant.ask("What is the capital of France?") == REFUSAL
