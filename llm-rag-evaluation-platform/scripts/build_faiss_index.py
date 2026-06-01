"""CLI for building the vector index from chunk JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from embeddings.pipeline import EmbeddingPipeline  # noqa: E402
from embeddings.providers import HashingEmbeddingProvider, get_embedding_provider  # noqa: E402
from ingestion.pipeline import IngestionPipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a FAISS vector index.")
    parser.add_argument("--chunks", default="artifacts/chunks/chunks.jsonl", help="Chunk JSONL path.")
    parser.add_argument("--output", default="artifacts/vector_index", help="Index output directory.")
    parser.add_argument("--provider", default="hashing", choices=["hashing", "openai", "huggingface"])
    parser.add_argument("--dimensions", type=int, default=384)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    chunks = IngestionPipeline.read_chunks(args.chunks)
    provider = (
        HashingEmbeddingProvider(dimensions=args.dimensions)
        if args.provider == "hashing"
        else get_embedding_provider(args.provider)
    )
    pipeline = EmbeddingPipeline(provider=provider, batch_size=args.batch_size)
    store = pipeline.build_index(chunks, index_path=args.output)
    print(json.dumps({"index_path": args.output, "vectors": store.size, "uses_faiss": store.uses_faiss}, indent=2))


if __name__ == "__main__":
    main()
