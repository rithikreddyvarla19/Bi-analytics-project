"""CLI for document ingestion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion.chunking import RecursiveTextChunker  # noqa: E402
from ingestion.pipeline import IngestionPipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest PDFs, CSVs, and text files into chunk JSONL.")
    parser.add_argument("--input", required=True, help="Input file or directory.")
    parser.add_argument("--output", default="artifacts/chunks/chunks.jsonl", help="Output JSONL path.")
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--chunk-overlap", type=int, default=120)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = IngestionPipeline(
        chunker=RecursiveTextChunker(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    )
    stats = pipeline.run(args.input, args.output)
    print(json.dumps(stats.__dict__, indent=2))


if __name__ == "__main__":
    main()
