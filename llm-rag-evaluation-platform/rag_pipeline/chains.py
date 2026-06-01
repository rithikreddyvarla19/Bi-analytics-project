"""Composable RAG engine."""

from __future__ import annotations

import time
from dataclasses import dataclass

from embeddings.providers import EmbeddingProvider, HashingEmbeddingProvider
from rag_pipeline.llm import LLMProvider, LocalTemplateLLM
from rag_pipeline.prompts import PromptRegistry
from rag_pipeline.vector_store import FAISSVectorStore, SearchResult


@dataclass(frozen=True)
class RAGResponse:
    question: str
    answer: str
    sources: list[SearchResult]
    prompt_id: str
    model: str
    latency_ms: float


class RAGEngine:
    """Retrieve, prompt, generate, and return source-cited responses."""

    def __init__(
        self,
        vector_store: FAISSVectorStore,
        embedder: EmbeddingProvider | None = None,
        llm: LLMProvider | None = None,
        prompt_registry: PromptRegistry | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.embedder = embedder or HashingEmbeddingProvider(dimensions=vector_store.dimensions)
        self.llm = llm or LocalTemplateLLM()
        self.prompt_registry = prompt_registry or PromptRegistry()

    def ask(
        self,
        question: str,
        *,
        k: int = 5,
        prompt_id: str = "enterprise_cited",
        metadata_filter: dict[str, object] | None = None,
    ) -> RAGResponse:
        started = time.perf_counter()
        query_embedding = self.embedder.embed_query(question)
        results = self.vector_store.search(query_embedding, k=k, metadata_filter=metadata_filter)
        prompt = self.prompt_registry.render(prompt_id, question, results)
        generation = self.llm.generate(prompt)
        answer = ensure_source_footer(generation.text, results)
        return RAGResponse(
            question=question,
            answer=answer,
            sources=results,
            prompt_id=prompt_id,
            model=generation.model,
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )


def ensure_source_footer(answer: str, results: list[SearchResult]) -> str:
    """Append source IDs when a provider omits citations entirely."""

    if not results or "[S" in answer:
        return answer
    labels = ", ".join(f"[S{index}]" for index, _ in enumerate(results, start=1))
    return f"{answer.strip()}\n\nSources: {labels}"
