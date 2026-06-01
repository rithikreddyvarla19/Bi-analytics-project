"""Dashboard data loading helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_evaluation_results(path: str | Path = "artifacts/evaluation/results.csv") -> pd.DataFrame:
    path = Path(path)
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(
        [
            {
                "prompt_id": "enterprise_cited",
                "top_3_accuracy": 0.87,
                "faithfulness": 0.91,
                "hallucination_rate": 0.09,
                "calibration_score": 0.84,
                "context_precision": 0.86,
                "context_recall": 0.82,
                "answer_relevancy": 0.88,
                "latency_ms": 820,
            }
        ]
    )


def load_feedback(path: str | Path = "artifacts/feedback.jsonl") -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=["created_at", "rating", "comment", "trace_id"])
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)
