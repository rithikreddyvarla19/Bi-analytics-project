.PHONY: install install-prod test lint format ingest index evaluate api dashboard docker-up docker-down

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt

install-prod:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

lint:
	python -m ruff check .

format:
	python -m ruff format .

ingest:
	python scripts/ingest_documents.py --input sample_datasets/documents --output artifacts/chunks/chunks.jsonl

index:
	python scripts/build_faiss_index.py --chunks artifacts/chunks/chunks.jsonl --output artifacts/vector_index

evaluate:
	python scripts/run_evaluation.py --dataset sample_datasets/ground_truth/rag_eval.csv --index artifacts/vector_index

api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

dashboard:
	streamlit run dashboard/app.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v
