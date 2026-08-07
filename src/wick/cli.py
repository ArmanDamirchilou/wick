import argparse
import sys
from pathlib import Path

from .pipeline import OfflineAssistant


def main() -> None:
    # Non-English answers must survive a legacy Windows console code page.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Ask questions about a PDF, fully offline.")
    parser.add_argument("pdf", type=Path, help="Path to the PDF file")
    parser.add_argument("question", help="Question to ask about the document")
    parser.add_argument("--model", type=Path, required=True, help="Path to a local GGUF model file")
    parser.add_argument(
        "--embed-model",
        default="all-MiniLM-L6-v2",
        help="Retrieval model; use a multilingual one "
        "(e.g. paraphrase-multilingual-MiniLM-L12-v2) for non-English PDFs",
    )
    args = parser.parse_args()

    try:
        assistant = OfflineAssistant(model_path=args.model, embed_model=args.embed_model)
        assistant.load_pdf(args.pdf)
        print(assistant.ask(args.question))
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
