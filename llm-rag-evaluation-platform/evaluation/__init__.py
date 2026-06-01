"""Automated evaluation framework for RAG quality."""

from evaluation.dataset import GroundTruthDataset, GroundTruthExample
from evaluation.metrics import EvaluationScore, evaluate_answer, relative_accuracy_lift
from evaluation.prompt_experiments import PromptExperimentRunner
from evaluation.runner import EvaluationRunner
from evaluation.tuning import HyperparameterTuner, TuningCandidate, TuningResult

__all__ = [
    "EvaluationRunner",
    "EvaluationScore",
    "GroundTruthDataset",
    "GroundTruthExample",
    "HyperparameterTuner",
    "PromptExperimentRunner",
    "TuningCandidate",
    "TuningResult",
    "evaluate_answer",
    "relative_accuracy_lift",
]
