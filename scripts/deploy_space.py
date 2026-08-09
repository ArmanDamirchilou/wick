"""Push space/ and the example PDFs to a Hugging Face Space.

Usage (from the repo root):
    huggingface-cli login
    python scripts/deploy_space.py <your-hf-username>/wick
"""

import sys
from pathlib import Path

from huggingface_hub import HfApi

REPO = Path(__file__).resolve().parent.parent


def main(space_id: str) -> None:
    api = HfApi()
    api.create_repo(space_id, repo_type="space", space_sdk="gradio", exist_ok=True)
    for source, target in [(REPO / "space", "."), (REPO / "examples", "examples")]:
        api.upload_folder(
            folder_path=str(source), path_in_repo=target,
            repo_id=space_id, repo_type="space",
        )
    print(f"https://huggingface.co/spaces/{space_id}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
