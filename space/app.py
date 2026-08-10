"""Hosted try-before-you-download demo for wick.

wick is an offline tool; this Space exists so a stranger can see what it does
without downloading a model first. It runs the real package, unmodified.
"""

import gradio as gr

from wick.models import download, download_embedder
from wick.pipeline import OfflineAssistant

EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

CHOICES = {
    "Qwen2.5 1.5B — faster, English": "qwen2.5-1.5b",
    "Gemma 3n E2B — multilingual, slower": "gemma-3n-e2b",
}

FAST, MULTILINGUAL = list(CHOICES)

EXAMPLES = [
    ["examples/earthquake-safety.pdf", "What should I do if I am trapped under rubble?", FAST],
    ["examples/earthquake-safety.pdf", "What is the population of Tokyo?", FAST],
    ["examples/water-cycle-fa.pdf", "بیشتر آب کره زمین کجاست؟", MULTILINGUAL],
]

_assistants: dict[str, OfflineAssistant] = {}
_loaded: dict[str, str] = {}


def assistant_for(model_name: str) -> OfflineAssistant:
    if model_name not in _assistants:
        _assistants[model_name] = OfflineAssistant(
            model_path=download(model_name), embed_model=EMBED_MODEL
        )
    return _assistants[model_name]


def ask(pdf_path: str, question: str, choice: str) -> tuple[str, str]:
    if not pdf_path:
        return "Upload a PDF (or pick one of the examples below) first.", ""
    if not question.strip():
        return "Ask a question about the document.", ""

    model_name = CHOICES[choice]
    assistant = assistant_for(model_name)
    # Re-embedding a PDF costs more than the answer does, so skip it when unchanged.
    if _loaded.get(model_name) != pdf_path:
        assistant.load_pdf(pdf_path)
        _loaded[model_name] = pdf_path

    answer = assistant.ask(question)
    passages = "\n\n".join(f"**[{i}]** {p}" for i, p in enumerate(answer.sources, start=1))
    return answer.text, passages or "_No passage cleared the relevance threshold._"


with gr.Blocks(title="wick — offline PDF Q&A", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# wick\n"
        "Ask questions about a PDF using a language model that runs on your own "
        "machine — no API keys, no network. This Space is a preview; the real thing "
        "is a command-line tool that keeps working with the internet unplugged.\n\n"
        "[Source and install instructions →](https://github.com/armandamirchilou/wick)"
    )
    with gr.Row():
        with gr.Column():
            pdf = gr.File(label="PDF", file_types=[".pdf"], type="filepath")
            question = gr.Textbox(label="Question", placeholder="What does this document say about…")
            model = gr.Radio(list(CHOICES), value=FAST, label="Local model")
            submit = gr.Button("Ask", variant="primary")
        with gr.Column():
            answer = gr.Textbox(label="Answer", lines=10, show_copy_button=True)
            with gr.Accordion("Where this came from", open=False):
                sources = gr.Markdown()

    gr.Markdown(
        "Answers come only from the document. When the text doesn't contain the answer, "
        "wick says so instead of guessing — a similarity threshold rejects the question "
        "before the model ever sees it."
    )
    gr.Examples(examples=EXAMPLES, inputs=[pdf, question, model])

    for trigger in (submit.click, question.submit):
        trigger(ask, inputs=[pdf, question, model], outputs=[answer, sources])

if __name__ == "__main__":
    download_embedder(EMBED_MODEL)
    demo.queue(max_size=12).launch()
