"""FAISS-backed vector search with a pure-Python fallback for tests."""

from __future__ import annotations

import json
import math
import pickle
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class SearchResult:
    id: str
    text: str
    score: float
    metadata: dict[str, object]


@dataclass
class _VectorRecord:
    id: str
    text: str
    embedding: list[float]
    metadata: dict[str, object]


def _normalize(vector: Iterable[float]) -> list[float]:
    values = [float(value) for value in vector]
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return values
    return [value / norm for value in values]


def _dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))


class FAISSVectorStore:
    """Small wrapper around FAISS IndexFlatIP with exact-search fallback."""

    def __init__(self, dimensions: int, use_faiss: bool = True) -> None:
        self.dimensions = dimensions
        self.records: list[_VectorRecord] = []
        self._faiss = None
        self._np = None
        self._index = None
        if use_faiss:
            try:  # pragma: no cover - optional production dependency
                import faiss
                import numpy as np

                self._faiss = faiss
                self._np = np
                self._index = faiss.IndexFlatIP(dimensions)
            except ImportError:
                self._faiss = None
                self._np = None
                self._index = None

    @property
    def size(self) -> int:
        return len(self.records)

    @property
    def uses_faiss(self) -> bool:
        return self._index is not None

    def add(self, item_id: str, text: str, embedding: list[float], metadata: dict[str, object]) -> None:
        vector = _normalize(embedding)
        if len(vector) != self.dimensions:
            raise ValueError(f"Expected {self.dimensions} dimensions, received {len(vector)}")
        self.records.append(_VectorRecord(item_id, text, vector, metadata))
        if self._index is not None:  # pragma: no cover - optional production dependency
            matrix = self._np.array([vector], dtype="float32")
            self._index.add(matrix)

    def add_many(self, records: Iterable[tuple[str, str, list[float], dict[str, object]]]) -> None:
        for item_id, text, embedding, metadata in records:
            self.add(item_id, text, embedding, metadata)

    def search(
        self,
        query_embedding: list[float],
        k: int = 5,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[SearchResult]:
        if k <= 0:
            return []
        query = _normalize(query_embedding)
        if len(query) != self.dimensions:
            raise ValueError(f"Expected {self.dimensions} query dimensions, received {len(query)}")

        if self._index is not None and not metadata_filter:  # pragma: no cover - optional production dependency
            matrix = self._np.array([query], dtype="float32")
            scores, indices = self._index.search(matrix, min(k, self.size))
            return [
                SearchResult(
                    id=self.records[int(index)].id,
                    text=self.records[int(index)].text,
                    score=float(score),
                    metadata=self.records[int(index)].metadata,
                )
                for score, index in zip(scores[0], indices[0], strict=False)
                if int(index) >= 0
            ]

        candidates = [
            record
            for record in self.records
            if self._matches_filter(record.metadata, metadata_filter)
        ]
        ranked = sorted(candidates, key=lambda record: _dot(query, record.embedding), reverse=True)
        return [
            SearchResult(
                id=record.id,
                text=record.text,
                score=round(_dot(query, record.embedding), 6),
                metadata=record.metadata,
            )
            for record in ranked[:k]
        ]

    def save(self, index_path: str | Path) -> None:
        path = Path(index_path)
        path.mkdir(parents=True, exist_ok=True)
        manifest = {
            "dimensions": self.dimensions,
            "records": [
                {
                    "id": record.id,
                    "text": record.text,
                    "metadata": record.metadata,
                }
                for record in self.records
            ],
        }
        (path / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        with (path / "vectors.pkl").open("wb") as handle:
            pickle.dump([asdict(record) for record in self.records], handle)
        if self._index is not None:  # pragma: no cover - optional production dependency
            self._faiss.write_index(self._index, str(path / "faiss.index"))

    @classmethod
    def load(cls, index_path: str | Path, *, use_faiss: bool = True) -> FAISSVectorStore:
        path = Path(index_path)
        manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
        store = cls(dimensions=int(manifest["dimensions"]), use_faiss=use_faiss)
        with (path / "vectors.pkl").open("rb") as handle:
            payload = pickle.load(handle)
        for record in payload:
            store.add(record["id"], record["text"], record["embedding"], record["metadata"])
        return store

    @staticmethod
    def _matches_filter(metadata: dict[str, object], metadata_filter: dict[str, object] | None) -> bool:
        if not metadata_filter:
            return True
        return all(metadata.get(key) == value for key, value in metadata_filter.items())
