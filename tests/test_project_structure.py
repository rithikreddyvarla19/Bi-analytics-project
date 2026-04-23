from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_project_paths_exist():
    required = [
        ROOT / "scripts/run_pipeline.py",
        ROOT / "spark_jobs/bronze_to_silver.py",
        ROOT / "spark_jobs/silver_to_gold.py",
        ROOT / "airflow/dags/retail_lakehouse_dag.py",
        ROOT / "infra/terraform/main.tf",
        ROOT / ".github/workflows/ci.yml",
    ]
    for path in required:
        assert path.exists(), f"Missing required artifact: {path}"
