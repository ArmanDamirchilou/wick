# Choosing a model

`wick` doesn't bundle a model — weights are multi-GB binaries, so they're
downloaded once and git-ignored. `wick --download-model` fetches the default
and you never think about it again:

```bash
wick --download-model                          # Qwen2.5 0.5B, ~400 MB
wick --download-model --model-name gemma-3n-e2b  # Gemma 3n E2B, ~3 GB
```

Downloads land in `~/.wick/models`, and `wick` looks there (and in `./models`)
automatically, so `--model` is only needed for a GGUF from somewhere else.

## Which one

| Hardware ceiling | Model | `--model-name` | Notes |
|---|---|---|---|
| ~2 GB RAM | Qwen2.5 0.5B (Q4_K_M) | `qwen2.5-0.5b` | The default. Tiny and fast; English answers are short but accurate |
| ~8 GB RAM, multilingual | Gemma 3n E2B (Q4_K_M) | `gemma-3n-e2b` | Trained on 140+ languages — the pick for Persian/Dari |

Any other GGUF works too — Phi-4-mini for a smaller English-only footprint,
Qwen3 4B for stronger cross-lingual handling:

```bash
wick document.pdf "Explain chapter 3" --model ./phi-4-mini-q4_k_m.gguf
```

Always grab the `Q4_K_M` or `Q5_K_M` quantization unless you've confirmed the
target hardware can handle more — those cut file size roughly 60–75% with
only a small quality hit, which is usually the difference between "runs on
a six-year-old laptop" and "doesn't."

## Non-English documents

The model above is the language model that writes the answer. Retrieval —
finding the right passage to answer from — is a *separate* model, and the
default (`all-MiniLM-L6-v2`) only handles English. A non-English PDF needs a
multilingual retrieval model downloaded alongside a multilingual LLM:

```bash
wick --download-model --model-name gemma-3n-e2b \
  --embed-model paraphrase-multilingual-MiniLM-L12-v2

wick chapter.pdf "این فصل درباره چیست؟" --model-name gemma-3n-e2b \
  --embed-model paraphrase-multilingual-MiniLM-L12-v2
```

A multilingual LLM on its own isn't enough: if retrieval can't find the right
passage, the relevance gate correctly refuses and you get "I don't know based
on this document." This path is tested end to end on Persian.
