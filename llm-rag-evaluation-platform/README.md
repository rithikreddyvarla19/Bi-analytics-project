# LLM-Powered Knowledge Assistant with RAG

Enterprise Retrieval-Augmented Generation knowledge assistant for answering 50K+ technical documents with grounded, source-linked responses, semantic search, prompt experimentation, LLM hyperparameter tuning, MLflow tracking, PostgreSQL feedback storage, and a Streamlit monitoring dashboard.

## What This Builds

- Ingests 50,000+ PDFs, CSVs, markdown, and text files with deterministic checksums.
- Chunks documents with overlap-aware recursive splitting.
- Generates embeddings with OpenAI, HuggingFace Transformers, PyTorch/TensorFlow-ready backends, or deterministic local hashing.
- Stores and searches vectors with FAISS, with a pure-Python fallback for local tests.
- Serves a source-linked knowledge assistant through FastAPI.
- Supports GPT-style hosted models and open-source HuggingFace models.
- Implements semantic search, prompt engineering, few-shot prompting, and prompt/retriever tuning.
- Evaluates top-3 answer accuracy, faithfulness, hallucination rate, calibration score, context precision, context recall, and answer relevancy.
- Validates ground-truth datasets before evaluation runs.
- Compares prompt variants and tracks experiments in MLflow.
- Displays accuracy metrics, hallucination trends, calibration scores, latency, user feedback, and prompt comparisons in Streamlit.
- Ships with Docker Compose, GitHub Actions, sample datasets, and AWS ECS deployment scaffolding.

## Architecture

```mermaid
flowchart LR
    Sources[PDF, CSV, Text Sources] --> Loader[Document Loaders]
    Loader --> Chunker[Recursive Chunker]
    Chunker --> Embedder[Embedding Pipeline]
    Embedder --> FAISS[FAISS Vector Index]
    FAISS --> Retriever[Retriever]
    Retriever --> Prompt[Prompt Registry]
    Prompt --> LLM[OpenAI or HuggingFace LLM]
    LLM --> API[FastAPI Knowledge Assistant API]
    API --> Eval[Evaluation Metrics]
    API --> Feedback[User Feedback]
    Eval --> MLflow[MLflow]
    Feedback --> Postgres[(PostgreSQL)]
    MLflow --> Dashboard[Streamlit Dashboard]
    Postgres --> Dashboard
```

Detailed architecture is in [docs/architecture.md](docs/architecture.md).

## Repository Layout

```text
ingestion/        Document loading and chunking
embeddings/       Embedding providers and batch indexing
rag_pipeline/     FAISS search, prompts, LLM providers, RAG orchestration
evaluation/       Ground-truth validation, metrics, prompt experiments, tuning
monitoring/       Feedback, telemetry, PostgreSQL models, MLflow adapter
dashboard/        Streamlit monitoring dashboard
api/              FastAPI application
tests/            Unit tests for core logic
docs/             Architecture, evaluation, deployment docs
deploy/aws/       ECS and Terraform deployment scaffolding
sample_datasets/  Demo documents and ground-truth examples
screenshots/      Release/demo screenshot drop zone
```

## Quick Start

```bash
cd llm-rag-evaluation-platform
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python scripts/seed_sample_index.py
python -m pytest -q
```

Run the API:

```bash
python -m pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Ask a technical-document question:

```bash
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"How often is hallucination monitoring performed?\",\"top_k\":3,\"prompt_id\":\"few_shot_technical\"}"
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

## Local Docker

```bash
cp .env.example .env
docker compose up --build
```

Open:

- FastAPI docs: http://localhost:8000/docs
- Streamlit dashboard: http://localhost:8501
- MLflow: http://localhost:5000

Seed a sample index in Docker:

```bash
docker compose run --rm api python scripts/seed_sample_index.py
```

## Production Configuration

Set these environment variables:

```bash
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=<secret>
VECTOR_INDEX_PATH=artifacts/vector_index
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/rag_platform
MLFLOW_TRACKING_URI=http://mlflow.your-domain.internal:5000
```

For open-source models:

```bash
EMBEDDING_PROVIDER=huggingface
LLM_PROVIDER=huggingface
```

## Core Workflows

Ingest documents:

```bash
python scripts/ingest_documents.py \
  --input /path/to/documents \
  --output artifacts/chunks/chunks.jsonl \
  --chunk-size 900 \
  --chunk-overlap 120
```

Build the vector index:

```bash
python scripts/build_faiss_index.py \
  --chunks artifacts/chunks/chunks.jsonl \
  --output artifacts/vector_index \
  --provider openai
```

Evaluate top-3 accuracy, calibration, hallucination rate, and groundedness:

```bash
python scripts/run_evaluation.py \
  --dataset sample_datasets/ground_truth/rag_eval.csv \
  --index artifacts/vector_index \
  --output artifacts/evaluation/results.csv \
  --baseline-top3 0.60 \
  --log-mlflow
```

## API Endpoints

- `GET /health`
- `POST /chat`
- `POST /feedback`
- `GET /metrics/summary`

## Testing and CI

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest -q
```

GitHub Actions runs lint and unit tests with lightweight dependencies so CI remains fast and deterministic.

## Resume-Aligned Outcomes

This project is structured around the resume scope:

- End-to-end RAG pipeline for 50K+ technical documents using Python, LangChain-compatible adapters, FAISS, PyTorch/TensorFlow-ready runtime checks, HuggingFace Transformers, and GPT-based providers.
- Grounded source-linked responses for product stakeholders through governed prompt templates.
- Semantic search, few-shot prompting, and prompt/retriever hyperparameter tuning against a curated ground-truth dataset.
- Evaluation reports that track top-3 answer accuracy, faithfulness, hallucination rate, calibration score, latency, and user feedback for continuous iteration.
- The monitoring model supports reporting accuracy lift against a baseline, including the 27% top-3 accuracy improvement described in the project summary.

## Deployment

See [docs/deployment_guide.md](docs/deployment_guide.md) and [deploy/aws/README.md](deploy/aws/README.md) for AWS ECS deployment guidance.
