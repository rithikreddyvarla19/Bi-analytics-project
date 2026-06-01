"""Build a local demo index from bundled sample documents."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from embeddings.pipeline import EmbeddingPipeline  # noqa: E402
from embeddings.providers import HashingEmbeddingProvider  # noqa: E402
from ingestion.chunking import RecursiveTextChunker  # noqa: E402
from ingestion.pipeline import IngestionPipeline  # noqa: E402


def main() -> None:
    ingestion = IngestionPipeline(chunker=RecursiveTextChunker(chunk_size=700, chunk_overlap=80))
    stats = ingestion.run("sample_datasets/documents", "artifacts/chunks/chunks.jsonl")
    chunks = ingestion.read_chunks("artifacts/chunks/chunks.jsonl")
    store = EmbeddingPipeline(HashingEmbeddingProvider(dimensions=384)).build_index(
        chunks,
        index_path="artifacts/vector_index",
    )
    print(
        f"Loaded {stats.documents_loaded} documents, "
        f"created {stats.chunks_created} chunks, indexed {store.size} vectors."
    )


if __name__ == "__main__":
    main()
