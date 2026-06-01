"""End-to-end ingestion pipeline."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from ingestion.chunking import RecursiveTextChunker, TextChunk
from ingestion.loaders import DocumentIngestor


@dataclass(frozen=True)
class IngestionStats:
    documents_loaded: int
    chunks_created: int
    elapsed_seconds: float
    output_path: str


class IngestionPipeline:
    """Load documents, chunk them, and persist retrieval-ready JSONL."""

    def __init__(
        self,
        ingestor: DocumentIngestor | None = None,
        chunker: RecursiveTextChunker | None = None,
    ) -> None:
        self.ingestor = ingestor or DocumentIngestor()
        self.chunker = chunker or RecursiveTextChunker()

    def run(self, input_path: str | Path, output_path: str | Path) -> IngestionStats:
        started = time.perf_counter()
        documents_loaded = 0
        chunks_created = 0
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for document in self.ingestor.iter_path(input_path):
                documents_loaded += 1
                for chunk in self.chunker.chunk_document(document):
                    chunks_created += 1
                    handle.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
        return IngestionStats(
            documents_loaded=documents_loaded,
            chunks_created=chunks_created,
            elapsed_seconds=round(time.perf_counter() - started, 4),
            output_path=str(output_path),
        )

    @staticmethod
    def write_chunks(chunks: list[TextChunk], output_path: str | Path) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for chunk in chunks:
                handle.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")

    @staticmethod
    def read_chunks(input_path: str | Path) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        with Path(input_path).open("r", encoding="utf-8") as handle:
            for line in handle:
                payload = json.loads(line)
                chunks.append(TextChunk(**payload))
        return chunks
