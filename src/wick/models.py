from pathlib import Path
from typing import NamedTuple


class Model(NamedTuple):
    repo: str
    filename: str
    size: str


# Q4_K_M throughout — the quantization that fits weak hardware (see docs/models.md).
CATALOG = {
    "qwen2.5-0.5b": Model(
        "Qwen/Qwen2.5-0.5B-Instruct-GGUF", "qwen2.5-0.5b-instruct-q4_k_m.gguf", "0.5 GB"
    ),
    "qwen2.5-1.5b": Model(
        "Qwen/Qwen2.5-1.5B-Instruct-GGUF", "qwen2.5-1.5b-instruct-q4_k_m.gguf", "1.1 GB"
    ),
    "gemma-3n-e2b": Model(
        "unsloth/gemma-3n-E2B-it-GGUF", "gemma-3n-E2B-it-Q4_K_M.gguf", "3.0 GB"
    ),
}

DEFAULT_MODEL = "qwen2.5-1.5b"

# A repo checkout with models already in ./models shouldn't re-download.
SEARCH_DIRS = (Path("models"), Path.home() / ".wick" / "models")


def download(name: str = DEFAULT_MODEL) -> Path:
    """Fetch a catalog model into ~/.wick/models — resumable, so a dropped connection can retry."""
    model = _catalog_entry(name)
    from huggingface_hub import hf_hub_download

    destination = Path.home() / ".wick" / "models"
    destination.mkdir(parents=True, exist_ok=True)
    return Path(hf_hub_download(model.repo, model.filename, local_dir=destination))


def download_embedder(model_name: str) -> None:
    """Warm the retrieval model's cache so the answering path never touches the network."""
    from .embeddings import SentenceTransformerEmbedder

    SentenceTransformerEmbedder(model_name)


def resolve(explicit: Path | None, name: str = DEFAULT_MODEL) -> Path:
    """Turn an optional --model path into a real GGUF file, or explain what's missing."""
    if explicit is not None:
        return explicit
    model = _catalog_entry(name)
    for directory in SEARCH_DIRS:
        candidate = directory / model.filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No local copy of {name} found.\n"
        f"Run 'wick --download-model' to fetch it ({model.size}, one time), "
        "or pass --model with the path to a GGUF file you already have."
    )


def _catalog_entry(name: str) -> Model:
    if name not in CATALOG:
        raise ValueError(f"Unknown model '{name}'. Available: {', '.join(CATALOG)}")
    return CATALOG[name]
