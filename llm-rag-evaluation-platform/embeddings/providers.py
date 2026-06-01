"""Embedding provider implementations.

The hashing provider is deterministic and dependency-light, making it useful
for tests, local development, and air-gapped demos. OpenAI and HuggingFace
providers are used in production through environment configuration.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass
from typing import Protocol


class EmbeddingProvider(Protocol):
    """Vectorize text into fixed-width dense embeddings."""

    dimensions: int

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""

    def embed_query(self, text: str) -> list[float]:
        """Embed a query."""


def normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


@dataclass
class HashingEmbeddingProvider:
    """A deterministic embedding model using signed feature hashing."""

    dimensions: int = 384

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            index = int(digest[:8], 16) % self.dimensions
            sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
            vector[index] += sign
        return normalize(vector)


class OpenAIEmbeddingProvider:
    """OpenAI embedding provider using the official SDK."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
        api_key: str | None = None,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional production dependency
            raise RuntimeError("Install openai to use OpenAI embeddings.") from exc

        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


class HuggingFaceEmbeddingProvider:
    """HuggingFace Transformers mean-pooled embedding provider."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str | None = None,
    ) -> None:
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
        except ImportError as exc:  # pragma: no cover - optional production dependency
            raise RuntimeError("Install torch and transformers to use HuggingFace embeddings.") from exc

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        if device:
            self.model.to(device)
        self.device = device
        self.model_name = model_name
        self.dimensions = int(self.model.config.hidden_size)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        with self.torch.no_grad():
            encoded = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
            if self.device:
                encoded = {key: value.to(self.device) for key, value in encoded.items()}
            output = self.model(**encoded)
            mask = encoded["attention_mask"].unsqueeze(-1).expand(output.last_hidden_state.size()).float()
            pooled = (output.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
            return [normalize(row.detach().cpu().tolist()) for row in pooled]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


def get_embedding_provider(provider: str | None = None, **kwargs: object) -> EmbeddingProvider:
    """Create an embedding provider from config."""

    selected = (provider or os.getenv("EMBEDDING_PROVIDER") or "hashing").lower()
    if selected == "openai":
        return OpenAIEmbeddingProvider(**kwargs)
    if selected in {"huggingface", "hf", "transformers"}:
        return HuggingFaceEmbeddingProvider(**kwargs)
    if selected == "hashing":
        return HashingEmbeddingProvider(**kwargs)
    raise ValueError(f"Unsupported embedding provider: {selected}")
