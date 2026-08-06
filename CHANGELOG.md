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

### Changed
- Answers are generated through each model's own chat template (llama.cpp chat
  completion) instead of a hand-written prompt with a hardcoded `</s>` stop
  token, so Gemma, Qwen, Phi, and Llama GGUFs all format correctly.

## [0.1.0] - 2026-07-26

### Added
- Initial project scaffold: PDF ingestion, chunking, local embeddings, a FAISS
  vector store, and a llama.cpp-backed CLI for asking offline questions.
- Test suite covering chunking and retrieval logic (no model download needed to run it).
- CI, contribution guide, and issue/PR templates.
