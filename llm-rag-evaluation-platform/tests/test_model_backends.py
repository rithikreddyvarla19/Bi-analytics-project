from embeddings.model_backends import detect_neural_backends


def test_detect_neural_backends_returns_booleans() -> None:
    status = detect_neural_backends()

    assert isinstance(status.pytorch_available, bool)
    assert isinstance(status.tensorflow_available, bool)
