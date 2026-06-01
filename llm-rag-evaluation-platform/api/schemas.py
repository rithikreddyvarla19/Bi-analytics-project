"""API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    prompt_id: str = "enterprise_cited"
    metadata_filter: dict[str, object] | None = None


class SourceResponse(BaseModel):
    id: str
    score: float
    text: str
    metadata: dict[str, object]


class ChatResponse(BaseModel):
    question: str
    answer: str
    prompt_id: str
    model: str
    latency_ms: float
    sources: list[SourceResponse]


class FeedbackRequest(BaseModel):
    trace_id: str | None = None
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""
    metadata: dict[str, object] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    vector_index_size: int
    environment: str
