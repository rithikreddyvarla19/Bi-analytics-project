"""Batch embedding and vector index construction."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from embeddings.providers import EmbeddingProvider, HashingEmbeddingProvider
from ingestion.chunking import TextChunk
from rag_pipeline.vector_store import FAISSVectorStore


@dataclass(frozen=True)
class EmbeddingRecord:
    chunk_id: str
    text: str
    embedding: list[float]
    metadata: dict[str, object]


class EmbeddingPipeline:
    """Embed chunks in batches and write them to a vector store."""

    def __init__(
        self,
        provider: EmbeddingProvider | None = None,
        batch_size: int = 64,
    ) -> None:
        self.provider = provider or HashingEmbeddingProvider()
        self.batch_size = batch_size

    def embed_chunks(self, chunks: Iterable[TextChunk]) -> list[EmbeddingRecord]:
        chunk_list = list(chunks)
        records: list[EmbeddingRecord] = []
        for start in range(0, len(chunk_list), self.batch_size):
            batch = chunk_list[start : start + self.batch_size]
            embeddings = self.provider.embed_texts([chunk.text for chunk in batch])
            for chunk, embedding in zip(batch, embeddings, strict=True):
                metadata = dict(chunk.metadata)
                metadata.update(
                    {
                        "document_id": chunk.document_id,
                        "source_path": chunk.source_path,
                        "token_count": chunk.token_count,
                    }
                )
                records.append(
                    EmbeddingRecord(
                        chunk_id=chunk.id,
                        text=chunk.text,
                        embedding=embedding,
                        metadata=metadata,
                    )
                )
        return records

    def build_index(self, chunks: Iterable[TextChunk], index_path: str | None = None) -> FAISSVectorStore:
        records = self.embed_chunks(chunks)
        store = FAISSVectorStore(dimensions=self.provider.dimensions)
        for record in records:
            store.add(record.chunk_id, record.text, record.embedding, record.metadata)
        if index_path:
            store.save(index_path)
        return store
