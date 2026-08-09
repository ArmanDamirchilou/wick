from pathlib import Path

# Q4_K_M throughout — the quantization that fits weak hardware (see docs/models.md).
CATALOG = {
    "qwen2.5-0.5b": ("Qwen/Qwen2.5-0.5B-Instruct-GGUF", "qwen2.5-0.5b-instruct-q4_k_m.gguf"),
    "gemma-3n-e2b": ("unsloth/gemma-3n-E2B-it-GGUF", "gemma-3n-E2B-it-Q4_K_M.gguf"),
}

# ~400 MB, so a first download finishes on a bad connection; bigger picks stay opt-in.
DEFAULT_MODEL = "qwen2.5-0.5b"

# A repo checkout with models already in ./models shouldn't re-download.
SEARCH_DIRS = (Path("models"), Path.home() / ".wick" / "models")


def download(name: str = DEFAULT_MODEL) -> Path:
    """Fetch a catalog model into ~/.wick/models — resumable, so a dropped connection can retry."""
    repo, filename = _catalog_entry(name)
    from huggingface_hub import hf_hub_download

    destination = Path.home() / ".wick" / "models"
    destination.mkdir(parents=True, exist_ok=True)
    return Path(hf_hub_download(repo, filename, local_dir=destination))


def download_embedder(model_name: str) -> None:
    """Warm the retrieval model's cache so the answering path never touches the network."""
    from .embeddings import _import_sentence_transformers

    _import_sentence_transformers()(model_name)


def resolve(explicit: Path | None, name: str = DEFAULT_MODEL) -> Path:
    """Turn an optional --model path into a real GGUF file, or explain what's missing."""
    if explicit is not None:
        return explicit
    _, filename = _catalog_entry(name)
    for directory in SEARCH_DIRS:
        candidate = directory / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No local copy of {name} found.\n"
        "Run 'wick --download-model' to fetch it (~400 MB, one time), "
        "or pass --model with the path to a GGUF file you already have."
    )


def _catalog_entry(name: str) -> tuple[str, str]:
    if name not in CATALOG:
        raise ValueError(f"Unknown model '{name}'. Available: {', '.join(CATALOG)}")
    return CATALOG[name]
