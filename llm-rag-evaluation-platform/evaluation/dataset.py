"""Ground-truth dataset loading and validation."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class GroundTruthExample:
    id: str
    question: str
    expected_answer: str
    expected_contexts: list[str] = field(default_factory=list)
    expected_source_ids: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationIssue:
    example_id: str
    severity: str
    message: str


class GroundTruthDataset:
    """A validated collection of human-approved RAG examples."""

    def __init__(self, examples: list[GroundTruthExample]) -> None:
        self.examples = examples

    def __len__(self) -> int:
        return len(self.examples)

    @classmethod
    def from_jsonl(cls, path: str | Path) -> GroundTruthDataset:
        examples: list[GroundTruthExample] = []
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    payload = json.loads(line)
                    examples.append(GroundTruthExample(**payload))
        return cls(examples)

    @classmethod
    def from_csv(cls, path: str | Path) -> GroundTruthDataset:
        examples: list[GroundTruthExample] = []
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                examples.append(
                    GroundTruthExample(
                        id=row.get("id", "").strip(),
                        question=row.get("question", "").strip(),
                        expected_answer=row.get("expected_answer", "").strip(),
                        expected_contexts=_split_list(row.get("expected_contexts", "")),
                        expected_source_ids=_split_list(row.get("expected_source_ids", "")),
                        metadata={key: value for key, value in row.items() if key.startswith("metadata_")},
                    )
                )
        return cls(examples)

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        seen_ids: set[str] = set()
        for index, example in enumerate(self.examples, start=1):
            label = example.id or f"row-{index}"
            if not example.id:
                issues.append(ValidationIssue(label, "error", "Missing example id."))
            elif example.id in seen_ids:
                issues.append(ValidationIssue(example.id, "error", "Duplicate example id."))
            seen_ids.add(example.id)

            if len(example.question) < 8:
                issues.append(ValidationIssue(label, "error", "Question is too short for reliable evaluation."))
            if len(example.expected_answer) < 3:
                issues.append(ValidationIssue(label, "error", "Expected answer is missing or too short."))
            if not example.expected_contexts and not example.expected_source_ids:
                issues.append(
                    ValidationIssue(
                        label,
                        "warning",
                        "No expected contexts or source ids supplied; recall metrics will be weaker.",
                    )
                )
        return issues

    def assert_valid(self) -> None:
        errors = [issue for issue in self.validate() if issue.severity == "error"]
        if errors:
            formatted = "; ".join(f"{issue.example_id}: {issue.message}" for issue in errors)
            raise ValueError(f"Ground-truth dataset failed validation: {formatted}")


def _split_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.replace("\n", "||").split("||") if item.strip()]
