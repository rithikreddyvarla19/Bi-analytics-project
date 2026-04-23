from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

import pandas as pd

try:
    from common import DATA_ROOT, OUTPUT_ROOT, configure_logging, ensure_dir, write_run_metadata
except ModuleNotFoundError:
    from scripts.common import DATA_ROOT, OUTPUT_ROOT, configure_logging, ensure_dir, write_run_metadata

logger = configure_logging("run_pipeline")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_step(step_name: str, command: list[str]) -> float:
    logger.info("Starting step: %s", step_name)
    start = time.time()
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)
    elapsed = round(time.time() - start, 2)
    logger.info("Completed step: %s (%.2fs)", step_name, elapsed)
    return elapsed


def collect_stage_counts() -> dict[str, int]:
    counts = {}
    for stage in ["raw", "bronze", "silver", "gold", "warehouse"]:
        stage_path = DATA_ROOT / stage
        if stage_path.exists():
            counts[stage] = sum(1 for _ in stage_path.rglob("*") if _.is_file())
    return counts


def build_run_report(step_metrics: list[dict[str, object]]) -> None:
    ensure_dir(OUTPUT_ROOT / "observability")
    metrics_df = pd.DataFrame(step_metrics)
    metrics_df.to_csv(OUTPUT_ROOT / "observability" / "pipeline_step_metrics.csv", index=False)



def main() -> None:
    parser = argparse.ArgumentParser(description="Run end-to-end retail lakehouse pipeline")
    parser.add_argument("--skip-streaming", action="store_true")
    args = parser.parse_args()

    steps = [
        ("generate_data", ["python", "scripts/generate_data.py"]),
        ("ingest_to_bronze", ["python", "scripts/ingest_to_bronze.py"]),
    ]

    if not args.skip_streaming:
        steps.extend(
            [
                ("simulate_stream", ["python", "scripts/streaming_simulator.py"]),
                ("streaming_aggregations", ["python", "spark_jobs/streaming_aggregations.py"]),
            ]
        )

    steps.extend(
        [
            ("bronze_to_silver", ["python", "spark_jobs/bronze_to_silver.py"]),
            ("silver_to_gold", ["python", "spark_jobs/silver_to_gold.py"]),
            ("build_warehouse", ["python", "scripts/build_warehouse.py"]),
            ("run_quality_checks", ["python", "scripts/run_quality_checks.py"]),
            ("export_kpis", ["python", "scripts/export_kpis.py"]),
        ]
    )

    step_metrics: list[dict[str, object]] = []
    for step_name, cmd in steps:
        elapsed = run_step(step_name, cmd)
        step_metrics.append({"step": step_name, "duration_seconds": elapsed, "status": "success"})

    build_run_report(step_metrics)
    write_run_metadata(
        {
            "pipeline": "cloud_native_retail_lakehouse",
            "steps": step_metrics,
            "stage_file_counts": collect_stage_counts(),
        }
    )
    logger.info("Pipeline execution completed successfully")


if __name__ == "__main__":
    main()

