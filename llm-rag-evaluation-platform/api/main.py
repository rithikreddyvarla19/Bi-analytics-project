"""FastAPI entrypoint for the RAG chatbot API."""

from __future__ import annotations

from fastapi import Depends, FastAPI

from api.config import get_settings
from api.dependencies import get_feedback_store, get_metrics_store, get_rag_engine
from api.schemas import ChatRequest, ChatResponse, FeedbackRequest, HealthResponse, SourceResponse
from monitoring.feedback import FeedbackStore, UserFeedback
from monitoring.telemetry import InMemoryMetricsStore
from rag_pipeline.chains import RAGEngine

settings = get_settings()
app = FastAPI(
    title="LLM RAG Evaluation Platform",
    version="0.1.0",
    description="Enterprise RAG API with evaluation, citations, and monitoring.",
)


@app.get("/health", response_model=HealthResponse)
def health(engine: RAGEngine = Depends(get_rag_engine)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        vector_index_size=engine.vector_store.size,
        environment=settings.environment,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    engine: RAGEngine = Depends(get_rag_engine),
    metrics: InMemoryMetricsStore = Depends(get_metrics_store),
) -> ChatResponse:
    response = engine.ask(
        request.question,
        k=request.top_k,
        prompt_id=request.prompt_id,
        metadata_filter=request.metadata_filter,
    )
    metrics.increment("chat_requests")
    metrics.record_latency("chat", response.latency_ms)
    return ChatResponse(
        question=response.question,
        answer=response.answer,
        prompt_id=response.prompt_id,
        model=response.model,
        latency_ms=response.latency_ms,
        sources=[
            SourceResponse(id=source.id, score=source.score, text=source.text, metadata=source.metadata)
            for source in response.sources
        ],
    )


@app.post("/feedback")
def feedback(request: FeedbackRequest, store: FeedbackStore = Depends(get_feedback_store)) -> dict[str, str]:
    store.append(
        UserFeedback(
            trace_id=request.trace_id,
            rating=request.rating,
            comment=request.comment,
            metadata=request.metadata,
        )
    )
    return {"status": "accepted"}


@app.get("/metrics/summary")
def metrics_summary(metrics: InMemoryMetricsStore = Depends(get_metrics_store)) -> dict[str, object]:
    return {
        "counters": dict(metrics.counters),
        "chat_latency": metrics.latency_summary("chat"),
    }
