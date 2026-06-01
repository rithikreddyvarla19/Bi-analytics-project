from embeddings.providers import HashingEmbeddingProvider


def test_hashing_embeddings_are_deterministic_and_normalized() -> None:
    provider = HashingEmbeddingProvider(dimensions=32)

    first = provider.embed_query("risk controls and audit evidence")
    second = provider.embed_query("risk controls and audit evidence")

    assert first == second
    assert len(first) == 32
    assert round(sum(value * value for value in first), 5) == 1.0
