"""Embedding providers and batch indexing helpers."""

from embeddings.model_backends import NeuralBackendStatus, detect_neural_backends
from embeddings.pipeline import EmbeddingPipeline
from embeddings.providers import (
    EmbeddingProvider,
    HashingEmbeddingProvider,
    HuggingFaceEmbeddingProvider,
    OpenAIEmbeddingProvider,
    get_embedding_provider,
)

__all__ = [
    "EmbeddingPipeline",
    "EmbeddingProvider",
    "HashingEmbeddingProvider",
    "HuggingFaceEmbeddingProvider",
    "NeuralBackendStatus",
    "OpenAIEmbeddingProvider",
    "detect_neural_backends",
    "get_embedding_provider",
]
