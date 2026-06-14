"""Provider-agnostic LLM layer.

A single ``complete(system, user, model)`` call backed by either the Anthropic
API or any OpenAI-compatible endpoint (Ollama / vLLM serving Qwen, etc.).
Switching backend is one env var (LLM_BACKEND) — the rest of the pipeline is
unaware of which provider answered.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import settings


class LLMError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _anthropic_client():
    import anthropic

    if not settings.anthropic_api_key:
        raise LLMError("ANTHROPIC_API_KEY is not set but LLM_BACKEND=anthropic")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


@lru_cache(maxsize=1)
def _openai_client():
    from openai import OpenAI

    # api_key is required by the client but ignored by Ollama; vLLM may check it.
    return OpenAI(base_url=settings.local_base_url, api_key=settings.local_api_key)


def _complete_anthropic(system: str, user: str, *, model: str, max_tokens: int) -> str:
    resp = _anthropic_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


def _complete_local(system: str, user: str, *, model: str, max_tokens: int) -> str:
    resp = _openai_client().chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (resp.choices[0].message.content or "").strip()


def complete(system: str, user: str, *, model: str, max_tokens: int = 2000) -> str:
    """Return the model's text response for a single-turn system+user prompt."""
    backend = settings.llm_backend.lower()
    if backend == "anthropic":
        return _complete_anthropic(system, user, model=model, max_tokens=max_tokens)
    if backend == "local":
        return _complete_local(system, user, model=model, max_tokens=max_tokens)
    raise LLMError(f"Unknown LLM_BACKEND: {settings.llm_backend!r}")
