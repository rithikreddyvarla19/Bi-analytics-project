"""Prompt experimentation framework."""

from __future__ import annotations

from dataclasses import dataclass

from evaluation.runner import EvaluationRecord, EvaluationRunner
from rag_pipeline.prompts import PromptTemplate


@dataclass(frozen=True)
class PromptExperiment:
    prompt_id: str
    prompt_name: str
    metrics: dict[str, float]
    records: list[EvaluationRecord]


class PromptExperimentRunner:
    """Register prompt variants and compare evaluation aggregates."""

    def __init__(self, evaluation_runner: EvaluationRunner) -> None:
        self.evaluation_runner = evaluation_runner

    def run(self, prompts: list[PromptTemplate], *, k: int = 5) -> list[PromptExperiment]:
        experiments: list[PromptExperiment] = []
        registry = self.evaluation_runner.rag_engine.prompt_registry
        for prompt in prompts:
            registry.register(prompt)
            records = self.evaluation_runner.run(prompt_id=prompt.id, k=k)
            experiments.append(
                PromptExperiment(
                    prompt_id=prompt.id,
                    prompt_name=prompt.name,
                    metrics=self.evaluation_runner.summarize(records),
                    records=records,
                )
            )
        return sorted(
            experiments,
            key=lambda experiment: (
                experiment.metrics.get("faithfulness", 0.0),
                experiment.metrics.get("answer_relevancy", 0.0),
            ),
            reverse=True,
        )
