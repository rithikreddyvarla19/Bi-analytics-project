from pathlib import Path

from build_kpi_outputs import create_kpi_outputs
from etl_pipeline import run_pipeline
from generate_raw_data import DataConfig, generate_all


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    generate_all(project_root / "data" / "raw", DataConfig())
    run_pipeline(project_root)
    create_kpi_outputs(
        processed_dir=project_root / "data" / "processed",
        output_dir=project_root / "outputs",
        dashboard_export_dir=project_root / "dashboard_spec" / "datasets",
    )


if __name__ == "__main__":
    main()
