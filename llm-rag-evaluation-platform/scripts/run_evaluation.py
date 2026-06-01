"""CLI for batch RAG evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from embeddings.providers import HashingEmbeddingProvider, get_embedding_provider  # noqa: E402
from evaluation.dataset import GroundTruthDataset  # noqa: E402
from evaluation.metrics import relative_accuracy_lift  # noqa: E402
from evaluation.runner import EvaluationRunner  # noqa: E402
from rag_pipeline.chains import RAGEngine  # noqa: E402
from rag_pipeline.llm import get_llm_provider  # noqa: E402
from rag_pipeline.vector_store import FAISSVectorStore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run automated RAG evaluation.")
    parser.add_argument("--dataset", default="sample_datasets/ground_truth/rag_eval.csv")
    parser.add_argument("--index", default="artifacts/vector_index")
    parser.add_argument("--output", default="artifacts/evaluation/results.csv")
    parser.add_argument("--prompt-id", default="enterprise_cited")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--embedding-provider", default="hashing")
    parser.add_argument("--llm-provider", default="local")
    parser.add_argument("--baseline-top3", type=float, default=None)
    parser.add_argument("--log-mlflow", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    dataset = (
        GroundTruthDataset.from_jsonl(dataset_path)
        if dataset_path.suffix == ".jsonl"
        else GroundTruthDataset.from_csv(dataset_path)
    )
    store = FAISSVectorStore.load(args.index)
    embedder = (
        HashingEmbeddingProvider(dimensions=store.dimensions)
        if args.embedding_provider == "hashing"
        else get_embedding_provider(args.embedding_provider)
    )
    engine = RAGEngine(store, embedder=embedder, llm=get_llm_provider(args.llm_provider))
    runner = EvaluationRunner(engine, dataset)
    records = runner.run(prompt_id=args.prompt_id, k=args.top_k)
    runner.write_csv(records, args.output)
    if args.log_mlflow:
        runner.log_to_mlflow(records)
    summary = runner.summarize(records)
    if args.baseline_top3 is not None:
        summary["relative_top_3_accuracy_lift"] = relative_accuracy_lift(
            summary.get("top_3_accuracy", 0.0),
            args.baseline_top3,
        )
    print(json.dumps({"output": args.output, "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
