"""Chunking primitives tuned for retrieval quality and reproducibility."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from ingestion.loaders import RawDocument


@dataclass(frozen=True)
class TextChunk:
    """A retrieval-ready text segment."""

    id: str
    document_id: str
    text: str
    source_path: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)
    token_count: int = 0


def approximate_token_count(text: str) -> int:
    """Cheap tokenizer proxy suitable for batching and dashboards."""

    return max(1, len(re.findall(r"\w+|[^\w\s]", text)))


class RecursiveTextChunker:
    """Split text recursively using semantic separators before hard wrapping."""

    def __init__(
        self,
        chunk_size: int = 900,
        chunk_overlap: int = 120,
        separators: Iterable[str] | None = None,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = tuple(separators or ("\n\n", "\n", ". ", " ", ""))

    def split_text(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+\n", "\n", text).strip()
        if not normalized:
            return []
        pieces = self._split_recursive(normalized, self.separators)
        return self._merge_with_overlap(pieces)

    def chunk_document(self, document: RawDocument) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        for index, chunk_text in enumerate(self.split_text(document.text)):
            chunk_id = self._chunk_id(document.id, index, chunk_text)
            metadata = dict(document.metadata)
            metadata.update(
                {
                    "chunk_index": index,
                    "source_type": document.source_type,
                    "document_checksum": document.checksum,
                }
            )
            chunks.append(
                TextChunk(
                    id=chunk_id,
                    document_id=document.id,
                    text=chunk_text,
                    source_path=document.source_path,
                    metadata=metadata,
                    token_count=approximate_token_count(chunk_text),
                )
            )
        return chunks

    def chunk_documents(self, documents: Iterable[RawDocument]) -> list[TextChunk]:
        return [chunk for document in documents for chunk in self.chunk_document(document)]

    def _split_recursive(self, text: str, separators: tuple[str, ...]) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]
        separator = separators[0]
        remaining = separators[1:]
        if separator == "":
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

        splits = text.split(separator)
        if len(splits) == 1:
            return self._split_recursive(text, remaining)

        pieces: list[str] = []
        for split in splits:
            candidate = split.strip()
            if not candidate:
                continue
            if len(candidate) <= self.chunk_size:
                pieces.append(candidate)
            else:
                pieces.extend(self._split_recursive(candidate, remaining))
        return pieces

    def _merge_with_overlap(self, pieces: list[str]) -> list[str]:
        chunks: list[str] = []
        current = ""
        for piece in pieces:
            separator = " " if current else ""
            candidate = f"{current}{separator}{piece}".strip()
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = self._apply_overlap(chunks[-1] if chunks else "", piece)

            while len(current) > self.chunk_size:
                chunks.append(current[: self.chunk_size].strip())
                overlap = current[max(0, self.chunk_size - self.chunk_overlap) : self.chunk_size]
                current = f"{overlap} {current[self.chunk_size:]}".strip()

        if current:
            chunks.append(current)
        return [chunk for chunk in chunks if chunk]

    def _apply_overlap(self, previous: str, piece: str) -> str:
        if not previous or self.chunk_overlap == 0:
            return piece
        overlap = previous[-self.chunk_overlap :].strip()
        return f"{overlap} {piece}".strip()

    @staticmethod
    def _chunk_id(document_id: str, index: int, text: str) -> str:
        digest = hashlib.sha1(f"{document_id}:{index}:{text}".encode()).hexdigest()
        return f"{document_id}-{index:05d}-{digest[:8]}"
