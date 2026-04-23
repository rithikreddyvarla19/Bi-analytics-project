from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def notify(status: str, **context):
    dag_run = context.get("dag_run")
    run_id = dag_run.run_id if dag_run else "manual"
    print(f"Notification placeholder | status={status} | run_id={run_id}")


with DAG(
    dag_id="retail_lakehouse_pipeline",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    schedule="@daily",
    tags=["data-engineering", "lakehouse", "retail"],
) as dag:
    generate_data = BashOperator(
        task_id="generate_data",
        bash_command=f"cd {PROJECT_ROOT} && python scripts/generate_data.py",
    )

    ingest_bronze = BashOperator(
        task_id="ingest_bronze",
        bash_command=f"cd {PROJECT_ROOT} && python scripts/ingest_to_bronze.py",
    )

    simulate_stream = BashOperator(
        task_id="simulate_stream",
        bash_command=f"cd {PROJECT_ROOT} && python scripts/streaming_simulator.py",
    )

    streaming_aggregate = BashOperator(
        task_id="streaming_aggregate",
        bash_command=f"cd {PROJECT_ROOT} && python spark_jobs/streaming_aggregations.py",
    )

    bronze_to_silver = BashOperator(
        task_id="bronze_to_silver",
        bash_command=f"cd {PROJECT_ROOT} && python spark_jobs/bronze_to_silver.py",
    )

    silver_to_gold = BashOperator(
        task_id="silver_to_gold",
        bash_command=f"cd {PROJECT_ROOT} && python spark_jobs/silver_to_gold.py",
    )

    build_warehouse = BashOperator(
        task_id="build_warehouse",
        bash_command=f"cd {PROJECT_ROOT} && python scripts/build_warehouse.py",
    )

    quality_checks = BashOperator(
        task_id="quality_checks",
        bash_command=f"cd {PROJECT_ROOT} && python scripts/run_quality_checks.py",
    )

    export_kpis = BashOperator(
        task_id="export_kpis",
        bash_command=f"cd {PROJECT_ROOT} && python scripts/export_kpis.py",
    )

    notify_success = PythonOperator(
        task_id="notify_success",
        python_callable=notify,
        op_kwargs={"status": "success"},
        trigger_rule="all_success",
    )

    notify_failure = PythonOperator(
        task_id="notify_failure",
        python_callable=notify,
        op_kwargs={"status": "failure"},
        trigger_rule="one_failed",
    )

    generate_data >> ingest_bronze >> [simulate_stream, bronze_to_silver]
    simulate_stream >> streaming_aggregate
    bronze_to_silver >> silver_to_gold >> build_warehouse >> quality_checks >> export_kpis
    [export_kpis, streaming_aggregate] >> [notify_success, notify_failure]
