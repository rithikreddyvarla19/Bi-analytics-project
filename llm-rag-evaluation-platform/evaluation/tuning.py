"""Prompt and retrieval hyperparameter tuning for the knowledge assistant."""

from __future__ import annotations

from dataclasses import dataclass

from evaluation.runner import EvaluationRecord, EvaluationRunner


@dataclass(frozen=True)
class TuningCandidate:
    prompt_id: str
    top_k: int
    model_name: str = "configured-llm"
    temperature: float = 0.0


@dataclass(frozen=True)
class TuningResult:
    candidate: TuningCandidate
    metrics: dict[str, float]
    records: list[EvaluationRecord]


class HyperparameterTuner:
    """Compare prompt and retriever settings against ground-truth examples."""

    def __init__(self, evaluation_runner: EvaluationRunner) -> None:
        self.evaluation_runner = evaluation_runner

    def run(self, candidates: list[TuningCandidate]) -> list[TuningResult]:
        results: list[TuningResult] = []
        for candidate in candidates:
            records = self.evaluation_runner.run(prompt_id=candidate.prompt_id, k=candidate.top_k)
            metrics = self.evaluation_runner.summarize(records)
            metrics.update(
                {
                    "top_k": float(candidate.top_k),
                    "temperature": candidate.temperature,
                }
            )
            results.append(TuningResult(candidate=candidate, metrics=metrics, records=records))
        return sorted(
            results,
            key=lambda result: (
                result.metrics.get("top_3_accuracy", 0.0),
                result.metrics.get("answer_relevancy", 0.0),
                result.metrics.get("calibration_score", 0.0),
            ),
            reverse=True,
        )
