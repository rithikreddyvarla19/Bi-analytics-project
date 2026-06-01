from evaluation.dataset import GroundTruthDataset, GroundTruthExample


def test_ground_truth_validation_flags_missing_fields() -> None:
    dataset = GroundTruthDataset(
        [
            GroundTruthExample(id="", question="Short?", expected_answer="", expected_contexts=[]),
            GroundTruthExample(id="valid", question="What is the leave policy?", expected_answer="16 weeks"),
        ]
    )

    issues = dataset.validate()

    assert any(issue.severity == "error" for issue in issues)
    assert any(issue.severity == "warning" for issue in issues)
