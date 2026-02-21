"""
Prometheus Metrics Middleware

Automatically tracks every HTTP request:
  - Total request count (by method, path, status)
  - Latency histogram
  - Error counter for 4xx / 5xx
  - Active in-flight gauge
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    REQUEST_ERRORS,
    ACTIVE_REQUESTS,
)


def _normalise_path(path: str) -> str:
    """
    Collapse path parameters so Prometheus labels stay low-cardinality.
    e.g. /api/v1/energy/123 → /api/v1/energy/{id}
    """
    parts = path.strip("/").split("/")
    normalised = []
    for part in parts:
        if part.isdigit():
            normalised.append("{id}")
        else:
            normalised.append(part)
    return "/" + "/".join(normalised) if normalised else "/"


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        method = request.method
        path = _normalise_path(request.url.path)

        # Skip metrics endpoint itself to avoid recursion
        if path == "/metrics":
            return await call_next(request)

        ACTIVE_REQUESTS.inc()
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            # Unhandled error → 500
            REQUEST_ERRORS.labels(method=method, endpoint=path, status_code="500").inc()
            REQUEST_COUNT.labels(method=method, endpoint=path, status_code="500").inc()
            ACTIVE_REQUESTS.dec()
            raise

        elapsed = time.perf_counter() - start
        status = str(response.status_code)

        REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(elapsed)

        if response.status_code >= 400:
            REQUEST_ERRORS.labels(method=method, endpoint=path, status_code=status).inc()

        ACTIVE_REQUESTS.dec()
        return response
