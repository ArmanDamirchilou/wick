# Choosing a model

`wick` doesn't ship a model — you point it at any local GGUF file. Model
weights are multi-GB binaries, which is why they're git-ignored instead of
committed. Pick based on how weak the target laptop is and which languages
it needs to handle:

| Hardware ceiling | Model | Notes |
|---|---|---|
| ~4 GB RAM | Phi-4-mini (Q4_K_M) | Smallest footprint, English-strongest |
| ~8 GB RAM, multilingual | Gemma 3n E2B/E4B | Trained on 140+ languages — the better pick for Persian/Dari |
| ~8 GB RAM, multilingual | Qwen3 4B | Strong cross-lingual handling, slightly slower on CPU |

Download a GGUF build from Hugging Face (search `<model name> GGUF`) and pass
its path with `--model`:

```bash
wick document.pdf "Explain chapter 3" --model ./models/gemma-3n-e4b-q4_k_m.gguf
```

Always grab the `Q4_K_M` or `Q5_K_M` quantization unless you've confirmed the
target hardware can handle more — those cut file size roughly 60–75% with
only a small quality hit, which is usually the difference between "runs on
a six-year-old laptop" and "doesn't."

## Non-English documents

The `--model` above is the language model that writes the answer. Retrieval —
finding the right passage to answer from — is a *separate* model, and the
default (`all-MiniLM-L6-v2`) only handles English. For a non-English PDF, pass a
multilingual retrieval model as well:

```bash
wick chapter.pdf "این فصل درباره چیست؟" --model ./models/gemma-3n-e2b-q4_k_m.gguf \
  --embed-model paraphrase-multilingual-MiniLM-L12-v2
```

Pair it with a multilingual language model — Gemma 3n is a good pick (see the
table above). This path is tested end to end on Persian.
