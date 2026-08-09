import ctypes
from pathlib import Path

REFUSAL = "I don't know based on this document."

# Module-level so ctypes doesn't collect the callback while llama.cpp still holds it.
_SILENCE = None


class LocalLLM:
    """Point this at any GGUF model file on disk — Gemma, Phi, Qwen, Llama all work."""

    def __init__(self, model_path: Path, *, n_ctx: int = 4096):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Download a GGUF model and pass its path with --model (see docs/models.md)."
            )
        import llama_cpp
        from llama_cpp import Llama

        _silence_llama_cpp(llama_cpp)
        self.llm = Llama(model_path=str(model_path), n_ctx=n_ctx, verbose=False)

    def answer(self, question: str, context: list[str]) -> str:
        # Chat completion applies each GGUF's own template, so stop tokens are always right.
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


def _silence_llama_cpp(llama_cpp) -> None:
    # verbose=False still lets the C library write backend notes to stderr.
    global _SILENCE
    if _SILENCE is None:
        _SILENCE = llama_cpp.llama_log_callback(lambda level, text, user_data: None)
        llama_cpp.llama_log_set(_SILENCE, ctypes.c_void_p(0))
