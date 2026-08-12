# wick

Ask questions about a PDF using a language model that runs on your own machine — no API keys, no account, no internet.

[![Try it in your browser](https://img.shields.io/badge/try%20it-in%20your%20browser-yellow?style=for-the-badge)](https://colab.research.google.com/github/ArmanDamirchilou/wick/blob/main/notebooks/try_wick.ipynb)
[![PyPI](https://img.shields.io/pypi/v/wick-offline?style=for-the-badge)](https://pypi.org/project/wick-offline/)
[![CI](https://github.com/armandamirchilou/wick/actions/workflows/ci.yml/badge.svg)](https://github.com/armandamirchilou/wick/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/armandamirchilou/wick/blob/main/LICENSE)

![wick answering questions about a PDF, offline](https://raw.githubusercontent.com/armandamirchilou/wick/main/docs/demo.gif)

## Try it

**[Run it in Colab →](https://colab.research.google.com/github/ArmanDamirchilou/wick/blob/main/notebooks/try_wick.ipynb)**
— installs the real package on a free machine and answers questions about a
document, including one you upload. Nothing to install locally.
(There's also a terminal recording: [asciinema cast](https://github.com/ArmanDamirchilou/wick/blob/main/docs/demo.cast).)

Or run it where it's meant to run — your own machine:

```bash
pip install "wick-offline[embeddings]"
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
wick --download-model
```

That's the only part that needs a connection. Now unplug it and point wick at a PDF:

```bash
wick your-document.pdf "What does it say about evacuation routes?"
```

Drop the question to keep asking without paying for the model load again:

```
$ wick your-document.pdf
your-document.pdf: 34 passages indexed. Ask a question, or press Ctrl-C to leave.

> What does it say about evacuation routes?
```

Real output, using the earthquake-safety guide in
[`examples/`](https://github.com/armandamirchilou/wick/tree/main/examples):

```
$ wick examples/earthquake-safety.pdf "What should I do if I am trapped under rubble?"

If you are trapped under rubble, tap steadily on a pipe or a wall so rescuers
can hear you. Do not shout unless you have no other option: shouting wastes
energy and makes you breathe in dangerous dust. Cover your mouth with cloth to
filter the air.
```

Ask something the document doesn't cover and it declines rather than guessing:

```
$ wick examples/earthquake-safety.pdf "What is the population of Tokyo?"

I don't know based on this document.
```

## Why

Internet access is something a lot of people take for granted. When it
disappears — through a blackout, a disaster, or a shutdown — access to
information shouldn't have to disappear with it. The tools in this space
mostly assume Docker, a stable connection, and someone comfortable in a
terminal. `wick` assumes a six-year-old laptop and no signal.

## Features

- Reads a PDF and chunks it for retrieval — no manual preprocessing.
- Runs with the network unplugged once a model is downloaded; the answering
  path puts the Hugging Face client in offline mode so it provably can't
  phone home.
- Answers only from the document. A similarity threshold rejects off-topic
  questions before the model sees them, so a small model can't quietly answer
  from its training data.
- `--show-sources` prints the passages an answer came from, so you can check
  it against the document instead of trusting it.
- Handles non-English documents, and picks the multilingual retrieval model on
  its own when the PDF isn't in Latin script — no flag to know about.
- A session (`wick doc.pdf` with no question) loads the model once and answers
  as many questions as you like: 2.1× faster over three questions in testing.
- Works with any local GGUF: Gemma, Phi, Qwen, Llama. Three are one flag away
  (`--download-model`), the rest take `--model /path/to.gguf`.
- Prints the answer and nothing else — no progress bars, no loader chatter.
  Status goes to stderr, so `wick doc.pdf "…" > answer.txt` gets just the answer.

## Non-English documents

Retrieval is a separate model from the one that writes the answer, and the
default only understands English — point it at a Persian PDF and it retrieves
nothing useful. wick checks the document's script and switches to a
multilingual encoder itself, so the only thing left to choose is a language
model that speaks the language:

```bash
wick --download-model --model-name gemma-3n-e2b
wick chapter.pdf "بیشتر آب کره زمین کجاست؟" --model-name gemma-3n-e2b
```

`--embed-model` still overrides the choice if you have a better encoder for
your language. See
[`docs/models.md`](https://github.com/armandamirchilou/wick/blob/main/docs/models.md)
for which model fits which hardware, with measured examples of what the small
ones get wrong.

## How it works

```
PDF → extract text → chunk → embed → FAISS index
                                          │
question → embed ──────────────────────► search ──► top-k chunks ──► local LLM ──► answer
```

Two design decisions are worth explaining:

**The relevance gate is what makes refusal reliable.** Telling a model "only
answer from the context" works on a large model and fails on a small one —
Qwen 0.5B will happily tell you the capital of France no matter what the
prompt says. So the refusal doesn't depend on the prompt: if the best-matching
chunk scores below a cosine-similarity threshold, the model is never called.
In testing, in-context questions scored 0.32–0.72 and out-of-context ones
0.00–0.10, in both English and Persian, which leaves a wide gap to put the
threshold in.

**Retrieval and generation are swappable, and separately.** `embeddings.py`
defines an `Embedder` protocol and `llm.py` wraps llama.cpp behind a two-method
class, so changing either one doesn't touch the pipeline. That's not
architecture for its own sake — it's the reason Persian support was a flag
rather than a rewrite, and the reason a contributor can add a backend without
reading the rest of the codebase.

FAISS uses a flat index with inner product over normalized vectors, which is
exact cosine similarity. Fine to a few thousand chunks; past that it's a real
problem to solve, but not this one.

## Local setup

Requires Python 3.10+. The second install line pulls a prebuilt CPU wheel for
`llama-cpp-python`, so you don't need a C++ toolchain — this is also the only
reliable path on Windows, where building from source hits the 260-character
path limit. With a compiler available, `pip install "wick-offline[embeddings,llm]"`
works instead.

Models land in `~/.wick/models` (`./models` is also checked). Nothing else is
written outside that directory.

Running from a clone:

```bash
git clone https://github.com/armandamirchilou/wick.git
cd wick
pip install -e ".[embeddings,dev]"
pytest
```

On Windows, [`demo.ps1`](https://github.com/armandamirchilou/wick/blob/main/demo.ps1) runs the whole walkthrough — English and
Persian — in one go.

## Roadmap

- **v0.2 (current)** — one-command install, hosted demo, verified Persian support.
- **v0.3** — School use: point it at a textbook chapter, ask curriculum questions.
- **v0.4** — Crisis packs: pre-built offline guides (first aid, earthquake, fire).
- **v0.5** — Accessibility: plain-language explanations for things like medication leaflets.

See [`CHANGELOG.md`](https://github.com/armandamirchilou/wick/blob/main/CHANGELOG.md) for what's actually shipped.

## Contributing

Contributions welcome — see [`CONTRIBUTING.md`](https://github.com/armandamirchilou/wick/blob/main/CONTRIBUTING.md) for setup,
workflow, and commit conventions. Issues labeled `good first issue` are a
place to start.

## Credits

Built on [llama.cpp](https://github.com/ggerganov/llama.cpp) (via
[llama-cpp-python](https://github.com/abetlen/llama-cpp-python)),
[sentence-transformers](https://www.sbert.net/),
[FAISS](https://github.com/facebookresearch/faiss), and
[pypdf](https://github.com/py-pdf/pypdf). Models by Alibaba (Qwen2.5) and
Google (Gemma 3n), quantized builds from
[Unsloth](https://huggingface.co/unsloth).

## License

MIT — see [`LICENSE`](https://github.com/armandamirchilou/wick/blob/main/LICENSE).
