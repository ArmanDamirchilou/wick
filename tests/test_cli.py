import pytest

from wick.cli import ENGLISH_EMBED, MULTILINGUAL_EMBED, parse_args, pick_embed_model


@pytest.mark.parametrize(
    "text",
    [
        "Drop, cover, and hold on until the shaking stops.",
        "Café façade naïve — accented Latin is still Latin.",
        "",
    ],
)
def test_latin_documents_keep_the_english_retrieval_model(text):
    assert pick_embed_model(text) == ENGLISH_EMBED


@pytest.mark.parametrize(
    "text",
    [
        "بیشتر آب کره زمین در اقیانوس‌ها است.",
        "पानी सौ डिग्री सेल्सियस पर उबलता है।",
        "Chapter 3 — فصل سوم درباره چرخه آب در طبیعت است و آب را دنبال می‌کند",
    ],
)
def test_non_latin_documents_switch_to_the_multilingual_model(text):
    assert pick_embed_model(text) == MULTILINGUAL_EMBED


def test_an_explicit_embed_model_is_left_alone(monkeypatch):
    monkeypatch.setattr("sys.argv", ["wick", "doc.pdf", "q", "--embed-model", "my/encoder"])
    assert parse_args().embed_model == "my/encoder"


def test_the_question_is_optional_so_a_session_can_start(monkeypatch):
    monkeypatch.setattr("sys.argv", ["wick", "doc.pdf"])
    args = parse_args()

    assert args.question is None
    assert args.embed_model is None  # left unset so the document can decide


def test_a_pdf_is_required_unless_downloading(monkeypatch):
    monkeypatch.setattr("sys.argv", ["wick"])
    with pytest.raises(SystemExit):
        parse_args()


def test_downloading_needs_no_pdf(monkeypatch):
    monkeypatch.setattr("sys.argv", ["wick", "--download-model"])
    assert parse_args().download_model is True
