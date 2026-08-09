# Contributing

Thanks for looking at this — it's a young project and there's a lot of room
to shape it. This doc covers how to get set up and how changes get merged.

## Getting set up

```bash
git clone https://github.com/armandamirchilou/wick.git
cd wick
pip install -e ".[dev]"
pytest
```

That installs the core package plus test/lint tooling. You don't need a
model file or the `embeddings`/`llm` extras just to run the test suite —
those are only required if you're actually running the assistant end to end.

To run it for real:

```bash
pip install -e ".[embeddings]"
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
wick --download-model
```

The prebuilt wheel avoids needing a C++ toolchain; `pip install -e ".[embeddings,llm]"`
builds from source if you'd rather. See `docs/models.md` for other models.

### Integration test

The default `pytest` run is fully mocked and needs no model or network. A
separate end-to-end test (marked `integration`) runs a real GGUF model over a
sample PDF and is deselected by default — including in CI. To run it, point
`WICK_TEST_MODEL` at a local model and select the marker:

```bash
WICK_TEST_MODEL=./models/your-model.gguf pytest -m integration
```

On Windows PowerShell:

```powershell
$env:WICK_TEST_MODEL = ".\models\your-model.gguf"; pytest -m integration
```

## Workflow

1. Open an issue first for anything beyond a small fix, so we can agree on
   direction before you put time into it. Issues labeled `good first issue`
   are a solid place to start.
2. Branch off `main`: `feature/<short-description>` or `fix/<short-description>`.
3. Keep PRs focused — one logical change per PR is much easier to review
   than a PR that touches five things.
4. Make sure `pytest` and `ruff check .` both pass before opening the PR.
5. Fill in the PR template. Link the issue it closes if there is one.

## Commit messages

```
<type>: <imperative, present-tense summary>

Optional body explaining why, not what — the diff already shows what changed.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`.

```
feat: add Persian sentence-transformers backend

The default MiniLM model handles Farsi poorly. Swapping in a
multilingual encoder fixes retrieval quality for non-English PDFs.
```

## Code style

- Run `ruff check .` before pushing — CI will fail the build otherwise.
- Match the style of the file you're editing.
- Comments should explain *why*, not narrate *what* the code already says.
- Prefer flat, early-return logic over deep nesting.

## Versioning

This project uses [Semantic Versioning](https://semver.org/). Every release
gets a git tag (`v0.2.0`, etc.) and a `CHANGELOG.md` entry. If your PR is
user-facing, add a line under `[Unreleased]` in the changelog.
