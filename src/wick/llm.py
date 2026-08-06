from pathlib import Path

REFUSAL = "I don't know based on this document."


class LocalLLM:
    """Point this at any GGUF model file on disk — Gemma, Phi, Qwen, Llama all work."""

    def __init__(self, model_path: Path, *, n_ctx: int = 4096):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Download a GGUF model and pass its path with --model (see docs/models.md)."
            )
        from llama_cpp import Llama

        self.llm = Llama(model_path=str(model_path), n_ctx=n_ctx, verbose=False)

    def answer(self, question: str, context: list[str]) -> str:
        # Chat completion applies the model's own template from the GGUF metadata,
        # so the right turn/stop tokens are used whether it's Gemma, Qwen, or Llama.
        out = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": self._build_prompt(question, context)}],
            max_tokens=512,
            temperature=0.0,
        )
        return out["choices"][0]["message"]["content"].strip()

    @staticmethod
    def _build_prompt(question: str, context: list[str]) -> str:
        joined = "\n\n".join(context) if context else "(no relevant context found)"
        return (
            "Use only the context below to answer the question. "
            f'If the answer is not in the context, reply exactly: "{REFUSAL}" '
            "Do not use any outside knowledge. Reply in the same language as the question.\n\n"
            f"Context:\n{joined}\n\n"
            f"Question: {question}\n\n"
            "Answer using only the context above."
        )
