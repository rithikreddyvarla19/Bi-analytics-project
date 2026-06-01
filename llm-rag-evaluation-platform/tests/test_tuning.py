from embeddings.providers import HashingEmbeddingProvider
from evaluation.dataset import GroundTruthDataset, GroundTruthExample
from evaluation.runner import EvaluationRunner
from evaluation.tuning import HyperparameterTuner, TuningCandidate
from rag_pipeline.chains import RAGEngine
from rag_pipeline.vector_store import FAISSVectorStore


def test_hyperparameter_tuner_ranks_top_3_accuracy() -> None:
    embedder = HashingEmbeddingProvider(dimensions=64)
    store = FAISSVectorStore(dimensions=64, use_faiss=False)
    text = "Technical documents require grounded source-linked responses for product stakeholders."
    store.add("chunk-1", text, embedder.embed_query(text), {"source_id": "technical-docs"})
    dataset = GroundTruthDataset(
        [
            GroundTruthExample(
                id="gt-1",
                question="What kind of responses are required?",
                expected_answer="Grounded source-linked responses are required.",
                expected_contexts=[text],
                expected_source_ids=["technical-docs"],
            )
        ]
    )
    runner = EvaluationRunner(RAGEngine(store, embedder=embedder), dataset)

    results = HyperparameterTuner(runner).run(
        [TuningCandidate(prompt_id="enterprise_cited", top_k=1)]
    )

    assert results[0].metrics["top_3_accuracy"] == 1.0
