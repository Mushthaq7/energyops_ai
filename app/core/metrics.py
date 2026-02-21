"""
Prometheus Metrics for GenAI Energy Analytics

Exposes key operational metrics:
  - HTTP request latency (histogram)
  - HTTP request count by status (counter)
  - HTTP error rate (counter)
  - Model / RAG response time (histogram)
  - Active requests (gauge)
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# ── HTTP metrics ──────────────────────────────────────────

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "Total HTTP 4xx/5xx responses",
    ["method", "endpoint", "status_code"],
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Number of in-flight requests",
)

# ── Model / RAG metrics ──────────────────────────────────

MODEL_RESPONSE_TIME = Histogram(
    "model_response_duration_seconds",
    "LLM / RAG model response time in seconds",
    ["operation"],  # "retrieval", "generation", "ask"
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

MODEL_REQUESTS = Counter(
    "model_requests_total",
    "Total model inference requests",
    ["operation", "status"],  # status: "success" | "error"
)

DOCUMENTS_INDEXED = Counter(
    "documents_indexed_total",
    "Total documents indexed into vector store",
)
