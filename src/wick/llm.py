from pathlib import Path


class LocalLLM:
    """Point this at any GGUF model file on disk — Gemma, Phi, Qwen, Llama all work."""

    def __init__(self, model_path: Path, *, n_ctx: int = 4096):
        from llama_cpp import Llama

        self.llm = Llama(model_path=str(model_path), n_ctx=n_ctx, verbose=False)

    def answer(self, question: str, context: list[str]) -> str:
        prompt = self._build_prompt(question, context)
        out = self.llm(prompt, max_tokens=512, stop=["</s>"])
        return out["choices"][0]["text"].strip()

    @staticmethod
    def _build_prompt(question: str, context: list[str]) -> str:
        joined = "\n\n".join(context)
        return (
            "Answer the question using only the context below. "
            "If the context doesn't contain the answer, say so.\n\n"
            f"Context:\n{joined}\n\nQuestion: {question}\nAnswer:"
        )
