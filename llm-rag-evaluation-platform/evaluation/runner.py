"""Batch evaluation runner with optional MLflow tracking."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from evaluation.dataset import GroundTruthDataset, GroundTruthExample
from evaluation.metrics import EvaluationScore, aggregate_scores, evaluate_answer
from rag_pipeline.chains import RAGEngine


@dataclass(frozen=True)
class EvaluationRecord:
    example_id: str
    question: str
    expected_answer: str
    generated_answer: str
    prompt_id: str
    latency_ms: float
    scores: EvaluationScore


class EvaluationRunner:
    """Evaluate a RAG engine against a ground-truth dataset."""

    def __init__(self, rag_engine: RAGEngine, dataset: GroundTruthDataset) -> None:
        self.rag_engine = rag_engine
        self.dataset = dataset

    def run(self, *, prompt_id: str = "enterprise_cited", k: int = 5) -> list[EvaluationRecord]:
        self.dataset.assert_valid()
        records: list[EvaluationRecord] = []
        for example in self.dataset.examples:
            records.append(self._evaluate_example(example, prompt_id=prompt_id, k=k))
        return records

    def summarize(self, records: list[EvaluationRecord]) -> dict[str, float]:
        return aggregate_scores([record.scores for record in records])

    def write_csv(self, records: list[EvaluationRecord], output_path: str | Path) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "example_id",
            "question",
            "expected_answer",
            "generated_answer",
            "prompt_id",
            "latency_ms",
            "faithfulness",
            "hallucination_rate",
            "context_precision",
            "context_recall",
            "answer_relevancy",
        ]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                row = {
                    key: value
                    for key, value in asdict(record).items()
                    if key not in {"scores"}
                }
                row.update(record.scores.as_dict())
                writer.writerow(row)

    def log_to_mlflow(self, records: list[EvaluationRecord], run_name: str = "rag-evaluation") -> None:
        try:
            import mlflow
        except ImportError:  # pragma: no cover - optional production dependency
            return
        with mlflow.start_run(run_name=run_name):
            summary = self.summarize(records)
            for key, value in summary.items():
                mlflow.log_metric(key, value)
            mlflow.log_metric("examples", len(records))

    def _evaluate_example(self, example: GroundTruthExample, *, prompt_id: str, k: int) -> EvaluationRecord:
        response = self.rag_engine.ask(example.question, prompt_id=prompt_id, k=k)
        scores = evaluate_answer(
            question=example.question,
            generated_answer=response.answer,
            retrieved_contexts=response.sources,
            expected_answer=example.expected_answer,
            expected_contexts=example.expected_contexts,
            expected_source_ids=example.expected_source_ids,
        )
        return EvaluationRecord(
            example_id=example.id,
            question=example.question,
            expected_answer=example.expected_answer,
            generated_answer=response.answer,
            prompt_id=prompt_id,
            latency_ms=response.latency_ms,
            scores=scores,
        )
