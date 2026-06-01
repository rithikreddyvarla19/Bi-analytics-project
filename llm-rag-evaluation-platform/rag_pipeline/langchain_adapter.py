"""Optional LangChain adapter for teams standardizing on LangChain primitives."""

from __future__ import annotations

from typing import Any

from embeddings.providers import EmbeddingProvider
from rag_pipeline.vector_store import FAISSVectorStore


class LangChainRAGAdapter:
    """Expose the platform vector store through a LangChain-like retriever API."""

    def __init__(self, vector_store: FAISSVectorStore, embedder: EmbeddingProvider) -> None:
        self.vector_store = vector_store
        self.embedder = embedder

    def as_retriever(self, search_kwargs: dict[str, Any] | None = None):
        try:
            from langchain_core.documents import Document
        except ImportError as exc:  # pragma: no cover - optional production dependency
            raise RuntimeError("Install langchain-core to use the LangChain adapter.") from exc

        adapter = self
        kwargs = dict(search_kwargs or {})

        class _Retriever:
            def invoke(self, query: str) -> list[Document]:
                embedding = adapter.embedder.embed_query(query)
                results = adapter.vector_store.search(embedding, k=int(kwargs.get("k", 5)))
                return [
                    Document(page_content=result.text, metadata={**result.metadata, "score": result.score})
                    for result in results
                ]

            def get_relevant_documents(self, query: str) -> list[Document]:
                return self.invoke(query)

        return _Retriever()
