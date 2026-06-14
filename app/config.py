"""Central configuration, loaded from environment / .env."""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM backend: "anthropic" or "local" (OpenAI-compatible).
    llm_backend: str = "anthropic"

    # Anthropic backend
    anthropic_api_key: str = ""
    generation_model: str = "claude-opus-4-8"
    interpretation_model: str = "claude-haiku-4-5"

    # Local backend (Ollama / vLLM, OpenAI-compatible)
    local_base_url: str = "http://localhost:11434/v1"
    local_api_key: str = "ollama"

    # ClickHouse (read-only user)
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_user: str = "assistant_ro"
    clickhouse_password: str = "readonly_pw"
    clickhouse_database: str = "analytics"

    # Pipeline behaviour
    max_sql_retries: int = 1
    max_result_rows: int = 200
    query_timeout_seconds: int = 15

    # Where to append the request log (jsonl).
    log_path: Path = PROJECT_ROOT / "logs" / "requests.jsonl"


settings = Settings()
