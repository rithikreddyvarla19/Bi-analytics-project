"""RAG evaluation metrics.

These metrics are deterministic lexical approximations that can run in CI and
offline environments. They can be complemented by an LLM judge in production,
but they provide stable guardrails for faithfulness, hallucination, retrieval
coverage, and answer relevance.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass

from rag_pipeline.vector_store import SearchResult


@dataclass(frozen=True)
class EvaluationScore:
    faithfulness: float
    hallucination_rate: float
    context_precision: float
    context_recall: float
    answer_relevancy: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def evaluate_answer(
    *,
    question: str,
    generated_answer: str,
    retrieved_contexts: list[SearchResult],
    expected_answer: str = "",
    expected_contexts: list[str] | None = None,
    expected_source_ids: list[str] | None = None,
) -> EvaluationScore:
    context_texts = [result.text for result in retrieved_contexts]
    retrieved_source_ids = [
        str(result.metadata.get("source_id") or result.id)
        for result in retrieved_contexts
    ]
    return EvaluationScore(
        faithfulness=faithfulness(generated_answer, context_texts),
        hallucination_rate=hallucination_rate(generated_answer, context_texts),
        context_precision=context_precision(retrieved_source_ids, expected_source_ids or []),
        context_recall=context_recall(
            context_texts,
            expected_contexts or [],
            retrieved_source_ids,
            expected_source_ids or [],
        ),
        answer_relevancy=answer_relevancy(question, generated_answer, expected_answer),
    )


def faithfulness(answer: str, contexts: list[str]) -> float:
    answer_terms = _content_terms(answer)
    if not answer_terms:
        return 0.0
    context_terms = _content_terms(" ".join(contexts))
    supported = sum(1 for term in answer_terms if term in context_terms)
    return _round(supported / len(answer_terms))


def hallucination_rate(answer: str, contexts: list[str]) -> float:
    return _round(1.0 - faithfulness(answer, contexts))


def context_precision(retrieved_source_ids: list[str], expected_source_ids: list[str]) -> float:
    if not retrieved_source_ids:
        return 0.0
    if not expected_source_ids:
        return 1.0
    expected = set(expected_source_ids)
    relevant_retrieved = sum(1 for source_id in retrieved_source_ids if source_id in expected)
    return _round(relevant_retrieved / len(retrieved_source_ids))


def context_recall(
    retrieved_contexts: list[str],
    expected_contexts: list[str],
    retrieved_source_ids: list[str],
    expected_source_ids: list[str],
) -> float:
    source_recall = 0.0
    if expected_source_ids:
        retrieved = set(retrieved_source_ids)
        expected = set(expected_source_ids)
        source_recall = len(retrieved.intersection(expected)) / len(expected)

    text_recall = 0.0
    if expected_contexts:
        retrieved_terms = _content_terms(" ".join(retrieved_contexts))
        expected_terms = _content_terms(" ".join(expected_contexts))
        if expected_terms:
            text_recall = len(retrieved_terms.intersection(expected_terms)) / len(expected_terms)

    if expected_source_ids and expected_contexts:
        return _round((source_recall + text_recall) / 2)
    if expected_source_ids:
        return _round(source_recall)
    if expected_contexts:
        return _round(text_recall)
    return 1.0


def answer_relevancy(question: str, answer: str, expected_answer: str = "") -> float:
    question_overlap = _jaccard(_content_terms(question), _content_terms(answer))
    if expected_answer:
        expected_overlap = _semantic_f1(answer, expected_answer)
        return _round((question_overlap + expected_overlap) / 2)
    return _round(question_overlap)


def aggregate_scores(scores: list[EvaluationScore]) -> dict[str, float]:
    if not scores:
        return {}
    keys = scores[0].as_dict().keys()
    return {key: _round(sum(score.as_dict()[key] for score in scores) / len(scores)) for key in keys}


def _semantic_f1(prediction: str, reference: str) -> float:
    predicted = _content_terms(prediction)
    expected = _content_terms(reference)
    if not predicted or not expected:
        return 0.0
    overlap = len(predicted.intersection(expected))
    precision = overlap / len(predicted)
    recall = overlap / len(expected)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left.intersection(right)) / len(left.union(right))


def _content_terms(text: str) -> set[str]:
    stopwords = {
        "about",
        "after",
        "also",
        "and",
        "are",
        "but",
        "for",
        "from",
        "have",
        "into",
        "that",
        "the",
        "their",
        "then",
        "this",
        "with",
        "your",
    }
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
        if token not in stopwords
    }


def _round(value: float) -> float:
    if math.isnan(value):
        return 0.0
    return round(max(0.0, min(1.0, value)), 4)
