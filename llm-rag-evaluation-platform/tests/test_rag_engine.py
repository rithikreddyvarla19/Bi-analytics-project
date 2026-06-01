from embeddings.providers import HashingEmbeddingProvider
from rag_pipeline.chains import RAGEngine
from rag_pipeline.vector_store import FAISSVectorStore


def test_rag_engine_returns_cited_sources() -> None:
    embedder = HashingEmbeddingProvider(dimensions=64)
    store = FAISSVectorStore(dimensions=64, use_faiss=False)
    text = "The model risk policy requires quarterly hallucination monitoring and human review."
    store.add("chunk-1", text, embedder.embed_query(text), {"source_path": "policy.txt"})
    engine = RAGEngine(store, embedder=embedder)

    response = engine.ask("What monitoring is required for hallucinations?", k=1)

    assert "hallucination" in response.answer.lower()
    assert response.sources[0].id == "chunk-1"
    assert response.latency_ms >= 0
