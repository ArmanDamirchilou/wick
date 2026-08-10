# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and version numbers follow [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).

## [Unreleased]

### Added
- Session mode: `wick document.pdf` with no question loads the model once and
  answers as many questions as you type. Three questions took 33.4s as separate
  commands and 15.7s in a session.
- `--show-sources` prints the passages an answer was drawn from, so the claim
  that answers come only from the document is checkable rather than trusted.
- The retrieval model is chosen from the document's script, so a Persian or
  Hindi PDF works without knowing that `--embed-model` exists.

### Changed
- `OfflineAssistant.ask()` returns an `Answer` with `.text` and `.sources`
  instead of a bare string.
- CI runs on Windows as well as Linux, across Python 3.10 and 3.12, and builds
  the package on every push.

## [0.2.0] - 2026-08-09

### Added
- `wick --download-model` fetches a model and the retrieval encoder in one
  step, so getting from install to a first answer is two commands.
- `--model` is now optional: wick looks for a downloaded model in `./models`
  and `~/.wick/models` before asking for a path.
- `--model-name` to pick from a small catalog: Qwen2.5 1.5B (the default,
  1.1 GB), Qwen2.5 0.5B for very weak machines, and the multilingual
  Gemma 3n E2B. Qwen2.5 0.5B was the first default and lost the job for
  answering "I don't know" to questions the document plainly answers.
- A Gradio demo (`space/`) and a deploy script, so the tool can be tried in a
  browser without downloading a model first.
- `scripts/record_demo.py`, which runs the real CLI and turns the captured
  output into the terminal recording in the README.
- Clear error message when the `--model` path doesn't point at a real file.
- Explicit errors for a missing PDF, a corrupt/non-PDF file, and a scanned or
  image-only PDF with no extractable text (instead of silently producing an
  empty index).
- `--embed-model` flag to choose the sentence-transformers retrieval model —
  point it at a multilingual encoder for non-English (e.g. Persian) PDFs.
- Retrieval relevance gate: a question whose best-matching chunk scores below a
  similarity threshold is answered "I don't know based on this document."
  rather than handed to the model, so a weak local model can't quietly answer
  out-of-context questions from its own training data.
- Bundled example documents (an English earthquake-safety guide and a Persian
  water-cycle chapter) and a `demo.ps1` walkthrough for a quick end-to-end run.

### Changed
- Published to PyPI as `wick-offline` — the `wick` name was already taken by an
  unrelated package. The import name and the command are still `wick`.
- Answering runs with the Hugging Face hub client in offline mode, so a cached
  setup provably makes no network calls.
- Answers are generated through each model's own chat template (llama.cpp chat
  completion) instead of a hand-written prompt with a hardcoded `</s>` stop
  token, so Gemma, Qwen, Phi, and Llama GGUFs all format correctly.
- The CLI reports failures as a single `error: ...` line and exits non-zero
  instead of printing a traceback.

### Fixed
- Loader progress bars, hub warnings, and llama.cpp backend notes no longer
  bury the answer — the CLI prints the answer and nothing else.
- Non-English answers (e.g. Persian) no longer crash the CLI with a
  `UnicodeEncodeError` on a legacy Windows console — stdout/stderr are set to
  UTF-8.

## [0.1.0] - 2026-07-26

### Added
- Initial project scaffold: PDF ingestion, chunking, local embeddings, a FAISS
  vector store, and a llama.cpp-backed CLI for asking offline questions.
- Test suite covering chunking and retrieval logic (no model download needed to run it).
- CI, contribution guide, and issue/PR templates.
