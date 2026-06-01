"""Optional neural backend discovery for PyTorch and TensorFlow deployments."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec


@dataclass(frozen=True)
class NeuralBackendStatus:
    pytorch_available: bool
    tensorflow_available: bool


def detect_neural_backends() -> NeuralBackendStatus:
    """Report which deep-learning runtimes are installed in the environment."""

    return NeuralBackendStatus(
        pytorch_available=find_spec("torch") is not None,
        tensorflow_available=find_spec("tensorflow") is not None,
    )
