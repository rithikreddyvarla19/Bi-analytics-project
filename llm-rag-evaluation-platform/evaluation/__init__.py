"""Automated evaluation framework for RAG quality."""

from evaluation.dataset import GroundTruthDataset, GroundTruthExample
from evaluation.metrics import EvaluationScore, evaluate_answer
from evaluation.prompt_experiments import PromptExperimentRunner
from evaluation.runner import EvaluationRunner

__all__ = [
    "EvaluationRunner",
    "EvaluationScore",
    "GroundTruthDataset",
    "GroundTruthExample",
    "PromptExperimentRunner",
    "evaluate_answer",
]
