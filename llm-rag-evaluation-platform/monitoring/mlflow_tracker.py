"""MLflow experiment tracking adapter."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass


class MLflowExperimentTracker:
    """Thin wrapper that keeps MLflow optional outside production."""

    def __init__(self, experiment_name: str = "rag-evaluation-platform") -> None:
        try:
            import mlflow
        except ImportError as exc:  # pragma: no cover - optional production dependency
            raise RuntimeError("Install mlflow to use experiment tracking.") from exc
        self.mlflow = mlflow
        self.mlflow.set_experiment(experiment_name)

    def log_run(
        self,
        run_name: str,
        metrics: dict[str, float],
        params: dict[str, object] | None = None,
        artifacts: list[str] | None = None,
    ) -> None:
        with self.mlflow.start_run(run_name=run_name):
            for key, value in (params or {}).items():
                self.mlflow.log_param(key, _serialize(value))
            for key, value in metrics.items():
                self.mlflow.log_metric(key, float(value))
            for artifact in artifacts or []:
                self.mlflow.log_artifact(artifact)


def _serialize(value: object) -> object:
    if is_dataclass(value):
        return asdict(value)
    return value
