"""Application configuration sourced from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "llm-powered-knowledge-assistant-rag"
    environment: str = os.getenv("ENVIRONMENT", "local")
    vector_index_path: str = os.getenv("VECTOR_INDEX_PATH", "artifacts/vector_index")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "hashing")
    embedding_dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "384"))
    llm_provider: str = os.getenv("LLM_PROVIDER", "local")
    default_top_k: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    feedback_path: str = os.getenv("FEEDBACK_PATH", "artifacts/feedback.jsonl")


def get_settings() -> Settings:
    return Settings()
