from rag_pipeline.vector_store import FAISSVectorStore


def test_vector_store_returns_ranked_results() -> None:
    store = FAISSVectorStore(dimensions=3, use_faiss=False)
    store.add("a", "paid parental leave policy", [1, 0, 0], {"source_id": "policy"})
    store.add("b", "quarterly revenue forecast", [0, 1, 0], {"source_id": "finance"})

    results = store.search([1, 0, 0], k=1)

    assert results[0].id == "a"
    assert results[0].score > 0.9


def test_vector_store_metadata_filter() -> None:
    store = FAISSVectorStore(dimensions=2, use_faiss=False)
    store.add("a", "hr policy", [1, 0], {"department": "hr"})
    store.add("b", "finance policy", [1, 0], {"department": "finance"})

    results = store.search([1, 0], k=5, metadata_filter={"department": "finance"})

    assert [result.id for result in results] == ["b"]
