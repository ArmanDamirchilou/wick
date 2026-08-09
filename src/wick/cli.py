import argparse
import logging
import os
import sys
from pathlib import Path

from . import models
from .pipeline import OfflineAssistant


def main() -> None:
    # Non-English answers must survive a legacy Windows console code page.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Ask questions about a PDF, fully offline.")
    parser.add_argument("pdf", type=Path, nargs="?", help="Path to the PDF file")
    parser.add_argument("question", nargs="?", help="Question to ask about the document")
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
        help="Download the catalog model and exit — the only step that needs internet",
    )
    parser.add_argument(
        "--embed-model",
        default="all-MiniLM-L6-v2",
        help="Retrieval model; use a multilingual one "
        "(e.g. paraphrase-multilingual-MiniLM-L12-v2) for non-English PDFs",
    )
    args = parser.parse_args()

    try:
        if args.download_model:
            print(f"Language model: {models.download(args.model_name)}")
            models.download_embedder(args.embed_model)
            print(f"Retrieval model: {args.embed_model}")
            print("Done — from here on wick needs no internet.")
            return
        if args.pdf is None or args.question is None:
            parser.error("a PDF and a question are required (or use --download-model)")

        _go_offline()
        model_path = models.resolve(args.model, args.model_name)
        assistant = OfflineAssistant(model_path=model_path, embed_model=args.embed_model)
        assistant.load_pdf(args.pdf)
        print(assistant.ask(args.question))
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        sys.exit(f"error: {e}")


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
