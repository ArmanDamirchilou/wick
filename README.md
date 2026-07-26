# wick

*(working name — see [naming note](#naming-note) below)*

An offline AI assistant that answers questions from local documents, no internet connection required.

<!-- TODO before shipping: replace with a real screenshot or short GIF of the CLI in action -->
<!-- TODO before shipping: replace with your live demo link once deployed -->
**[Try it →](#)**

![CI](https://github.com/<your-username>/wick/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)

## Why

Internet access is something a lot of people take for granted. When it
disappears — through a blackout, a disaster, or a shutdown — access to
information shouldn't have to disappear with it. `wick` reads a PDF once,
then answers questions about it entirely offline: no API calls, no signal,
no dependency on a network that might not be there when it matters most.

## Quick start

```bash
pip install -e ".[embeddings,llm]"
```

Download a local model (see [`docs/models.md`](docs/models.md) for picks
suited to weak hardware), then:

```bash
wick document.pdf "Explain chapter 3" --model ./models/your-model.gguf
```

## Features

- Reads a PDF and chunks it for retrieval — no manual preprocessing needed.
- Runs fully offline once the model is downloaded: no API keys, no cloud calls.
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

## Naming note

`wick` is a placeholder while the project is young. If you're reading this
after the rename, the name below the title is stale — open an issue.

## License

MIT — see [`LICENSE`](LICENSE).
