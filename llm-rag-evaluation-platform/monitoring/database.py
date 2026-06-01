"""PostgreSQL persistence models for chat traces and feedback."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone


def _sqlalchemy():
    try:
        from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text, create_engine
        from sqlalchemy.orm import declarative_base, sessionmaker
    except ImportError as exc:  # pragma: no cover - optional production dependency
        raise RuntimeError("Install sqlalchemy and psycopg2-binary for PostgreSQL monitoring.") from exc
    return JSON, Column, DateTime, Float, Integer, String, Text, create_engine, declarative_base, sessionmaker


JSON, Column, DateTime, Float, Integer, String, Text, create_engine, declarative_base, sessionmaker = _sqlalchemy()

Base = declarative_base()


class ChatTrace(Base):
    __tablename__ = "chat_traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    prompt_id = Column(String(128), nullable=False)
    model = Column(String(128), nullable=False)
    latency_ms = Column(Float, nullable=False)
    sources = Column(JSON, nullable=False, default=list)
    evaluation = Column(JSON, nullable=True)


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    trace_id = Column(String(128), nullable=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=False, default=dict)


def database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql+psycopg2://rag:rag@postgres:5432/rag_platform")


def create_session_factory(url: str | None = None):
    engine = create_engine(url or database_url(), pool_pre_ping=True, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def session_scope(url: str | None = None) -> Iterator[object]:
    factory = create_session_factory(url)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
