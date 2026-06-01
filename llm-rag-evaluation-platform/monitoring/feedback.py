"""User feedback capture."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class UserFeedback:
    trace_id: str | None
    rating: int
    comment: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> None:
        if self.rating < 1 or self.rating > 5:
            raise ValueError("rating must be between 1 and 5")


class FeedbackStore:
    """Append-only JSONL feedback store used by local and container deployments."""

    def __init__(self, path: str | Path = "artifacts/feedback.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, feedback: UserFeedback) -> None:
        feedback.validate()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(feedback), ensure_ascii=False) + "\n")

    def read_all(self) -> list[UserFeedback]:
        if not self.path.exists():
            return []
        items: list[UserFeedback] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    items.append(UserFeedback(**json.loads(line)))
        return items
