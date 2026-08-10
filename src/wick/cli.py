import argparse
import logging
import os
import sys
from pathlib import Path

from . import models
from .ingest import extract_text
from .pipeline import Answer, OfflineAssistant

ENGLISH_EMBED = "all-MiniLM-L6-v2"
MULTILINGUAL_EMBED = "paraphrase-multilingual-MiniLM-L12-v2"


def main() -> None:
    # Non-English answers must survive a legacy Windows console code page.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    args = parse_args()
    try:
        if args.download_model:
            download(args)
            return

        _go_offline()
        text = extract_text(args.pdf)
        embed_model = args.embed_model or pick_embed_model(text)
        assistant = OfflineAssistant(
            model_path=models.resolve(args.model, args.model_name), embed_model=embed_model
        )
        assistant.load_text(text)

        if args.question:
            report(assistant.ask(args.question), args.show_sources)
            return
        converse(assistant, args.pdf, args.show_sources)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        sys.exit(f"error: {e}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask questions about a PDF, fully offline.",
        epilog="Omit the question to open a session and ask several without reloading the model.",
    )
    parser.add_argument("pdf", type=Path, nargs="?", help="Path to the PDF file")
    parser.add_argument("question", nargs="?", help="Question to ask; omit for a session")
    parser.add_argument(
        "--model",
        type=Path,
        help="Path to a local GGUF model file; defaults to the downloaded catalog model",
    )
    parser.add_argument(
        "--model-name",
        default=models.DEFAULT_MODEL,
        choices=sorted(models.CATALOG),
        help="Which catalog model to download or look for",
    )
    parser.add_argument(
        "--download-model",
        action="store_true",
        help="Download the models and exit — the only step that needs internet",
    )
    parser.add_argument(
        "--embed-model",
        help=f"Retrieval model (default: {ENGLISH_EMBED}, "
        f"or {MULTILINGUAL_EMBED} when the document isn't in Latin script)",
    )
    parser.add_argument(
        "--show-sources",
        action="store_true",
        help="Print the passages the answer was drawn from",
    )
    args = parser.parse_args()
    if not args.download_model and args.pdf is None:
        parser.error("a PDF is required (or use --download-model)")
    return args


def download(args: argparse.Namespace) -> None:
    print(f"Language model: {models.download(args.model_name)}")
    for embed_model in {args.embed_model or ENGLISH_EMBED, MULTILINGUAL_EMBED}:
        models.download_embedder(embed_model)
        print(f"Retrieval model: {embed_model}")
    print("Done — from here on wick needs no internet.")


def pick_embed_model(text: str) -> str:
    """The English default can't retrieve from a Persian or Hindi document at all."""
    letters = [char for char in text if char.isalpha()]
    non_latin = sum(1 for char in letters if ord(char) > 0x24F)
    return MULTILINGUAL_EMBED if letters and non_latin > len(letters) * 0.2 else ENGLISH_EMBED


def converse(assistant: OfflineAssistant, pdf: Path, show_sources: bool) -> None:
    print(
        f"{pdf.name}: {assistant.passages} passages indexed. "
        "Ask a question, or press Ctrl-C to leave.",
        file=sys.stderr,
    )
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(file=sys.stderr)
            return
        if question:
            report(assistant.ask(question), show_sources)


def report(answer: Answer, show_sources: bool) -> None:
    print(answer.text, flush=True)  # sources go to stderr, so keep the streams in order
    if not show_sources:
        return
    for index, passage in enumerate(answer.sources, start=1):
        print(f"\n[{index}] {excerpt(passage)}", file=sys.stderr)


def excerpt(passage: str, limit: int = 240) -> str:
    collapsed = " ".join(passage.split())
    return collapsed if len(collapsed) <= limit else collapsed[:limit].rstrip() + "…"


def _go_offline() -> None:
    # Answering is a no-network operation; the hub client is told so before it loads.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"
    for name in ("huggingface_hub", "sentence_transformers", "transformers"):
        logging.getLogger(name).setLevel(logging.ERROR)


if __name__ == "__main__":
    main()
