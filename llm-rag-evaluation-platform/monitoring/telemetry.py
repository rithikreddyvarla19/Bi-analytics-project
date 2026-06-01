"""Lightweight telemetry primitives used by API and dashboard."""

from __future__ import annotations

import statistics
import time
from collections import defaultdict
from contextlib import ContextDecorator
from dataclasses import dataclass, field


@dataclass
class LatencyTimer(ContextDecorator):
    name: str
    store: InMemoryMetricsStore | None = None
    started_at: float = field(default=0.0, init=False)
    elapsed_ms: float = field(default=0.0, init=False)

    def __enter__(self) -> LatencyTimer:
        self.started_at = time.perf_counter()
        return self

    def __exit__(self, *exc: object) -> None:
        self.elapsed_ms = round((time.perf_counter() - self.started_at) * 1000, 2)
        if self.store:
            self.store.record_latency(self.name, self.elapsed_ms)


class InMemoryMetricsStore:
    """Process-local metrics buffer for demos and smoke tests."""

    def __init__(self) -> None:
        self.latencies: dict[str, list[float]] = defaultdict(list)
        self.counters: dict[str, int] = defaultdict(int)

    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] += amount

    def record_latency(self, name: str, latency_ms: float) -> None:
        self.latencies[name].append(latency_ms)

    def latency_summary(self, name: str) -> dict[str, float]:
        values = self.latencies.get(name, [])
        if not values:
            return {"count": 0, "p50_ms": 0.0, "p95_ms": 0.0, "avg_ms": 0.0}
        ordered = sorted(values)
        p95_index = min(len(ordered) - 1, int(len(ordered) * 0.95))
        return {
            "count": len(values),
            "p50_ms": round(statistics.median(ordered), 2),
            "p95_ms": round(ordered[p95_index], 2),
            "avg_ms": round(statistics.mean(ordered), 2),
        }
