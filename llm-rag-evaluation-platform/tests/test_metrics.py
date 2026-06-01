from evaluation.metrics import evaluate_answer
from rag_pipeline.vector_store import SearchResult


def test_evaluation_metrics_capture_supported_answer() -> None:
    contexts = [
        SearchResult(
            id="source-1",
            text="Employees receive 16 weeks of paid parental leave after one year of service.",
            score=0.9,
            metadata={"source_id": "hr-handbook"},
        )
    ]

    score = evaluate_answer(
        question="How much parental leave do employees receive?",
        generated_answer="Employees receive 16 weeks of paid parental leave. [S1]",
        retrieved_contexts=contexts,
        expected_answer="16 weeks of paid parental leave",
        expected_contexts=["Employees receive 16 weeks of paid parental leave"],
        expected_source_ids=["hr-handbook"],
    )

    assert score.faithfulness >= 0.8
    assert score.hallucination_rate <= 0.2
    assert score.context_precision == 1.0
    assert score.context_recall == 1.0
