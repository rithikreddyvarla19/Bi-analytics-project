.PHONY: setup run-pipeline test lint airflow-init

setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

run-pipeline:
	python scripts/run_pipeline.py

test:
	pytest -q

lint:
	ruff check scripts spark_jobs tests

airflow-init:
	docker compose up -d postgres
	docker compose up airflow
