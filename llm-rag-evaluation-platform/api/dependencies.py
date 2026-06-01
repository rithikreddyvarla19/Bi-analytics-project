"""FastAPI dependency factories."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from api.config import Settings, get_settings
from embeddings.providers import HashingEmbeddingProvider, get_embedding_provider
from monitoring.feedback import FeedbackStore
from monitoring.telemetry import InMemoryMetricsStore
from rag_pipeline.chains import RAGEngine
from rag_pipeline.llm import get_llm_provider
from rag_pipeline.vector_store import FAISSVectorStore


@lru_cache(maxsize=1)
def get_rag_engine() -> RAGEngine:
    settings = get_settings()
    index_path = Path(settings.vector_index_path)
    if (index_path / "manifest.json").exists():
        vector_store = FAISSVectorStore.load(index_path)
    else:
        vector_store = FAISSVectorStore(dimensions=settings.embedding_dimensions)

    embedder = _build_embedder(settings, vector_store.dimensions)
    llm = get_llm_provider(settings.llm_provider)
    return RAGEngine(vector_store=vector_store, embedder=embedder, llm=llm)


@lru_cache(maxsize=1)
def get_feedback_store() -> FeedbackStore:
    return FeedbackStore(get_settings().feedback_path)


@lru_cache(maxsize=1)
def get_metrics_store() -> InMemoryMetricsStore:
    return InMemoryMetricsStore()


def _build_embedder(settings: Settings, dimensions: int):
    if settings.embedding_provider == "hashing":
        return HashingEmbeddingProvider(dimensions=dimensions)
    return get_embedding_provider(settings.embedding_provider)
