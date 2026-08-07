# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and version numbers follow [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).

## [Unreleased]

### Added
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
- Answers are generated through each model's own chat template (llama.cpp chat
  completion) instead of a hand-written prompt with a hardcoded `</s>` stop
  token, so Gemma, Qwen, Phi, and Llama GGUFs all format correctly.
- The CLI reports failures as a single `error: ...` line and exits non-zero
  instead of printing a traceback.

### Fixed
- Non-English answers (e.g. Persian) no longer crash the CLI with a
  `UnicodeEncodeError` on a legacy Windows console — stdout/stderr are set to
  UTF-8.

## [0.1.0] - 2026-07-26

### Added
- Initial project scaffold: PDF ingestion, chunking, local embeddings, a FAISS
  vector store, and a llama.cpp-backed CLI for asking offline questions.
- Test suite covering chunking and retrieval logic (no model download needed to run it).
- CI, contribution guide, and issue/PR templates.
