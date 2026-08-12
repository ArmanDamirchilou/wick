---
title: wick — offline PDF Q&A
emoji: 🕯️
colorFrom: yellow
colorTo: gray
sdk: gradio
sdk_version: 6.23.1
app_file: app.py
pinned: false
license: mit
---

A hosted preview of [wick](https://github.com/armandamirchilou/wick), a
command-line assistant that answers questions about a local PDF with no
internet connection.

The Space installs the package straight from the repository's `main` branch and
runs it unmodified, so what you see here is what you get after installing it
yourself. The difference is where the model runs: here it's on a shared CPU,
and on your own machine it's yours — with the network unplugged.

The first answer after a restart is slow, because the model is still being
fetched in the background. Later answers take a few seconds.

> Deploying this needs a Hugging Face PRO subscription — since 2026, Gradio
> Spaces on free CPU return `402 Payment Required`. The equivalent free demo is
> the [Colab notebook](https://colab.research.google.com/github/ArmanDamirchilou/wick/blob/main/notebooks/try_wick.ipynb),
> which is what the README links to. Deploy this one with
> `python scripts/deploy_space.py <user>/wick`.
