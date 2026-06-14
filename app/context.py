"""Build the schema context that is fed to the model.

MVP-0: load every markdown file under ``knowledge/`` and concatenate it. This is
the single extension point for the future RAG phase — replace the body of
``build_context`` with a top-k retrieval over a vector store; its signature
already takes the user's question.
"""
from __future__ import annotations

from app.config import KNOWLEDGE_DIR


def _read_section(path) -> str:
    rel = path.relative_to(KNOWLEDGE_DIR)
    return f"# === {rel} ===\n{path.read_text(encoding='utf-8').strip()}\n"


def build_context(question: str | None = None) -> str:  # noqa: ARG001 (question unused in MVP-0)
    """Return the schema knowledge base as one string.

    ``question`` is accepted but ignored in MVP-0; in the RAG phase it will drive
    top-k retrieval so the prompt only carries the relevant slices.
    """
    if not KNOWLEDGE_DIR.exists():
        return ""
    parts = [_read_section(p) for p in sorted(KNOWLEDGE_DIR.rglob("*.md"))]
    return "\n".join(parts)
