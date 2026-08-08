# wick

An offline AI assistant that answers questions from local documents, no internet connection required.

![CI](https://github.com/armandamirchilou/wick/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)

## Why

Internet access is something a lot of people take for granted. When it
disappears — through a blackout, a disaster, or a shutdown — access to
information shouldn't have to disappear with it. `wick` reads a PDF once,
then answers questions about it entirely offline: no API calls, no signal,
no dependency on a network that might not be there when it matters most.

## Quick start

Install the retrieval backend, then a prebuilt CPU build of the model runtime:

```bash
pip install -e ".[embeddings]"
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

The second line grabs a prebuilt `llama-cpp-python` wheel, so you don't need a
C++ compiler (this is also the reliable path on Windows). If you have a
toolchain and would rather build from source, `pip install -e ".[embeddings,llm]"`
works too.

Download a local model (see [`docs/models.md`](docs/models.md) for picks suited
to weak hardware), then ask a question:

```bash
wick examples/earthquake-safety.pdf "What should I do during the shaking?" --model ./models/your-model.gguf
```

For a non-English document, add a multilingual retrieval model so the search
step understands the language:

```bash
wick chapter.pdf "این فصل درباره چیست؟" --model ./models/your-model.gguf --embed-model paraphrase-multilingual-MiniLM-L12-v2
```

## Example

Real output, using the bundled example guide and a Gemma 3n model:

```
$ wick examples/earthquake-safety.pdf "What should I do if I am trapped under rubble?" --model ./models/gemma-3n-E2B-it-Q4_K_M.gguf

If you are trapped under rubble, tap steadily on a pipe or a wall so rescuers
can hear you. Do not shout unless you have no other option: shouting wastes
energy and makes you breathe in dangerous dust. Cover your mouth with cloth to
filter the air.
```

Ask something the document doesn't cover and it declines rather than guessing:

```
$ wick examples/earthquake-safety.pdf "What is the population of Tokyo?" --model ./models/gemma-3n-E2B-it-Q4_K_M.gguf

I don't know based on this document.
```

On Windows, [`demo.ps1`](demo.ps1) runs this whole walkthrough — English and
Persian — in one go:

```powershell
.\demo.ps1 -Model .\models\gemma-3n-E2B-it-Q4_K_M.gguf
```

## Features

- Reads a PDF and chunks it for retrieval — no manual preprocessing needed.
- Runs fully offline once the model is downloaded: no API keys, no cloud calls.
- Answers only from the document — when the text doesn't contain the answer, it
  says so instead of making one up.
- Handles non-English documents with a multilingual retrieval model (tested on
  Persian).
- Works with local GGUF models — Gemma, Phi, Qwen, or Llama, your choice.
- Swappable embedding and LLM backends behind clean interfaces, so
  contributors can add new ones without touching the pipeline.

## How it works

```
PDF → extract text → chunk → embed → FAISS index
                                          │
question → embed ──────────────────────► search ──► top-k chunks ──► local LLM ──► answer
```

Retrieval and generation are two separate, swappable pieces
(`embeddings.py` / `llm.py`), so a contributor can drop in a different
embedding model or inference backend without touching the rest of the
pipeline.

## Roadmap

- **v0.1 (current)** — MVP: PDF in, offline Q&A out, runs on a laptop.
- **v0.2** — School use: point it at a textbook chapter, ask curriculum-shaped questions.
- **v0.3** — Crisis packs: pre-built offline guides (first aid, earthquake, fire).
- **v0.4** — Accessibility: plain-language explanations for things like medication leaflets.

See [`CHANGELOG.md`](CHANGELOG.md) for what's actually shipped so far.

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) for
setup, workflow, and commit conventions. Check open issues labeled
`good first issue` for a place to start.

## License

MIT — see [`LICENSE`](LICENSE).
