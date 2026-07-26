import argparse
from pathlib import Path

from .pipeline import OfflineAssistant


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions about a PDF, fully offline.")
    parser.add_argument("pdf", type=Path, help="Path to the PDF file")
    parser.add_argument("question", help="Question to ask about the document")
    parser.add_argument("--model", type=Path, required=True, help="Path to a local GGUF model file")
    args = parser.parse_args()

    assistant = OfflineAssistant(model_path=args.model)
    assistant.load_pdf(args.pdf)
    print(assistant.ask(args.question))


if __name__ == "__main__":
    main()
